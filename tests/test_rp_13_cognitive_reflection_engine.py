from datetime import datetime, timedelta, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import CognitiveAgendaReasoner
from app.cognitive_reflection_engine import (
    CognitiveReflectionEngine,
    CognitiveReflectionOutcome,
    CognitiveReflectionPolicy,
)
from app.continuous_internal_cognitive_loop import ContinuousInternalCognitiveLoop

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def item(
    *,
    key="focus",
    score=0.7,
    relevance=0.8,
    status=CognitiveAgendaStatus.ACTIVE,
    last_seen_at=NOW,
):
    return CognitiveAgendaItem(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=f"Revisar {key}",
        sources=("test",),
        score=score,
        priority=0.7,
        urgency=0.4,
        relevance=relevance,
        status=status,
        first_seen_at=NOW,
        last_seen_at=last_seen_at,
        expires_at=None,
        rationale="test",
    )


def snapshot(*items):
    return CognitiveAgendaSnapshot(
        generated_at=NOW,
        items=tuple(items),
        primary_focus=items[0] if items else None,
    )


def deliberate(agenda):
    return CognitiveAgendaReasoner().deliberate(agenda, now=NOW)


def test_empty_agenda_has_explicit_no_reflection_state():
    result = CognitiveReflectionEngine().reflect(snapshot(), None, now=NOW)
    assert result.outcome is CognitiveReflectionOutcome.NO_REFLECTION
    assert result.agenda_key is None


def test_stable_supported_focus_is_affirmed():
    agenda = snapshot(item())
    result = CognitiveReflectionEngine().reflect(
        agenda,
        deliberate(agenda),
        now=NOW,
    )
    assert result.outcome is CognitiveReflectionOutcome.AFFIRM_FOCUS
    assert result.recommends_agenda_reassessment is False


def test_blocked_focus_waits_for_change():
    agenda = snapshot(item(status=CognitiveAgendaStatus.BLOCKED))
    result = CognitiveReflectionEngine().reflect(
        agenda,
        deliberate(agenda),
        now=NOW,
    )
    assert result.outcome is CognitiveReflectionOutcome.WAIT_FOR_CHANGE


def test_stale_focus_is_released_for_reassessment():
    agenda = snapshot(item(last_seen_at=NOW - timedelta(hours=1)))
    result = CognitiveReflectionEngine().reflect(
        agenda,
        deliberate(agenda),
        now=NOW,
    )
    assert result.outcome is CognitiveReflectionOutcome.RELEASE_STALE_FOCUS
    assert result.recommends_agenda_reassessment is True


def test_low_reasoning_confidence_requests_more_evidence():
    agenda = snapshot(item(relevance=0.1))
    result = CognitiveReflectionEngine().reflect(
        agenda,
        deliberate(agenda),
        now=NOW,
    )
    assert result.outcome is CognitiveReflectionOutcome.SEEK_MORE_EVIDENCE


def test_close_competitor_triggers_priority_reassessment():
    agenda = snapshot(item(key="a", score=0.70), item(key="b", score=0.66))
    result = CognitiveReflectionEngine().reflect(
        agenda,
        deliberate(agenda),
        now=NOW,
    )
    assert result.outcome is CognitiveReflectionOutcome.REASSESS_PRIORITY


def test_persistent_low_escalation_focus_is_reconsidered():
    agenda = snapshot(item(score=0.4))
    engine = CognitiveReflectionEngine(
        policy=CognitiveReflectionPolicy(persistence_cycles=2)
    )
    engine.reflect(agenda, deliberate(agenda), now=NOW)
    result = engine.reflect(agenda, deliberate(agenda), now=NOW)
    assert result.outcome is CognitiveReflectionOutcome.REASSESS_PRIORITY


def test_focus_change_resets_persistence_counter():
    engine = CognitiveReflectionEngine(
        policy=CognitiveReflectionPolicy(persistence_cycles=2)
    )
    first = snapshot(item(key="a", score=0.4))
    second = snapshot(item(key="b", score=0.4))
    engine.reflect(first, deliberate(first), now=NOW)
    result = engine.reflect(second, deliberate(second), now=NOW)
    assert result.outcome is CognitiveReflectionOutcome.AFFIRM_FOCUS
    assert "cycles=1" in result.rationale


def test_reflection_never_requests_user_authorization_or_executes():
    agenda = snapshot(item())
    result = CognitiveReflectionEngine().reflect(
        agenda,
        deliberate(agenda),
        now=NOW,
    )
    assert result.requires_user_authorization is False


def test_policy_rejects_invalid_values():
    with pytest.raises(ValueError, match="positive"):
        CognitiveReflectionPolicy(persistence_cycles=0)
    with pytest.raises(ValueError, match="between 0 and 1"):
        CognitiveReflectionPolicy(competing_focus_margin=1.1)


def test_rp10_exposes_reflection_without_changing_rationale_contract():
    agenda = snapshot(item())

    class Agenda:
        def refresh(self, *, now):
            return agenda

    state = ContinuousInternalCognitiveLoop(agenda_manager=Agenda()).tick(now=NOW)
    assert state.rationale == "agenda:focus"
    assert state.deliberation is not None
    assert state.reflection is not None
    assert state.reflection.outcome is CognitiveReflectionOutcome.AFFIRM_FOCUS
