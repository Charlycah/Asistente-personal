from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from app.unified_cognitive_coordination import (
    CognitiveStrategyApplicationEvidence,
    CognitiveStrategyApplicationOutcomeStatus,
    UnifiedCognitiveCoordinator,
)
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
    GovernedExplicitHypothesisSource,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


def _world():
    return PersistentWorldModelView().build(
        (
            PersistentWorldFact(
                fact_id="fact-final-closure",
                domain=PersistentWorldDomain.HOUSEHOLD,
                fact_key="heating:state",
                value="on",
                source_authority="canonical_memory",
                source_reference="household-final",
                epistemic_level=EpistemicLevel.FACT,
                evidence_codes=("household:observed",),
                persisted_by_source=True,
                active=True,
            ),
        )
    )


def _source():
    return GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-final-closure",
        kind=ExplicitHypothesisSourceKind.SCENARIO,
        proposition="La calefacción está encendida.",
        world_domain="household",
        fact_key="heating:state",
        assumed_value="on",
        temporal_scope="current",
        source_reference="structured-final-closure",
        source_fingerprint="d" * 64,
    )


def _request(*, admitted=True):
    kwargs = {}
    if admitted:
        kwargs = {
            "explicit_hypothesis_source": _source(),
            "hypothesis_world_snapshot": _world(),
        }
    return GovernedConversationPipelineRequest(
        owner="carlos",
        session_id="session-final-closure",
        text="Analiza y planifica esta situación.",
        **kwargs,
    )


def test_explicit_hypothesis_admission_requires_source_and_world_together():
    with pytest.raises(ValueError, match="must be admitted together"):
        GovernedConversationPipelineRequest(
            owner="carlos",
            session_id="session-final-closure",
            text="Analiza.",
            explicit_hypothesis_source=_source(),
        )


def test_ordinary_turn_without_explicit_source_does_not_bind_epistemic_episode():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    result = GovernedRuntimePreparation._bind_productive_epistemic_episode(
        request=_request(admitted=False),
        reasoning_runtime=gateway,
        now=NOW,
    )
    assert result is None
    assert gateway.snapshot.evaluations == 0


def test_productive_preparation_binding_builds_exact_same_turn_epistemic_episode():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    result = GovernedRuntimePreparation._bind_productive_epistemic_episode(
        request=_request(),
        reasoning_runtime=gateway,
        now=NOW,
    )
    assert result is not None
    assert result.method_outcome is not None
    assert result.productive_reference_id == result.method_outcome.source_reference


def test_runtime_reference_is_available_after_preparation_binding():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    request = _request()
    result = GovernedRuntimePreparation._bind_productive_epistemic_episode(
        request=request,
        reasoning_runtime=gateway,
        now=NOW,
    )
    refs = gateway.productive_epistemic_reference_ids(
        owner=request.owner,
        session_id=request.session_id,
        turn_id=result.turn_id,
    )
    assert refs == (result.productive_reference_id,)


def test_productive_strategy_outcome_is_constructed_and_admitted_once():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    request = _request()
    epistemic = GovernedRuntimePreparation._bind_productive_epistemic_episode(
        request=request,
        reasoning_runtime=gateway,
        now=NOW,
    )
    coordinator = UnifiedCognitiveCoordinator(registry=None)
    strategy = coordinator.synthesize_strategy_advisory(request)
    assert strategy is not None
    coordinator._productive_strategy_instances[strategy.source_fingerprint] = strategy
    application = CognitiveStrategyApplicationEvidence(
        strategy_fingerprint=strategy.source_fingerprint,
        owner=request.owner,
        scope=request.session_id,
        status=CognitiveStrategyApplicationOutcomeStatus.APPLIED,
        requested_stage_sequence=("reasoning",),
        applied_stage_sequence=("reasoning",),
        skipped_stages=(),
        failed_stages=(),
        unmet_requirements=(),
        contribution_reference_ids=(epistemic.productive_reference_id,),
        rationale_codes=("test:exact_productive_application",),
        source_fingerprint="e" * 64,
    )
    first = GovernedRuntimePreparation._close_productive_epistemic_strategy_outcome(
        request=request,
        epistemic_episode=epistemic,
        strategy_application_evidence=application,
        strategy_coordinator=coordinator,
    )
    second = GovernedRuntimePreparation._close_productive_epistemic_strategy_outcome(
        request=request,
        epistemic_episode=epistemic,
        strategy_application_evidence=application,
        strategy_coordinator=coordinator,
    )
    assert first.observation_id == second.observation_id
    assert len(coordinator._productive_strategy_outcomes) == 1


def test_wrong_runtime_reference_fails_closed_before_metacognitive_admission():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    request = _request()
    epistemic = GovernedRuntimePreparation._bind_productive_epistemic_episode(
        request=request,
        reasoning_runtime=gateway,
        now=NOW,
    )
    coordinator = UnifiedCognitiveCoordinator(registry=None)
    strategy = coordinator.synthesize_strategy_advisory(request)
    assert strategy is not None
    coordinator._productive_strategy_instances[strategy.source_fingerprint] = strategy
    application = CognitiveStrategyApplicationEvidence(
        strategy_fingerprint=strategy.source_fingerprint,
        owner=request.owner,
        scope=request.session_id,
        status=CognitiveStrategyApplicationOutcomeStatus.APPLIED,
        requested_stage_sequence=("reasoning",),
        applied_stage_sequence=("reasoning",),
        skipped_stages=(),
        failed_stages=(),
        unmet_requirements=(),
        contribution_reference_ids=("another-turn-reference",),
        rationale_codes=("test:wrong_reference",),
        source_fingerprint="f" * 64,
    )
    with pytest.raises(ValueError, match="reference lineage mismatch"):
        GovernedRuntimePreparation._close_productive_epistemic_strategy_outcome(
            request=request,
            epistemic_episode=epistemic,
            strategy_application_evidence=application,
            strategy_coordinator=coordinator,
        )
    assert coordinator._productive_strategy_outcomes == []


def test_not_applicable_epistemic_episode_cannot_create_strategy_outcome():
    request = _request(admitted=False)
    coordinator = UnifiedCognitiveCoordinator(registry=None)
    assert (
        GovernedRuntimePreparation._close_productive_epistemic_strategy_outcome(
            request=request,
            epistemic_episode=None,
            strategy_application_evidence=None,
            strategy_coordinator=coordinator,
        )
        is None
    )
    assert coordinator._productive_strategy_outcomes == []
