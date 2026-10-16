from datetime import datetime, timedelta, timezone

import pytest

from core.controlled_autonomy import (
    DeterministicSelfReflector,
    ExperienceMemorySnapshot,
    ExperiencePattern,
    JsonPersistentGoalStore,
    JsonSelfReflectionStore,
    PersistentGoalSnapshot,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 27, 21, 0, tzinfo=timezone.utc)


def _pattern(*, succeeded: int, failed: int) -> ExperiencePattern:
    occurrences = succeeded + failed
    return ExperiencePattern(
        situation_kind="audio_runtime_requires_diagnosis",
        action="diagnose_audio_runtime",
        occurrences=occurrences,
        succeeded=succeeded,
        degraded=0,
        failed=failed,
        unknown=0,
        last_observed_at=NOW,
        last_summary="diagnostic outcome",
    )


def test_m327_10_reflection_identifies_due_goals(tmp_path) -> None:
    goals = JsonPersistentGoalStore(tmp_path / "goals.json")
    goals.create(
        title="Revisar audio",
        description="Confirmar estabilidad",
        priority=0.8,
        created_at=NOW - timedelta(hours=2),
        review_at=NOW - timedelta(minutes=1),
    )

    report = DeterministicSelfReflector().reflect(
        experience=ExperienceMemorySnapshot(patterns=()),
        goals=goals.snapshot(now=NOW),
        observed_at=NOW,
    )

    assert report.due_goal_count == 1
    assert report.findings[0].code == "goals_due_for_review"


def test_m327_10_reflection_identifies_repeated_failure() -> None:
    report = DeterministicSelfReflector().reflect(
        experience=ExperienceMemorySnapshot(
            patterns=(_pattern(succeeded=0, failed=3),)
        ),
        goals=PersistentGoalSnapshot(goals=(), observed_at=NOW),
        observed_at=NOW,
    )

    assert report.findings[0].code == "repeated_unsuccessful_experience"
    assert "permissions unchanged" in report.findings[0].recommendation


def test_m327_10_reflection_report_survives_restart(tmp_path) -> None:
    path = tmp_path / "self_reflections.json"
    report = DeterministicSelfReflector().reflect(
        experience=ExperienceMemorySnapshot(patterns=()),
        goals=PersistentGoalSnapshot(goals=(), observed_at=NOW),
        observed_at=NOW,
    )
    JsonSelfReflectionStore(path).append(report)

    restored = JsonSelfReflectionStore(path).snapshot()

    assert restored.reports == (report,)


def test_m327_10_runtime_runs_explicit_reflection(tmp_path) -> None:
    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "journal.jsonl",
        persistent_goals_path=tmp_path / "goals.json",
        self_reflection_path=tmp_path / "self_reflections.json",
    )
    runtime.create_persistent_goal(
        title="Revisar audio",
        description="Confirmar estabilidad",
        priority=0.8,
        created_at=NOW - timedelta(hours=2),
        review_at=NOW - timedelta(minutes=1),
    )

    report = runtime.run_self_reflection(observed_at=NOW)

    assert report.due_goal_count == 1
    assert runtime.snapshot.self_reflection_count == 1
    assert runtime.self_reflections().reports == (report,)


def test_m327_10_corrupted_reflection_file_is_rejected(tmp_path) -> None:
    path = tmp_path / "self_reflections.json"
    path.write_text("not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid self reflection file"):
        JsonSelfReflectionStore(path)
