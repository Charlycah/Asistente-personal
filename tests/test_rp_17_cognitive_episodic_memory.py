from datetime import datetime, timedelta, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import CognitiveAgendaReasoner
from app.cognitive_episodic_memory import (
    CognitiveEpisodeKind,
    CognitiveEpisodeStatus,
    CognitiveEpisodicMemory,
    CognitiveEpisodicMemoryPolicy,
    CognitiveEpisodicMemoryTransition,
)
from app.cognitive_hypothesis_workspace import CognitiveHypothesisWorkspace
from app.cognitive_reflection_engine import CognitiveReflectionEngine
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


def world(focus, *others, model=None, now=NOW):
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
    return (model or CognitiveWorldModel()).update(stream, workspace, now=now)


def test_created_world_model_records_focus_established_episode():
    result = CognitiveEpisodicMemory().remember(world(item()), now=NOW)
    assert result.transition is CognitiveEpisodicMemoryTransition.RECORDED
    assert result.episodes[0].kind is CognitiveEpisodeKind.FOCUS_ESTABLISHED
    assert result.episodes[0].focus_key == "focus"


def test_episode_contains_world_entities_and_relations():
    episode = CognitiveEpisodicMemory().remember(world(item()), now=NOW).episodes[0]
    assert "focus" in episode.entity_keys
    assert episode.relation_keys


def test_episode_preserves_deduplicated_provenance():
    episode = CognitiveEpisodicMemory().remember(world(item()), now=NOW).episodes[0]
    assert episode.sources == ("test",)


def test_repeated_equivalent_updates_consolidate_episode():
    model = CognitiveWorldModel()
    memory = CognitiveEpisodicMemory(
        policy=CognitiveEpisodicMemoryPolicy(consolidate_after=2)
    )
    memory.remember(world(item(), model=model), now=NOW)
    first_update = world(item(), model=model, now=NOW + timedelta(seconds=1))
    memory.remember(first_update, now=NOW + timedelta(seconds=1))
    second_update = world(item(), model=model, now=NOW + timedelta(seconds=2))
    result = memory.remember(second_update, now=NOW + timedelta(seconds=2))
    assert result.transition is CognitiveEpisodicMemoryTransition.CONSOLIDATED
    assert result.episodes[-1].status is CognitiveEpisodeStatus.CONSOLIDATED
    assert result.episodes[-1].repetitions == 2


def test_focus_change_records_new_episode():
    model = CognitiveWorldModel()
    memory = CognitiveEpisodicMemory()
    memory.remember(world(item(key="a"), model=model), now=NOW)
    result = memory.remember(
        world(item(key="b"), model=model, now=NOW + timedelta(seconds=1)),
        now=NOW + timedelta(seconds=1),
    )
    assert len(result.episodes) == 2
    assert result.episodes[-1].focus_key == "b"


def test_suspension_is_recorded():
    model = CognitiveWorldModel()
    model.update(None, None, now=NOW)
    active = world(item(), model=model)
    memory = CognitiveEpisodicMemory()
    memory.remember(active, now=NOW)
    suspended = model.update(None, None, now=NOW + timedelta(seconds=1))
    result = memory.remember(suspended, now=NOW + timedelta(seconds=1))
    assert result.episodes[-1].kind is CognitiveEpisodeKind.MODEL_SUSPENDED


def test_no_world_model_produces_no_change():
    result = CognitiveEpisodicMemory().remember(None, now=NOW)
    assert result.transition is CognitiveEpisodicMemoryTransition.NO_CHANGE
    assert result.episodes == ()


def test_memory_respects_maximum_episode_count():
    memory = CognitiveEpisodicMemory(
        policy=CognitiveEpisodicMemoryPolicy(max_episodes=2)
    )
    for index in range(3):
        memory.remember(world(item(key=str(index))), now=NOW + timedelta(seconds=index))
    assert len(memory.remember(None, now=NOW).episodes) == 2


def test_policy_validation():
    with pytest.raises(ValueError, match="positive"):
        CognitiveEpisodicMemoryPolicy(max_episodes=0)
    with pytest.raises(ValueError, match="between zero and one"):
        CognitiveEpisodicMemoryPolicy(minimum_confidence=1.1)


def test_episode_does_not_store_chain_of_thought():
    episode = CognitiveEpisodicMemory().remember(world(item()), now=NOW).episodes[0]
    assert not hasattr(episode, "chain_of_thought")
    assert not hasattr(episode, "reasoning_steps")


def test_rp10_exposes_episodic_memory_without_changing_rationale():
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
    assert state.episodic_memory is not None
    assert state.episodic_memory.latest_episode_key == "episode:1"
    assert state.episodic_memory.requires_user_authorization is False
