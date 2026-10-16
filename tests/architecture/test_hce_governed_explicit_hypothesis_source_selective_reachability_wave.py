from __future__ import annotations

from dataclasses import replace

import pytest

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
    GovernedExplicitHypothesisSource,
    GovernedExplicitHypothesisSourceAdapterV1,
    GovernedExplicitHypothesisSourceStatus,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)


def _world():
    return PersistentWorldModelView().build(
        (
            PersistentWorldFact(
                fact_id="fact-home-heating",
                domain=PersistentWorldDomain.HOUSEHOLD,
                fact_key="heating:state",
                value="on",
                source_authority="household_memory",
                source_reference="household-1",
                epistemic_level=EpistemicLevel.FACT,
                evidence_codes=("household:observed",),
                persisted_by_source=True,
                active=True,
            ),
            PersistentWorldFact(
                fact_id="fact-weather-rain",
                domain=PersistentWorldDomain.ENVIRONMENT,
                fact_key="weather:rain",
                value="present",
                source_authority="canonical_memory",
                source_reference="weather-1",
                epistemic_level=EpistemicLevel.FACT,
                evidence_codes=("weather:observed",),
                persisted_by_source=True,
                active=True,
            ),
        )
    )


def _scenario_source():
    return GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-scenario-1",
        kind=ExplicitHypothesisSourceKind.SCENARIO,
        proposition="La calefacción está encendida.",
        world_domain="household",
        fact_key="heating:state",
        assumed_value="on",
        temporal_scope="current",
        source_reference="structured-decision-1",
        source_fingerprint="a" * 64,
        evidence_codes=("source:explicit_structured",),
    )


def _causal_source():
    return GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-causal-1",
        kind=ExplicitHypothesisSourceKind.CAUSAL,
        proposition="La lluvia puede aumentar la humedad.",
        cause_domain="environment",
        cause_key="weather:rain",
        cause_value="present",
        effect_domain="household",
        effect_key="humidity:state",
        effect_value="high",
        temporal_scope="future",
        source_reference="structured-decision-2",
        source_fingerprint="b" * 64,
        evidence_codes=("source:explicit_structured",),
    )


