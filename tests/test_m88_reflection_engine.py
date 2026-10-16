from datetime import datetime, timedelta, timezone

import pytest

from core.adaptive_cognition import (
    AdaptiveReflectionEngine,
    AdaptiveReflectionManager,
    InMemoryReflectionRepository,
    MetaReasoningAssessment,
    MetaReasoningDimension,
    MetaReasoningFinding,
    MetaReasoningFindingSeverity,
    MetaReasoningJudgement,
    ReflectionImportance,
    ReflectionObservation,
    ReflectionOutcome,
    ReflectionPatternKind,
    ReflectionPolicy,
)

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def assessment(
    score: float,
    *,
    offset: int = 0,
    review: bool = False,
    recommendation: str = "Acquire additional governed evidence.",
) -> MetaReasoningAssessment:
    severity = (
        MetaReasoningFindingSeverity.HIGH
        if review
        else MetaReasoningFindingSeverity.INFO
    )
    finding = MetaReasoningFinding(
        MetaReasoningDimension.EVIDENCE_SUFFICIENCY,
        f"Evidence quality at {score:.2f}.",
        severity,
        score,
    )
    judgement = (
        MetaReasoningJudgement.UNCERTAIN
        if review
        else MetaReasoningJudgement.ACCEPTABLE
    )
    return MetaReasoningAssessment(
        reasoning_result_id=f"result-{offset}",
        judgement=judgement,
        score=score,
        summary="Assessment summary.",
        findings=(finding,),
        recommendations=(recommendation,) if recommendation else (),
        created_at=NOW + timedelta(minutes=offset),
    )


def test_observation_requires_sources() -> None:
    with pytest.raises(ValueError):
        ReflectionObservation(
            ReflectionPatternKind.SCORE_TREND,
            "trend",
            ReflectionImportance.INFO,
            0.8,
            (),
        )


def test_observation_identity_is_stable() -> None:
    item = ReflectionObservation(
        ReflectionPatternKind.SCORE_TREND,
        "trend",
        ReflectionImportance.INFO,
        0.8,
        ("a",),
    )
    assert len(item.observation_id) == 64


def test_observation_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        ReflectionObservation(
            ReflectionPatternKind.SCORE_TREND,
            "trend",
            ReflectionImportance.INFO,
            2.0,
            ("a",),
        )


def test_policy_rejects_invalid_counts() -> None:
    with pytest.raises(ValueError):
        ReflectionPolicy(recurring_count=1)


def test_engine_requires_assessments() -> None:
    with pytest.raises(ValueError):
        AdaptiveReflectionEngine().reflect(())


def test_single_assessment_is_insufficient() -> None:
    record = AdaptiveReflectionEngine().reflect((assessment(0.7),), now=NOW)
    assert record.normalized_outcome is ReflectionOutcome.INSUFFICIENT


def test_improving_scores_are_detected() -> None:
    record = AdaptiveReflectionEngine().reflect(
        (assessment(0.4), assessment(0.8, offset=1)), now=NOW
    )
    assert record.normalized_outcome is ReflectionOutcome.IMPROVING


def test_degrading_scores_require_review() -> None:
    record = AdaptiveReflectionEngine().reflect(
        (assessment(0.9), assessment(0.5, offset=1)), now=NOW
    )
    assert record.normalized_outcome is ReflectionOutcome.DEGRADING
    assert record.requires_review


def test_stable_scores_are_detected() -> None:
    record = AdaptiveReflectionEngine().reflect(
        (assessment(0.7), assessment(0.72, offset=1)), now=NOW
    )
    assert record.normalized_outcome is ReflectionOutcome.STABLE


def test_mixed_review_states_are_detected() -> None:
    record = AdaptiveReflectionEngine().reflect(
        (assessment(0.7), assessment(0.7, offset=1, review=True)), now=NOW
    )
    assert record.normalized_outcome is ReflectionOutcome.MIXED


def test_recurring_dimension_becomes_observation() -> None:
    record = AdaptiveReflectionEngine().reflect(
        (
            assessment(0.5, review=True),
            assessment(0.5, offset=1, review=True),
        ),
        now=NOW,
    )
    assert any(
        item.normalized_kind is ReflectionPatternKind.RECURRING_DIMENSION
        for item in record.observations
    )


def test_recurring_recommendation_becomes_observation() -> None:
    record = AdaptiveReflectionEngine().reflect(
        (assessment(0.5), assessment(0.5, offset=1)), now=NOW
    )
    assert any(
        item.normalized_kind is ReflectionPatternKind.RECURRING_RECOMMENDATION
        for item in record.observations
    )


def test_source_assessments_are_not_mutated() -> None:
    source = assessment(0.7)
    before = source.to_dict()
    AdaptiveReflectionEngine().reflect((source,), now=NOW)
    assert source.to_dict() == before


def test_record_identity_is_sha256() -> None:
    record = AdaptiveReflectionEngine().reflect((assessment(0.7),), now=NOW)
    assert len(record.record_id) == 64


def test_record_is_serializable() -> None:
    payload = AdaptiveReflectionEngine().reflect((assessment(0.7),), now=NOW).to_dict()
    assert payload["assessment_ids"]
    assert payload["outcome"] == "insufficient"


def test_repository_stores_records() -> None:
    repository = InMemoryReflectionRepository()
    record = AdaptiveReflectionEngine().reflect((assessment(0.7),), now=NOW)
    repository.add(record)
    assert repository.get(record.record_id) == record


def test_repository_rejects_duplicates() -> None:
    repository = InMemoryReflectionRepository()
    record = AdaptiveReflectionEngine().reflect((assessment(0.7),), now=NOW)
    repository.add(record)
    with pytest.raises(ValueError):
        repository.add(record)


def test_manager_persists_last_record() -> None:
    manager = AdaptiveReflectionManager()
    record = manager.reflect((assessment(0.7),), now=NOW)
    assert manager.last_record == record
    assert manager.repository.get(record.record_id) == record


def test_manager_prompt_preserves_governance_boundary() -> None:
    lines = AdaptiveReflectionManager().system_prompt_lines()
    assert any("no reescribe" in line for line in lines)
    assert any("no cambian conocimiento" in line for line in lines)


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError):
        AdaptiveReflectionEngine().reflect(
            (assessment(0.7),), now=datetime(2026, 7, 10, 12, 0)
        )
