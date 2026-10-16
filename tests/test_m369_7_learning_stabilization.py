from pathlib import Path

from app.learning_stabilization import LearningStabilizationAudit
from app.safe_learning_policies import SafeLearningPolicies
from core.safe_learning_policies import (
    LearningPolicyCandidate,
    SafeLearningDisposition,
)


def test_m369_7_certifies_exact_governed_authority_chain() -> None:
    report = LearningStabilizationAudit().audit()

    assert report.schema_version == "m369.7"
    assert report.authority_chain == (
        "learning_foundation",
        "preference_learning",
        "habit_detection",
        "pattern_recognition",
        "adaptive_reasoning",
        "safe_learning_policies",
    )
    assert tuple(item.schema_version for item in report.authorities) == (
        "m369.1",
        "m369.2",
        "m369.3",
        "m369.4",
        "m369.5",
        "m369.6",
    )


def test_m369_7_certifies_side_effect_boundaries() -> None:
    report = LearningStabilizationAudit().audit()

    assert report.authority_names_unique is True
    assert report.parent_chain_valid is True
    assert report.read_only_boundary is True
    assert report.runtime_isolated is True
    assert report.persistence_absent is True
    assert report.automatic_application_absent is True
    assert report.integration_invariants_verified is True
    assert report.series_closed is True



def test_m369_7_report_is_complete_and_read_only() -> None:
    report = LearningStabilizationAudit().audit()

    assert len(report.authorities) == 6
    assert all(item.read_only for item in report.authorities)
    assert all(not item.automatic_application for item in report.authorities)

def test_m369_7_safe_policy_never_auto_promotes_learning() -> None:
    candidate = LearningPolicyCandidate(
        candidate_id="candidate-stable",
        subject="response_format",
        evidence_ids=("evidence-1", "evidence-2"),
        confidence=0.95,
        age_days=1,
    )

    decision = SafeLearningPolicies().evaluate(candidate)

    assert decision.disposition is SafeLearningDisposition.REVIEW_REQUIRED
    assert decision.review_authorized is True
    assert decision.acceptance_authorized is False
    assert decision.persistence_authorized is False
    assert decision.adaptation_authorized is False


def test_m369_7_sensitive_learning_requires_consent() -> None:
    candidate = LearningPolicyCandidate(
        candidate_id="candidate-sensitive",
        subject="sensitive_preference",
        evidence_ids=("evidence-1", "evidence-2"),
        confidence=0.95,
        age_days=1,
        sensitive=True,
        consent_present=False,
    )

    decision = SafeLearningPolicies().evaluate(candidate)

    assert decision.disposition is SafeLearningDisposition.REJECTED
    assert "sensitive_learning_requires_consent" in decision.explanation_codes


def test_m369_7_documentation_closes_series() -> None:
    root = Path(__file__).resolve().parents[1]
    stabilization = (root / "docs/M369_7_LEARNING_STABILIZATION.md").read_text(
        encoding="utf-8"
    )
    report = (root / "docs/M369_SERIES_REPORT.md").read_text(encoding="utf-8")

    assert "serie M369 queda cerrada" in stabilization
    assert "learning_foundation" in stabilization
    assert "M369.1" in report and "M369.7" in report
    assert "9054" in report
    assert "M369.7" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M369.7 — Learning Stabilization" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
