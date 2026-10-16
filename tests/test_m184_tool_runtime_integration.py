from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from core.tool_gateway import (
    ToolCapability,
    ToolGatewayManager,
    ToolGatewayStatus,
)
from core.tool_runtime_integration import (
    ToolRuntimeConfig,
    ToolRuntimeIntegration,
    ToolRuntimeStatus,
)
from tests.test_m178_runtime_composition_root import RecordingProvider, dependencies


def request(prompt="hola"):
    return LLMRequest(
        prompt=prompt,
        system_prompt="system",
        model="local",
        max_tokens=20,
        temperature=0.1,
        metadata={"source": "test"},
    )


def runtime(*, config=None, capability=None, handler=None):
    gateway = ToolGatewayManager()
    if capability is not None:
        gateway.register_capability(capability, handler)
    return ToolRuntimeIntegration(gateway, config=config), gateway


def test_config_normalizes_prefix():
    assert ToolRuntimeConfig(command_prefix=" /tool ").command_prefix == "/tool"


def test_config_rejects_blank_prefix():
    with pytest.raises(ValueError, match="prefix"):
        ToolRuntimeConfig(command_prefix=" ")


def test_config_rejects_tiny_payload_limit():
    with pytest.raises(ValueError, match="payload"):
        ToolRuntimeConfig(maximum_payload_characters=1)


def test_non_tool_turn_keeps_request_unchanged():
    item, gateway = runtime()
    original = request()
    result = item.enrich(
        owner="Carlos", session_id="desktop-main", text="hola", request=original
    )
    assert result.status is ToolRuntimeStatus.NOT_REQUESTED
    assert result.request is original
    assert len(gateway.history) == 1
    assert gateway.audit_log == ()


def test_disabled_runtime_never_observes_or_executes():
    item, gateway = runtime(config=ToolRuntimeConfig(enabled=False))
    result = item.enrich(
        owner="Carlos",
        session_id="desktop-main",
        text='/tool weather.current {"city":"Buenos Aires"}',
        request=request(),
    )
    assert result.rationale == ("tool_runtime_disabled",)
    assert gateway.history == gateway.audit_log == ()


def test_blank_identity_is_rejected():
    item, _ = runtime()
    with pytest.raises(ValueError, match="owner and session"):
        item.enrich(owner=" ", session_id="x", text="hola", request=request())


def test_command_requires_capability():
    item, _ = runtime()
    with pytest.raises(ValueError, match="capability"):
        item.enrich(owner="Carlos", session_id="s", text="/tool", request=request())


def test_payload_must_be_valid_json():
    item, _ = runtime()
    with pytest.raises(ValueError, match="valid JSON"):
        item.enrich(
            owner="Carlos", session_id="s", text="/tool echo {bad", request=request()
        )


def test_payload_must_be_object():
    item, _ = runtime()
    with pytest.raises(ValueError, match="JSON object"):
        item.enrich(
            owner="Carlos", session_id="s", text="/tool echo []", request=request()
        )


def test_payload_limit_is_enforced():
    item, _ = runtime(config=ToolRuntimeConfig(maximum_payload_characters=5))
    with pytest.raises(ValueError, match="exceeds"):
        item.enrich(
            owner="Carlos",
            session_id="s",
            text='/tool echo {"x":123}',
            request=request(),
        )


def test_registered_read_only_tool_executes_through_gateway():
    item, gateway = runtime(
        capability=ToolCapability("weather.current", "Clima local"),
        handler=lambda payload: {"city": payload["city"], "temperature": 21},
    )
    result = item.enrich(
        owner="Carlos",
        session_id="desktop-main",
        text='/tool weather.current {"city":"Buenos Aires"}',
        request=request(),
    )
    assert result.status is ToolRuntimeStatus.EXECUTED
    assert result.gateway_status is ToolGatewayStatus.ROUTED
    assert result.gateway_result is gateway.last_result
    assert result.gateway_result is not None


def test_tool_output_is_added_to_prompt_as_evidence():
    item, _ = runtime(
        capability=ToolCapability("echo", "Echo"),
        handler=lambda payload: payload,
    )
    result = item.enrich(
        owner="Carlos",
        session_id="s",
        text='/tool echo {"value":"ok"}',
        request=request("responde"),
    )
    assert "Resultado gobernado de herramienta local" in result.request.prompt
    assert '"value": "ok"' in result.request.prompt
    assert result.request.metadata["tool_context"] == "included"


