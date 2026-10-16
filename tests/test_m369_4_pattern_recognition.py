from datetime import date, timedelta
from pathlib import Path

import pytest

from app.habit_detection import HabitDetection
from app.learning_foundation import LearningFoundation
from app.pattern_recognition import PatternRecognition
from app.preference_learning import PreferenceLearning
from core.habit_detection import HabitOccurrence
from core.learning_foundation import LearningObservation
from core.pattern_recognition import PatternDisposition, PatternEvidence
from core.preference_learning import PreferenceEvidence


def _habit(seed: int, behavior: str = "ruff_before_pytest"):
    preferences = []
    for index in range(3):
        learning_evidence = []
        for offset in (0, 1):
            observation = LearningObservation(
                observation_id=f"obs-{seed}-{index}-{offset}",
                statement="Carlos sigue el proceso de validación acordado.",
                source="validated_release_process",
                source_reference=f"M369.4-{seed}-{index}-{offset}",
                confidence=0.9,
            )
            candidate = LearningFoundation().structure_candidate(
                subject="release_validation_order",
                proposed_value=behavior,
                observations=(observation,),
                confidence=0.9,
            )
            learning_evidence.append(
                PreferenceEvidence.from_learning_candidate(candidate)
            )
        preferences.append(
            PreferenceLearning().evaluate(evidence=tuple(learning_evidence))
        )

    start = date(2026, 8, 1) + timedelta(days=seed * 3)
    occurrences = tuple(
        HabitOccurrence.from_preference_candidate(
            preference,
            occurrence_id=f"occurrence-{seed}-{index}",
            observed_on=start + timedelta(days=index),
        )
        for index, preference in enumerate(preferences)
    )
    return HabitDetection().evaluate(occurrences=occurrences)


def _evidence(seed: int) -> PatternEvidence:
    return PatternEvidence.from_habit_candidate(
        _habit(seed),
        evidence_id=f"pattern-evidence-{seed}",
        context="validated_release",
        observed_value="ruff_before_pytest",
    )


def test_m369_4_declares_one_subordinate_pattern_authority() -> None:
    snapshot = PatternRecognition().snapshot

    assert snapshot.schema_version == "m369.4"
    assert snapshot.canonical_authority == "pattern_recognition"
    assert snapshot.parent_authority == "habit_detection"
    assert snapshot.minimum_evidence_count == 2


def test_m369_4_single_habit_is_insufficient_evidence() -> None:
    result = PatternRecognition().evaluate(evidence=(_evidence(1),))

    assert result.disposition is PatternDisposition.INSUFFICIENT_EVIDENCE
    assert result.accepted_as_pattern is False
    assert result.persistence_authorized is False


def test_m369_4_distinct_consistent_habits_require_review() -> None:
    result = PatternRecognition().evaluate(
        evidence=(_evidence(1), _evidence(2))
    )

    assert result.disposition is PatternDisposition.REVIEW_REQUIRED
    assert result.evidence_count == 2
    assert len(result.habit_ids) == 2
    assert result.confidence == 0.9


def test_m369_4_identity_is_deterministic() -> None:
    authority = PatternRecognition()
    first = _evidence(1)
    second = _evidence(2)

    direct = authority.evaluate(evidence=(first, second))
    reversed_result = authority.evaluate(evidence=(second, first))

    assert direct.pattern_id == reversed_result.pattern_id
    assert direct.evidence_ids == reversed_result.evidence_ids


def test_m369_4_rejects_duplicates_or_conflicting_relations() -> None:
    authority = PatternRecognition()
    evidence = _evidence(1)

    with pytest.raises(ValueError, match="must be unique"):
        authority.evaluate(evidence=(evidence, evidence))

    conflicting = PatternEvidence(
        evidence_id="conflicting",
        habit_id="habit-conflicting",
        subject="release_validation_order",
        context="validated_release",
        observed_value="pytest_before_ruff",
        confidence=0.5,
    )
    with pytest.raises(ValueError, match="one subject, context and value"):
        authority.evaluate(evidence=(evidence, conflicting))


def test_m369_4_rejects_non_reviewable_habit_sources() -> None:
    short_occurrence = HabitOccurrence(
        occurrence_id="short",
        preference_id="preference-short",
        subject="release_validation_order",
        behavior="ruff_before_pytest",
        observed_on=date(2026, 8, 1),
        confidence=0.9,
    )
    habit = HabitDetection().evaluate(occurrences=(short_occurrence,))

    with pytest.raises(ValueError, match="reviewable habit"):
        PatternEvidence.from_habit_candidate(
            habit,
            evidence_id="pattern-short",
            context="validated_release",
        )


def test_m369_4_adds_no_adaptation_or_side_effects() -> None:
    snapshot = PatternRecognition().snapshot

    assert snapshot.read_only is True
    assert snapshot.automatic_pattern_acceptance is False
    assert snapshot.adaptive_reasoning_enabled is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False


def test_m369_4_documentation_declares_pattern_limits() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M369_4_PATTERN_RECOGNITION.md").read_text(
        encoding="utf-8"
    )

    assert "pattern_recognition" in document
    assert "insufficient_evidence" in document
    assert "no acepta patrones automáticamente" in document
    assert "M369.4" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M369.4 — Pattern Recognition" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
