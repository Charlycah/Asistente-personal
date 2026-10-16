from pathlib import Path

import pytest

from core.governed_external_intelligence import (
    ExternalExecutionScope,
    ExternalIntelligenceCapability,
    ExternalIntelligenceRequest,
    ExternalIntelligenceStatus,
    GovernedExternalProviderIntegration,
)
from core.governed_provider_execution_adapter import (
    GovernedProviderExecutionAdapter,
    LocalProviderExecutionConfig,
    LocalProviderExecutionRequest,
    LocalProviderExecutionStatus,
)
from core.llm_provider import LLMRequest, LLMResponse
from tests.test_m173_governed_provider_execution_adapter import (
    NOW,
    RecordingProvider,
    local_route,
    remote_route,
)


def _external_request(target_id: str = "ollama") -> ExternalIntelligenceRequest:
    return ExternalIntelligenceRequest(
        request_id=f"external-{target_id}",
        owner="Carlos",
        capability=ExternalIntelligenceCapability.INFERENCE_PROVIDER,
        purpose="admit governed provider result as subordinate evidence",
        target_id=target_id,
    )


def _execution(route=None, provider=None, config=None):
    route = route or local_route()
    provider = provider or RecordingProvider()
    request = LocalProviderExecutionRequest(
        owner="Carlos",
        route=route,
        inference_request=LLMRequest(prompt="Hola ROBY"),
    )
    result = GovernedProviderExecutionAdapter(
        (provider,),
        config=config,
    ).execute(request, now=NOW)
    return result, provider


def test_m400_3_admits_completed_ollama_execution() -> None:
    execution, provider = _execution()
    envelope = GovernedExternalProviderIntegration().admit_execution_result(
        _external_request(),
        execution,
        network_used=True,
    )
    assert len(provider.calls) == 1
    assert envelope.status is ExternalIntelligenceStatus.ACCEPTED
    assert envelope.inference is not None
    assert envelope.inference.provider == "ollama"
    assert envelope.provenance.execution_scope is ExternalExecutionScope.LOCAL
    assert envelope.provenance.network_used is True
    assert envelope.provenance.trace_ids == (
        execution.request.route.route_id,
        execution.execution_id,
    )
    assert envelope.cognitive_authority_granted is False


def test_m400_3_integration_does_not_execute_provider_itself() -> None:
    source = Path(
        "core/governed_external_intelligence/provider_integration.py"
    ).read_text(encoding="utf-8")
    assert ".generate(" not in source
    assert "GovernedProviderExecutionAdapter(" not in source
    assert "GovernedProviderRouter(" not in source


def test_m400_3_requires_existing_attempted_execution() -> None:
    route = local_route()
    request = LocalProviderExecutionRequest(
        owner="Carlos",
        route=route,
        inference_request=LLMRequest(prompt="Hola ROBY"),
        execution_requested=False,
    )
    result = GovernedProviderExecutionAdapter((RecordingProvider(),)).execute(
        request,
        now=NOW,
    )
    assert result.status is LocalProviderExecutionStatus.NOT_APPLICABLE
    with pytest.raises(ValueError, match="attempted execution"):
        GovernedExternalProviderIntegration().admit_execution_result(
            _external_request(),
            result,
            network_used=False,
        )


def test_m400_3_preserves_provider_failure_as_rejected_evidence() -> None:
    response = LLMResponse(
        text="",
        provider="ollama",
        model="llama3",
        accepted=False,
        error="provider_failure",
    )
    execution, _ = _execution(provider=RecordingProvider(response=response))
    assert execution.status is LocalProviderExecutionStatus.FAILED
    envelope = GovernedExternalProviderIntegration().admit_execution_result(
        _external_request(),
        execution,
        network_used=True,
    )
    assert envelope.status is ExternalIntelligenceStatus.REJECTED
    assert envelope.inference is not None
    assert envelope.inference.provider_error == "provider_failure"


def test_m400_3_admits_remote_only_after_existing_governed_execution() -> None:
    route = remote_route()
    config = LocalProviderExecutionConfig(allow_remote_execution=True)
    execution, provider = _execution(
        route=route,
        provider=RecordingProvider(
            "gemini",
            response=LLMResponse(
                text="remote candidate",
                provider="gemini",
                model="gemini",
            ),
        ),
        config=config,
    )
    assert execution.status is LocalProviderExecutionStatus.COMPLETED
    envelope = GovernedExternalProviderIntegration().admit_execution_result(
        _external_request("gemini"),
        execution,
        network_used=True,
    )
    assert len(provider.calls) == 1
    assert envelope.provenance.execution_scope is ExternalExecutionScope.REMOTE
    assert envelope.provenance.actor_id == "gemini"
    assert envelope.cognitive_authority_granted is False


def test_m400_3_rejects_target_route_mismatch() -> None:
    execution, _ = _execution()
    with pytest.raises(ValueError, match="target must match governed route"):
        GovernedExternalProviderIntegration().admit_execution_result(
            _external_request("gemini"),
            execution,
            network_used=True,
        )


def test_m400_3_rejects_owner_mismatch() -> None:
    execution, _ = _execution()
    request = ExternalIntelligenceRequest(
        request_id="other-owner",
        owner="Cristina",
        capability="inference_provider",
        purpose="test mismatch",
        target_id="ollama",
    )
    with pytest.raises(ValueError, match="owner must match"):
        GovernedExternalProviderIntegration().admit_execution_result(
            request,
            execution,
            network_used=True,
        )


def test_m400_3_requires_inference_capability() -> None:
    execution, _ = _execution()
    request = ExternalIntelligenceRequest(
        request_id="source-request",
        owner="Carlos",
        capability="information_source",
        purpose="not provider inference",
        target_id="ollama",
    )
    with pytest.raises(ValueError, match="inference capability"):
        GovernedExternalProviderIntegration().admit_execution_result(
            request,
            execution,
            network_used=True,
        )


def test_m400_3_keeps_network_use_separate_from_execution_scope() -> None:
    execution, _ = _execution()
    envelope = GovernedExternalProviderIntegration().admit_execution_result(
        _external_request(),
        execution,
        network_used=False,
    )
    assert envelope.provenance.execution_scope is ExternalExecutionScope.LOCAL
    assert envelope.provenance.network_used is False


def test_m400_3_integration_has_no_cognitive_authority() -> None:
    integration = GovernedExternalProviderIntegration()
    assert integration.integration_id == "external_intelligence_provider_integration"
    assert not hasattr(integration, "authority_id")
    for forbidden in (
        "route",
        "select_provider",
        "generate",
        "decide",
        "plan",
        "remember",
        "mutate",
    ):
        assert not hasattr(integration, forbidden)


def test_m400_3_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M400_3_GOVERNED_EXTERNAL_INTELLIGENCE_PROVIDER_INTEGRATION.md"
    ).read_text(encoding="utf-8")
    assert "provider execution → external evidence envelope" in document
    assert "capacidad/evidencia externa ≠ autoridad cognitiva" in document
    assert "no selecciona ni ejecuta providers" in document
    assert "Ollama" in document
    assert "Gemini" in document
    assert "Mistral" in document
