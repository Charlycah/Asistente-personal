from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.criterion_importance_compatibility import (
    CriterionImportanceCompatibilityFoundationV1,
)
from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidenceProducerV1,
    ExplicitComplexDecisionCriteriaStatus,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitDecisionDeliberationStatus,
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_option_criterion_evidence import (
    ExplicitOptionCriterionEvidenceProducerV1,
    ExplicitOptionCriterionEvidenceStatus,
)
from core.gcdr_assessment_adapter import CertifiedGCDRAssessmentAdapterV1
from core.gcdr_complete_input_assembly import GCDRCompleteInputAssemblyFoundationV1
from core.governed_complex_decision_reasoning import (
    ComplexDecisionReasoningStatus,
)
from core.option_criteria_certified_linkage import (
    CertifiedOptionCriterionEvidenceLinkageV1,
)
from core.productive_gcdr_advisory_wiring import ProductiveGCDRAdvisoryWiringV1

WIRING = ProductiveGCDRAdvisoryWiringV1()


def _assembly(
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
    return GCDRCompleteInputAssemblyFoundationV1().assemble(
        option_adaptation=option_adaptation,
        criteria_evidence=criteria,
        assessment_adaptation=assessments,
        importance_compatibility=importance,
    )


def test_consumes_certified_complete_assembly_and_returns_gcdr_report():
    assembly = _assembly()
    result = WIRING.advise(assembly)
    assert result.assembly_fingerprint == assembly.source_fingerprint
    assert result.report_fingerprint == result.report.source_fingerprint
    assert result.report.source_option_ids == tuple(
        sorted(option.option_id for option in assembly.options)
    )


def test_existing_gcdr_withholds_recommendation_when_matrix_has_insufficient_pairs():
    result = WIRING.advise(_assembly())
    assert result.report.status is ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE
    assert result.report.recommended_option_id is None


def test_complete_explicit_matrix_can_produce_advisory_recommendation():
    assembly = _assembly(
        relation_text=(
            "A cumple seguridad. A cumple costo. "
            "B no cumple seguridad. B no cumple costo."
        )
    )
    result = WIRING.advise(assembly)
    option_a = assembly.options[0].option_id
    assert result.report.status is ComplexDecisionReasoningStatus.COMPLETE
    assert result.report.recommended_option_id == option_a


def test_required_criterion_can_block_option_without_action_authority():
    assembly = _assembly(
        criteria_text=(
            "Los criterios son seguridad y costo. Seguridad es obligatoria."
        ),
        relation_text=(
            "A no cumple seguridad. A cumple costo. "
            "B cumple seguridad. B cumple costo."
        ),
    )
    result = WIRING.advise(assembly)
    blocked = next(
        item
        for item in result.report.option_assessments
        if item.option_id == assembly.options[0].option_id
    )
    assert blocked.blocking_criterion_ids == (assembly.criteria[0].criterion_id,)
    assert blocked.action_authorized is False


def test_ordinal_importance_is_not_promoted_to_cardinal_weight():
    assembly = _assembly(
        criteria_text=(
            "Los criterios son seguridad y costo. "
            "Seguridad es más importante que costo."
        )
    )
    result = WIRING.advise(assembly)
    assert all(item.explicit_importance is None for item in result.report.criteria)
    assert assembly.ordinal_importance_relations


def test_result_fingerprint_is_deterministic():
    assembly = _assembly()
    first = WIRING.advise(assembly)
    second = WIRING.advise(assembly)
    assert first.source_fingerprint == second.source_fingerprint
    assert first.report.source_fingerprint == second.report.source_fingerprint


def test_result_is_immutable():
    result = WIRING.advise(_assembly())
    with pytest.raises(FrozenInstanceError):
        result.source_fingerprint = "x" * 64


def test_productive_result_preserves_canonical_decision_authority():
    result = WIRING.advise(_assembly())
    assert result.canonical_authority == "unified_cognitive_coordination"
    assert result.canonical_facade == "CanonicalDecisionFacade"
    assert result.report.canonical_authority == result.canonical_authority
    assert result.report.canonical_facade == result.canonical_facade


def test_productive_wiring_is_advisory_only_and_preserves_human_decision():
    result = WIRING.advise(_assembly())
    assert result.read_only is True
    assert result.advisory_only is True
    assert result.human_decision_preserved is True
    assert result.consumes_certified_assembly_only is True
    assert result.infers_missing_evidence is False
    assert result.synthesizes_importance is False
    assert result.creates_plans is False
    assert result.modifies_organization is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False


def test_gcdr_report_preserves_non_power_contract_productively():
    report = WIRING.advise(_assembly()).report
    assert report.read_only is True
    assert report.advisory_only is True
    assert report.human_decision_preserved is True
    assert report.creates_plans is False
    assert report.persists_results is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
    assert report.modifies_world_model is False
    assert report.modifies_planning is False
    assert report.modifies_organization is False
    assert report.executes_actions is False
    assert report.grants_authority is False
    assert report.starts_background_process is False


def test_wiring_does_not_import_gateway_runtime_memory_learning_or_actions():
    import inspect

    import core.productive_gcdr_advisory_wiring as module

    source = inspect.getsource(module)
    assert "OfficialConversationGateway" not in source
    assert "OfficialMemoryGateway" not in source
    assert "from app.official_conversation_gateway" not in source
    assert "from app.memory" not in source
    assert "from core.learning" not in source
    assert "from domain.governed_action" not in source


def test_wiring_reuses_existing_gcdr_without_reimplementing_selection():
    import inspect

    import core.productive_gcdr_advisory_wiring as module

    source = inspect.getsource(module)
    assert "GovernedComplexDecisionReasoningFoundationV1().assess" in source
    assert "_dominates(" not in source
    assert "_lexicographic_selection(" not in source


def test_current_turn_combined_intake_is_not_yet_gcdr_reachable():
    text = (
        "Entre A y B, ¿cuál conviene? Los criterios son seguridad y costo. "
        "A cumple seguridad."
    )
    deliberation = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(text)
    criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1().analyze(text)
    relations = ExplicitOptionCriterionEvidenceProducerV1().analyze(text)
    assert deliberation.status is not ExplicitDecisionDeliberationStatus.EXPLICIT
    assert criteria.status is ExplicitComplexDecisionCriteriaStatus.EXPLICIT
    assert relations.status is ExplicitOptionCriterionEvidenceStatus.EXPLICIT


def test_productive_wiring_stays_outside_gateway_until_intake_contract_exists():
    import inspect

    import core.productive_gcdr_advisory_wiring as module

    source = inspect.getsource(module)
    assert "OfficialConversationGateway" not in source
    assert "submit(" not in source


def test_schema_is_versioned():
    result = WIRING.advise(_assembly())
    assert result.schema_version == "post-m409.1-productive-gcdr-advisory-wiring-v1"
