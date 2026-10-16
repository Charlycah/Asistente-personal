from datetime import date, timedelta
from pathlib import Path

import pytest

from app.habit_detection import HabitDetection
from app.learning_foundation import LearningFoundation
from app.preference_learning import PreferenceLearning
from core.habit_detection import HabitDisposition, HabitOccurrence
from core.learning_foundation import LearningObservation
from core.preference_learning import PreferenceEvidence


def _preference(index: int):
    evidence = []
    for offset in (0, 1):
        observation = LearningObservation(
            observation_id=f"obs-{index}-{offset}",
            statement="Carlos valida Ruff antes de pytest.",
            source="validated_release_process",
            source_reference=f"M369.3-{index}-{offset}",
            confidence=0.9,
        )
        candidate = LearningFoundation().structure_candidate(
            subject="release_validation_order",
            proposed_value="ruff_before_pytest",
            observations=(observation,),
            confidence=0.9,
        )
        evidence.append(PreferenceEvidence.from_learning_candidate(candidate))
    return PreferenceLearning().evaluate(evidence=tuple(evidence))


def _occurrence(index: int, day: date) -> HabitOccurrence:
    return HabitOccurrence.from_preference_candidate(
        _preference(index),
        occurrence_id=f"habit-occurrence-{index}",
        observed_on=day,
    )


def test_m369_3_declares_one_subordinate_habit_authority() -> None:
    snapshot = HabitDetection().snapshot

    assert snapshot.schema_version == "m369.3"
    assert snapshot.canonical_authority == "habit_detection"
    assert snapshot.parent_authority == "preference_learning"
    assert snapshot.minimum_occurrence_count == 3


def test_m369_3_short_history_is_not_a_habit() -> None:
    result = HabitDetection().evaluate(
        occurrences=(_occurrence(1, date(2026, 8, 1)),)
    )

    assert result.disposition is HabitDisposition.INSUFFICIENT_HISTORY
    assert result.accepted_as_habit is False
    assert result.persistence_authorized is False


def test_m369_3_repeated_temporal_history_requires_review() -> None:
    start = date(2026, 8, 1)
    result = HabitDetection().evaluate(
        occurrences=tuple(
            _occurrence(index, start + timedelta(days=index - 1))
            for index in (1, 2, 3)
        )
    )

    assert result.disposition is HabitDisposition.REVIEW_REQUIRED
    assert result.occurrence_count == 3
    assert result.distinct_day_count == 3
    assert result.span_days == 2
    assert result.confidence == 0.9


def test_m369_3_same_day_repetition_is_insufficient_history() -> None:
    same_day = date(2026, 8, 1)
    result = HabitDetection().evaluate(
        occurrences=tuple(_occurrence(index, same_day) for index in (1, 2, 3))
    )

    assert result.disposition is HabitDisposition.INSUFFICIENT_HISTORY
    assert result.distinct_day_count == 1


def test_m369_3_identity_is_deterministic_and_time_ordered() -> None:
    authority = HabitDetection()
    first = _occurrence(1, date(2026, 8, 1))
    second = _occurrence(2, date(2026, 8, 2))
    third = _occurrence(3, date(2026, 8, 3))

    direct = authority.evaluate(occurrences=(first, second, third))
    reversed_result = authority.evaluate(occurrences=(third, second, first))

    assert direct.habit_id == reversed_result.habit_id
    assert direct.occurrence_ids == (
        "habit-occurrence-1",
        "habit-occurrence-2",
        "habit-occurrence-3",
    )


def test_m369_3_rejects_duplicates_or_conflicts() -> None:
    authority = HabitDetection()
    repeated = _occurrence(1, date(2026, 8, 1))

    with pytest.raises(ValueError, match="must be unique"):
        authority.evaluate(occurrences=(repeated, repeated))

    conflicting = HabitOccurrence(
        occurrence_id="different",
        preference_id="preference-different",
        subject="release_validation_order",
        behavior="pytest_before_ruff",
        observed_on=date(2026, 8, 2),
        confidence=0.5,
    )
    with pytest.raises(ValueError, match="one subject and behavior"):
        authority.evaluate(occurrences=(repeated, conflicting))


def test_m369_3_adds_no_automatic_learning_or_side_effects() -> None:
    snapshot = HabitDetection().snapshot

    assert snapshot.read_only is True
    assert snapshot.automatic_habit_acceptance is False
    assert snapshot.pattern_recognition_enabled is False
    assert snapshot.adaptive_reasoning_enabled is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False


def test_m369_3_documentation_declares_habit_limits() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M369_3_HABIT_DETECTION.md").read_text(
        encoding="utf-8"
    )

    assert "habit_detection" in document
    assert "insufficient_history" in document
    assert "no acepta hábitos automáticamente" in document
    assert "M369.3" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M369.3 — Habit Detection" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
