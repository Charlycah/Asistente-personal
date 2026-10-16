from datetime import datetime, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import (
    CognitiveAgendaReasoner,
    CognitiveAgendaReasoningDisposition,
    CognitiveAgendaReasoningPolicy,
)
from app.continuous_internal_cognitive_loop import (
    CognitiveFocus,
    ContinuousInternalCognitiveLoop,
)

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def item(
    *,
    key="follow-up",
    kind=CognitiveAgendaKind.FOLLOW_UP,
    score=0.7,
    urgency=0.5,
    relevance=0.8,
    status=CognitiveAgendaStatus.ACTIVE,
    sources=("test",),
):
    return CognitiveAgendaItem(
        key=key,
        kind=kind,
        title="Retomar el tema pendiente",
        sources=sources,
        score=score,
        priority=0.8,
        urgency=urgency,
        relevance=relevance,
        status=status,
        first_seen_at=NOW,
        last_seen_at=NOW,
        expires_at=None,
        rationale="pending",
    )


def snapshot(focus=None):
    items = (focus,) if focus is not None else ()
    return CognitiveAgendaSnapshot(
        generated_at=NOW,
        items=items,
        primary_focus=focus,
    )


def test_empty_agenda_produces_no_deliberation():
    assert CognitiveAgendaReasoner().deliberate(snapshot(), now=NOW) is None


def test_medium_score_prepares_follow_up():
    result = CognitiveAgendaReasoner().deliberate(snapshot(item()), now=NOW)
    assert result.disposition is CognitiveAgendaReasoningDisposition.PREPARE_FOLLOW_UP
    assert result.requires_user_authorization is False


def test_high_urgent_commitment_proposes_but_does_not_execute_action():
    focus = item(
        kind=CognitiveAgendaKind.COMMITMENT,
        score=0.9,
        urgency=0.9,
    )
    result = CognitiveAgendaReasoner().deliberate(snapshot(focus), now=NOW)
    assert result.disposition is CognitiveAgendaReasoningDisposition.PROPOSE_ACTION
    assert result.requires_user_authorization is True


def test_blocked_item_waits_for_unblocking():
    result = CognitiveAgendaReasoner().deliberate(
        snapshot(item(status=CognitiveAgendaStatus.BLOCKED)),
        now=NOW,
    )
    assert result.disposition is CognitiveAgendaReasoningDisposition.WAIT_FOR_UNBLOCKING


def test_watching_item_remains_observational():
    result = CognitiveAgendaReasoner().deliberate(
        snapshot(item(status=CognitiveAgendaStatus.WATCHING)),
        now=NOW,
    )
    assert result.disposition is CognitiveAgendaReasoningDisposition.OBSERVE


def test_low_score_continues_without_escalation():
    result = CognitiveAgendaReasoner().deliberate(
        snapshot(item(score=0.4, urgency=0.1)),
        now=NOW,
    )
    assert result.disposition is CognitiveAgendaReasoningDisposition.CONTINUE


def test_multiple_sources_raise_but_bound_confidence():
    result = CognitiveAgendaReasoner().deliberate(
        snapshot(item(sources=("goals", "projects", "memory"))),
        now=NOW,
    )
    assert 0.45 < result.confidence <= 1.0


def test_policy_rejects_invalid_thresholds():
    with pytest.raises(ValueError, match="between 0 and 1"):
        CognitiveAgendaReasoningPolicy(urgent_threshold=1.1)


def test_policy_rejects_inverted_action_thresholds():
    with pytest.raises(ValueError, match="must not be lower"):
        CognitiveAgendaReasoningPolicy(
            propose_action_score=0.5,
            prepare_follow_up_score=0.7,
        )


def test_rp10_exposes_deliberation_as_resident_cognitive_state():
    class Agenda:
        def refresh(self, *, now):
            return snapshot(item(score=0.9, urgency=0.9))

    state = ContinuousInternalCognitiveLoop(agenda_manager=Agenda()).tick(now=NOW)
    assert state.focus is CognitiveFocus.COGNITIVE_AGENDA
    assert state.deliberation is not None
    assert state.rationale == "agenda:follow-up"
    assert state.deliberation.rationale.startswith("agenda_reasoning:propose_action")
