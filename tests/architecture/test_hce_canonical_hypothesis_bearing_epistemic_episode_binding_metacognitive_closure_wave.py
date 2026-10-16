from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from app.governed_reasoning_runtime import (
    CanonicalProductiveEpistemicAssessmentStatus,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
    GovernedExplicitHypothesisSource,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)

NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


def _world():
    return PersistentWorldModelView().build(
        (
            PersistentWorldFact(
                fact_id="fact-home-heating",
                domain=PersistentWorldDomain.HOUSEHOLD,
                fact_key="heating:state",
                value="on",
                source_authority="canonical_memory",
                source_reference="household-1",
                epistemic_level=EpistemicLevel.FACT,
                evidence_codes=("household:observed",),
                persisted_by_source=True,
                active=True,
            ),
        )
    )


def _scenario_source():
    return GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-scenario-closure-1",
        kind=ExplicitHypothesisSourceKind.SCENARIO,
        proposition="La calefacción está encendida.",
        world_domain="household",
        fact_key="heating:state",
        assumed_value="on",
        temporal_scope="current",
        source_reference="structured-source-closure-1",
        source_fingerprint="a" * 64,
        evidence_codes=("source:explicit_structured",),
    )


def _none_source():
    return GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-none-closure-1",
        kind=ExplicitHypothesisSourceKind.NONE,
        proposition=None,
        source_reference="structured-source-none",
        source_fingerprint="b" * 64,
    )


def _episode(gateway, turn_id="turn-closure-1"):
    return gateway.evaluate_productive_episode(
        owner="carlos",
        session_id="session-closure",
        text="Analiza la situación.",
        now=NOW,
        turn_id=turn_id,
        scope_reference="session-closure",
        observe_productive_intake=False,
    )


def test_non_hypothesis_source_remains_not_applicable():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = _episode(gateway)
    assessment = gateway.bind_productive_epistemic_assessment(
        episode,
        _none_source(),
        world=_world(),
    )
    assert assessment.status is (
        CanonicalProductiveEpistemicAssessmentStatus.NOT_APPLICABLE
    )
    assert assessment.deepening is None
    assert assessment.method_outcome is None


def test_scenario_source_binds_complete_epistemic_chain_to_same_turn():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = _episode(gateway)
    assessment = gateway.bind_productive_epistemic_assessment(
        episode,
        _scenario_source(),
        world=_world(),
    )
    assert assessment.status is CanonicalProductiveEpistemicAssessmentStatus.ASSESSED
    assert assessment.turn_id == episode.turn_id
    assert assessment.reasoning_episode_fingerprint == episode.source_fingerprint
    assert assessment.hypothesis_source_result.scenario_report is not None
    report = assessment.hypothesis_source_result.scenario_report
    assert assessment.productive_reference_id == report.simulation_id
    assert assessment.deepening.source_reference == report.simulation_id
    assert assessment.sufficiency.source_hypothesis_deepening_report_id == (
        assessment.deepening.report_id
    )
    assert assessment.quality.source_epistemic_sufficiency_assessment_id == (
        assessment.sufficiency.assessment_id
    )
    assert assessment.method_provenance.source_reasoning_quality_assessment_id == (
        assessment.quality.assessment_id
    )
    assert assessment.method_outcome.source_reference == report.simulation_id
    assert assessment.world_snapshot_id == _world().snapshot_id


def test_same_turn_binding_is_idempotent_and_does_not_run_twice():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = _episode(gateway)
    first = gateway.bind_productive_epistemic_assessment(
        episode,
        _scenario_source(),
        world=_world(),
    )
    second = gateway.bind_productive_epistemic_assessment(
        episode,
        _scenario_source(),
        world=_world(),
    )
    assert second is first


def test_different_source_or_world_cannot_replace_bound_same_turn_episode():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = _episode(gateway)
    gateway.bind_productive_epistemic_assessment(
        episode,
        _scenario_source(),
        world=_world(),
    )
    changed = replace(_scenario_source(), source_fingerprint="c" * 64)
    with pytest.raises(ValueError, match="already bound"):
        gateway.bind_productive_epistemic_assessment(
            episode,
            changed,
            world=_world(),
        )


def test_later_turn_does_not_reuse_prior_epistemic_episode():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    first_episode = _episode(gateway, "turn-closure-1")
    first = gateway.bind_productive_epistemic_assessment(
        first_episode,
        _scenario_source(),
        world=_world(),
    )
    second_episode = gateway.evaluate_productive_episode(
        owner="carlos",
        session_id="session-closure",
        text="Analiza una situación posterior.",
        now=NOW,
        turn_id="turn-closure-2",
        scope_reference="session-closure",
        observe_productive_intake=False,
    )
    second = gateway.bind_productive_epistemic_assessment(
        second_episode,
        _scenario_source(),
        world=_world(),
    )
    assert first.turn_id != second.turn_id
    assert first.assessment_episode_id != second.assessment_episode_id


def test_bound_reference_can_be_exposed_only_for_exact_canonical_turn():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = _episode(gateway)
    assessment = gateway.bind_productive_epistemic_assessment(
        episode,
        _scenario_source(),
        world=_world(),
    )
    refs = gateway.productive_epistemic_reference_ids(
        owner="carlos",
        session_id="session-closure",
        turn_id=episode.turn_id,
    )
    assert refs == (assessment.productive_reference_id,)
    assert (
        gateway.productive_epistemic_reference_ids(
            owner="carlos",
            session_id="session-closure",
            turn_id="another-turn",
        )
        == ()
    )


def test_binding_is_read_only_and_does_not_create_memory_or_learning():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    assessment = gateway.bind_productive_epistemic_assessment(
        _episode(gateway),
        _scenario_source(),
        world=_world(),
    )
    assert assessment.read_only is True
    assert assessment.persists is False
    assert assessment.creates_memory is False
    assert assessment.creates_learning is False
    assert assessment.executes_actions is False
    assert assessment.grants_authority is False


def test_reasoning_runtime_contribution_exposes_exact_bound_reference():
    from app.governed_reasoning_runtime import CanonicalProductiveReasoningSource
    from core.llm_provider import LLMRequest
    from core.reasoning_runtime_integration import ReasoningRuntimeContributor

    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = gateway.evaluate_productive_episode(
        owner="carlos",
        session_id="session-runtime-ref",
        text="Analiza la situación.",
        now=NOW,
        turn_id=(
            __import__(
                "core.governed_operational_conversation_pipeline",
                fromlist=["build_governed_conversation_turn_identity"],
            )
            .build_governed_conversation_turn_identity(
                __import__(
                    "core.governed_operational_conversation_pipeline",
                    fromlist=["GovernedConversationPipelineRequest"],
                ).GovernedConversationPipelineRequest(
                    owner="carlos",
                    session_id="session-runtime-ref",
                    text="Analiza la situación.",
                ),
                NOW,
            )
            .turn_id
        ),
        scope_reference="session-runtime-ref",
        observe_productive_intake=False,
    )
    assessment = gateway.bind_productive_epistemic_assessment(
        episode,
        _scenario_source(),
        world=_world(),
    )
    contributor = ReasoningRuntimeContributor(
        CanonicalProductiveReasoningSource(gateway)
    )
    contribution = contributor.contribute(
        owner="carlos",
        session_id="session-runtime-ref",
        text="Analiza la situación.",
        request=LLMRequest(prompt="unused"),
        now=NOW,
    )
    assert assessment.productive_reference_id in contribution.reference_ids
