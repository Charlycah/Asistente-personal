from pathlib import Path

import pytest

from app.adaptive_reasoning import AdaptiveReasoning
from core.adaptive_reasoning import (
    AdaptiveLearningEvidence,
    AdaptiveReasoningContext,
    AdaptiveReasoningDisposition,
)
from core.pattern_recognition import (
    PatternCandidate,
    PatternDisposition,
)


def _pattern(
    *,
    pattern_id: str = "pattern-concise",
    subject: str = "response_style",
    value: str = "concise",
    confidence: float = 0.9,
    disposition: PatternDisposition = PatternDisposition.REVIEW_REQUIRED,
) -> PatternCandidate:
    return PatternCandidate(
        pattern_id=pattern_id,
        subject=subject,
        context="validated_conversation",
        observed_value=value,
        evidence_ids=(f"evidence-{pattern_id}-1", f"evidence-{pattern_id}-2"),
        habit_ids=(f"habit-{pattern_id}-1", f"habit-{pattern_id}-2"),
        evidence_count=2,
        confidence=confidence,
        disposition=disposition,
        accepted_as_pattern=False,
        persistence_authorized=False,
    )


def _context() -> AdaptiveReasoningContext:
    return AdaptiveReasoningContext(
        context_id="reply-1",
        subject="response_style",
        available_options=("balanced", "concise", "detailed"),
        default_option="balanced",
    )


def test_m369_5_declares_one_subordinate_adaptive_authority() -> None:
    snapshot = AdaptiveReasoning().snapshot

    assert snapshot.schema_version == "m369.5"
    assert snapshot.canonical_authority == "adaptive_reasoning"
    assert snapshot.parent_authority == "pattern_recognition"
    assert snapshot.read_only is True


def test_m369_5_reviewed_pattern_produces_advisory_suggestion() -> None:
    evidence = AdaptiveLearningEvidence.from_pattern_candidate(_pattern())
    result = AdaptiveReasoning().evaluate(
        context=_context(),
        evidence=(evidence,),
    )

    assert result.disposition is AdaptiveReasoningDisposition.REVIEW_REQUIRED
    assert result.default_option == "balanced"
    assert result.suggested_option == "concise"
    assert result.confidence == 0.9
    assert result.application_authorized is False


def test_m369_5_non_applicable_learning_preserves_default() -> None:
    evidence = AdaptiveLearningEvidence.from_pattern_candidate(
        _pattern(subject="notification_style")
    )
    result = AdaptiveReasoning().evaluate(
        context=_context(),
        evidence=(evidence,),
    )

    assert (
        result.disposition
        is AdaptiveReasoningDisposition.NO_APPLICABLE_LEARNING
    )
    assert result.suggested_option is None
    assert result.pattern_ids == ()


def test_m369_5_rejects_unreviewable_patterns() -> None:
    with pytest.raises(ValueError, match="reviewable pattern"):
        AdaptiveLearningEvidence.from_pattern_candidate(
            _pattern(disposition=PatternDisposition.INSUFFICIENT_EVIDENCE)
        )


def test_m369_5_rejects_conflicting_adaptive_evidence() -> None:
    first = AdaptiveLearningEvidence.from_pattern_candidate(_pattern())
    second = AdaptiveLearningEvidence.from_pattern_candidate(
        _pattern(pattern_id="pattern-detailed", value="detailed")
    )

    with pytest.raises(ValueError, match="support one option"):
        AdaptiveReasoning().evaluate(
            context=_context(),
            evidence=(first, second),
        )


def test_m369_5_requires_explicit_bounded_options() -> None:
    with pytest.raises(ValueError, match="default must be available"):
        AdaptiveReasoningContext(
            context_id="reply-invalid",
            subject="response_style",
            available_options=("concise",),
            default_option="balanced",
        )


def test_m369_5_adds_no_goal_policy_runtime_or_persistence_changes() -> None:
    snapshot = AdaptiveReasoning().snapshot

    assert snapshot.automatic_application is False
    assert snapshot.goal_modification_authorized is False
    assert snapshot.policy_modification_authorized is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False


def test_m369_5_documentation_declares_adaptive_limits() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M369_5_ADAPTIVE_REASONING.md").read_text(
        encoding="utf-8"
    )

    assert "adaptive_reasoning" in document
    assert "review_required" in document
    assert "no aplica adaptaciones automáticamente" in document
    assert "M369.5" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M369.5 — Adaptive Reasoning" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
