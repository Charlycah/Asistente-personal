from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaStatus,
)
from core.explicit_complex_decision_intake_envelope import (
    ExplicitComplexDecisionIntakeEnvelopeFoundationV1,
    ExplicitComplexDecisionIntakeEnvelopeStatus,
    ExplicitComplexDecisionIntakeSectionKind,
)
from core.explicit_human_decision_deliberation import ExplicitDecisionDeliberationStatus
from core.explicit_option_criterion_evidence import (
    ExplicitOptionCriterionEvidenceStatus,
)

FOUNDATION = ExplicitComplexDecisionIntakeEnvelopeFoundationV1()


def _complete_text() -> str:
    return (
        "Decisión:\n"
        "¿A o B?\n\n"
        "Criterios:\n"
        "Los criterios son seguridad y costo. Seguridad es obligatoria. "
        "Seguridad es más importante que costo.\n\n"
        "Evidencia:\n"
        "A cumple seguridad. B no cumple seguridad. "
        "A cumple costo. B cumple costo."
    )


def test_complete_envelope_delegates_to_existing_certified_producers() -> None:
    result = FOUNDATION.analyze(_complete_text())
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.COMPLETE
    assert result.deliberation_evidence is not None
    assert result.criteria_evidence is not None
    assert result.option_criterion_evidence is not None
    assert (
        result.deliberation_evidence.status
        is ExplicitDecisionDeliberationStatus.EXPLICIT
    )
    assert (
        result.criteria_evidence.status
        is ExplicitComplexDecisionCriteriaStatus.EXPLICIT
    )
    assert (
        result.option_criterion_evidence.status
        is ExplicitOptionCriterionEvidenceStatus.EXPLICIT
    )


def test_sections_are_exact_parent_substrings_with_global_offsets() -> None:
    text = _complete_text()
    result = FOUNDATION.analyze(text)
    sections = (
        result.decision_section,
        result.criteria_section,
        result.evidence_section,
    )
    assert all(section is not None for section in sections)
    for section in sections:
        assert section is not None
        assert text[section.start_offset : section.end_offset] == section.raw_payload
        assert len(section.payload_fingerprint) == 64


def test_section_kinds_preserve_fixed_order() -> None:
    result = FOUNDATION.analyze(_complete_text())
    assert result.decision_section is not None
    assert result.criteria_section is not None
    assert result.evidence_section is not None
    assert (
        result.decision_section.kind
        is ExplicitComplexDecisionIntakeSectionKind.DECISION
    )
    assert (
        result.criteria_section.kind
        is ExplicitComplexDecisionIntakeSectionKind.CRITERIA
    )
    assert (
        result.evidence_section.kind
        is ExplicitComplexDecisionIntakeSectionKind.EVIDENCE
    )


def test_child_offsets_remain_relative_to_child_payload() -> None:
    result = FOUNDATION.analyze(_complete_text())
    assert result.decision_section is not None
    assert result.deliberation_evidence is not None
    alternative = result.deliberation_evidence.alternatives[0]
    child_slice = result.decision_section.raw_payload[
        alternative.start_offset : alternative.end_offset
    ]
    assert child_slice == alternative.raw_text
    global_start = result.decision_section.start_offset + alternative.start_offset
    global_end = result.decision_section.start_offset + alternative.end_offset
    assert result.source_text[global_start:global_end] == alternative.raw_text


def test_non_envelope_abstains_without_exposing_artifacts() -> None:
    result = FOUNDATION.analyze("¿A o B?")
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.NOT_ENVELOPE
    assert result.decision_section is None
    assert result.deliberation_evidence is None


def test_missing_section_is_ambiguous_when_envelope_headers_are_present() -> None:
    result = FOUNDATION.analyze(
        "Decisión:\n¿A o B?\n\nCriterios:\nLos criterios son seguridad y costo."
    )
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.AMBIGUOUS


def test_repeated_section_is_ambiguous() -> None:
    result = FOUNDATION.analyze(
        "Decisión:\n¿A o B?\n\nCriterios:\nLos criterios son seguridad y costo.\n\n"
        "Criterios:\nLos criterios son precio y tiempo.\n\n"
        "Evidencia:\nA cumple seguridad."
    )
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.AMBIGUOUS


def test_wrong_section_order_is_ambiguous() -> None:
    result = FOUNDATION.analyze(
        "Criterios:\nLos criterios son seguridad y costo.\n\nDecisión:\n¿A o B?\n\n"
        "Evidencia:\nA cumple seguridad."
    )
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.AMBIGUOUS


def test_text_before_first_header_is_ambiguous() -> None:
    result = FOUNDATION.analyze("Quiero decidir.\n" + _complete_text())
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.AMBIGUOUS


def test_empty_payload_is_incomplete() -> None:
    result = FOUNDATION.analyze(
        "Decisión:\n\nCriterios:\nLos criterios son seguridad y costo.\n\n"
        "Evidencia:\nA cumple seguridad."
    )
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.INCOMPLETE


def test_structured_but_nonsemantic_evidence_is_incomplete_not_inferred() -> None:
    result = FOUNDATION.analyze(
        "Decisión:\n¿A o B?\n\nCriterios:\nLos criterios son seguridad y costo.\n\n"
        "Evidencia:\nA cuesta 100 y B cuesta 120."
    )
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.INCOMPLETE
    assert result.option_criterion_evidence is not None
    assert (
        result.option_criterion_evidence.status
        is ExplicitOptionCriterionEvidenceStatus.NOT_OPTION_CRITERION_EVIDENCE
    )


def test_envelope_does_not_link_references() -> None:
    result = FOUNDATION.analyze(
        "Decisión:\n¿A o B?\n\nCriterios:\nLos criterios son seguridad y costo.\n\n"
        "Evidencia:\nC cumple privacidad."
    )
    assert result.status is ExplicitComplexDecisionIntakeEnvelopeStatus.COMPLETE
    assert result.performs_linkage is False


def test_result_is_deterministic_and_immutable() -> None:
    first = FOUNDATION.analyze(_complete_text())
    second = FOUNDATION.analyze(_complete_text())
    assert first == second
    assert first.source_fingerprint == second.source_fingerprint
    with pytest.raises(FrozenInstanceError):
        first.source_fingerprint = "x" * 64


def test_non_power_contract_is_explicit() -> None:
    result = FOUNDATION.analyze(_complete_text())
    assert result.read_only is True
    assert result.framing_only is True
    assert result.parses_decision_semantics is False
    assert result.parses_criteria_semantics is False
    assert result.parses_option_criterion_semantics is False
    assert result.generates_options is False
    assert result.generates_criteria is False
    assert result.infers_outcomes is False
    assert result.resolves_context is False
    assert result.uses_llm is False
    assert result.uses_retrieval is False
    assert result.uses_memory is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.performs_linkage is False
    assert result.builds_assessments is False
    assert result.assembles_gcdr_input is False
    assert result.calls_gcdr is False
    assert result.evaluates_decision is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_schema_is_versioned() -> None:
    result = FOUNDATION.analyze(_complete_text())
    assert result.schema_version == (
        "post-m409.1-explicit-complex-decision-intake-envelope-v1"
    )
