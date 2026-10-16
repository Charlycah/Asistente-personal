from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidenceProducerV1,
    ExplicitComplexDecisionCriteriaStatus,
)


@pytest.fixture
def producer() -> ExplicitComplexDecisionCriteriaEvidenceProducerV1:
    return ExplicitComplexDecisionCriteriaEvidenceProducerV1()


def test_extracts_two_explicit_criteria_with_exact_spans(producer):
    text = "Estoy entre A y B. Los criterios son seguridad y costo."
    result = producer.analyze(text)
    assert result.status is ExplicitComplexDecisionCriteriaStatus.EXPLICIT
    assert tuple(item.raw_text for item in result.criteria) == ("seguridad", "costo")
    assert all(
        text[item.start_offset : item.end_offset] == item.raw_text
        for item in result.criteria
    )


def test_extracts_required_criterion_only_when_explicit(producer):
    text = "Los criterios son seguridad y costo. Seguridad es obligatoria."
    result = producer.analyze(text)
    assert result.criteria[0].required is True
    assert result.criteria[0].required_source_span is not None
    assert result.criteria[1].required is False


def test_extracts_explicit_importance_relation_without_numeric_weight(producer):
    text = "Los criterios son seguridad y costo. Seguridad es más importante que costo."
    result = producer.analyze(text)
    assert len(result.importance_relations) == 1
    relation = result.importance_relations[0]
    assert relation.more_important_criterion_id == result.criteria[0].criterion_id
    assert relation.less_important_criterion_id == result.criteria[1].criterion_id
    assert "más importante que" in relation.raw_text


def test_combines_required_and_importance_evidence(producer):
    text = (
        "Estoy entre A y B. Los criterios son seguridad y costo. "
        "Seguridad es obligatoria y seguridad es más importante que costo."
    )
    result = producer.analyze(text)
    assert result.status is ExplicitComplexDecisionCriteriaStatus.EXPLICIT
    assert result.criteria[0].required is True
    assert len(result.importance_relations) == 1


def test_three_criteria_preserve_source_order(producer):
    result = producer.analyze("Los criterios son seguridad, costo y tiempo.")
    assert tuple(item.normalized_text for item in result.criteria) == (
        "seguridad", "costo", "tiempo"
    )
    assert tuple(item.ordinal for item in result.criteria) == (0, 1, 2)


def test_one_criterion_is_insufficient(producer):
    result = producer.analyze("Los criterios son seguridad.")
    assert result.status is ExplicitComplexDecisionCriteriaStatus.INSUFFICIENT_CRITERIA
    assert result.criteria == ()


def test_non_criteria_turn_abstains(producer):
    result = producer.analyze("¿Qué me conviene, A o B?")
    assert result.status is ExplicitComplexDecisionCriteriaStatus.NOT_COMPLEX_CRITERIA
    assert result.criteria == ()


def test_implicit_criteria_are_not_invented(producer):
    result = producer.analyze("Quiero algo seguro, barato y rápido.")
    assert result.status is ExplicitComplexDecisionCriteriaStatus.NOT_COMPLEX_CRITERIA


def test_duplicate_criteria_are_ambiguous(producer):
    result = producer.analyze("Los criterios son costo y costo.")
    assert result.status is ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS
    assert result.criteria == ()


def test_contextual_placeholder_criterion_is_ambiguous(producer):
    result = producer.analyze("Los criterios son seguridad y eso.")
    assert result.status is ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS


def test_more_than_five_criteria_are_ambiguous(producer):
    result = producer.analyze("Los criterios son a, b, c, d, e y f.")
    assert result.status is ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS


def test_unknown_required_statement_does_not_create_criterion(producer):
    result = producer.analyze(
        "Los criterios son seguridad y costo. Tiempo es obligatorio."
    )
    assert tuple(item.normalized_text for item in result.criteria) == (
        "seguridad",
        "costo",
    )
    assert not any(item.required for item in result.criteria)


def test_unknown_importance_statement_does_not_create_relation(producer):
    result = producer.analyze(
        "Los criterios son seguridad y costo. Tiempo es más importante que costo."
    )
    assert result.importance_relations == ()


def test_option_assessment_is_not_extracted(producer):
    result = producer.analyze(
        "Los criterios son seguridad y costo. A es mejor que B en seguridad."
    )
    assert result.status is ExplicitComplexDecisionCriteriaStatus.EXPLICIT
    assert result.importance_relations == ()
    assert not hasattr(result, "option_assessments")


def test_deterministic_fingerprint(producer):
    text = "Los criterios son seguridad y costo. Seguridad es obligatoria."
    assert (
        producer.analyze(text).source_fingerprint
        == producer.analyze(text).source_fingerprint
    )


def test_fingerprint_changes_with_source_evidence(producer):
    a = producer.analyze("Los criterios son seguridad y costo.")
    b = producer.analyze("Los criterios son seguridad y tiempo.")
    assert a.source_fingerprint != b.source_fingerprint


def test_criterion_ids_are_stable_across_surrounding_text(producer):
    a = producer.analyze("Los criterios son seguridad y costo.")
    b = producer.analyze("Estoy decidiendo. Los criterios son seguridad y costo.")
    assert tuple(item.criterion_id for item in a.criteria) == tuple(
        item.criterion_id for item in b.criteria
    )


def test_evidence_is_immutable(producer):
    result = producer.analyze("Los criterios son seguridad y costo.")
    with pytest.raises(FrozenInstanceError):
        result.criteria[0].required = True


def test_governed_non_power_invariants(producer):
    result = producer.analyze("Los criterios son seguridad y costo.")
    assert result.read_only is True
    assert result.generates_criteria is False
    assert result.infers_importance is False
    assert result.evaluates_options is False
    assert result.resolves_context is False
    assert result.uses_llm is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_schema_is_versioned(producer):
    result = producer.analyze("Los criterios son seguridad y costo.")
    assert result.schema_version == "post-m409.1-explicit-complex-decision-criteria-v1"
