from datetime import datetime, timedelta, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import CognitiveAgendaReasoner
from app.cognitive_reflection_engine import CognitiveReflectionEngine
from app.cognitive_thought_stream import (
    CognitiveThoughtStream,
    CognitiveThoughtStreamPolicy,
    CognitiveThoughtThreadStatus,
    CognitiveThoughtTransition,
)
from app.continuous_internal_cognitive_loop import ContinuousInternalCognitiveLoop

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def item(*, key="focus", status=CognitiveAgendaStatus.ACTIVE, sources=("test",)):
    return CognitiveAgendaItem(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=f"Revisar {key}",
        sources=sources,
        score=0.7,
        priority=0.7,
        urgency=0.4,
        relevance=0.8,
        status=status,
        first_seen_at=NOW,
        last_seen_at=NOW,
        expires_at=None,
        rationale="test",
    )


def snapshot(focus=None):
    return CognitiveAgendaSnapshot(
        generated_at=NOW,
        items=(focus,) if focus is not None else (),
        primary_focus=focus,
    )


def inputs(focus):
    agenda = snapshot(focus)
    deliberation = CognitiveAgendaReasoner().deliberate(agenda, now=NOW)
    reflection = CognitiveReflectionEngine().reflect(agenda, deliberation, now=NOW)
    return agenda, deliberation, reflection


def test_new_focus_starts_persistent_thread():
    result = CognitiveThoughtStream().advance(*inputs(item()), now=NOW)
    assert result.transition is CognitiveThoughtTransition.STARTED
    assert result.active_key == "focus"
    assert result.threads[0].cycles == 1


def test_same_focus_continues_thread_across_cycles():
    stream = CognitiveThoughtStream()
    data = inputs(item())
    stream.advance(*data, now=NOW)
    result = stream.advance(*data, now=NOW + timedelta(seconds=15))
    assert result.transition is CognitiveThoughtTransition.CONTINUED
    assert result.threads[0].cycles == 2


def test_focus_change_pauses_previous_thread():
    stream = CognitiveThoughtStream()
    stream.advance(*inputs(item(key="a")), now=NOW)
    result = stream.advance(*inputs(item(key="b")), now=NOW)
    statuses = {thread.key: thread.status for thread in result.threads}
    assert statuses["a"] is CognitiveThoughtThreadStatus.PAUSED
    assert statuses["b"] is CognitiveThoughtThreadStatus.ACTIVE


def test_returning_focus_resumes_previous_thread():
    stream = CognitiveThoughtStream()
    stream.advance(*inputs(item(key="a")), now=NOW)
    stream.advance(*inputs(item(key="b")), now=NOW)
    result = stream.advance(*inputs(item(key="a")), now=NOW)
    assert result.transition is CognitiveThoughtTransition.RESUMED


def test_empty_agenda_pauses_active_thread():
    stream = CognitiveThoughtStream()
    stream.advance(*inputs(item()), now=NOW)
    result = stream.advance(snapshot(), None, None, now=NOW)
    assert result.transition is CognitiveThoughtTransition.PAUSED
    assert result.active_key is None


def test_blocked_focus_becomes_waiting_thread():
    result = CognitiveThoughtStream().advance(
        *inputs(item(status=CognitiveAgendaStatus.BLOCKED)), now=NOW
    )
    assert result.transition is CognitiveThoughtTransition.WAITING
    assert result.threads[0].status is CognitiveThoughtThreadStatus.WAITING


def test_evidence_sources_accumulate_without_duplicates():
    stream = CognitiveThoughtStream()
    stream.advance(*inputs(item(sources=("a",))), now=NOW)
    result = stream.advance(*inputs(item(sources=("a", "b"))), now=NOW)
    assert result.threads[0].evidence_sources == ("a", "b")


def test_old_paused_thread_is_released():
    stream = CognitiveThoughtStream(
        policy=CognitiveThoughtStreamPolicy(release_after=timedelta(minutes=1))
    )
    stream.advance(*inputs(item(key="a")), now=NOW)
    stream.advance(snapshot(), None, None, now=NOW)
    result = stream.advance(snapshot(), None, None, now=NOW + timedelta(minutes=2))
    assert result.threads[0].status is CognitiveThoughtThreadStatus.RELEASED


def test_stream_never_requests_authorization_or_stores_hidden_reasoning():
    result = CognitiveThoughtStream().advance(*inputs(item()), now=NOW)
    assert result.requires_user_authorization is False
    assert "thought_stream:" in result.rationale
    assert not hasattr(result.threads[0], "chain_of_thought")


def test_policy_rejects_invalid_values():
    with pytest.raises(ValueError, match="positive"):
        CognitiveThoughtStreamPolicy(max_threads=0)
    with pytest.raises(ValueError, match="negative"):
        CognitiveThoughtStreamPolicy(release_after=timedelta(seconds=-1))


def test_rp10_exposes_stream_without_changing_rationale_contract():
    agenda = snapshot(item())

    class Agenda:
        def refresh(self, *, now):
            return agenda

    state = ContinuousInternalCognitiveLoop(agenda_manager=Agenda()).tick(now=NOW)
    assert state.rationale == "agenda:focus"
    assert state.reflection is not None
    assert state.thought_stream is not None
    assert state.thought_stream.active_key == "focus"
