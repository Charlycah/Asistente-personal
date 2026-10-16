from __future__ import annotations

from datetime import datetime, timezone

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)
from core.governed_reasoning.causal_prediction import CausalHypothesis
from core.governed_reasoning.counterfactual_path_comparison import (
    CounterfactualPathComparisonStatus,
    GovernedCounterfactualPathComparator,
)
from core.governed_reasoning.multistage_causal_path import (
    GovernedMultiStageCausalPathComposer,
    MultiStageCausalPathStatus,
    MultiStageCausalStageStatus,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)

OWNER = "Carlos"
SESSION = "counterfactual-green"
NOW = datetime(2026, 8, 28, 16, 30, tzinfo=timezone.utc)


def _fact(fact_id: str, key: str, value: str) -> PersistentWorldFact:
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


def _world(*facts: PersistentWorldFact):
    return PersistentWorldModelView().build(facts)


def _stage(
    relation_id: str,
    *,
    cause_key: str,
    cause_value: str,
    effect_key: str,
    effect_value: str,
) -> CausalHypothesis:
    return CausalHypothesis(
        relation_id=relation_id,
        proposition=f"If {cause_value}, then {effect_value} may follow",
        cause_domain="environment",
        cause_key=cause_key,
        cause_value=cause_value,
        effect_domain="environment",
        effect_key=effect_key,
        effect_value=effect_value,
        evidence_codes=("explicit_causal_hypothesis",),
        temporal_scope="future",
    )


def _path_a(world=None):
    world = world or _world(_fact("fact-weather", "weather.current", "rain"))
    stages = (
        _stage(
            "rel-rain-wet",
            cause_key="weather.current",
            cause_value="rain",
            effect_key="patio.state",
            effect_value="wet",
        ),
        _stage(
            "rel-wet-slippery",
            cause_key="patio.state",
            cause_value="wet",
            effect_key="hazard.state",
            effect_value="slippery",
        ),
    )
    return GovernedMultiStageCausalPathComposer().compose(
        owner=OWNER,
        session_id=SESSION,
        baseline=world,
        hypotheses=stages,
    )


def _path_b(world=None):
    world = world or _world(_fact("fact-weather", "weather.current", "rain"))
    stages = (
        _stage(
            "rel-rain-wet-b",
            cause_key="weather.current",
            cause_value="rain",
            effect_key="patio.state",
            effect_value="wet",
        ),
        _stage(
            "rel-wet-safe",
            cause_key="patio.state",
            cause_value="wet",
            effect_key="hazard.state",
            effect_value="safe",
        ),
    )
    return GovernedMultiStageCausalPathComposer().compose(
        owner=OWNER,
        session_id=SESSION,
        baseline=world,
        hypotheses=stages,
    )


def test_a_to_b_to_c_forms_governed_multistage_path():
    path = _path_a()
    assert path.status is MultiStageCausalPathStatus.PATH_CANDIDATE
    assert tuple(stage.relation_id for stage in path.stages) == (
        "rel-rain-wet",
        "rel-wet-slippery",
    )
    assert path.stages[0].status is MultiStageCausalStageStatus.BASELINE_SUPPORTED
    assert path.stages[1].status is (
        MultiStageCausalStageStatus.CONDITIONALLY_PROPAGATED
    )
    assert path.stages[1].conditional_on_relation_id == "rel-rain-wet"
    assert path.terminal_projection == (
        "environment",
        "hazard.state",
        "slippery",
    )


def test_broken_a_to_b_then_x_to_c_chain_fails_closed():
    world = _world(_fact("fact-weather", "weather.current", "rain"))
    stages = (
        _stage(
            "rel-a-b",
            cause_key="weather.current",
            cause_value="rain",
            effect_key="patio.state",
            effect_value="wet",
        ),
        _stage(
            "rel-x-c",
            cause_key="system.mode",
            cause_value="manual",
            effect_key="hazard.state",
            effect_value="slippery",
        ),
    )
    path = GovernedMultiStageCausalPathComposer().compose(
        owner=OWNER,
        session_id=SESSION,
        baseline=world,
        hypotheses=stages,
    )
    assert path.status is MultiStageCausalPathStatus.BROKEN_CHAIN
    assert path.stages == ()
    assert path.terminal_projection is None


def test_unresolved_first_stage_blocks_downstream_projection():
    path = _path_a(_world())
    assert path.status is MultiStageCausalPathStatus.UPSTREAM_UNRESOLVED
    assert path.stages[0].status is MultiStageCausalStageStatus.UNRESOLVED
    assert path.stages[1].status is MultiStageCausalStageStatus.BLOCKED_BY_UPSTREAM
    assert path.terminal_projection is None


