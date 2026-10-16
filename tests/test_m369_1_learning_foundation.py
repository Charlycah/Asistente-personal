from pathlib import Path

import pytest

from app.learning_foundation import LearningFoundation
from core.learning_foundation import (
    LearningCandidateDisposition,
    LearningDomain,
    LearningObservation,
)


def _observation(
    observation_id: str = "obs-1",
    statement: str = "Carlos valida siempre Ruff antes de cerrar una versión.",
) -> LearningObservation:
    return LearningObservation(
        observation_id=observation_id,
        statement=statement,
        source="validated_baseline",
        source_reference="M368.7:9008-tests",
        confidence=1.0,
    )


def test_m369_1_declares_one_canonical_learning_authority() -> None:
    snapshot = LearningFoundation().snapshot

    assert snapshot.schema_version == "m369.1"
    assert snapshot.canonical_authority == "learning_foundation"
    assert snapshot.parent_memory_authority == "cognitive_memory"
    assert snapshot.supported_domains == tuple(LearningDomain)
    assert {item.authority_key for item in snapshot.authorities} == {
        "learning_foundation"
    }


def test_m369_1_reconciles_existing_learning_surfaces() -> None:
    snapshot = LearningFoundation().snapshot

    assert snapshot.authority_for(LearningDomain.OBSERVATIONS).implementation_path == (
        "core.learning:LearningSignal"
    )
    assert snapshot.authority_for(LearningDomain.POLICY).implementation_path == (
        "core.cognitive_memory:CognitiveLearningPolicy"
    )


def test_m369_1_structures_reviewable_candidate_from_explicit_evidence() -> None:
    candidate = LearningFoundation().structure_candidate(
        subject="release_validation",
        proposed_value="Ruff y suite completa son obligatorios",
        observations=(_observation(),),
        confidence=1.0,
    )

    assert candidate.observation_ids == ("obs-1",)
    assert candidate.disposition is LearningCandidateDisposition.REVIEW_REQUIRED
    assert candidate.accepted_as_knowledge is False
    assert candidate.persistence_authorized is False


def test_m369_1_candidate_identity_is_deterministic() -> None:
    authority = LearningFoundation()
    kwargs = {
        "subject": "release_validation",
        "proposed_value": "Ruff y suite completa son obligatorios",
        "observations": (_observation(),),
        "confidence": 1.0,
    }

    assert authority.structure_candidate(**kwargs).candidate_id == (
        authority.structure_candidate(**kwargs).candidate_id
    )


def test_m369_1_requires_explicit_unique_observations() -> None:
    authority = LearningFoundation()

    with pytest.raises(ValueError, match="explicit observations"):
        authority.structure_candidate(
            subject="subject",
            proposed_value="value",
            observations=(),
            confidence=0.5,
        )

    repeated = _observation()
    with pytest.raises(ValueError, match="must be unique"):
        authority.structure_candidate(
            subject="subject",
            proposed_value="value",
            observations=(repeated, repeated),
            confidence=0.5,
        )


def test_m369_1_adds_no_automatic_learning_or_side_effects() -> None:
    snapshot = LearningFoundation().snapshot

    assert snapshot.read_only is True
    assert snapshot.automatic_learning is False
    assert snapshot.automatic_preference_learning is False
    assert snapshot.automatic_habit_detection is False
    assert snapshot.automatic_pattern_recognition is False
    assert snapshot.adaptive_reasoning_enabled is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False


def test_m369_1_documentation_declares_foundation_limits() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M369_1_LEARNING_FOUNDATION.md").read_text(
        encoding="utf-8"
    )

    assert "learning_foundation" in document
    assert "review_required" in document
    assert "no acepta candidatos como conocimiento" in document
    assert "M369.1" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M369.1 — Learning Foundation" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