def test_complete_explicit_scenario_source_is_selectively_reachable():
    result = GovernedExplicitHypothesisSourceAdapterV1().evaluate(
        _scenario_source(),
        _world(),
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.SCENARIO_ELIGIBLE
    assert len(result.scenario_hypotheses) == 1
    assert result.scenario_report is not None
    hypothesis = result.scenario_hypotheses[0]
    assert hypothesis.world_domain == "household"
    assert hypothesis.fact_key == "heating:state"
    assert hypothesis.assumed_value == "on"
    assert result.scenario_report.world_snapshot_id == _world().snapshot_id
    assert result.causal_report is None


def test_complete_explicit_causal_source_is_selectively_reachable():
    result = GovernedExplicitHypothesisSourceAdapterV1().evaluate(
        _causal_source(),
        _world(),
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.CAUSAL_ELIGIBLE
    assert len(result.causal_hypotheses) == 1
    assert result.causal_report is not None
    hypothesis = result.causal_hypotheses[0]
    assert hypothesis.cause_key == "weather:rain"
    assert hypothesis.effect_key == "humidity:state"
    assert result.causal_report.world_snapshot_id == _world().snapshot_id
    assert result.scenario_report is None


def test_incomplete_scenario_semantics_fail_closed():
    source = replace(_scenario_source(), assumed_value=None)
    result = GovernedExplicitHypothesisSourceAdapterV1().evaluate(
        source,
        _world(),
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.REVIEW_REQUIRED
    assert result.scenario_hypotheses == ()
    assert result.scenario_report is None


def test_incomplete_causal_semantics_fail_closed():
    source = replace(_causal_source(), effect_value=None)
    result = GovernedExplicitHypothesisSourceAdapterV1().evaluate(
        source,
        _world(),
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.REVIEW_REQUIRED
    assert result.causal_hypotheses == ()
    assert result.causal_report is None


def test_non_hypothesis_source_is_not_applicable():
    source = GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-none-1",
        kind=ExplicitHypothesisSourceKind.NONE,
        proposition=None,
        source_reference="structured-decision-3",
        source_fingerprint="c" * 64,
    )
    result = GovernedExplicitHypothesisSourceAdapterV1().evaluate(
        source,
        _world(),
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.NOT_APPLICABLE
    assert result.scenario_report is None
    assert result.causal_report is None


def test_generic_decision_option_is_not_promoted_into_hypothesis():
    from core.governed_decision_advisory import GovernedDecisionOption

    option = GovernedDecisionOption(
        option_id="option-a",
        title="Comprar A",
        organization_item_id=None,
        scenario_hypothesis_id=None,
        causal_relation_id=None,
        explicit_preference=0.0,
    )
    result = GovernedExplicitHypothesisSourceAdapterV1().from_decision_options(
        (option,),
        world=_world(),
        source_fingerprint="d" * 64,
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.NOT_APPLICABLE
    assert result.scenario_hypotheses == ()
    assert result.causal_hypotheses == ()


def test_source_fields_are_not_inferred_from_proposition_text():
    source = GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-scenario-text-only",
        kind=ExplicitHypothesisSourceKind.SCENARIO,
        proposition="La calefacción está encendida.",
        source_reference="structured-decision-4",
        source_fingerprint="e" * 64,
    )
    result = GovernedExplicitHypothesisSourceAdapterV1().evaluate(
        source,
        _world(),
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.REVIEW_REQUIRED
    assert result.scenario_hypotheses == ()


def test_gateway_exposes_same_reasoning_authority_reachability():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    result = gateway.evaluate_explicit_hypothesis_source(
        _scenario_source(),
        world=_world(),
    )
    assert result.status is GovernedExplicitHypothesisSourceStatus.SCENARIO_ELIGIBLE
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.persists is False
    assert result.creates_memory is False
    assert result.creates_learning is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_world_snapshot_is_bound_into_result_and_tampering_changes_lineage():
    adapter = GovernedExplicitHypothesisSourceAdapterV1()
    first = adapter.evaluate(_scenario_source(), _world())
    modified_world = PersistentWorldModelView().build(())
    second = adapter.evaluate(_scenario_source(), modified_world)
    assert first.world_snapshot_id != second.world_snapshot_id
    assert first.source_fingerprint != second.source_fingerprint


def test_source_contract_rejects_non_sha256_lineage():
    with pytest.raises(ValueError, match="SHA-256"):
        GovernedExplicitHypothesisSource(
            source_id="explicit-hypothesis-source-invalid",
            kind=ExplicitHypothesisSourceKind.SCENARIO,
            proposition="x",
            world_domain="household",
            fact_key="x",
            assumed_value="y",
            source_reference="source",
            source_fingerprint="not-a-hash",
        )


def test_existing_decision_advisor_can_consume_reached_scenario_report():
    from app.canonical_decision_facade import CanonicalDecisionFacade
    from core.governed_decision_advisory import GovernedDecisionOption

    reached = GovernedExplicitHypothesisSourceAdapterV1().evaluate(
        _scenario_source(),
        _world(),
    )
    hypothesis_id = reached.scenario_hypotheses[0].hypothesis_id
    option = GovernedDecisionOption(
        option_id="option-scenario-a",
        title="Mantener calefacción",
        organization_item_id=None,
        scenario_hypothesis_id=hypothesis_id,
        causal_relation_id=None,
        explicit_preference=0.0,
    )
    report = CanonicalDecisionFacade().advise(
        (option,),
        scenarios=reached.scenario_report,
    )
    assert report.assessments[0].scenario_kind == "consistent"
    assert "scenario:consistent_with_persistent_fact" in (
        report.assessments[0].reason_codes
    )
