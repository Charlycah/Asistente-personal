from datetime import datetime, timedelta, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import CognitiveAgendaReasoner
from app.cognitive_episodic_memory import CognitiveEpisodicMemory
from app.cognitive_hypothesis_workspace import CognitiveHypothesisWorkspace
from app.cognitive_reflection_engine import CognitiveReflectionEngine
from app.cognitive_self_model import (
    CognitiveSelfMode,
    CognitiveSelfModel,
    CognitiveSelfModelPolicy,
    CognitiveSelfModelTransition,
)
from app.cognitive_thought_stream import CognitiveThoughtStream
from app.cognitive_world_model import CognitiveWorldModel
from app.continuous_internal_cognitive_loop import ContinuousInternalCognitiveLoop

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def item(*, key="focus", score=0.7):
    return CognitiveAgendaItem(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=f"Revisar {key}",
        sources=("test", "test"),
        score=score,
        priority=score,
        urgency=0.4,
        relevance=0.8,
        status=CognitiveAgendaStatus.ACTIVE,
        first_seen_at=NOW,
        last_seen_at=NOW,
        expires_at=None,
        rationale="test",
    )


def context(focus, *others, now=NOW, world_model=None, memory=None):
    agenda = CognitiveAgendaSnapshot(
        generated_at=now,
        items=(focus, *others),
        primary_focus=focus,
    )
    deliberation = CognitiveAgendaReasoner().deliberate(agenda, now=now)
    reflection = CognitiveReflectionEngine().reflect(agenda, deliberation, now=now)
    stream = CognitiveThoughtStream().advance(agenda, deliberation, reflection, now=now)
    workspace = CognitiveHypothesisWorkspace().evaluate(
        stream, deliberation, reflection, now=now
    )
    model = world_model or CognitiveWorldModel()
    world = model.update(stream, workspace, now=now)
    episodes = (memory or CognitiveEpisodicMemory()).remember(world, now=now)
    return world, episodes, deliberation, reflection


def test_active_focus_creates_engaged_self_model():
    result = CognitiveSelfModel().assess(*context(item()), now=NOW)
    assert result.transition is CognitiveSelfModelTransition.CREATED
    assert result.mode is CognitiveSelfMode.ENGAGED
    assert result.active_focus_key == "focus"


def test_self_model_exposes_bounded_metrics():
    result = CognitiveSelfModel().assess(*context(item()), now=NOW)
    assert 0.0 <= result.confidence <= 1.0
    assert 0.0 <= result.uncertainty <= 1.0
    assert 0.0 <= result.stability <= 1.0
    assert result.cognitive_load > 0


def test_close_competitor_marks_reassessment():
    result = CognitiveSelfModel().assess(
        *context(item(score=0.7), item(key="other", score=0.68)),
        now=NOW,
    )
    assert result.mode is CognitiveSelfMode.REASSESSING
    assert result.pending_reassessment is True


def test_equivalent_cycle_is_stable():
    model = CognitiveSelfModel()
    inputs = context(item())
    model.assess(*inputs, now=NOW)
    result = model.assess(*inputs, now=NOW + timedelta(seconds=1))
    assert result.transition is CognitiveSelfModelTransition.STABLE
    assert result.revisions == 2


def test_focus_change_updates_self_model():
    model = CognitiveSelfModel()
    model.assess(*context(item(key="a")), now=NOW)
    result = model.assess(*context(item(key="b")), now=NOW + timedelta(seconds=1))
    assert result.transition is CognitiveSelfModelTransition.UPDATED
    assert result.active_focus_key == "b"


def test_suspended_world_suspends_self_model():
    world_model = CognitiveWorldModel()
    memory = CognitiveEpisodicMemory()
    active = context(item(), world_model=world_model, memory=memory)
    self_model = CognitiveSelfModel()
    self_model.assess(*active, now=NOW)
    suspended_world = world_model.update(None, None, now=NOW + timedelta(seconds=1))
    suspended_memory = memory.remember(suspended_world, now=NOW + timedelta(seconds=1))
    result = self_model.assess(
        suspended_world,
        suspended_memory,
        None,
        None,
        now=NOW + timedelta(seconds=1),
    )
    assert result.mode is CognitiveSelfMode.SUSPENDED
    assert result.transition is CognitiveSelfModelTransition.SUSPENDED


def test_capabilities_are_explicit_and_non_operational():
    result = CognitiveSelfModel().assess(*context(item()), now=NOW)
    assert "episodic_recall" in result.available_capabilities
    assert "execute_action" not in result.available_capabilities


def test_sources_are_deduplicated():
    result = CognitiveSelfModel().assess(*context(item()), now=NOW)
    assert result.evidence_sources == ("test",)


def test_policy_validation():
    with pytest.raises(ValueError, match="positive"):
        CognitiveSelfModelPolicy(high_load_threshold=0)
    with pytest.raises(ValueError, match="between zero and one"):
        CognitiveSelfModelPolicy(uncertainty_threshold=1.1)


def test_self_model_does_not_store_chain_of_thought():
    result = CognitiveSelfModel().assess(*context(item()), now=NOW)
    assert not hasattr(result, "chain_of_thought")
    assert not hasattr(result, "reasoning_steps")


def test_rp10_exposes_self_model_without_changing_rationale():
    focus = item()
    agenda = CognitiveAgendaSnapshot(
        generated_at=NOW,
        items=(focus,),
        primary_focus=focus,
    )

    class Agenda:
        def refresh(self, *, now):
            return agenda

    state = ContinuousInternalCognitiveLoop(agenda_manager=Agenda()).tick(now=NOW)
    assert state.rationale == "agenda:focus"
    assert state.self_model is not None
    assert state.self_model.active_focus_key == "focus"
    assert state.self_model.requires_user_authorization is False