def test_original_llm_request_fields_are_preserved():
    item, _ = runtime(
        capability=ToolCapability("echo", "Echo"), handler=lambda payload: payload
    )
    original = request("base")
    enriched = item.enrich(
        owner="Carlos",
        session_id="s",
        text='/tool echo {"x":1}',
        request=original,
    ).request
    assert (enriched.system_prompt, enriched.model, enriched.max_tokens) == (
        "system",
        "local",
        20,
    )
    assert enriched.metadata["source"] == "test"


def test_prompt_inclusion_can_be_disabled():
    item, _ = runtime(
        config=ToolRuntimeConfig(include_output_in_prompt=False),
        capability=ToolCapability("echo", "Echo"),
        handler=lambda payload: payload,
    )
    original = request()
    result = item.enrich(
        owner="Carlos",
        session_id="s",
        text='/tool echo {"x":1}',
        request=original,
    )
    assert result.request is original
    assert result.succeeded


def test_unknown_tool_is_blocked_by_existing_gateway_policy():
    item, gateway = runtime()
    result = item.enrich(
        owner="Carlos", session_id="s", text="/tool missing", request=request()
    )
    assert result.status is ToolRuntimeStatus.BLOCKED
    assert result.rationale == ("capability_not_registered",)
    assert gateway.last_result is result.gateway_result


def test_handler_failure_is_contained():
    def boom(payload):
        raise RuntimeError("secret details")

    item, _ = runtime(capability=ToolCapability("fail", "Fails safely"), handler=boom)
    result = item.enrich(
        owner="Carlos", session_id="s", text="/tool fail", request=request()
    )
    assert result.status is ToolRuntimeStatus.BLOCKED
    assert result.gateway_result.error == "handler_error:RuntimeError"
    assert "secret details" not in result.gateway_result.error


def test_mutating_capability_is_blocked_before_gateway_execution():
    item, gateway = runtime(
        capability=ToolCapability(
            "files.write", "Writes file", metadata={"side_effect": "write"}
        ),
        handler=lambda payload: {"written": True},
    )
    result = item.enrich(
        owner="Carlos", session_id="s", text="/tool files.write", request=request()
    )
    assert result.status is ToolRuntimeStatus.BLOCKED
    assert result.rationale == ("platform_mutation_not_allowed",)
    assert gateway.audit_log == ()


def test_invocation_id_is_stable_for_same_identity_and_payload():
    item, _ = runtime()
    first = item.enrich(
        owner="Carlos", session_id="s", text='/tool missing {"x":1}', request=request()
    )
    second = item.enrich(
        owner="Carlos", session_id="s", text='/tool missing {"x":1}', request=request()
    )
    assert first.invocation.invocation_id == second.invocation.invocation_id


def test_composition_does_not_touch_tool_runtime():
    class RecordingToolRuntime:
        def __init__(self):
            self.calls = []

        def enrich(self, **kwargs):
            self.calls.append(kwargs)

    port = RecordingToolRuntime()
    RuntimeCompositionRoot(replace(dependencies(), tool_runtime=port)).compose()
    assert port.calls == []


def test_composed_pipeline_executes_tool_before_provider():
    provider = RecordingProvider()
    item, gateway = runtime(
        capability=ToolCapability("weather.current", "Clima"),
        handler=lambda payload: {"temperature": 21},
    )
    deps = replace(dependencies(provider=provider), tool_runtime=item)
    result = (
        RuntimeCompositionRoot(deps)
        .build()
        .process(
            GovernedConversationPipelineRequest(
                owner="Carlos",
                session_id="desktop-main",
                text="/tool weather.current",
            )
        )
    )
    assert result.provider_call_performed
    assert len(provider.calls) == 1
    assert "Resultado gobernado de herramienta local" in provider.calls[0].prompt
    assert len(gateway.audit_log) == 1


def test_context_models_are_immutable():
    item, _ = runtime()
    result = item.enrich(owner="Carlos", session_id="s", text="hola", request=request())
    with pytest.raises(FrozenInstanceError):
        result.status = ToolRuntimeStatus.FAILED
