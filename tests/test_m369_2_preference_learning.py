from pathlib import Path

import pytest

from app.learning_foundation import LearningFoundation
from app.preference_learning import PreferenceLearning
from core.learning_foundation import LearningObservation
from core.preference_learning import PreferenceDisposition, PreferenceEvidence


def _evidence(index: int, confidence: float = 0.8) -> PreferenceEvidence:
    observation = LearningObservation(
        observation_id=f"obs-{index}",
        statement="Carlos prefiere validar Ruff antes de la suite.",
        source="validated_release_process",
        source_reference=f"M369.1-run-{index}",
        confidence=confidence,
    )
    candidate = LearningFoundation().structure_candidate(
        subject="release_validation_order",
        proposed_value="ruff_before_pytest",
        observations=(observation,),
        confidence=confidence,
    )
    return PreferenceEvidence.from_learning_candidate(candidate)


def test_m369_2_declares_one_subordinate_preference_authority() -> None:
    snapshot = PreferenceLearning().snapshot

    assert snapshot.schema_version == "m369.2"
    assert snapshot.canonical_authority == "preference_learning"
    assert snapshot.parent_authority == "learning_foundation"
    assert snapshot.minimum_evidence_count == 2


def test_m369_2_single_observation_is_not_a_preference() -> None:
    result = PreferenceLearning().evaluate(evidence=(_evidence(1),))

    assert result.disposition is PreferenceDisposition.INSUFFICIENT_EVIDENCE
    assert result.accepted_as_preference is False
    assert result.persistence_authorized is False


def test_m369_2_accumulated_consistent_evidence_requires_review() -> None:
    result = PreferenceLearning().evaluate(
        evidence=(_evidence(1, 0.8), _evidence(2, 1.0))
    )

    assert result.disposition is PreferenceDisposition.REVIEW_REQUIRED
    assert result.evidence_count == 2
    assert result.observation_ids == ("obs-1", "obs-2")
    assert result.confidence == 0.9


def test_m369_2_identity_is_deterministic() -> None:
    authority = PreferenceLearning()
    evidence = (_evidence(1), _evidence(2))

    assert authority.evaluate(evidence=evidence).preference_id == (
        authority.evaluate(evidence=evidence).preference_id
    )


def test_m369_2_rejects_duplicate_or_conflicting_evidence() -> None:
    authority = PreferenceLearning()
    repeated = _evidence(1)

    with pytest.raises(ValueError, match="must be unique"):
        authority.evaluate(evidence=(repeated, repeated))

    conflicting_candidate = LearningFoundation().structure_candidate(
        subject="release_validation_order",
        proposed_value="pytest_before_ruff",
        observations=(
            LearningObservation(
                observation_id="obs-conflict",
                statement="Orden alternativo.",
                source="test",
                source_reference="conflict",
                confidence=0.5,
            ),
        ),
        confidence=0.5,
    )
    with pytest.raises(ValueError, match="one subject and value"):
        authority.evaluate(
            evidence=(
                _evidence(1),
                PreferenceEvidence.from_learning_candidate(conflicting_candidate),
            )
        )


def test_m369_2_adds_no_automatic_learning_or_side_effects() -> None:
    snapshot = PreferenceLearning().snapshot

    assert snapshot.read_only is True
    assert snapshot.automatic_preference_learning is False
    assert snapshot.habit_detection_enabled is False
    assert snapshot.pattern_recognition_enabled is False
    assert snapshot.adaptive_reasoning_enabled is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False


def test_m369_2_documentation_declares_preference_limits() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M369_2_PREFERENCE_LEARNING.md").read_text(
        encoding="utf-8"
    )

    assert "preference_learning" in document
    assert "insufficient_evidence" in document
    assert "no convierte una observación aislada" in document
    assert "M369.2" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M369.2 — Preference Learning" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
