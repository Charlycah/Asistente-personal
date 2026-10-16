from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.criterion_importance_compatibility import (
    CriterionImportanceCompatibilityFoundationV1,
    CriterionImportanceCompatibilityStatus,
)
from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidenceProducerV1,
)

FOUNDATION = CriterionImportanceCompatibilityFoundationV1()


def _evidence(text: str):
    return ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(text)


def test_no_importance_relation_is_compatible_without_cardinal_weight():
    result = FOUNDATION.assess(_evidence("Los criterios son seguridad y costo."))
    assert (
        result.status
        is CriterionImportanceCompatibilityStatus.COMPATIBLE_NO_CARDINAL_IMPORTANCE
    )
    assert all(item.explicit_importance is None for item in result.bindings)
    assert result.ordinal_relations == ()


def test_explicit_ordinal_relation_is_preserved_without_numeric_synthesis():
    evidence = _evidence(
        "Los criterios son seguridad y costo. Seguridad es más importante que costo."
    )
    result = FOUNDATION.assess(evidence)
    assert (
        result.status
        is CriterionImportanceCompatibilityStatus.ORDINAL_IMPORTANCE_PRESERVED
    )
    relation = result.ordinal_relations[0]
    assert relation.more_important_criterion_id == evidence.criteria[0].criterion_id
    assert relation.less_important_criterion_id == evidence.criteria[1].criterion_id
    assert all(item.explicit_importance is None for item in result.bindings)


def test_ordinal_relation_preserves_exact_source_span():
    evidence = _evidence(
        "Los criterios son seguridad y costo. Seguridad es prioritaria que costo."
    )
    result = FOUNDATION.assess(evidence)
    relation = result.ordinal_relations[0]
    start, end = relation.source_span
    assert evidence.source_text[start:end] == relation.raw_text
    assert relation.source_fingerprint == evidence.source_fingerprint


def test_required_criterion_does_not_become_cardinal_importance():
    evidence = _evidence(
        "Los criterios son seguridad y costo. Seguridad es obligatoria."
    )
    assert evidence.criteria[0].required is True
    result = FOUNDATION.assess(evidence)
    assert result.bindings[0].explicit_importance is None
    assert result.bindings[0].has_explicit_ordinal_importance is False


def test_importance_relation_does_not_make_criterion_required():
    evidence = _evidence(
        "Los criterios son seguridad y costo. Seguridad es más importante que costo."
    )
    assert all(not criterion.required for criterion in evidence.criteria)
    result = FOUNDATION.assess(evidence)
    assert all(item.explicit_importance is None for item in result.bindings)


def test_relation_marks_only_explicitly_related_criteria():
    evidence = _evidence(
        "Los criterios son seguridad, costo y tiempo. "
        "Seguridad es más importante que costo."
    )
    result = FOUNDATION.assess(evidence)
    assert tuple(item.has_explicit_ordinal_importance for item in result.bindings) == (
        True,
        True,
        False,
    )


def test_multiple_relations_are_preserved_without_transitive_closure():
    evidence = _evidence(
        "Los criterios son seguridad, costo y tiempo. "
        "Seguridad es más importante que costo. "
        "Costo es más importante que tiempo."
    )
    result = FOUNDATION.assess(evidence)
    assert len(result.ordinal_relations) == 2
    pairs = tuple(
        (
            relation.more_important_criterion_id,
            relation.less_important_criterion_id,
        )
        for relation in result.ordinal_relations
    )
    assert (
        evidence.criteria[0].criterion_id,
        evidence.criteria[2].criterion_id,
    ) not in pairs


def test_non_explicit_criteria_fail_closed_without_bindings():
    result = FOUNDATION.assess(_evidence("Seguridad importa más que costo."))
    assert (
        result.status is CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE
    )
    assert result.bindings == ()
    assert result.ordinal_relations == ()


def test_result_fingerprint_is_deterministic_and_content_sensitive():
    first = FOUNDATION.assess(_evidence("Los criterios son seguridad y costo."))
    second = FOUNDATION.assess(_evidence("Los criterios son seguridad y costo."))
    ordered = FOUNDATION.assess(
        _evidence(
            "Los criterios son seguridad y costo. "
            "Seguridad es más importante que costo."
        )
    )
    assert first.source_fingerprint == second.source_fingerprint
    assert first.source_fingerprint != ordered.source_fingerprint


def test_result_and_bindings_are_immutable():
    result = FOUNDATION.assess(_evidence("Los criterios son seguridad y costo."))
    with pytest.raises(FrozenInstanceError):
        result.status = CriterionImportanceCompatibilityStatus.INCOMPATIBLE_PROVENANCE
    with pytest.raises(FrozenInstanceError):
        result.bindings[0].explicit_importance = 1.0


def test_non_power_contract_is_explicit():
    result = FOUNDATION.assess(_evidence("Los criterios son seguridad y costo."))
    assert result.read_only is True
    assert result.derivational is True
    assert result.infers_importance is False
    assert result.assigns_importance is False
    assert result.ranks_criteria is False
    assert result.normalizes_weights is False
    assert result.infers_transitivity is False
    assert result.uses_llm is False
    assert result.uses_retrieval is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.evaluates_options is False
    assert result.evaluates_decision is False
    assert result.calls_gcdr is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_module_does_not_depend_on_gcdr_or_productive_runtime():
    import inspect

    import core.criterion_importance_compatibility as module

    source = inspect.getsource(module)
    assert "governed_complex_decision_reasoning" not in source
    assert "OfficialConversationGateway" not in source
    assert "CanonicalDecisionFacade" not in source


def test_schema_is_versioned():
    result = FOUNDATION.assess(_evidence("Los criterios son seguridad y costo."))
    assert result.schema_version == "post-m409.1-criterion-importance-compatibility-v1"
