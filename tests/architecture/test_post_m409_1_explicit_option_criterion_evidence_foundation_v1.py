from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.explicit_option_criterion_evidence import (
    ExplicitOptionCriterionEvidenceProducerV1,
    ExplicitOptionCriterionEvidenceStatus,
    ExplicitOptionCriterionOutcome,
)


@pytest.fixture
def producer() -> ExplicitOptionCriterionEvidenceProducerV1:
    return ExplicitOptionCriterionEvidenceProducerV1()


def test_extracts_explicit_favorable_relation_with_exact_span(producer):
    text = "A cumple seguridad."
    result = producer.analyze(text)
    assert result.status is ExplicitOptionCriterionEvidenceStatus.EXPLICIT
    relation = result.relations[0]
    assert relation.option_reference == "A"
    assert relation.criterion_reference == "seguridad"
    assert relation.outcome is ExplicitOptionCriterionOutcome.FAVORABLE
    assert text[relation.start_offset : relation.end_offset] == relation.raw_text


def test_extracts_satisface_as_explicit_favorable(producer):
    result = producer.analyze("Plan B satisface privacidad.")
    relation = result.relations[0]
    assert relation.option_reference == "Plan B"
    assert relation.criterion_reference == "privacidad"
    assert relation.outcome is ExplicitOptionCriterionOutcome.FAVORABLE


def test_extracts_explicit_unfavorable_relation(producer):
    result = producer.analyze("B no cumple seguridad.")
    assert result.relations[0].outcome is ExplicitOptionCriterionOutcome.UNFAVORABLE


def test_extracts_no_satisface_as_unfavorable(producer):
    result = producer.analyze("Plan B no satisface privacidad.")
    assert result.relations[0].outcome is ExplicitOptionCriterionOutcome.UNFAVORABLE


def test_extracts_explicit_insufficient_relation(producer):
    result = producer.analyze("No sé si B cumple seguridad.")
    assert result.relations[0].outcome is ExplicitOptionCriterionOutcome.INSUFFICIENT


def test_extracts_not_clear_as_insufficient(producer):
    result = producer.analyze("No está claro si B satisface seguridad.")
    assert result.relations[0].outcome is ExplicitOptionCriterionOutcome.INSUFFICIENT


def test_explicit_favorable_respect_pattern(producer):
    result = producer.analyze("A es favorable respecto de seguridad.")
    assert result.relations[0].outcome is ExplicitOptionCriterionOutcome.FAVORABLE


def test_explicit_unfavorable_respect_pattern(producer):
    result = producer.analyze("A es desfavorable respecto de seguridad.")
    assert result.relations[0].outcome is ExplicitOptionCriterionOutcome.UNFAVORABLE


def test_multiple_relations_preserve_source_order(producer):
    text = "A cumple seguridad. B no cumple seguridad."
    result = producer.analyze(text)
    assert tuple(item.option_reference for item in result.relations) == ("A", "B")
    assert tuple(item.ordinal for item in result.relations) == (0, 1)


def test_non_relation_turn_abstains(producer):
    result = producer.analyze("Estoy entre A y B.")
    assert (
        result.status
        is ExplicitOptionCriterionEvidenceStatus.NOT_OPTION_CRITERION_EVIDENCE
    )
    assert result.relations == ()


def test_descriptive_value_does_not_become_favorable(producer):
    result = producer.analyze("A cuesta menos.")
    assert (
        result.status
        is ExplicitOptionCriterionEvidenceStatus.NOT_OPTION_CRITERION_EVIDENCE
    )


def test_comparative_statement_is_not_interpreted(producer):
    result = producer.analyze("A es mejor que B en seguridad.")
    assert (
        result.status
        is ExplicitOptionCriterionEvidenceStatus.NOT_OPTION_CRITERION_EVIDENCE
    )


def test_numeric_value_is_not_interpreted(producer):
    result = producer.analyze("A cuesta 100 y B cuesta 120.")
    assert (
        result.status
        is ExplicitOptionCriterionEvidenceStatus.NOT_OPTION_CRITERION_EVIDENCE
    )


def test_neutral_is_not_invented_from_missing_evidence(producer):
    result = producer.analyze("No dije nada sobre seguridad.")
    assert (
        result.status
        is ExplicitOptionCriterionEvidenceStatus.NOT_OPTION_CRITERION_EVIDENCE
    )
    assert result.relations == ()


def test_contextual_option_reference_is_ambiguous(producer):
    result = producer.analyze("La primera cumple seguridad.")
    assert result.status is ExplicitOptionCriterionEvidenceStatus.AMBIGUOUS
    assert result.relations == ()


def test_contextual_criterion_reference_is_ambiguous(producer):
    result = producer.analyze("A cumple eso.")
    assert result.status is ExplicitOptionCriterionEvidenceStatus.AMBIGUOUS


def test_duplicate_pair_is_ambiguous(producer):
    result = producer.analyze("A cumple seguridad. A cumple seguridad.")
    assert result.status is ExplicitOptionCriterionEvidenceStatus.AMBIGUOUS


def test_conflicting_pair_is_ambiguous(producer):
    result = producer.analyze("A cumple seguridad. A no cumple seguridad.")
    assert result.status is ExplicitOptionCriterionEvidenceStatus.AMBIGUOUS


def test_evidence_id_is_stable_across_surrounding_text(producer):
    a = producer.analyze("A cumple seguridad.")
    b = producer.analyze("Decisión actual. A cumple seguridad.")
    assert a.relations[0].evidence_id == b.relations[0].evidence_id


def test_source_fingerprint_is_deterministic_and_source_sensitive(producer):
    a1 = producer.analyze("A cumple seguridad.")
    a2 = producer.analyze("A cumple seguridad.")
    b = producer.analyze("B cumple seguridad.")
    assert a1.source_fingerprint == a2.source_fingerprint
    assert a1.source_fingerprint != b.source_fingerprint


def test_evidence_is_immutable(producer):
    result = producer.analyze("A cumple seguridad.")
    with pytest.raises(FrozenInstanceError):
        result.relations[0].outcome = ExplicitOptionCriterionOutcome.UNFAVORABLE


def test_governed_non_power_invariants(producer):
    result = producer.analyze("A cumple seguridad.")
    assert result.read_only is True
    assert result.generates_options is False
    assert result.generates_criteria is False
    assert result.infers_outcome is False
    assert result.resolves_context is False
    assert result.uses_llm is False
    assert result.uses_retrieval is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.evaluates_decision is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_does_not_create_gcdr_assessment(producer):
    result = producer.analyze("A cumple seguridad.")
    assert not hasattr(result, "criterion_assessments")
    assert not hasattr(result.relations[0], "evidence_codes")
    assert not hasattr(result.relations[0], "explicit_value")


def test_schema_is_versioned(producer):
    result = producer.analyze("A cumple seguridad.")
    assert result.schema_version == "post-m409.1-explicit-option-criterion-evidence-v1"
