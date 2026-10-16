from __future__ import annotations

from core.safe_learning_policies import (
    LearningPolicyCandidate,
    SafeLearningDecision,
    SafeLearningDisposition,
    SafeLearningPolicySnapshot,
)


class SafeLearningPolicies:
    """Deterministic safety gate for reviewable learning candidates."""

    SCHEMA_VERSION = "m369.6"
    CANONICAL_AUTHORITY = "safe_learning_policies"
    PARENT_AUTHORITY = "adaptive_reasoning"
    MINIMUM_EVIDENCE_COUNT = 2
    MINIMUM_CONFIDENCE = 0.6
    MAXIMUM_AGE_DAYS = 90
    CONTRADICTION_TOLERANCE = 0

    @property
    def snapshot(self) -> SafeLearningPolicySnapshot:
        return SafeLearningPolicySnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_authority=self.PARENT_AUTHORITY,
            minimum_evidence_count=self.MINIMUM_EVIDENCE_COUNT,
            minimum_confidence=self.MINIMUM_CONFIDENCE,
            maximum_age_days=self.MAXIMUM_AGE_DAYS,
            contradiction_tolerance=self.CONTRADICTION_TOLERANCE,
            sensitive_learning_requires_consent=True,
            automatic_acceptance=False,
            automatic_persistence=False,
            automatic_adaptation=False,
            runtime_behavior_changed=False,
        )

    def evaluate(self, candidate: LearningPolicyCandidate) -> SafeLearningDecision:
        if candidate.contradiction_count > self.CONTRADICTION_TOLERANCE:
            return self._decision(
                candidate,
                SafeLearningDisposition.REJECTED,
                ("contradictory_evidence",),
            )
        if candidate.sensitive and not candidate.consent_present:
            return self._decision(
                candidate,
                SafeLearningDisposition.REJECTED,
                ("sensitive_learning_requires_consent",),
            )
        if candidate.age_days > self.MAXIMUM_AGE_DAYS:
            return self._decision(
                candidate,
                SafeLearningDisposition.EXPIRED,
                ("learning_evidence_expired",),
            )
        if (
            len(candidate.evidence_ids) < self.MINIMUM_EVIDENCE_COUNT
            or candidate.confidence < self.MINIMUM_CONFIDENCE
        ):
            return self._decision(
                candidate,
                SafeLearningDisposition.INSUFFICIENT_EVIDENCE,
                ("evidence_or_confidence_below_threshold",),
            )
        return self._decision(
            candidate,
            SafeLearningDisposition.REVIEW_REQUIRED,
            ("policy_checks_passed", "human_review_still_required"),
        )

    @staticmethod
    def _decision(
        candidate: LearningPolicyCandidate,
        disposition: SafeLearningDisposition,
        explanation_codes: tuple[str, ...],
    ) -> SafeLearningDecision:
        return SafeLearningDecision(
            candidate_id=candidate.candidate_id,
            disposition=disposition,
            explanation_codes=explanation_codes,
            review_authorized=(
                disposition is SafeLearningDisposition.REVIEW_REQUIRED
            ),
            acceptance_authorized=False,
            persistence_authorized=False,
            adaptation_authorized=False,
        )