def test_intermediate_projection_never_becomes_world_fact():
    world = _world(_fact("fact-weather", "weather.current", "rain"))
    before = world
    path = _path_a(world)
    assert world == before
    assert all(not stage.establishes_fact for stage in path.stages)
    assert all(not stage.is_future_fact for stage in path.stages)
    assert path.creates_facts is False
    assert path.modifies_world_model is False


def test_two_explicit_paths_form_counterfactual_comparison_without_winner():
    comparison = GovernedCounterfactualPathComparator().compare(
        (_path_a(), _path_b())
    )
    assert comparison.status is (
        CounterfactualPathComparisonStatus.COMPARISON_CANDIDATE
    )
    assert len(comparison.path_ids) == 2
    assert comparison.divergences
    assert comparison.selects_winner is False
    assert comparison.establishes_preference is False
    assert comparison.establishes_truth is False
    assert comparison.establishes_causality is False


def test_single_path_cannot_be_presented_as_counterfactual_comparison():
    comparison = GovernedCounterfactualPathComparator().compare((_path_a(),))
    assert comparison.status is CounterfactualPathComparisonStatus.INSUFFICIENT_PATHS
    assert comparison.divergences == ()


def test_counterfactual_comparison_preserves_baseline_path_and_relation_lineage():
    left = _path_a()
    right = _path_b()
    comparison = GovernedCounterfactualPathComparator().compare((left, right))
    assert comparison.baseline_snapshot_id == left.baseline_snapshot_id
    assert set(comparison.path_ids) == {left.path_id, right.path_id}
    assert dict(comparison.relation_lineage)[left.path_id] == left.relation_ids
    assert dict(comparison.relation_lineage)[right.path_id] == right.relation_ids


def test_path_and_comparison_preserve_strict_governed_limits():
    path = _path_a()
    comparison = GovernedCounterfactualPathComparator().compare(
        (path, _path_b())
    )
    for artifact in (path, comparison):
        assert artifact.read_only is True
        assert artifact.consultative is True
        assert artifact.persists_results is False
        assert artifact.modifies_world_model is False
        assert artifact.modifies_memory is False
        assert artifact.modifies_learning is False
        assert artifact.modifies_planning is False
        assert artifact.registers_rule is False
        assert artifact.executes_transfer is False
        assert artifact.executes_actions is False
        assert artifact.grants_authority is False


def test_productive_gateway_binds_paths_and_same_turn_counterfactual_comparison():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    world = _world(_fact("fact-weather", "weather.current", "rain"))
    left = gateway.bind_productive_multistage_causal_path(
        owner=OWNER,
        session_id=SESSION,
        turn_id="path-a-turn",
        baseline=world,
        hypotheses=(
            _stage(
                "rel-a1",
                cause_key="weather.current",
                cause_value="rain",
                effect_key="patio.state",
                effect_value="wet",
            ),
            _stage(
                "rel-a2",
                cause_key="patio.state",
                cause_value="wet",
                effect_key="hazard.state",
                effect_value="slippery",
            ),
        ),
    )
    right = _path_b(world)
    text = "Comparar las dos trayectorias contrafactuales."
    request = GovernedConversationPipelineRequest(
        owner=OWNER,
        session_id=SESSION,
        text=text,
    )
    turn_id = build_governed_conversation_turn_identity(request, NOW).turn_id
    comparison = gateway.bind_productive_counterfactual_path_comparison(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
        paths=(left, right),
    )
    refs = gateway.productive_counterfactual_path_comparison_reference_ids(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert comparison.comparison_id in refs
    assert left.path_id in refs
    assert right.path_id in refs
    assert comparison.baseline_snapshot_id in refs


def test_counterfactual_comparison_reaches_reasoning_consultatively_same_turn():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    text = "Comparar las dos trayectorias contrafactuales."
    request = GovernedConversationPipelineRequest(
        owner=OWNER,
        session_id=SESSION,
        text=text,
    )
    turn_id = build_governed_conversation_turn_identity(request, NOW).turn_id
    comparison = gateway.bind_productive_counterfactual_path_comparison(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
        paths=(_path_a(), _path_b()),
    )
    source = CanonicalProductiveReasoningSource(gateway)
    lines = source.counterfactual_path_comparison_context_lines(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=NOW,
    )
    assert "Comparación contrafactual gobernada disponible" in lines[0]
    assert "no establece verdad ni causalidad" in lines[1]
    assert "no autoriza planificación" in lines[1]
    refs = source.reference_ids(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=NOW,
    )
    assert comparison.comparison_id in refs
