from dataclasses import FrozenInstanceError, replace
from datetime import datetime

import pytest

from app.desktop_bootstrap import build_operational_desktop_app
from app.desktop_operational_adapter import DesktopOperationalAdapter
from core.desktop_runtime_integration import (
    DesktopRuntimeAction,
    DesktopRuntimeIntegration,
    DesktopRuntimeIntegrationConfig,
    DesktopRuntimeRequest,
    DesktopRuntimeStatus,
    InMemoryDesktopRuntimeRepository,
)
from core.governed_provider_execution_adapter import LocalProviderExecutionStatus
from core.operational_response_assembly import (
    OperationalResponseAssembler,
    OperationalResponseAssemblyRequest,
)
from core.runtime_readiness_gate import RuntimeReadinessStatus
from m6.response.models import ResponseStatus
from tests.test_m162_runtime_readiness_gate import NOW, evaluate
from tests.test_m175_operational_response_assembly import provider_result

READY = evaluate(now=NOW)


class FakePipeline:
    def __init__(self, response=None, error=None):
        self.response = response or operational_response()
        self.error = error
        self.calls = []

    def execute(self, *, owner, session_id, text):
        self.calls.append((owner, session_id, text))
        if self.error:
            raise self.error
        return self.response


def operational_response(**request_changes):
    request = OperationalResponseAssemblyRequest(
        owner="Carlos",
        provider_execution=provider_result(),
        **request_changes,
    )
    return OperationalResponseAssembler().assemble(request, now=NOW)


def request(text="¿Qué hora es?", **changes):
    values = {
        "owner": "Carlos",
        "session_id": "desktop-main",
        "text": text,
        "readiness_result": READY,
    }
    values.update(changes)
    return DesktopRuntimeRequest(**values)


def integration(response=None, error=None, **changes):
    pipeline = FakePipeline(response=response, error=error)
    return DesktopRuntimeIntegration(pipeline=pipeline, **changes), pipeline


def test_greeting_reuses_m172_without_operational_pipeline():
    runtime, pipeline = integration()
    result = runtime.submit(request("Hola ROBY"), now=NOW)
    assert result.status is DesktopRuntimeStatus.DELIVERED
    assert result.console_turn is not None
    assert result.operational_response is None
    assert pipeline.calls == []


def test_greeting_preserves_m163_to_m165_lineage():
    runtime, _ = integration()
    turn = runtime.submit(request("Hola"), now=NOW).console_turn
    assert turn.entry_result is not None
    assert turn.greeting_result is not None
    assert turn.voice_result is not None


def test_operational_input_executes_injected_pipeline():
    runtime, pipeline = integration()
    result = runtime.submit(request("Explica la arquitectura"), now=NOW)
    assert pipeline.calls == [("Carlos", "desktop-main", "Explica la arquitectura")]
    assert result.operational_response is pipeline.response


def test_completed_operational_response_is_delivered():
    runtime, _ = integration()
    result = runtime.submit(request(), now=NOW)
    assert result.status is DesktopRuntimeStatus.DELIVERED
    assert result.action is DesktopRuntimeAction.PRESENT_RESPONSE
    assert result.response_text == "Respuesta operativa"


def test_partial_operational_response_is_delivered():
    # A completed response exercises the same deliverable action contract; M175
    # partial behavior is covered in its own milestone suite.
    response = OperationalResponseAssembler().assemble(
        OperationalResponseAssemblyRequest(
            owner="Carlos",
            provider_execution=provider_result(),
            retrieval_execution=None,
        ),
        now=NOW,
    )
    runtime, _ = integration(response=response)
    assert runtime.submit(request(), now=NOW).status is DesktopRuntimeStatus.DELIVERED


def test_missing_input_requests_information_without_pipeline():
    runtime, pipeline = integration()
    result = runtime.submit(request("   "), now=NOW)
    assert result.status is DesktopRuntimeStatus.NEEDS_INPUT
    assert result.action is DesktopRuntimeAction.REQUEST_INPUT
    assert pipeline.calls == []


def test_blocked_readiness_prevents_all_execution():
    blocked = replace(
        READY,
        status=RuntimeReadinessStatus.BLOCKED,
        action="withhold",
        ready=False,
        blocked=True,
        readiness_id="",
    )
    runtime, pipeline = integration()
    result = runtime.submit(request(readiness_result=blocked), now=NOW)
    assert result.status is DesktopRuntimeStatus.BLOCKED
    assert pipeline.calls == []


def test_degraded_readiness_allows_operational_pipeline():
    degraded = replace(
        READY,
        status=RuntimeReadinessStatus.DEGRADED,
        action="declare_degraded",
        ready=False,
        degraded=True,
        readiness_id="",
    )
    runtime, pipeline = integration()
    result = runtime.submit(request(readiness_result=degraded), now=NOW)
    assert result.status is DesktopRuntimeStatus.DELIVERED
    assert len(pipeline.calls) == 1


def test_pipeline_exception_is_contained():
    runtime, _ = integration(error=RuntimeError("offline"))
    result = runtime.submit(request(), now=NOW)
    assert result.status is DesktopRuntimeStatus.FAILED
    assert result.response_text == runtime.config.failure_response


