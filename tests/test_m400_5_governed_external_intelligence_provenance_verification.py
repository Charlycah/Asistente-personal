from dataclasses import replace
from pathlib import Path

from app.governed_external_information_source_integration import (
    GovernedExternalInformationSourceIntegration,
)
from core.governed_external_intelligence import (
    ExternalIntelligenceRequest,
    ExternalVerificationStatus,
    GovernedExternalIntelligenceVerifier,
    GovernedExternalProviderIntegration,
)
from core.governed_provider_execution_adapter import (
    GovernedProviderExecutionAdapter,
    LocalProviderExecutionRequest,
)
from core.llm_provider import LLMRequest
from tests.test_m173_governed_provider_execution_adapter import (
    NOW,
    RecordingProvider,
    local_route,
)
from tests.test_m400_4_governed_external_information_source_integration import (
    _nasa_result,
)


def _provider_envelope():
    route = local_route()
    execution = GovernedProviderExecutionAdapter(
        (RecordingProvider(),)
    ).execute(
        LocalProviderExecutionRequest(
            owner="Carlos",
            route=route,
            inference_request=LLMRequest(prompt="Hola ROBY"),
        ),
        now=NOW,
    )
    request = ExternalIntelligenceRequest(
        request_id="verify-ollama",
        owner="Carlos",
        capability="inference_provider",
        purpose="verify governed provider evidence",
        target_id="ollama",
    )
    return GovernedExternalProviderIntegration().admit_execution_result(
        request,
        execution,
        network_used=True,
    )


def _source_envelope():
    request = ExternalIntelligenceRequest(
        request_id="verify-nasa",
        owner="Carlos",
        capability="information_source",
        purpose="verify governed source evidence",
        target_id="nasa",
    )
    return GovernedExternalInformationSourceIntegration().admit_query_result(
        request,
        _nasa_result(),
        network_used=True,
    )


def test_m400_5_verifies_provider_provenance_without_certifying_truth() -> None:
    envelope = _provider_envelope()
    result = GovernedExternalIntelligenceVerifier().verify(envelope)
    assert result.status is ExternalVerificationStatus.VERIFIED
    assert result.envelope_id == envelope.envelope_id
    assert len(result.provenance_digest) == 64
    assert "provider_identity_matches_provenance" in result.checks
    assert result.limitations == ("external_content_truth_is_not_certified",)
    assert result.truth_certified is False
    assert result.cognitive_authority_granted is False


def test_m400_5_source_without_execution_trace_is_limited() -> None:
    envelope = _source_envelope()
    result = GovernedExternalIntelligenceVerifier().verify(envelope)
    assert result.status is ExternalVerificationStatus.LIMITED
    assert "source_identity_matches_provenance" in result.checks
    assert "source_execution_trace_is_not_available" in result.limitations
    assert result.truth_certified is False


def test_m400_5_verification_is_deterministic() -> None:
    verifier = GovernedExternalIntelligenceVerifier()
    envelope = _provider_envelope()
    first = verifier.verify(envelope)
    second = verifier.verify(envelope)
    assert first == second
    assert first.verification_id == second.verification_id


def test_m400_5_rejected_external_result_remains_rejected() -> None:
    envelope = _provider_envelope()
    rejected = replace(envelope, status="rejected", envelope_id="")
    result = GovernedExternalIntelligenceVerifier().verify(rejected)
    assert result.status is ExternalVerificationStatus.REJECTED
    assert "external_result_was_rejected_at_admission" in result.limitations


def test_m400_5_verifier_does_not_execute_or_route_external_capabilities() -> None:
    source = Path(
        "core/governed_external_intelligence/verification.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        ".generate(",
        ".execute(",
        "GovernedProviderRouter(",
        "GovernedProviderExecutionAdapter(",
        "NasaGovernedSourceAdapter(",
        "urlopen",
        "requests.",
    ):
        assert forbidden not in source


def test_m400_5_verifier_has_no_cognitive_authority() -> None:
    verifier = GovernedExternalIntelligenceVerifier()
    assert verifier.verifier_id == "external_intelligence_provenance_verifier"
    assert not hasattr(verifier, "authority_id")
    for forbidden in (
        "decide",
        "plan",
        "remember",
        "mutate",
        "select_provider",
        "select_source",
        "fetch",
        "execute",
    ):
        assert not hasattr(verifier, forbidden)


def test_m400_5_verification_identity_detects_inconsistent_id() -> None:
    result = GovernedExternalIntelligenceVerifier().verify(_provider_envelope())
    try:
        replace(result, verification_id="tampered")
    except ValueError as exc:
        assert "verification id is inconsistent" in str(exc)
    else:
        raise AssertionError("tampered verification id must be rejected")


def test_m400_5_provenance_digest_changes_with_provenance() -> None:
    verifier = GovernedExternalIntelligenceVerifier()
    envelope = _provider_envelope()
    first = verifier.verify(envelope)
    changed_provenance = replace(
        envelope.provenance,
        network_used=not envelope.provenance.network_used,
    )
    changed = replace(
        envelope,
        provenance=changed_provenance,
        envelope_id="",
    )
    second = verifier.verify(changed)
    assert first.provenance_digest != second.provenance_digest


def test_m400_5_keeps_verification_separate_from_truth() -> None:
    result = GovernedExternalIntelligenceVerifier().verify(_source_envelope())
    assert "external_content_truth_is_not_certified" in result.limitations
    assert result.truth_certified is False


def test_m400_5_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M400_5_GOVERNED_EXTERNAL_INTELLIGENCE_PROVENANCE_VERIFICATION.md"
    ).read_text(encoding="utf-8")
    assert "procedencia verificable ≠ verdad certificada" in document
    assert "predicción ≠ certeza" in document
    assert "capacidad/evidencia externa ≠ autoridad cognitiva" in document
    assert "no ejecuta providers ni fuentes" in document
