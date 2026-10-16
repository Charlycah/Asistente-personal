from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.canonical_decision_facade import CanonicalDecisionFacade
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_decision_advisory import (
    DecisionAdvisoryStatus,
    DecisionOptionDisposition,
    GovernedDecisionAdvisor,
    GovernedDecisionOption,
)
from core.governed_reasoning.causal_prediction import (
    CausalHypothesis,
    GovernedCausalPredictiveReasoner,
)
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulator,
    ScenarioHypothesis,
)
from core.intelligent_personal_organization import (
    IntelligentPersonalOrganizationView,
    PersonalOrganizationItem,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)

ROOT = Path(__file__).resolve().parents[2]


def _world():
    facts = (
        PersistentWorldFact(
            fact_id="fact-weather",
            domain=PersistentWorldDomain.ENVIRONMENT,
            fact_key="weather",
            value="rain",
            source_authority="canonical_memory",
            source_reference="memory:weather",
            epistemic_level=EpistemicLevel.FACT,
            evidence_codes=("explicit:weather",),
            persisted_by_source=True,
        ),
        PersistentWorldFact(
            fact_id="fact-road",
            domain=PersistentWorldDomain.ENVIRONMENT,
            fact_key="road",
            value="wet",
            source_authority="canonical_memory",
            source_reference="memory:road",
            epistemic_level=EpistemicLevel.FACT,
            evidence_codes=("explicit:road",),
            persisted_by_source=True,
        ),
    )
    return PersistentWorldModelView().build(facts)


def _organization():
    item = PersonalOrganizationItem(
        item_id="task-a",
        capability="tasks",
        title="Prepare umbrella",
        urgency=0.9,
        importance=0.8,
        context_relevance=0.8,
        user_declared=True,
    )
    return IntelligentPersonalOrganizationView().organize((item,))


def _scenarios():
    hypothesis = ScenarioHypothesis(
        hypothesis_id="scenario-rain",
        proposition="It is raining",
        world_domain="environment",
        fact_key="weather",
        assumed_value="rain",
        evidence_codes=("scenario:explicit",),
    )
    return GovernedScenarioSimulator().simulate(_world(), (hypothesis,))


def _causal():
    hypothesis = CausalHypothesis(
        relation_id="relation-rain-road",
        proposition="Rain is associated with a wet road",
        cause_domain="environment",
        cause_key="weather",
        cause_value="rain",
        effect_domain="environment",
        effect_key="road",
        effect_value="wet",
        evidence_codes=("causal:explicit",),
    )
    return GovernedCausalPredictiveReasoner().analyze(_world(), (hypothesis,))


def _option(option_id: str = "option-a", **changes) -> GovernedDecisionOption:
    values = {
        "option_id": option_id,
        "title": f"Option {option_id}",
        "organization_item_id": "task-a",
        "scenario_hypothesis_id": "scenario-rain",
        "causal_relation_id": "relation-rain-road",
    }
    values.update(changes)
    return GovernedDecisionOption(**values)


def test_m391_6_preserves_canonical_decision_authority() -> None:
    advisor = GovernedDecisionAdvisor()
    report = advisor.assess(
        (_option(),),
        organization=_organization(),
        scenarios=_scenarios(),
        causal=_causal(),
    )
    assert advisor.CANONICAL_AUTHORITY == "unified_cognitive_coordination"
    assert advisor.CANONICAL_FACADE == "CanonicalDecisionFacade"
    assert report.canonical_authority == "unified_cognitive_coordination"
    assert report.canonical_facade == "CanonicalDecisionFacade"


def test_m391_6_canonical_facade_exposes_advisory_without_binding() -> None:
    report = CanonicalDecisionFacade().advise(
        (_option(),),
        organization=_organization(),
        scenarios=_scenarios(),
        causal=_causal(),
    )
    assert report.recommended_option_id == "option-a"
    assert report.status is DecisionAdvisoryStatus.COMPLETE


def test_m391_6_combines_existing_governed_evidence() -> None:
    report = GovernedDecisionAdvisor().assess(
        (_option(),),
        organization=_organization(),
        scenarios=_scenarios(),
        causal=_causal(),
    )
    item = report.assessments[0]
    assert item.disposition is DecisionOptionDisposition.RECOMMEND
    assert item.priority_score is not None
    assert item.organization_kind == "prioritize"
    assert item.scenario_kind == "consistent"
    assert item.causal_kind == "association_compatible"
    assert item.prediction_kind == "conditionally_expected"


def test_m391_6_recommendation_is_never_action_authority() -> None:
    report = GovernedDecisionAdvisor().assess(
        (_option(scenario_hypothesis_id=None, causal_relation_id=None),),
        organization=_organization(),
    )
    assert report.recommended_option_id == "option-a"
    assert report.assessments[0].action_authorized is False
    assert report.advisory_only is True
    assert report.human_decision_preserved is True
    assert report.executes_actions is False


def test_m391_6_missing_linked_evidence_requires_review() -> None:
    report = GovernedDecisionAdvisor().assess((_option(),))
    assert report.recommended_option_id is None
    assert report.status is DecisionAdvisoryStatus.REVIEW_REQUIRED
    assert report.assessments[0].disposition is DecisionOptionDisposition.REVIEW
    assert (
        "decision:organization_evidence_missing"
        in report.assessments[0].reason_codes
    )


