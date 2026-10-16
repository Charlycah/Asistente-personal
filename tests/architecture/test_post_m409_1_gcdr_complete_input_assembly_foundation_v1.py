from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from core.criterion_importance_compatibility import (
    CriterionImportanceCompatibilityFoundationV1,
)
from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidenceProducerV1,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_option_criterion_evidence import (
    ExplicitOptionCriterionEvidenceProducerV1,
)
from core.gcdr_assessment_adapter import CertifiedGCDRAssessmentAdapterV1
from core.gcdr_complete_input_assembly import (
    GCDRCompleteInputAssemblyFoundationV1,
    GCDRCompleteInputAssemblyStatus,
)
from core.governed_complex_decision_reasoning import (
    ComplexDecisionCriterionOutcome,
)
from core.option_criteria_certified_linkage import (
    CertifiedOptionCriterionEvidenceLinkageV1,
)

FOUNDATION = GCDRCompleteInputAssemblyFoundationV1()


def _pipeline(
    *,
    criteria_text: str = "Los criterios son seguridad y costo.",
    relation_text: str = "A cumple seguridad.",
):
    deliberation = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "Entre A y B, ¿cuál conviene?"
    )
    option_adaptation = ExplicitDeliberationDecisionOptionAdapter().adapt(deliberation)
    criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(
        criteria_text
    )
    relations = ExplicitOptionCriterionEvidenceProducerV1().analyze(relation_text)
    linkage = CertifiedOptionCriterionEvidenceLinkageV1().link(
        deliberation=deliberation,
        option_adaptation=option_adaptation,
        criteria_evidence=criteria,
        relation_evidence=relations,
    )
    assessments = CertifiedGCDRAssessmentAdapterV1().adapt(
        option_adaptation=option_adaptation,
        criteria_evidence=criteria,
        linkage=linkage,
    )
    importance = CriterionImportanceCompatibilityFoundationV1().assess(criteria)
    return option_adaptation, criteria, assessments, importance


def _assemble(**kwargs):
    option_adaptation, criteria, assessments, importance = _pipeline(**kwargs)
    return FOUNDATION.assemble(
        option_adaptation=option_adaptation,
        criteria_evidence=criteria,
        assessment_adaptation=assessments,
        importance_compatibility=importance,
    )


def test_assembles_certified_options_criteria_and_assessments():
    option_adaptation, criteria_evidence, assessments, _ = _pipeline()
    result = _assemble()
    assert result.status is GCDRCompleteInputAssemblyStatus.ASSEMBLED
    assert result.options == option_adaptation.options
    assert result.assessments == assessments.assessments
    assert tuple(item.criterion_id for item in result.criteria) == tuple(
        item.criterion_id for item in criteria_evidence.criteria
    )


def test_criterion_adaptation_preserves_text_required_and_none_importance():
    result = _assemble(
        criteria_text=(
            "Los criterios son seguridad y costo. Seguridad es obligatoria."
        )
    )
    first, second = result.criteria
    assert first.title == "seguridad"
    assert first.required is True
    assert second.required is False
    assert all(item.explicit_importance is None for item in result.criteria)


def test_criterion_provenance_codes_preserve_source_and_required_span():
    result = _assemble(
        criteria_text=(
            "Los criterios son seguridad y costo. Seguridad es obligatoria."
        )
    )
    first = result.criteria[0]
    assert any(
        code.startswith("criterion_evidence:") for code in first.provenance_codes
    )
    assert any(code.startswith("criterion_span:") for code in first.provenance_codes)
    assert any(
        code.startswith("criterion_required_span:") for code in first.provenance_codes
    )


def test_ordinal_importance_is_preserved_without_cardinal_synthesis():
    result = _assemble(
        criteria_text=(
            "Los criterios son seguridad y costo. "
            "Seguridad es más importante que costo."
        )
    )
    assert len(result.ordinal_importance_relations) == 1
    relation = result.ordinal_importance_relations[0]
    assert relation.more_important_criterion_id == result.criteria[0].criterion_id
    assert relation.less_important_criterion_id == result.criteria[1].criterion_id
    assert all(item.explicit_importance is None for item in result.criteria)


