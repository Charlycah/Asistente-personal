from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.cognitive_authority_map import CognitiveAuthorityMap
from app.cognitive_operational_inventory import CognitiveAuthority
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.causal_prediction import (
    CausalAssessmentKind,
    CausalHypothesis,
    CausalPredictionStatus,
    GovernedCausalPredictiveReasoner,
    PredictiveOutcomeKind,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 19, 0, tzinfo=timezone.utc)


def _fact(
    fact_id: str,
    key: str,
    value: str,
) -> PersistentWorldFact:
    return PersistentWorldFact(
        fact_id=fact_id,
        domain=PersistentWorldDomain.ENVIRONMENT,
        fact_key=key,
        value=value,
        source_authority="canonical_memory",
        source_reference=f"ref:{fact_id}",
        epistemic_level=EpistemicLevel.FACT,
        evidence_codes=("explicit_governed_source",),
        persisted_by_source=True,
        source_updated_at=NOW,
    )


def _hypothesis(
    *,
    relation_id: str = "rel-rain-wet",
    cause_value: str = "rain",
    effect_value: str = "wet",
) -> CausalHypothesis:
    return CausalHypothesis(
        relation_id=relation_id,
        proposition="If weather is rain, patio state could become wet",
        cause_domain="environment",
        cause_key="weather.current",
        cause_value=cause_value,
        effect_domain="environment",
        effect_key="patio.state",
        effect_value=effect_value,
        evidence_codes=("explicit_causal_hypothesis",),
    )


def _world(
    *,
    weather: str = "rain",
    patio: str = "wet",
):
    return PersistentWorldModelView().build(
        (
            _fact("fact-weather", "weather.current", weather),
            _fact("fact-patio", "patio.state", patio),
        )
    )


def test_m391_4_preserves_governed_reasoning_as_single_authority() -> None:
    assignment = CognitiveAuthorityMap().snapshot.authority_for(
        CognitiveAuthority.REASONING
    )
    reasoner = GovernedCausalPredictiveReasoner()
    assert assignment.primary == "governed_reasoning"
    assert reasoner.CANONICAL_AUTHORITY == "governed_reasoning"
    assert not hasattr(reasoner, "authority_id")


def test_m391_4_cooccurrence_does_not_prove_causality() -> None:
    report = GovernedCausalPredictiveReasoner().analyze(
        _world(),
        (_hypothesis(),),
    )
    assessment = report.assessments[0]
    assert assessment.kind is CausalAssessmentKind.ASSOCIATION_COMPATIBLE
    assert assessment.epistemic_level is EpistemicLevel.HYPOTHESIS
    assert assessment.establishes_causality is False
    assert report.proves_causality is False


def test_m391_4_prediction_remains_inference_not_fact() -> None:
    report = GovernedCausalPredictiveReasoner().analyze(
        _world(),
        (_hypothesis(),),
    )
    prediction = report.predictions[0]
    assert prediction.kind is PredictiveOutcomeKind.CONDITIONALLY_EXPECTED
    assert prediction.epistemic_level is EpistemicLevel.INFERENCE
    assert prediction.is_future_fact is False
    assert report.creates_facts is False


def test_m391_4_effect_contradiction_remains_visible() -> None:
    report = GovernedCausalPredictiveReasoner().analyze(
        _world(patio="dry"),
        (_hypothesis(),),
    )
    assert report.assessments[0].kind is CausalAssessmentKind.EFFECT_CONTRADICTED
    assert report.predictions[0].kind is PredictiveOutcomeKind.CURRENTLY_CONTRADICTED
    assert "causal_hypothesis_contradicted" in report.risk_codes


def test_m391_4_cause_contradiction_remains_visible() -> None:
    report = GovernedCausalPredictiveReasoner().analyze(
        _world(weather="sunny"),
        (_hypothesis(),),
    )
    assert report.assessments[0].kind is CausalAssessmentKind.CAUSE_CONTRADICTED
    assert report.predictions[0].kind is PredictiveOutcomeKind.CURRENTLY_CONTRADICTED


def test_m391_4_missing_evidence_stays_unresolved() -> None:
    world = PersistentWorldModelView().build()
    report = GovernedCausalPredictiveReasoner().analyze(world, (_hypothesis(),))
    assert report.status is CausalPredictionStatus.INSUFFICIENT_EVIDENCE
    assert report.assessments[0].kind is CausalAssessmentKind.UNRESOLVED
    assert report.predictions[0].kind is PredictiveOutcomeKind.UNRESOLVED


