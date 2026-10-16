from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.governed_external_intelligence import (
    ExternalExecutionScope,
    ExternalIntelligenceCapability,
    ExternalIntelligenceProvenance,
    ExternalIntelligenceRequest,
    ExternalIntelligenceStatus,
    GovernedExternalIntelligenceBoundary,
)
from core.llm_provider import LLMResponse

NOW = datetime(2026, 8, 10, 22, 0, tzinfo=timezone.utc)


def _provenance(
    actor_id: str,
    capability: ExternalIntelligenceCapability,
    *,
    scope: ExternalExecutionScope,
    network_used: bool,
) -> ExternalIntelligenceProvenance:
    return ExternalIntelligenceProvenance(
        actor_id=actor_id,
        capability=capability,
        execution_scope=scope,
        network_used=network_used,
        observed_at=NOW,
        trace_ids=("trace-1",),
    )


def test_m400_2_boundary_has_non_cognitive_boundary_id() -> None:
    boundary = GovernedExternalIntelligenceBoundary()
    assert boundary.boundary_id == "external_intelligence_boundary"
    assert not hasattr(boundary, "authority_id")


def test_m400_2_request_requires_explicit_owner_and_purpose() -> None:
    with pytest.raises(ValueError, match="owner"):
        ExternalIntelligenceRequest(
            request_id="req-1",
            owner=" ",
            capability="inference_provider",
            purpose="answer request",
        )
    with pytest.raises(ValueError, match="purpose"):
        ExternalIntelligenceRequest(
            request_id="req-1",
            owner="roby",
            capability="inference_provider",
            purpose=" ",
        )


def test_m400_2_admits_local_ollama_as_subordinate_inference() -> None:
    request = ExternalIntelligenceRequest(
        request_id="req-ollama",
        owner="roby",
        capability=ExternalIntelligenceCapability.INFERENCE_PROVIDER,
        purpose="generate candidate language",
        target_id="ollama",
    )
    provenance = _provenance(
        "ollama",
        ExternalIntelligenceCapability.INFERENCE_PROVIDER,
        scope=ExternalExecutionScope.LOCAL,
        network_used=True,
    )
    envelope = GovernedExternalIntelligenceBoundary().admit_inference(
        request,
        LLMResponse(text="candidate", provider="ollama", model="local-model"),
        provenance,
    )
    assert envelope.status is ExternalIntelligenceStatus.ACCEPTED
    assert envelope.inference is not None
    assert envelope.inference.provider == "ollama"
    assert envelope.provenance.execution_scope is ExternalExecutionScope.LOCAL
    assert envelope.cognitive_authority_granted is False
    assert "provider_does_not_gain_cognitive_authority" in envelope.rationale


def test_m400_2_admits_remote_provider_without_promoting_authority() -> None:
    request = ExternalIntelligenceRequest(
        request_id="req-gemini",
        owner="roby",
        capability="inference_provider",
        purpose="external inference",
        target_id="gemini",
    )
    provenance = _provenance(
        "gemini",
        ExternalIntelligenceCapability.INFERENCE_PROVIDER,
        scope=ExternalExecutionScope.REMOTE,
        network_used=True,
    )
    envelope = GovernedExternalIntelligenceBoundary().admit_inference(
        request,
        LLMResponse(text="candidate", provider="gemini"),
        provenance,
    )
    assert envelope.cognitive_authority_granted is False
    assert envelope.provenance.actor_id == "gemini"


def test_m400_2_rejected_provider_response_remains_evidence() -> None:
    request = ExternalIntelligenceRequest(
        request_id="req-mistral",
        owner="roby",
        capability="inference_provider",
        purpose="external inference",
        target_id="mistral",
    )
    provenance = _provenance(
        "mistral",
        ExternalIntelligenceCapability.INFERENCE_PROVIDER,
        scope=ExternalExecutionScope.REMOTE,
        network_used=True,
    )
    envelope = GovernedExternalIntelligenceBoundary().admit_inference(
        request,
        LLMResponse(
            text="",
            provider="mistral",
            accepted=False,
            error="provider_failure",
        ),
        provenance,
    )
    assert envelope.status is ExternalIntelligenceStatus.REJECTED
    assert envelope.inference is not None
    assert envelope.inference.provider_error == "provider_failure"
    assert envelope.cognitive_authority_granted is False


