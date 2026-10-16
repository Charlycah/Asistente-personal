from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from app.approved_learning_memory_materialization import ApprovedLearningScope
from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationResult,
    GovernedLearningCandidateM369EvaluationStatus,
)
from app.m369_explicit_human_learning_approval import (
    HumanLearningApprovalOutcome,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)
from core.safe_learning_policies import SafeLearningDisposition


@dataclass(frozen=True)
class GovernedExplicitHumanLearningApprovalResponse:
    approval_request_id: str
    source_evaluation_fingerprint: str
    learning_candidate_id: str
    policy_candidate_id: str
    human_response_reference: str
    response_text: str
    approver: str
    scope: ApprovedLearningScope
    exact_linkage: bool = True

    def __post_init__(self) -> None:
        required = (
            self.approval_request_id,
            self.source_evaluation_fingerprint,
            self.learning_candidate_id,
            self.policy_candidate_id,
            self.human_response_reference,
            self.response_text,
            self.approver,
        )
        if any(not value.strip() for value in required):
            raise ValueError(
                "governed human learning approval requires complete provenance"
            )


@dataclass(frozen=True)
class GovernedApprovedLearningEvidence:
    approval_id: str
    approval_request_id: str
    source_evaluation_fingerprint: str
    learning_candidate_id: str
    policy_candidate_id: str
    human_response_reference: str
    approver: str
    scope: ApprovedLearningScope
    source_fingerprint: str
    read_only: bool = True
    persists_results: bool = False
    writes_memory: bool = False
    writes_knowledge: bool = False
    materializes_learning: bool = False

    def __post_init__(self) -> None:
        required = (
            self.approval_id,
            self.approval_request_id,
            self.source_evaluation_fingerprint,
            self.learning_candidate_id,
            self.policy_candidate_id,
            self.human_response_reference,
            self.approver,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("governed approved learning evidence requires provenance")
        if not self.read_only or any(
            (
                self.persists_results,
                self.writes_memory,
                self.writes_knowledge,
                self.materializes_learning,
            )
        ):
            raise ValueError("governed approved learning evidence violates STOP")


@dataclass(frozen=True)
class GovernedG6HumanLearningApprovalResult:
    outcome: HumanLearningApprovalOutcome
    source_evaluation_fingerprint: str
    learning_candidate_id: str
    policy_candidate_id: str
    approval_request_id: str
    human_response_reference: str
    approver: str
    scope: ApprovedLearningScope
    rationale_codes: tuple[str, ...]
    approved_evidence: GovernedApprovedLearningEvidence | None = None
    read_only: bool = True
    persists_results: bool = False
    writes_memory: bool = False
    writes_knowledge: bool = False
    materializes_learning: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes:
            raise ValueError("governed human learning approval requires rationale")
        approved = self.outcome is HumanLearningApprovalOutcome.APPROVED
        if (self.approved_evidence is not None) is not approved:
            raise ValueError("approved evidence presence must match approval outcome")
        if not self.read_only or any(
            (
                self.persists_results,
                self.writes_memory,
                self.writes_knowledge,
                self.materializes_learning,
            )
        ):
            raise ValueError("governed human learning approval violates STOP")


class GovernedG6ExplicitHumanLearningApprovalV1:
    """Source-neutral G6 seam into the existing M369 human approval semantics."""

    def __init__(self, *, human_approval_foundation=None) -> None:
        self._human_approval_foundation = (
            human_approval_foundation
            or M369ExplicitHumanLearningApprovalEvidenceFoundation()
        )

    @staticmethod
    def source_evaluation_fingerprint(
        evaluation: GovernedLearningCandidateM369EvaluationResult,
    ) -> str:
        policy = evaluation.policy_candidate
        decision = evaluation.safe_learning_decision
        payload = (
            evaluation.status.value,
            evaluation.source_candidate.candidate_id,
            tuple(item.candidate_id for item in evaluation.corroborating_candidates),
            policy.candidate_id if policy is not None else "",
            policy.evidence_ids if policy is not None else (),
            policy.confidence if policy is not None else None,
            decision.disposition.value if decision is not None else "",
            decision.review_authorized if decision is not None else False,
            decision.acceptance_authorized if decision is not None else False,
            decision.persistence_authorized if decision is not None else False,
            decision.adaptation_authorized if decision is not None else False,
        )
        return sha256(repr(payload).encode("utf-8")).hexdigest()

    def evaluate(
        self,
        evaluation: GovernedLearningCandidateM369EvaluationResult,
        response: GovernedExplicitHumanLearningApprovalResponse,
    ) -> GovernedG6HumanLearningApprovalResult:
        if not self._review_eligible(evaluation):
            return self._result(
                response,
                HumanLearningApprovalOutcome.ABSTAIN,
                ("g6_review_required_source_required",),
            )
        if not self._exactly_linked(evaluation, response):
            return self._result(
                response,
                HumanLearningApprovalOutcome.ABSTAIN,
                ("exact_g6_learning_approval_linkage_required",),
            )

        outcome = self._human_approval_foundation.classify_explicit_response(
            response.response_text
        )
        rationale = self._rationale_for(outcome)
        if outcome is not HumanLearningApprovalOutcome.APPROVED:
            return self._result(response, outcome, rationale)

        fingerprint = self._approval_fingerprint(response)
        evidence = GovernedApprovedLearningEvidence(
            approval_id=f"governed-g6-human-learning-approved-{fingerprint[:16]}",
            approval_request_id=response.approval_request_id,
            source_evaluation_fingerprint=response.source_evaluation_fingerprint,
            learning_candidate_id=response.learning_candidate_id,
            policy_candidate_id=response.policy_candidate_id,
            human_response_reference=response.human_response_reference,
            approver=response.approver,
            scope=response.scope,
            source_fingerprint=fingerprint,
        )
        return self._result(response, outcome, rationale, evidence)

    @staticmethod
    def _review_eligible(
        evaluation: GovernedLearningCandidateM369EvaluationResult,
    ) -> bool:
        decision = evaluation.safe_learning_decision
        return bool(
            evaluation.status
            is GovernedLearningCandidateM369EvaluationStatus.REVIEW_REQUIRED
            and evaluation.policy_candidate is not None
            and decision is not None
            and decision.disposition is SafeLearningDisposition.REVIEW_REQUIRED
            and decision.review_authorized is True
            and decision.acceptance_authorized is False
            and decision.persistence_authorized is False
            and decision.adaptation_authorized is False
        )

    def _exactly_linked(
        self,
        evaluation: GovernedLearningCandidateM369EvaluationResult,
        response: GovernedExplicitHumanLearningApprovalResponse,
    ) -> bool:
        policy = evaluation.policy_candidate
        return bool(
            response.exact_linkage
            and policy is not None
            and response.source_evaluation_fingerprint
            == self.source_evaluation_fingerprint(evaluation)
            and response.learning_candidate_id
            == evaluation.source_candidate.candidate_id
            and response.policy_candidate_id == policy.candidate_id
        )

    @staticmethod
    def _approval_fingerprint(
        response: GovernedExplicitHumanLearningApprovalResponse,
    ) -> str:
        payload = (
            response.approval_request_id,
            response.source_evaluation_fingerprint,
            response.learning_candidate_id,
            response.policy_candidate_id,
            response.human_response_reference,
            response.response_text,
            response.approver,
            response.scope.value,
            response.exact_linkage,
        )
        return sha256(repr(payload).encode("utf-8")).hexdigest()

    @staticmethod
    def _rationale_for(
        outcome: HumanLearningApprovalOutcome,
    ) -> tuple[str, ...]:
        return {
            HumanLearningApprovalOutcome.APPROVED: (
                "explicit_human_learning_approval",
                "exact_g6_linkage_preserved",
            ),
            HumanLearningApprovalOutcome.REJECTED: (
                "explicit_human_learning_rejection",
            ),
            HumanLearningApprovalOutcome.DEFERRED: (
                "explicit_human_learning_deferral",
            ),
            HumanLearningApprovalOutcome.UNCLEAR: (
                "human_learning_response_not_explicit_enough",
            ),
            HumanLearningApprovalOutcome.ABSTAIN: (
                "unsupported_or_non_explicit_learning_approval_response",
            ),
        }[outcome]

    @staticmethod
    def _result(
        response: GovernedExplicitHumanLearningApprovalResponse,
        outcome: HumanLearningApprovalOutcome,
        rationale: tuple[str, ...],
        evidence: GovernedApprovedLearningEvidence | None = None,
    ) -> GovernedG6HumanLearningApprovalResult:
        return GovernedG6HumanLearningApprovalResult(
            outcome=outcome,
            source_evaluation_fingerprint=response.source_evaluation_fingerprint,
            learning_candidate_id=response.learning_candidate_id,
            policy_candidate_id=response.policy_candidate_id,
            approval_request_id=response.approval_request_id,
            human_response_reference=response.human_response_reference,
            approver=response.approver,
            scope=response.scope,
            rationale_codes=rationale,
            approved_evidence=evidence,
        )
