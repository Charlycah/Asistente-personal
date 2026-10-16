from datetime import datetime, timedelta, timezone

import pytest

from core.controlled_autonomy import GoalStatus, JsonPersistentGoalStore
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 27, 20, 0, tzinfo=timezone.utc)


def test_m327_9_goal_survives_restart(tmp_path) -> None:
    path = tmp_path / "persistent_goals.json"
    created = JsonPersistentGoalStore(path).create(
        title="Supervisar audio",
        description="Mantener seguimiento del runtime de audio",
        priority=0.8,
        created_at=NOW,
        review_at=NOW + timedelta(hours=1),
        source="test",
    )

    restored = JsonPersistentGoalStore(path).snapshot(now=NOW)

    assert restored.goals == (created,)
    assert restored.active_count == 1
    assert restored.due_for_review_count == 0


def test_m327_9_goal_state_and_progress_are_persisted(tmp_path) -> None:
    path = tmp_path / "persistent_goals.json"
    store = JsonPersistentGoalStore(path)
    created = store.create(
        title="Revisar componente",
        description="Confirmar estabilidad",
        priority=0.6,
        created_at=NOW,
    )

    updated = store.update(
        created.goal_id,
        updated_at=NOW + timedelta(minutes=5),
        status=GoalStatus.COMPLETED,
        progress_summary="Estabilidad confirmada",
    )
    restored = JsonPersistentGoalStore(path).snapshot().goals[0]

    assert updated.status is GoalStatus.COMPLETED
    assert restored == updated
    assert restored.progress_summary == "Estabilidad confirmada"


def test_m327_9_due_goals_are_reported_and_ordered_first(tmp_path) -> None:
    store = JsonPersistentGoalStore(tmp_path / "persistent_goals.json")
    due = store.create(
        title="Objetivo vencido",
        description="Requiere revisión",
        priority=0.4,
        created_at=NOW,
        review_at=NOW + timedelta(minutes=5),
    )
    store.create(
        title="Objetivo futuro",
        description="Todavía no requiere revisión",
        priority=0.9,
        created_at=NOW,
        review_at=NOW + timedelta(hours=2),
    )

    snapshot = store.snapshot(now=NOW + timedelta(minutes=10))

    assert snapshot.goals[0].goal_id == due.goal_id
    assert snapshot.due_for_review_count == 1


def test_m327_9_runtime_exposes_persistent_goal_counters(tmp_path) -> None:
    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "journal.jsonl",
        persistent_goals_path=tmp_path / "persistent_goals.json",
    )
    runtime.create_persistent_goal(
        title="Supervisar audio",
        description="Mantener seguimiento",
        priority=0.8,
        created_at=NOW - timedelta(hours=1),
        review_at=NOW - timedelta(minutes=1),
    )

    goals = runtime.persistent_goals(now=NOW)
    snapshot = runtime.snapshot

    assert goals.due_for_review_count == 1
    assert snapshot.persistent_goal_count == 1
    assert snapshot.active_persistent_goal_count == 1


def test_m327_9_corrupted_goal_file_is_rejected(tmp_path) -> None:
    path = tmp_path / "persistent_goals.json"
    path.write_text("not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persistent goal file"):
        JsonPersistentGoalStore(path)