def test_m391_4_world_conflicts_are_not_resolved() -> None:
    world = PersistentWorldModelView().build(
        (
            _fact("weather-a", "weather.current", "rain"),
            _fact("weather-b", "weather.current", "sunny"),
            _fact("patio", "patio.state", "wet"),
        )
    )
    report = GovernedCausalPredictiveReasoner().analyze(world, (_hypothesis(),))
    assert report.status is CausalPredictionStatus.WORLD_CONFLICT_REVIEW_REQUIRED
    assert world.conflict_keys == ("environment:weather.current",)
    assert report.modifies_world_model is False


def test_m391_4_causal_inputs_must_remain_hypotheses() -> None:
    with pytest.raises(ValueError, match="remain hypotheses"):
        replace(_hypothesis(), epistemic_level=EpistemicLevel.FACT)


def test_m391_4_predictions_cannot_be_promoted_to_future_facts() -> None:
    report = GovernedCausalPredictiveReasoner().analyze(
        _world(),
        (_hypothesis(),),
    )
    with pytest.raises(ValueError, match="future facts"):
        replace(report.predictions[0], is_future_fact=True)


def test_m391_4_same_inputs_are_deterministic_and_order_independent() -> None:
    world = _world()
    hypotheses = (
        _hypothesis(relation_id="b"),
        _hypothesis(relation_id="a"),
    )
    reasoner = GovernedCausalPredictiveReasoner()
    assert reasoner.analyze(world, hypotheses) == reasoner.analyze(
        world,
        tuple(reversed(hypotheses)),
    )


def test_m391_4_reports_are_immutable() -> None:
    report = GovernedCausalPredictiveReasoner().analyze(
        _world(),
        (_hypothesis(),),
    )
    with pytest.raises(FrozenInstanceError):
        report.status = CausalPredictionStatus.DEGRADED
    with pytest.raises(FrozenInstanceError):
        report.hypotheses[0].cause_value = "changed"


def test_m391_4_does_not_persist_learn_plan_or_execute() -> None:
    report = GovernedCausalPredictiveReasoner().analyze(
        _world(),
        (_hypothesis(),),
    )
    assert report.read_only is True
    assert report.persists_results is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.executes_actions is False
    assert report.grants_authority is False
    assert report.starts_background_process is False
    assert report.calibrates_probability is False


def test_m391_4_safe_failure_degrades_without_authority() -> None:
    class BrokenReasoner(GovernedCausalPredictiveReasoner):
        @classmethod
        def _assess(cls, world, hypothesis):
            raise RuntimeError("synthetic failure")

    report = BrokenReasoner().analyze_safely(_world(), (_hypothesis(),))
    assert report.status is CausalPredictionStatus.DEGRADED
    assert report.hypotheses == ()
    assert report.assessments == ()
    assert report.predictions == ()
    assert report.risk_codes == ("causal_prediction_failure",)
    assert report.grants_authority is False


def test_m391_4_rejects_duplicate_relation_ids() -> None:
    with pytest.raises(ValueError, match="identifiers must be unique"):
        GovernedCausalPredictiveReasoner().analyze(
            _world(),
            (_hypothesis(), _hypothesis()),
        )


def test_m391_4_reads_only_explicit_world_snapshot() -> None:
    source = (
        ROOT / "core" / "governed_reasoning" / "causal_prediction.py"
    ).read_text(encoding="utf-8")
    assert "PersistentWorldSnapshot" in source
    assert "HouseholdMemory" not in source
    assert "CanonicalMemory" not in source
    assert "RelationshipMemory" not in source


def test_m391_4_has_no_credentials_storage_or_background_dependency() -> None:
    source = (
        ROOT / "core" / "governed_reasoning" / "causal_prediction.py"
    ).read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "sqlite" not in source.casefold()
    assert "threading" not in source
    assert "asyncio" not in source
    assert "sleep(" not in source


def test_m391_4_preserves_scenario_simulator_contract() -> None:
    source = (
        ROOT / "core" / "governed_reasoning" / "scenario_simulation.py"
    ).read_text(encoding="utf-8")
    assert "m391.4" not in source.casefold()
    assert "GovernedCausalPredictiveReasoner" not in source


def test_m391_4_preserves_canonical_core_constructor_line() -> None:
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


def test_m391_4_documentation_records_governed_scope() -> None:
    document = ROOT / "docs" / "M391_4_GOVERNED_CAUSAL_PREDICTION.md"
    text = document.read_text(encoding="utf-8")
    assert "governed_reasoning" in text
    assert "PersistentWorldSnapshot" in text
    assert "no demuestra causalidad" in text
    assert "predicción" in text
    assert "M391.4" in (ROOT / "README.md").read_text(encoding="utf-8")
