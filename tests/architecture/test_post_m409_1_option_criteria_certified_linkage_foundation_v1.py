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
    ExplicitOptionCriterionOutcome,
)
from core.option_criteria_certified_linkage import (
    CertifiedOptionCriterionEvidenceLinkageV1,
    CertifiedOptionCriterionLinkageStatus,
)


def _sources(option_text: str = "A cumple seguridad."):
    deliberation = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "Entre A y B, ¿cuál conviene?"
    )
    adaptation = ExplicitDeliberationDecisionOptionAdapter().adapt(deliberation)
    criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(
        "Los criterios son seguridad y costo."
    )
    relations = ExplicitOptionCriterionEvidenceProducerV1().analyze(option_text)
    return deliberation, adaptation, criteria, relations


def _link(option_text: str = "A cumple seguridad."):
    deliberation, adaptation, criteria, relations = _sources(option_text)
    return CertifiedOptionCriterionEvidenceLinkageV1().link(
        deliberation=deliberation,
        option_adaptation=adaptation,
        criteria_evidence=criteria,
        relation_evidence=relations,
    )


def test_links_exact_certified_option_and_criterion_identity():
    result = _link()
    assert result.status is CertifiedOptionCriterionLinkageStatus.LINKED
    binding = result.bindings[0]
    deliberation, adaptation, criteria, _ = _sources()
    assert binding.option_id == adaptation.options[0].option_id
    assert binding.criterion_id == criteria.criteria[0].criterion_id
    assert binding.option_source_fingerprint == deliberation.source_fingerprint


def test_preserves_explicit_outcome_without_inference():
    result = _link("B no cumple costo.")
    assert result.bindings[0].outcome is ExplicitOptionCriterionOutcome.UNFAVORABLE


def test_preserves_insufficient_outcome():
    result = _link("No sé si B cumple costo.")
    assert result.bindings[0].outcome is ExplicitOptionCriterionOutcome.INSUFFICIENT


def test_case_and_superficial_whitespace_normalization_is_exact_identity():
    result = _link("a cumple SEGURIDAD.")
    assert result.status is CertifiedOptionCriterionLinkageStatus.LINKED


def test_partial_option_name_does_not_link():
    deliberation = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "Entre comprar Peugeot y comprar Ford, ¿cuál conviene?"
    )
    adaptation = ExplicitDeliberationDecisionOptionAdapter().adapt(deliberation)
    criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(
        "Los criterios son seguridad y costo."
    )
    relations = ExplicitOptionCriterionEvidenceProducerV1().analyze(
        "Peugeot cumple seguridad."
    )
    result = CertifiedOptionCriterionEvidenceLinkageV1().link(
        deliberation=deliberation,
        option_adaptation=adaptation,
        criteria_evidence=criteria,
        relation_evidence=relations,
    )
    assert result.status is CertifiedOptionCriterionLinkageStatus.UNRESOLVED_OPTION
    assert result.bindings == ()


def test_unknown_criterion_fails_closed():
    result = _link("A cumple privacidad.")
    assert result.status is CertifiedOptionCriterionLinkageStatus.UNRESOLVED_CRITERION
    assert result.bindings == ()


def test_unknown_option_fails_closed():
    result = _link("C cumple seguridad.")
    assert result.status is CertifiedOptionCriterionLinkageStatus.UNRESOLVED_OPTION


def test_batch_failure_exposes_no_partial_bindings():
    result = _link("A cumple seguridad. C cumple costo.")
    assert result.status is CertifiedOptionCriterionLinkageStatus.UNRESOLVED_OPTION
    assert result.bindings == ()


def test_non_relation_evidence_returns_no_evidence():
    result = _link("No dije nada sobre seguridad.")
    assert result.status is CertifiedOptionCriterionLinkageStatus.NO_EVIDENCE
    assert result.bindings == ()


def test_adaptation_lineage_mismatch_fails_closed():
    deliberation, adaptation, criteria, relations = _sources()
    other = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "Entre C y D, ¿cuál conviene?"
    )
    result = CertifiedOptionCriterionEvidenceLinkageV1().link(
        deliberation=other,
        option_adaptation=adaptation,
        criteria_evidence=criteria,
        relation_evidence=relations,
    )
    assert (
        result.status is CertifiedOptionCriterionLinkageStatus.INCOMPATIBLE_PROVENANCE
    )


def test_binding_preserves_all_three_source_spans():
    result = _link()
    binding = result.bindings[0]
    assert binding.option_source_span[1] > binding.option_source_span[0]
    assert binding.criterion_source_span[1] > binding.criterion_source_span[0]
    assert binding.relation_source_span[1] > binding.relation_source_span[0]


def test_result_fingerprint_is_deterministic():
    assert _link().source_fingerprint == _link().source_fingerprint


def test_result_is_immutable():
    result = _link()
    with pytest.raises(FrozenInstanceError):
        result.status = CertifiedOptionCriterionLinkageStatus.NO_EVIDENCE


def test_non_power_invariants_are_explicit():
    result = _link()
    assert result.read_only is True
    assert result.parses_text is False
    assert result.generates_options is False
    assert result.generates_criteria is False
    assert result.infers_outcome is False
    assert result.uses_fuzzy_matching is False
    assert result.uses_semantic_matching is False
    assert result.uses_llm is False
    assert result.uses_retrieval is False
    assert result.resolves_context is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.evaluates_decision is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_linkage_does_not_create_gcdr_assessment():
    result = _link()
    assert not hasattr(result.bindings[0], "evidence_codes")
    assert not hasattr(result.bindings[0], "explicit_value")
    assert not hasattr(result, "recommended_option_id")


def test_schema_is_versioned():
    result = _link()
    assert result.schema_version == "post-m409.1-option-criteria-certified-linkage-v1"


def test_linkage_module_has_no_productive_or_gcdr_dependency():
    import inspect

    import core.option_criteria_certified_linkage as module

    source = inspect.getsource(module)
    assert "governed_complex_decision_reasoning" not in source
    assert "OfficialConversationGateway" not in source
    assert "CanonicalDecisionFacade" not in source


def test_linkage_preserves_multiple_exact_relations_in_source_order():
    result = _link("A cumple seguridad. B no cumple costo.")
    assert result.status is CertifiedOptionCriterionLinkageStatus.LINKED
    assert tuple(binding.outcome for binding in result.bindings) == (
        ExplicitOptionCriterionOutcome.FAVORABLE,
        ExplicitOptionCriterionOutcome.UNFAVORABLE,
    )