def test_assessment_matrix_remains_complete_and_preserves_insufficient_pairs():
    result = _assemble()
    assert len(result.assessments) == len(result.options) * len(result.criteria)
    outcomes = tuple(item.outcome for item in result.assessments)
    assert ComplexDecisionCriterionOutcome.FAVORABLE in outcomes
    assert ComplexDecisionCriterionOutcome.INSUFFICIENT in outcomes


def test_assessment_adapter_exposes_explicit_source_lineage():
    option_adaptation, criteria, assessments, _ = _pipeline()
    assert (
        assessments.option_adaptation_fingerprint
        == option_adaptation.source_fingerprint
    )
    assert assessments.criteria_evidence_fingerprint == criteria.source_fingerprint
    assert len(assessments.linkage_fingerprint) == 64


def test_option_lineage_mismatch_fails_closed():
    option_adaptation, criteria, assessments, importance = _pipeline()
    broken = replace(
        assessments,
        option_adaptation_fingerprint="f" * 64,
    )
    with pytest.raises(ValueError, match="option lineage"):
        FOUNDATION.assemble(
            option_adaptation=option_adaptation,
            criteria_evidence=criteria,
            assessment_adaptation=broken,
            importance_compatibility=importance,
        )


def test_criterion_lineage_mismatch_fails_closed_even_when_ids_match():
    option_adaptation, _, assessments, _ = _pipeline()
    other_criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(
        "Los criterios son seguridad y costo. Seguridad es obligatoria."
    )
    other_importance = CriterionImportanceCompatibilityFoundationV1().assess(
        other_criteria
    )
    with pytest.raises(ValueError, match="criterion lineage"):
        FOUNDATION.assemble(
            option_adaptation=option_adaptation,
            criteria_evidence=other_criteria,
            assessment_adaptation=assessments,
            importance_compatibility=other_importance,
        )


def test_importance_lineage_mismatch_fails_closed():
    option_adaptation, criteria, assessments, importance = _pipeline()
    broken_binding = replace(
        importance.bindings[0],
        criterion_source_fingerprint="f" * 64,
    )
    broken = replace(
        importance,
        bindings=(broken_binding, *importance.bindings[1:]),
    )
    with pytest.raises(ValueError, match="importance lineage"):
        FOUNDATION.assemble(
            option_adaptation=option_adaptation,
            criteria_evidence=criteria,
            assessment_adaptation=assessments,
            importance_compatibility=broken,
        )


def test_incomplete_assessment_matrix_fails_closed():
    option_adaptation, criteria, assessments, importance = _pipeline()
    broken = replace(assessments, assessments=assessments.assessments[:-1])
    with pytest.raises(ValueError, match="complete assessment matrix"):
        FOUNDATION.assemble(
            option_adaptation=option_adaptation,
            criteria_evidence=criteria,
            assessment_adaptation=broken,
            importance_compatibility=importance,
        )


def test_result_fingerprint_is_deterministic_and_content_sensitive():
    first = _assemble()
    second = _assemble()
    required = _assemble(
        criteria_text=(
            "Los criterios son seguridad y costo. Seguridad es obligatoria."
        )
    )
    assert first.source_fingerprint == second.source_fingerprint
    assert first.source_fingerprint != required.source_fingerprint


def test_result_is_immutable():
    result = _assemble()
    with pytest.raises(FrozenInstanceError):
        result.status = GCDRCompleteInputAssemblyStatus.ASSEMBLED


def test_non_power_contract_is_explicit():
    result = _assemble()
    assert result.read_only is True
    assert result.derivational is True
    assert result.generates_options is False
    assert result.generates_criteria is False
    assert result.infers_importance is False
    assert result.assigns_importance is False
    assert result.infers_assessments is False
    assert result.evaluates_decision is False
    assert result.ranks_options is False
    assert result.recommends_option is False
    assert result.calls_gcdr is False
    assert result.uses_llm is False
    assert result.uses_retrieval is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_assembly_module_does_not_call_gcdr_or_productive_runtime():
    import inspect

    import core.gcdr_complete_input_assembly as module

    source = inspect.getsource(module)
    assert "GovernedComplexDecisionReasoningFoundationV1" not in source
    assert "OfficialConversationGateway" not in source
    assert "CanonicalDecisionFacade" not in source


def test_schema_is_versioned():
    result = _assemble()
    assert result.schema_version == "post-m409.1-gcdr-complete-input-assembly-v1"
