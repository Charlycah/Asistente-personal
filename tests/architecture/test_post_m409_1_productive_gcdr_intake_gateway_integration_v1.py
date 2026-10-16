from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from core.explicit_complex_decision_intake_envelope import (
    ExplicitComplexDecisionIntakeEnvelopeFoundationV1,
)
from core.gcdr_intake_conversational_realization import (
    GCDRIntakeConversationalOutcome,
    GCDRIntakeConversationalRealizerV1,
)
from core.productive_gcdr_intake_integration import (
    ProductiveGCDRIntakeIntegrationStatus,
    ProductiveGCDRIntakeIntegrationV1,
)

ROOT = Path(__file__).resolve().parents[2]


def _complete_text() -> str:
    return (
        "Decisión:\n"
        "¿A o B?\n\n"
        "Criterios:\n"
        "Los criterios son seguridad y costo. Seguridad es obligatoria.\n\n"
        "Evidencia:\n"
        "A cumple seguridad. A cumple costo. "
        "B no cumple seguridad. B cumple costo."
    )


def _invalid_linkage_text() -> str:
    return (
        "Decisión:\n"
        "¿A o B?\n\n"
        "Criterios:\n"
        "Los criterios son seguridad y costo.\n\n"
        "Evidencia:\n"
        "C cumple privacidad."
    )


def _intake(text: str):
    return ExplicitComplexDecisionIntakeEnvelopeFoundationV1().analyze(text)


class Turn:
    response_text = "respuesta normal"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False
    response_path = "pipeline"
    degradation_reason = "not_applicable"


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def converse(self, text: str, **kwargs) -> Turn:
        self.calls.append((text, kwargs))
        return Turn()


def test_integration_consumes_complete_envelope_end_to_end() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(_intake(_complete_text()))

    assert result.status is ProductiveGCDRIntakeIntegrationStatus.ADVISORY_READY
    assert result.assembly is not None
    assert result.advisory is not None
    assert result.advisory.assembly_fingerprint == result.assembly.source_fingerprint
    assert result.advisory.report.recommended_option_id is not None
    assert len(result.source_fingerprint) == 64


def test_non_complete_envelope_is_not_applicable() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(_intake("¿A o B?"))

    assert result.status is ProductiveGCDRIntakeIntegrationStatus.NOT_APPLICABLE
    assert result.assembly is None
    assert result.advisory is None


def test_complete_but_unlinked_envelope_fails_certification_closed() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(
        _intake(_invalid_linkage_text())
    )

    assert (
        result.status
        is ProductiveGCDRIntakeIntegrationStatus.CERTIFICATION_FAILED
    )
    assert result.assembly is None
    assert result.advisory is None
    assert "gcdr_intake:certified_linkage_required" in result.rationale_codes


def test_integration_result_is_deterministic_and_immutable() -> None:
    foundation = ProductiveGCDRIntakeIntegrationV1()
    first = foundation.integrate(_intake(_complete_text()))
    second = foundation.integrate(_intake(_complete_text()))

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.source_fingerprint = "x" * 64


def test_integration_non_power_contract_is_explicit() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(_intake(_complete_text()))

    assert result.read_only is True
    assert result.advisory_only is True
    assert result.infers_options is False
    assert result.infers_criteria is False
    assert result.infers_evidence is False
    assert result.repairs_references is False
    assert result.resolves_context is False
    assert result.uses_memory is False
    assert result.uses_retrieval is False
    assert result.uses_llm is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.creates_plan is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_realizer_renders_existing_gcdr_recommendation_only() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(_intake(_complete_text()))
    realization = GCDRIntakeConversationalRealizerV1().realize(result)

    assert (
        realization.outcome
        is GCDRIntakeConversationalOutcome.RECOMMENDATION_PRESENT
    )
    assert "análisis multicriterio gobernado favorece «A»" in realization.response_text
    assert "decisión sigue siendo tuya" in realization.response_text
    assert realization.derives_new_reasoning is False
    assert realization.uses_llm is False


def test_realizer_renders_certification_failure_without_guessing() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(
        _intake(_invalid_linkage_text())
    )
    realization = GCDRIntakeConversationalRealizerV1().realize(result)

    assert (
        realization.outcome
        is GCDRIntakeConversationalOutcome.CERTIFICATION_FAILED
    )
    assert "no puede certificarse" in realization.response_text
    assert "No voy a completar referencias" in realization.response_text
    assert realization.referenced_option_ids == ()


