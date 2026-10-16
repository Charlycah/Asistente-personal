from __future__ import annotations

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_decision_advisory import (
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
    ScenarioOutcomeKind,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)


def _fact(fact_id: str, key: str, value: str) -> PersistentWorldFact:
    return PersistentWorldFact(
        fact_id=fact_id,
        domain=PersistentWorldDomain.ENVIRONMENT,
        fact_key=key,
        value=value,
        source_authority="canonical_memory",
        source_reference=f"challenge:{fact_id}",
        epistemic_level=EpistemicLevel.FACT,
        evidence_codes=("challenge:explicit",),
        persisted_by_source=True,
    )


def _world(*, car: str = "available", train: str = "available"):
    return PersistentWorldModelView().build(
        (
            _fact("car", "transport.car", car),
            _fact("train", "transport.train", train),
            _fact("arrival", "trip.arrival", "viable"),
        )
    )


def _scenario(option: str, assumed: str) -> ScenarioHypothesis:
    return ScenarioHypothesis(
        hypothesis_id=f"future-{option}",
        proposition=f"Future transport state for {option}",
        world_domain="environment",
        fact_key=f"transport.{option}",
        assumed_value=assumed,
        evidence_codes=(f"prospection:option:{option}",),
        temporal_scope="future",
    )


def _causal(option: str, cause_value: str, effect_value: str) -> CausalHypothesis:
    return CausalHypothesis(
        relation_id=f"relation-{option}-arrival",
        proposition=f"{option} state may affect arrival",
        cause_domain="environment",
        cause_key=f"transport.{option}",
        cause_value=cause_value,
        effect_domain="environment",
        effect_key="trip.arrival",
        effect_value=effect_value,
        evidence_codes=(f"prospection:option:{option}",),
        temporal_scope="future",
    )


def _option(option: str) -> GovernedDecisionOption:
    return GovernedDecisionOption(
        option_id=option,
        title=option,
        scenario_hypothesis_id=f"future-{option}",
        causal_relation_id=f"relation-{option}-arrival",
    )


def test_mf1_currently_supported_future_can_support_option_a():
    world = _world(car="available", train="unavailable")
    scenarios = GovernedScenarioSimulator().simulate(
        world,
        (_scenario("car", "available"), _scenario("train", "available")),
    )
    causal = GovernedCausalPredictiveReasoner().analyze(
        world,
        (
            _causal("car", "available", "viable"),
            _causal("train", "available", "viable"),
        ),
    )
    report = GovernedDecisionAdvisor().assess(
        (_option("car"), _option("train")),
        scenarios=scenarios,
        causal=causal,
    )
    assert report.recommended_option_id == "car"


def test_mf2_currently_supported_future_can_support_option_b():
    world = _world(car="unavailable", train="available")
    scenarios = GovernedScenarioSimulator().simulate(
        world,
        (_scenario("car", "available"), _scenario("train", "available")),
    )
    causal = GovernedCausalPredictiveReasoner().analyze(
        world,
        (
            _causal("car", "available", "viable"),
            _causal("train", "available", "viable"),
        ),
    )
    report = GovernedDecisionAdvisor().assess(
        (_option("car"), _option("train")),
        scenarios=scenarios,
        causal=causal,
    )
    assert report.recommended_option_id == "train"


def test_mf3_counterfactual_future_is_not_treated_as_current_fact_conflict():
    world = _world(car="available", train="available")
    scenarios = GovernedScenarioSimulator().simulate(
        world,
        (_scenario("car", "unavailable"),),
    )
    outcome = scenarios.outcomes[0]
    assert outcome.kind is not ScenarioOutcomeKind.CONTRADICTED


def test_mf4_two_alternative_futures_can_coexist_for_same_current_state():
    world = _world(car="available")
    scenarios = GovernedScenarioSimulator().simulate(
        world,
        (
            ScenarioHypothesis(
                hypothesis_id="car-stays-available",
                proposition="Car remains available",
                world_domain="environment",
                fact_key="transport.car",
                assumed_value="available",
                temporal_scope="future",
            ),
            ScenarioHypothesis(
                hypothesis_id="car-breaks",
                proposition="Car becomes unavailable",
                world_domain="environment",
                fact_key="transport.car",
                assumed_value="unavailable",
                temporal_scope="future",
            ),
        ),
    )
    kinds = {item.hypothesis_id: item.kind for item in scenarios.outcomes}
    assert kinds["car-stays-available"] is ScenarioOutcomeKind.CONSISTENT
    assert kinds["car-breaks"] is not ScenarioOutcomeKind.CONTRADICTED


def test_mf5_future_effect_need_not_already_exist_as_current_fact():
    world = PersistentWorldModelView().build(
        (_fact("car", "transport.car", "available"),)
    )
    causal = GovernedCausalPredictiveReasoner().analyze(
        world,
        (_causal("car", "available", "viable"),),
    )
    assert causal.predictions[0].kind.value == "conditionally_expected"


def test_mf6_uncertain_future_withholds_instead_of_inventing_winner():
    world = PersistentWorldModelView().build(
        (_fact("weather", "weather", "uncertain"),)
    )
    scenarios = GovernedScenarioSimulator().simulate(
        world,
        (
            _scenario("car", "available"),
            _scenario("train", "available"),
        ),
    )
    report = GovernedDecisionAdvisor().assess(
        (_option("car"), _option("train")),
        scenarios=scenarios,
    )
    assert report.recommended_option_id is None
    assert all(
        item.disposition is DecisionOptionDisposition.REVIEW
        for item in report.assessments
    )


def test_mf7_changing_only_projected_consequences_can_reverse_recommendation():
    world = _world(car="available", train="available")
    options = (_option("car"), _option("train"))
    scenarios = GovernedScenarioSimulator().simulate(
        world,
        (_scenario("car", "available"), _scenario("train", "available")),
    )
    first = GovernedCausalPredictiveReasoner().analyze(
        world,
        (
            _causal("car", "available", "viable"),
            _causal("train", "available", "blocked"),
        ),
    )
    second = GovernedCausalPredictiveReasoner().analyze(
        world,
        (
            _causal("car", "available", "blocked"),
            _causal("train", "available", "viable"),
        ),
    )
    advisor = GovernedDecisionAdvisor()
    before = advisor.assess(options, scenarios=scenarios, causal=first)
    after = advisor.assess(options, scenarios=scenarios, causal=second)
    assert before.recommended_option_id == "car"
    assert after.recommended_option_id == "train"


def test_mf8_prospection_remains_read_only_and_non_executing():
    world = _world()
    scenarios = GovernedScenarioSimulator().simulate(
        world,
        (_scenario("car", "available"),),
    )
    causal = GovernedCausalPredictiveReasoner().analyze(
        world,
        (_causal("car", "available", "viable"),),
    )
    report = GovernedDecisionAdvisor().assess(
        (_option("car"),),
        scenarios=scenarios,
        causal=causal,
    )
    assert scenarios.read_only is True
    assert scenarios.modifies_world_model is False
    assert causal.read_only is True
    assert causal.modifies_world_model is False
    assert report.read_only is True
    assert report.advisory_only is True
    assert report.executes_actions is False