def test_m391_6_scenario_contradiction_blocks_option() -> None:
    contradicted = GovernedScenarioSimulator().simulate(
        _world(),
        (
            ScenarioHypothesis(
                hypothesis_id="scenario-rain",
                proposition="Weather is sunny",
                world_domain="environment",
                fact_key="weather",
                assumed_value="sunny",
            ),
        ),
    )
    report = GovernedDecisionAdvisor().assess(
        (_option(causal_relation_id=None),),
        organization=_organization(),
        scenarios=contradicted,
    )
    assert report.recommended_option_id is None
    assert report.assessments[0].disposition is DecisionOptionDisposition.BLOCKED


def test_m391_6_causal_contradiction_blocks_option() -> None:
    contradicted = GovernedCausalPredictiveReasoner().analyze(
        _world(),
        (
            CausalHypothesis(
                relation_id="relation-rain-road",
                proposition="Sun causes wet road",
                cause_domain="environment",
                cause_key="weather",
                cause_value="sunny",
                effect_domain="environment",
                effect_key="road",
                effect_value="wet",
            ),
        ),
    )
    report = GovernedDecisionAdvisor().assess(
        (_option(scenario_hypothesis_id=None),),
        organization=_organization(),
        causal=contradicted,
    )
    assert report.recommended_option_id is None
    assert report.assessments[0].disposition is DecisionOptionDisposition.BLOCKED


def test_m391_6_explicit_preference_is_visible_not_hidden() -> None:
    option = GovernedDecisionOption(
        option_id="manual",
        title="User-declared option",
        explicit_preference=0.7,
    )
    report = GovernedDecisionAdvisor().assess((option,))
    assert report.recommended_option_id == "manual"
    assert "decision:explicit_preference" in report.assessments[0].reason_codes


def test_m391_6_priority_then_preference_breaks_ties_deterministically() -> None:
    organization = _organization()
    options = (
        _option(
            "b",
            scenario_hypothesis_id=None,
            causal_relation_id=None,
            explicit_preference=0.9,
        ),
        _option(
            "a",
            scenario_hypothesis_id=None,
            causal_relation_id=None,
            explicit_preference=0.1,
        ),
    )
    report = GovernedDecisionAdvisor().assess(options, organization=organization)
    assert report.recommended_option_id == "b"


def test_m391_6_same_inputs_are_deterministic() -> None:
    advisor = GovernedDecisionAdvisor()
    kwargs = {
        "organization": _organization(),
        "scenarios": _scenarios(),
        "causal": _causal(),
    }
    assert advisor.assess((_option(),), **kwargs) == advisor.assess(
        (_option(),), **kwargs
    )


def test_m391_6_empty_options_are_insufficient() -> None:
    report = GovernedDecisionAdvisor().assess(())
    assert report.status is DecisionAdvisoryStatus.INSUFFICIENT_EVIDENCE
    assert report.recommended_option_id is None


def test_m391_6_duplicate_option_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="ids must be unique"):
        GovernedDecisionAdvisor().assess((_option(), _option()))


def test_m391_6_report_is_immutable() -> None:
    report = GovernedDecisionAdvisor().assess(
        (_option(),), organization=_organization()
    )
    with pytest.raises(FrozenInstanceError):
        report.read_only = False
    with pytest.raises(FrozenInstanceError):
        report.assessments[0].disposition = DecisionOptionDisposition.BLOCKED


def test_m391_6_advisory_cannot_be_promoted_to_action() -> None:
    report = GovernedDecisionAdvisor().assess(
        (_option(),), organization=_organization()
    )
    with pytest.raises(ValueError, match="cannot authorize action"):
        replace(report.assessments[0], action_authorized=True)


def test_m391_6_is_read_only_and_non_mutating() -> None:
    report = GovernedDecisionAdvisor().assess(
        (_option(),), organization=_organization()
    )
    assert report.read_only is True
    assert report.creates_facts is False
    assert report.creates_plans is False
    assert report.creates_tasks is False
    assert report.persists_results is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.modifies_organization is False
    assert report.executes_actions is False
    assert report.grants_authority is False
    assert report.starts_background_process is False


def test_m391_6_safe_failure_degrades_without_authority() -> None:
    report = GovernedDecisionAdvisor().assess_safely((_option(), _option()))
    assert report.status is DecisionAdvisoryStatus.DEGRADED
    assert report.assessments == ()
    assert report.recommended_option_id is None
    assert report.risk_codes == ("decision_advisory_failure",)


def test_m391_6_does_not_add_runtime_persistence_or_credentials() -> None:
    source = (ROOT / "core" / "governed_decision_advisory.py").read_text(
        encoding="utf-8"
    ).casefold()
    for forbidden in (
        "credentials.json",
        ".roby",
        "sqlite",
        "threading",
        "asyncio",
        "sleep(",
        "execute(",
        "create_task(",
    ):
        assert forbidden not in source


def test_m391_6_preserves_canonical_core_constructor_line() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]


def test_m391_6_documentation_records_governed_scope() -> None:
    document = ROOT / "docs" / "M391_6_GOVERNED_DECISION_ADVISORY.md"
    text = document.read_text(encoding="utf-8")
    assert "CanonicalDecisionFacade" in text
    assert "unified_cognitive_coordination" in text
    assert "no crea" in text
    assert "M391.6" in (ROOT / "README.md").read_text(encoding="utf-8")