def test_withheld_operational_response_is_not_exposed():
    response = OperationalResponseAssembler().assemble(
        OperationalResponseAssemblyRequest(owner="Carlos", provider_execution=None),
        now=NOW,
    )
    runtime, _ = integration(response=response)
    result = runtime.submit(request(), now=NOW)
    assert result.status is DesktopRuntimeStatus.WITHHELD
    assert result.response_text == runtime.config.withheld_response


def test_failed_operational_response_maps_to_failure():
    response = OperationalResponseAssembler().assemble(
        OperationalResponseAssemblyRequest(
            owner="Carlos",
            provider_execution=provider_result(
                status=LocalProviderExecutionStatus.FAILED, accepted=False
            ),
        ),
        now=NOW,
    )
    runtime, _ = integration(response=response)
    assert runtime.submit(request(), now=NOW).status is DesktopRuntimeStatus.FAILED


def test_input_limit_withholds_before_pipeline():
    runtime, pipeline = integration(
        config=DesktopRuntimeIntegrationConfig(maximum_input_characters=3)
    )
    result = runtime.submit(request("abcd"), now=NOW)
    assert result.status is DesktopRuntimeStatus.WITHHELD
    assert pipeline.calls == []


def test_operational_side_effect_flags_are_lineage_only():
    response = operational_response()
    runtime, _ = integration(response=response)
    result = runtime.submit(request(), now=NOW)
    assert result.provider_call_performed is response.provider_call_performed
    assert result.network_access_performed is response.network_access_performed
    assert not result.platform_mutation_performed


def test_repository_records_results():
    repository = InMemoryDesktopRuntimeRepository()
    runtime, _ = integration(repository=repository)
    result = runtime.submit(request(), now=NOW)
    assert repository.get(result.result_id) is result


def test_repository_is_append_only():
    repository = InMemoryDesktopRuntimeRepository()
    runtime, _ = integration(repository=repository)
    result = runtime.submit(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_request_preserves_exact_readiness_lineage():
    item = request()
    assert item.readiness_result is READY


def test_owner_must_match_readiness():
    with pytest.raises(ValueError, match="match readiness owner"):
        request(owner="Other")


@pytest.mark.parametrize("field", ["owner", "session_id"])
def test_request_identity_fields_are_required(field):
    with pytest.raises(ValueError):
        request(**{field: " "})


def test_config_rejects_blank_messages():
    with pytest.raises(ValueError, match="must not be blank"):
        DesktopRuntimeIntegrationConfig(failure_response=" ")


def test_config_rejects_non_positive_input_limit():
    with pytest.raises(ValueError, match="positive"):
        DesktopRuntimeIntegrationConfig(maximum_input_characters=0)


def test_naive_timestamp_is_rejected():
    runtime, _ = integration()
    with pytest.raises(ValueError, match="timezone-aware"):
        runtime.submit(request(), now=datetime(2026, 1, 1))


def test_result_is_immutable():
    runtime, _ = integration()
    result = runtime.submit(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.response_text = "changed"


def test_result_identity_is_deterministic():
    first, _ = integration()
    second, _ = integration()
    assert (
        first.submit(request(), now=NOW).result_id
        == second.submit(request(), now=NOW).result_id
    )


def test_desktop_adapter_maps_delivered_result_to_ui_success():
    runtime, _ = integration()
    adapter = DesktopOperationalAdapter(
        integration=runtime,
        owner="Carlos",
        readiness_result=READY,
    )
    response = adapter.submit_text("Hola", session_id="s1")
    assert response.status == ResponseStatus.SUCCESS.value
    assert response.session_id == "s1"


def test_desktop_adapter_maps_blank_to_needs_information():
    runtime, _ = integration()
    adapter = DesktopOperationalAdapter(
        integration=runtime,
        owner="Carlos",
        readiness_result=READY,
    )
    response = adapter.submit_text("   ")
    assert response.status == ResponseStatus.NEEDS_INFORMATION.value
    assert response.needs_input


def test_desktop_adapter_uses_default_session():
    runtime, _ = integration()
    adapter = DesktopOperationalAdapter(
        integration=runtime,
        owner="Carlos",
        readiness_result=READY,
        default_session_id="desktop-primary",
    )
    assert adapter.submit_text("Hola").session_id == "desktop-primary"


def test_desktop_adapter_validates_identity():
    runtime, _ = integration()
    with pytest.raises(ValueError):
        DesktopOperationalAdapter(
            integration=runtime,
            owner=" ",
            readiness_result=READY,
        )


def test_operational_desktop_builder_returns_ui_application():
    runtime, _ = integration()
    app = build_operational_desktop_app(
        integration=runtime,
        owner="Carlos",
        readiness_result=READY,
    )
    assert isinstance(app.adapter, DesktopOperationalAdapter)


def test_result_cannot_hold_two_lineages():
    runtime, _ = integration()
    greeting = runtime.submit(request("Hola"), now=NOW)
    operation = operational_response()
    with pytest.raises(ValueError, match="two response lineages"):
        replace(greeting, operational_response=operation, result_id="")