def test_m400_2_admits_nasa_as_information_source_not_provider() -> None:
    request = ExternalIntelligenceRequest(
        request_id="req-nasa",
        owner="roby",
        capability=ExternalIntelligenceCapability.INFORMATION_SOURCE,
        purpose="retrieve official space evidence",
        target_id="nasa",
    )
    provenance = _provenance(
        "nasa",
        ExternalIntelligenceCapability.INFORMATION_SOURCE,
        scope=ExternalExecutionScope.REMOTE,
        network_used=True,
    )
    envelope = GovernedExternalIntelligenceBoundary().admit_information(
        request,
        source_id="nasa",
        items=({"title": "JWST observation"},),
        provenance=provenance,
    )
    assert envelope.status is ExternalIntelligenceStatus.ACCEPTED
    assert envelope.information is not None
    assert envelope.inference is None
    assert envelope.information.source_id == "nasa"
    assert "source_does_not_gain_cognitive_authority" in envelope.rationale


def test_m400_2_rejects_capability_mixing() -> None:
    request = ExternalIntelligenceRequest(
        request_id="req-nasa",
        owner="roby",
        capability="information_source",
        purpose="retrieve source",
    )
    provenance = _provenance(
        "nasa",
        ExternalIntelligenceCapability.INFORMATION_SOURCE,
        scope=ExternalExecutionScope.REMOTE,
        network_used=True,
    )
    with pytest.raises(ValueError, match="inference request"):
        GovernedExternalIntelligenceBoundary().admit_inference(
            request,
            LLMResponse(text="x", provider="nasa"),
            provenance,
        )


def test_m400_2_rejects_mismatched_target_and_provenance() -> None:
    request = ExternalIntelligenceRequest(
        request_id="req-1",
        owner="roby",
        capability="inference_provider",
        purpose="external inference",
        target_id="ollama",
    )
    provenance = _provenance(
        "gemini",
        ExternalIntelligenceCapability.INFERENCE_PROVIDER,
        scope=ExternalExecutionScope.REMOTE,
        network_used=True,
    )
    with pytest.raises(ValueError, match="requested target"):
        GovernedExternalIntelligenceBoundary().admit_inference(
            request,
            LLMResponse(text="x", provider="gemini"),
            provenance,
        )


def test_m400_2_rejects_provenance_capability_mismatch() -> None:
    request = ExternalIntelligenceRequest(
        request_id="req-1",
        owner="roby",
        capability="inference_provider",
        purpose="external inference",
    )
    provenance = _provenance(
        "ollama",
        ExternalIntelligenceCapability.INFORMATION_SOURCE,
        scope=ExternalExecutionScope.LOCAL,
        network_used=False,
    )
    with pytest.raises(ValueError, match="capability must match"):
        GovernedExternalIntelligenceBoundary().admit_inference(
            request,
            LLMResponse(text="x", provider="ollama"),
            provenance,
        )


def test_m400_2_boundary_does_not_select_or_execute_external_capabilities() -> None:
    boundary = GovernedExternalIntelligenceBoundary()
    for name in (
        "route",
        "select_provider",
        "generate",
        "execute",
        "fetch",
        "http_get",
        "enable_source",
        "register_provider",
        "mutate",
    ):
        assert not hasattr(boundary, name)


def test_m400_2_module_contains_no_network_or_execution_implementation() -> None:
    source = Path("core/governed_external_intelligence/boundary.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "subprocess",
        "urlopen",
        "requests.",
        "httpx",
        "socket",
        "ProviderRouter(",
        "GovernedProviderRouter(",
        "NasaGovernedSourceAdapter(",
    ):
        assert forbidden not in source


def test_m400_2_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M400_2_GOVERNED_EXTERNAL_INTELLIGENCE_BOUNDARY_CONTRACT.md"
    ).read_text(encoding="utf-8")
    assert "capacidad/evidencia externa ≠ autoridad cognitiva" in document
    assert "Inference Provider" in document
    assert "Information Source" in document
    assert "no selecciona ni ejecuta" in document
    assert "Milestone M400.2 — Governed External Intelligence Boundary & Contract" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M400.2 — Governed External Intelligence Boundary & Contract" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M400.2 — Regla de frontera de inteligencia externa" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
