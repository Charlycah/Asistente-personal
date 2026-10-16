from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

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
from core.governed_complex_decision_reasoning import ComplexDecisionCriterionOutcome
from core.option_criteria_certified_linkage import (
    CertifiedOptionCriterionEvidenceLinkageV1,
)


def _sources(relation_text: str = "A cumple seguridad."):
    deliberation = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "Entre A y B, ¿cuál conviene?"
    )
    option_adaptation = ExplicitDeliberationDecisionOptionAdapter().adapt(deliberation)
    criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(
        "Los criterios son seguridad y costo."
    )
    relations = ExplicitOptionCriterionEvidenceProducerV1().analyze(relation_text)
    linkage = CertifiedOptionCriterionEvidenceLinkageV1().link(
        deliberation=deliberation,
        option_adaptation=option_adaptation,
        criteria_evidence=criteria,
        relation_evidence=relations,
    )
    return option_adaptation, criteria, linkage


def _adapt(relation_text: str = "A cumple seguridad."):
    option_adaptation, criteria, linkage = _sources(relation_text)
    return CertifiedGCDRAssessmentAdapterV1().adapt(
        option_adaptation=option_adaptation,
        criteria_evidence=criteria,
        linkage=linkage,
    )


def test_builds_complete_option_criterion_matrix():
    option_adaptation, criteria, _ = _sources()
    result = _adapt()
    assert len(result.assessments) == (
        len(option_adaptation.options) * len(criteria.criteria)
    )
    assert tuple(
        (item.option_id, item.criterion_id) for item in result.assessments
    ) == tuple(
        (option.option_id, criterion.criterion_id)
        for option in option_adaptation.options
        for criterion in criteria.criteria
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    (
        ("A cumple seguridad.", ComplexDecisionCriterionOutcome.FAVORABLE),
        ("A no cumple seguridad.", ComplexDecisionCriterionOutcome.UNFAVORABLE),
        ("No sé si A cumple seguridad.", ComplexDecisionCriterionOutcome.INSUFFICIENT),
    ),
)
def test_maps_certified_outcome_by_exact_enum_value(text, expected):
    result = _adapt(text)
    assert result.assessments[0].outcome is expected
    assert result.assessments[0].explicit_value is None


def test_missing_pairs_become_insufficient_not_neutral():
    result = _adapt()
    assert result.assessments[0].outcome is ComplexDecisionCriterionOutcome.FAVORABLE
    for item in result.assessments[1:]:
        assert item.outcome is ComplexDecisionCriterionOutcome.INSUFFICIENT
        assert item.evidence_codes == ("gcdr_adapter:no_certified_evidence_for_pair",)
        assert item.explicit_value is None


def test_explicit_assessment_preserves_certified_evidence_identity():
    option_adaptation, criteria, linkage = _sources()
    result = _adapt()
    binding = linkage.bindings[0]
    assessment = result.assessments[0]
    assert binding.evidence_id in assessment.evidence_codes[0]
    assert assessment.option_id == binding.option_id
    assert assessment.criterion_id == binding.criterion_id
    assert assessment.source_fingerprint is not None
    assert len(assessment.source_fingerprint) == 64


def test_non_linked_input_fails_closed():
    option_adaptation, criteria, linkage = _sources("No dije nada sobre seguridad.")
    with pytest.raises(ValueError, match="requires linked certified evidence"):
        CertifiedGCDRAssessmentAdapterV1().adapt(
            option_adaptation=option_adaptation,
            criteria_evidence=criteria,
            linkage=linkage,
        )


def test_option_provenance_mismatch_fails_closed():
    option_adaptation, criteria, linkage = _sources()
    other_deliberation = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "Entre C y D, ¿cuál conviene?"
    )
    other_adaptation = ExplicitDeliberationDecisionOptionAdapter().adapt(
        other_deliberation
    )
    with pytest.raises(ValueError, match="option provenance"):
        CertifiedGCDRAssessmentAdapterV1().adapt(
            option_adaptation=other_adaptation,
            criteria_evidence=criteria,
            linkage=linkage,
        )


def test_criterion_provenance_mismatch_fails_closed():
    option_adaptation, _, linkage = _sources()
    other_criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(
        "Los criterios son privacidad y precio."
    )
    with pytest.raises(ValueError, match="criterion provenance"):
        CertifiedGCDRAssessmentAdapterV1().adapt(
            option_adaptation=option_adaptation,
            criteria_evidence=other_criteria,
            linkage=linkage,
        )


def test_result_fingerprint_is_deterministic():
    assert _adapt().source_fingerprint == _adapt().source_fingerprint


def test_result_is_immutable():
    result = _adapt()
    with pytest.raises(FrozenInstanceError):
        result.source_fingerprint = "x" * 64


def test_non_power_contract_is_explicit():
    result = _adapt()
    assert result.read_only is True
    assert result.derivational is True
    assert result.parses_text is False
    assert result.infers_outcome is False
    assert result.assigns_value is False
    assert result.uses_llm is False
    assert result.uses_retrieval is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.evaluates_decision is False
    assert result.calls_gcdr is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_adapter_does_not_call_gcdr_or_productive_runtime():
    import inspect

    import core.gcdr_assessment_adapter as module

    source = inspect.getsource(module)
    assert "GovernedComplexDecisionReasoningFoundationV1" not in source
    assert "OfficialConversationGateway" not in source
    assert "CanonicalDecisionFacade" not in source


def test_schema_is_versioned():
    assert _adapt().schema_version == "post-m409.1-gcdr-assessment-adapter-v1"