def test_realizer_rejects_non_applicable_intake() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(_intake("mensaje normal"))

    with pytest.raises(ValueError, match="must not be realized"):
        GCDRIntakeConversationalRealizerV1().realize(result)


def test_gateway_intercepts_complete_complex_decision_without_runtime() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit(_complete_text(), session_id="main")

    assert runtime.calls == []
    assert turn.response_path == "interceptor"
    assert turn.pipeline_result_id.startswith("complex-decision-")
    assert turn.operational_response_id.startswith("gcdr-advisory-response-")
    assert "análisis multicriterio gobernado favorece «A»" in turn.response_text
    assert "explicit_complex_decision_intake" in turn.rationale
    assert "productive_gcdr_intake_integration" in turn.rationale
    assert "governed_complex_decision_reasoning" in turn.rationale
    assert "human_decision_preserved" in turn.rationale


def test_gateway_certification_failure_is_bounded_interceptor_not_simple_advisor(
) -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit(_invalid_linkage_text(), session_id="main")

    assert runtime.calls == []
    assert turn.response_path == "interceptor"
    assert turn.pipeline_result_id == "gcdr-certification-failed"
    assert "no puede certificarse" in turn.response_text
    assert "integration:certification_failed" in turn.rationale
    assert "governed_decision_advisory" not in turn.rationale


def test_gateway_preserves_simple_deliberation_historical_route() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit("¿A o B?", session_id="main")

    assert runtime.calls == []
    assert turn.pipeline_result_id.startswith("decision-advisory-")
    assert turn.operational_response_id.startswith("decision-advisory-response-")
    assert "governed_decision_advisory" in turn.rationale
    assert "explicit_complex_decision_intake" not in turn.rationale


def test_gateway_preserves_runtime_for_incomplete_envelope() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    text = (
        "Decisión:\n¿A o B?\n\n"
        "Criterios:\nLos criterios son seguridad y costo."
    )

    turn = gateway.submit(text, session_id="main")

    assert len(runtime.calls) == 1
    assert runtime.calls[0][0] == text
    assert turn.response_text == "respuesta normal"


def test_gateway_external_evidence_bypasses_local_gcdr_interceptor() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    external = (object(),)

    turn = gateway.submit(
        _complete_text(),
        session_id="main",
        external_evidence=external,
    )

    assert len(runtime.calls) == 1
    assert runtime.calls[0][1]["external_evidence"] == external
    assert turn.response_text == "respuesta normal"


def test_identification_keeps_precedence_over_complex_decision_intake() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)

    class IntakeMustNotRun:
        def analyze(self, text: str):
            raise AssertionError(f"complex intake ran for identification: {text}")

    gateway._complex_decision_intake = IntakeMustNotRun()
    turn = gateway.submit("Confirmo que soy Carlos", session_id="main")

    assert turn.pipeline_result_id.startswith("identity-")
    assert runtime.calls == []


def test_gateway_epilogue_and_cycle_sealing_are_preserved() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())

    gateway.submit(_complete_text(), session_id="gcdr-session")

    assert gateway.snapshot.submitted_turns == 1
    assert gateway.snapshot.last_session_id == "gcdr-session"
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()


def test_gateway_imports_only_intake_integration_and_realizer_boundaries() -> None:
    source = (ROOT / "app" / "official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )

    assert "ExplicitComplexDecisionIntakeEnvelopeFoundationV1" in source
    assert "ProductiveGCDRIntakeIntegrationV1" in source
    assert "GCDRIntakeConversationalRealizerV1" in source
    for forbidden in (
        "CertifiedOptionCriterionEvidenceLinkageV1",
        "CertifiedGCDRAssessmentAdapterV1",
        "CriterionImportanceCompatibilityFoundationV1",
        "GCDRCompleteInputAssemblyFoundationV1",
        "GovernedComplexDecisionReasoningFoundationV1",
    ):
        assert forbidden not in source


def test_integration_schema_is_versioned() -> None:
    result = ProductiveGCDRIntakeIntegrationV1().integrate(_intake(_complete_text()))
    assert result.schema_version == "post-m409.1-productive-gcdr-intake-integration-v1"
