from datetime import datetime, timedelta, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaKind,
    CognitiveAgendaManager,
    CognitiveAgendaPolicy,
    CognitiveAgendaSignal,
)
from app.cognitive_agenda_sources import CallableCognitiveAgendaSource
from app.continuous_internal_cognitive_loop import (
    CognitiveFocus,
    ContinuousInternalCognitiveLoop,
)

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def signal(
    key: str,
    *,
    priority: float = 0.5,
    urgency: float = 0.0,
    relevance: float = 0.5,
    source: str = "test",
    expires_at=None,
):
    return CognitiveAgendaSignal(
        key=key,
        kind=CognitiveAgendaKind.FOLLOW_UP,
        title=key,
        source=source,
        priority=priority,
        urgency=urgency,
        relevance=relevance,
        observed_at=NOW,
        expires_at=expires_at,
    )


def source(name, *signals):
    return CallableCognitiveAgendaSource(name, lambda _now: signals)


def test_empty_agenda_has_no_primary_focus():
    snapshot = CognitiveAgendaManager().refresh(now=NOW)
    assert snapshot.items == ()
    assert snapshot.primary_focus is None


def test_priority_selects_primary_focus():
    manager = CognitiveAgendaManager(
        (source("runtime", signal("low"), signal("high", priority=1.0)),)
    )
    assert manager.refresh(now=NOW).primary_focus.key == "high"


def test_equivalent_signals_are_deduplicated_and_sources_are_merged():
    manager = CognitiveAgendaManager(
        (
            source("goals", signal("shared", source="goals", priority=0.8)),
            source("projects", signal("shared", source="projects", urgency=0.9)),
        )
    )
    item = manager.refresh(now=NOW).items[0]
    assert item.sources == ("goals", "projects")
    assert item.priority == 0.8
    assert item.urgency == 0.9


def test_expired_signals_are_not_kept_active():
    manager = CognitiveAgendaManager(
        (source("runtime", signal("old", expires_at=NOW)),)
    )
    assert manager.refresh(now=NOW).items == ()


def test_capacity_limits_working_set():
    manager = CognitiveAgendaManager(
        (source("runtime", *(signal(str(index)) for index in range(5))),),
        policy=CognitiveAgendaPolicy(capacity=2),
    )
    assert len(manager.refresh(now=NOW).items) == 2


def test_order_is_deterministic_when_scores_match():
    manager = CognitiveAgendaManager((source("runtime", signal("b"), signal("a")),))
    assert [item.key for item in manager.refresh(now=NOW).items] == ["a", "b"]


def test_continuity_bonus_preserves_recent_concern():
    manager = CognitiveAgendaManager((source("runtime", signal("same")),))
    first = manager.refresh(now=NOW).items[0]
    second = manager.refresh(now=NOW + timedelta(minutes=1)).items[0]
    assert second.score > first.score
    assert second.first_seen_at == first.first_seen_at


def test_source_failure_is_isolated():
    def broken(_now):
        raise RuntimeError("offline")

    manager = CognitiveAgendaManager(
        (
            CallableCognitiveAgendaSource("broken", broken),
            source("healthy", signal("active")),
        )
    )
    snapshot = manager.refresh(now=NOW)
    assert snapshot.primary_focus.key == "active"
    assert snapshot.source_failures == ("broken",)


def test_invalid_signal_score_is_rejected():
    with pytest.raises(ValueError, match="between 0 and 1"):
        signal("invalid", priority=1.1)


def test_policy_rejects_non_positive_capacity():
    with pytest.raises(ValueError, match="positive"):
        CognitiveAgendaPolicy(capacity=0)


def test_rp10_uses_agenda_as_primary_cognitive_focus():
    manager = CognitiveAgendaManager((source("goals", signal("goal:home")),))
    state = ContinuousInternalCognitiveLoop(agenda_manager=manager).tick(now=NOW)
    assert state.focus is CognitiveFocus.COGNITIVE_AGENDA
    assert state.rationale == "agenda:goal:home"
    assert state.agenda is manager.snapshot


def test_rp10_keeps_legacy_fallback_when_agenda_is_empty():
    manager = CognitiveAgendaManager()
    loop = ContinuousInternalCognitiveLoop(
        agenda_manager=manager,
        open_commitments=lambda: 1,
    )
    assert loop.tick(now=NOW).focus is CognitiveFocus.OPEN_COMMITMENTS


def test_environment_wiring_builds_composed_agenda(monkeypatch):
    from app.always_on_personal_runtime_wiring import (
        build_continuous_cognitive_loop_from_environment,
    )

    monkeypatch.setenv("ROBY_PERSONAL_RUNTIME_ENABLED", "true")
    monkeypatch.setenv("ROBY_CONTINUOUS_COGNITIVE_LOOP_ENABLED", "true")
    # This test verifies source composition, not persistence. Isolate it from
    # any real agenda database left in the developer's working directory.
    monkeypatch.setenv("ROBY_COGNITIVE_AGENDA_PERSISTENCE_ENABLED", "false")
    loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=lambda: None,
        open_commitments=lambda: 2,
        ambient_activity=lambda: 0,
    )
    state = loop.tick(now=NOW)
    assert state.focus is CognitiveFocus.COGNITIVE_AGENDA
    assert state.agenda.primary_focus.key == "commitments:open"
