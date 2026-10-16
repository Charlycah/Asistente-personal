from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum

from app.safe_learning_policies import SafeLearningPolicies
from core.learning_foundation import (
    LearningCandidate,
    LearningCandidateDisposition,
)
from core.safe_learning_policies import (
    LearningPolicyCandidate,
    SafeLearningDecision,
    SafeLearningDisposition,
)


class GovernedLearningCandidateM369EvaluationStatus(StrEnum):
    NOT_ELIGIBLE = "not_eligible"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class GovernedLearningCandidateM369EvaluationResult:
    status: GovernedLearningCandidateM369EvaluationStatus
    source_candidate: LearningCandidate
    corroborating_candidates: tuple[LearningCandidate, ...]
    policy_candidate: LearningPolicyCandidate | None
    safe_learning_decision: SafeLearningDecision | None
    read_only: bool = True
    uses_existing_m369: bool = True
    accepts_learning: bool = False
    persists_results: bool = False
    writes_memory: bool = False
    writes_knowledge: bool = False


class GovernedLearningCandidateM369EvaluationV1:
    def __init__(self, *, safe_learning_policies=None) -> None:
        self._safe_learning_policies = safe_learning_policies or SafeLearningPolicies()

    def evaluate(
        self,
        source_candidate: LearningCandidate,
        *,
        corroborating_candidates: tuple[LearningCandidate, ...] = (),
        age_days: int,
    ) -> GovernedLearningCandidateM369EvaluationResult:
        candidates = (source_candidate, *corroborating_candidates)
        if not self._eligible_inputs(candidates, age_days=age_days):
            return self._not_eligible(source_candidate, corroborating_candidates)

        normalized_subject = self._normalize(source_candidate.subject)
        normalized_value = self._normalize(source_candidate.proposed_value)
        if any(
            self._normalize(item.subject) != normalized_subject
            or self._normalize(item.proposed_value) != normalized_value
            for item in corroborating_candidates
        ):
            return self._not_eligible(source_candidate, corroborating_candidates)

        evidence_ids = tuple(item.candidate_id for item in candidates)
        if len(evidence_ids) != len(set(evidence_ids)):
            return self._not_eligible(source_candidate, corroborating_candidates)

        confidence = round(
            sum(item.confidence for item in candidates) / len(candidates), 12
        )
        policy_candidate = LearningPolicyCandidate(
            candidate_id=self._policy_candidate_id(evidence_ids),
            subject=source_candidate.subject.strip(),
            evidence_ids=evidence_ids,
            confidence=confidence,
            age_days=age_days,
        )
        decision = self._safe_learning_policies.evaluate(policy_candidate)
        return GovernedLearningCandidateM369EvaluationResult(
            status=self._status_for(decision.disposition),
            source_candidate=source_candidate,
            corroborating_candidates=corroborating_candidates,
            policy_candidate=policy_candidate,
            safe_learning_decision=decision,
        )

    @staticmethod
    def _eligible_inputs(
        candidates: tuple[LearningCandidate, ...], *, age_days: int
    ) -> bool:
        if isinstance(age_days, bool) or not isinstance(age_days, int) or age_days < 0:
            return False
        return all(
            isinstance(item, LearningCandidate)
            and item.disposition is LearningCandidateDisposition.REVIEW_REQUIRED
            and item.accepted_as_knowledge is False
            and item.persistence_authorized is False
            for item in candidates
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.split()).casefold()

    @staticmethod
    def _policy_candidate_id(evidence_ids: tuple[str, ...]) -> str:
        payload = "\x1f".join(evidence_ids).encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()[:24]
        return f"governed-m369-evaluation-{digest}"

    @staticmethod
    def _status_for(
        disposition: SafeLearningDisposition,
    ) -> GovernedLearningCandidateM369EvaluationStatus:
        return GovernedLearningCandidateM369EvaluationStatus(disposition.value)

    @staticmethod
    def _not_eligible(
        source_candidate: LearningCandidate,
        corroborating_candidates: tuple[LearningCandidate, ...],
    ) -> GovernedLearningCandidateM369EvaluationResult:
        return GovernedLearningCandidateM369EvaluationResult(
            status=GovernedLearningCandidateM369EvaluationStatus.NOT_ELIGIBLE,
            source_candidate=source_candidate,
            corroborating_candidates=corroborating_candidates,
            policy_candidate=None,
            safe_learning_decision=None,
        )
