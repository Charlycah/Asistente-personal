from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.cognitive_authority_map import CognitiveAuthorityMap
from app.cognitive_operational_inventory import CognitiveAuthority
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulator,
    ScenarioHypothesis,
    ScenarioOutcomeKind,
    ScenarioSimulationStatus,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 18, 0, tzinfo=timezone.utc)


def _fact(
    *,
    fact_id: str = "fact-home-city",
    value: str = "San Miguel de Tucumán",
) -> PersistentWorldFact:
    return PersistentWorldFact(
        fact_id=fact_id,
        domain=PersistentWorldDomain.ENVIRONMENT,
        fact_key="home.city",
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
    hypothesis_id: str = "hyp-city",
    assumed_value: str = "San Miguel de Tucumán",
) -> ScenarioHypothesis:
    return ScenarioHypothesis(
        hypothesis_id=hypothesis_id,
        proposition=f"El hogar podría estar en {assumed_value}",
        world_domain="environment",
        fact_key="home.city",
        assumed_value=assumed_value,
        evidence_codes=("explicit_hypothesis",),
    )


def test_m391_3_preserves_governed_reasoning_as_single_authority() -> None:
    assignment = CognitiveAuthorityMap().snapshot.authority_for(
        CognitiveAuthority.REASONING
    )
    simulator = GovernedScenarioSimulator()
    assert assignment.primary == "governed_reasoning"
    assert simulator.CANONICAL_AUTHORITY == "governed_reasoning"
    assert not hasattr(simulator, "authority_id")


def test_m391_3_consistent_scenario_remains_hypothesis() -> None:
    world = PersistentWorldModelView().build((_fact(),))
    report = GovernedScenarioSimulator().simulate(world, (_hypothesis(),))
    assert report.status is ScenarioSimulationStatus.COMPLETE
    assert report.outcomes[0].kind is ScenarioOutcomeKind.CONSISTENT
    assert report.outcomes[0].epistemic_level is EpistemicLevel.HYPOTHESIS
    assert report.creates_facts is False


def test_m391_3_contradicted_scenario_is_not_rewritten() -> None:
    world = PersistentWorldModelView().build((_fact(),))
    hypothesis = _hypothesis(assumed_value="Córdoba")
    report = GovernedScenarioSimulator().simulate(world, (hypothesis,))
    assert report.outcomes[0].kind is ScenarioOutcomeKind.CONTRADICTED
    assert report.hypotheses[0] == hypothesis
    assert "scenario_contradicted" in report.risk_codes


def test_m391_3_missing_world_evidence_stays_unresolved() -> None:
    world = PersistentWorldModelView().build()
    report = GovernedScenarioSimulator().simulate(world, (_hypothesis(),))
    assert report.status is ScenarioSimulationStatus.INSUFFICIENT_EVIDENCE
    assert report.outcomes[0].kind is ScenarioOutcomeKind.UNRESOLVED
    assert report.outcomes[0].matched_fact_ids == ()


def test_m391_3_world_conflict_is_exposed_not_resolved() -> None:
    world = PersistentWorldModelView().build(
        (_fact(fact_id="a", value="A"), _fact(fact_id="b", value="B"))
    )
    report = GovernedScenarioSimulator().simulate(
        world,
        (_hypothesis(assumed_value="A"),),
    )
    assert report.status is ScenarioSimulationStatus.WORLD_CONFLICT_REVIEW_REQUIRED
    assert report.resolves_world_conflicts is False
    assert world.conflict_keys == ("environment:home.city",)


def test_m391_3_requires_explicit_hypothesis_epistemic_level() -> None:
    with pytest.raises(ValueError, match="remain hypotheses"):
        replace(_hypothesis(), epistemic_level=EpistemicLevel.FACT)


def test_m391_3_same_inputs_produce_same_report() -> None:
    world = PersistentWorldModelView().build((_fact(),))
    hypotheses = (
        _hypothesis(hypothesis_id="b"),
        _hypothesis(hypothesis_id="a"),
    )
    simulator = GovernedScenarioSimulator()
    assert simulator.simulate(world, hypotheses) == simulator.simulate(
        world, tuple(reversed(hypotheses))
    )


def test_m391_3_report_and_inputs_are_immutable() -> None:
    world = PersistentWorldModelView().build((_fact(),))
    hypothesis = _hypothesis()
    report = GovernedScenarioSimulator().simulate(world, (hypothesis,))
    with pytest.raises(FrozenInstanceError):
        hypothesis.assumed_value = "changed"
    with pytest.raises(FrozenInstanceError):
        report.status = ScenarioSimulationStatus.DEGRADED


def test_m391_3_does_not_persist_or_execute() -> None:
    world = PersistentWorldModelView().build((_fact(),))
    report = GovernedScenarioSimulator().simulate(world, (_hypothesis(),))
    assert report.read_only is True
    assert report.persists_hypotheses is False
    assert report.modifies_world_model is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.executes_actions is False
    assert report.grants_authority is False
    assert report.starts_background_process is False


def test_m391_3_safe_failure_degrades_without_authority() -> None:
    class BrokenSimulator(GovernedScenarioSimulator):
        @staticmethod
        def _evaluate(world, hypothesis):
            raise RuntimeError("synthetic failure")

    world = PersistentWorldModelView().build((_fact(),))
    report = BrokenSimulator().simulate_safely(world, (_hypothesis(),))
    assert report.status is ScenarioSimulationStatus.DEGRADED
    assert report.hypotheses == ()
    assert report.outcomes == ()
    assert report.risk_codes == ("scenario_simulation_failure",)
    assert report.grants_authority is False


def test_m391_3_rejects_duplicate_hypothesis_ids() -> None:
    world = PersistentWorldModelView().build((_fact(),))
    with pytest.raises(ValueError, match="identifiers must be unique"):
        GovernedScenarioSimulator().simulate(
            world,
            (_hypothesis(), _hypothesis()),
        )


def test_m391_3_uses_only_explicit_persistent_world_snapshot() -> None:
    source = (
        ROOT / "core" / "governed_reasoning" / "scenario_simulation.py"
    ).read_text(encoding="utf-8")
    assert "PersistentWorldSnapshot" in source
    assert "HouseholdMemory" not in source
    assert "CanonicalMemory" not in source
    assert "RelationshipMemory" not in source


def test_m391_3_has_no_credentials_storage_or_background_dependency() -> None:
    path = ROOT / "core" / "governed_reasoning" / "scenario_simulation.py"
    source = path.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "sqlite" not in source.casefold()
    assert "threading" not in source
    assert "asyncio" not in source
    assert "sleep(" not in source


def test_m391_3_does_not_modify_historical_hypothesis_workspace() -> None:
    path = ROOT / "app" / "cognitive_hypothesis_workspace.py"
    source = path.read_text(encoding="utf-8")
    assert "m391.3" not in source.casefold()
    assert "GovernedScenarioSimulator" not in source


def test_m391_3_preserves_canonical_core_constructor_line() -> None:
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


def test_m391_3_documentation_records_governed_scope() -> None:
    document = ROOT / "docs" / "M391_3_GOVERNED_HYPOTHESIS_SCENARIOS.md"
    text = document.read_text(encoding="utf-8")
    assert "governed_reasoning" in text
    assert "PersistentWorldSnapshot" in text
    assert "no convierte" in text
    assert "M391.3" in (ROOT / "README.md").read_text(encoding="utf-8")
