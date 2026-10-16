from pathlib import Path

from app.safe_learning_policies import SafeLearningPolicies
from core.safe_learning_policies import (
    LearningPolicyCandidate,
    SafeLearningDisposition,
)


def _candidate(**overrides: object) -> LearningPolicyCandidate:
    values: dict[str, object] = {
        "candidate_id": "learning-1",
        "subject": "response_style",
        "evidence_ids": ("evidence-1", "evidence-2"),
        "confidence": 0.8,
        "age_days": 10,
    }
    values.update(overrides)
    return LearningPolicyCandidate(**values)  # type: ignore[arg-type]


def test_m369_6_declares_one_subordinate_policy_authority() -> None:
    snapshot = SafeLearningPolicies().snapshot

    assert snapshot.schema_version == "m369.6"
    assert snapshot.canonical_authority == "safe_learning_policies"
    assert snapshot.parent_authority == "adaptive_reasoning"


def test_m369_6_sufficient_candidate_still_requires_review() -> None:
    decision = SafeLearningPolicies().evaluate(_candidate())

    assert decision.disposition is SafeLearningDisposition.REVIEW_REQUIRED
    assert decision.review_authorized is True
    assert decision.acceptance_authorized is False


def test_m369_6_rejects_contradictory_evidence() -> None:
    decision = SafeLearningPolicies().evaluate(
        _candidate(contradiction_count=1)
    )

    assert decision.disposition is SafeLearningDisposition.REJECTED
    assert decision.explanation_codes == ("contradictory_evidence",)


def test_m369_6_requires_consent_for_sensitive_learning() -> None:
    decision = SafeLearningPolicies().evaluate(
        _candidate(sensitive=True, consent_present=False)
    )

    assert decision.disposition is SafeLearningDisposition.REJECTED
    assert "sensitive_learning_requires_consent" in decision.explanation_codes


def test_m369_6_expires_stale_learning() -> None:
    decision = SafeLearningPolicies().evaluate(_candidate(age_days=91))

    assert decision.disposition is SafeLearningDisposition.EXPIRED


def test_m369_6_keeps_weak_learning_as_insufficient() -> None:
    decision = SafeLearningPolicies().evaluate(
        _candidate(evidence_ids=("evidence-1",), confidence=0.5)
    )

    assert decision.disposition is SafeLearningDisposition.INSUFFICIENT_EVIDENCE


def test_m369_6_never_auto_applies_or_persists_learning() -> None:
    decision = SafeLearningPolicies().evaluate(_candidate())
    snapshot = SafeLearningPolicies().snapshot

    assert decision.persistence_authorized is False
    assert decision.adaptation_authorized is False
    assert snapshot.automatic_acceptance is False
    assert snapshot.automatic_persistence is False
    assert snapshot.automatic_adaptation is False
    assert snapshot.runtime_behavior_changed is False


def test_m369_6_documentation_declares_policy_limits() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M369_6_SAFE_LEARNING_POLICIES.md").read_text(
        encoding="utf-8"
    )

    assert "safe_learning_policies" in document
    assert "review_required" in document
    assert "no acepta aprendizajes automáticamente" in document
    assert "M369.6" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M369.6 — Safe Learning Policies" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
