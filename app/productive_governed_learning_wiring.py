from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .approved_learning_memory_materialization import (
    ApprovedLearningMemoryMaterializationProposalFoundation,
    ApprovedLearningMemoryMaterializationReport,
    LearningMemoryMaterializationOutcome,
)
from .approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
    GovernedMemoryWriteRequest,
)
from .curiosity_m369_learning_evaluation import CuriosityM369LearningEvaluationReport
from .governed_knowledge_revision_application_proposal import (
    GovernedKnowledgeRevisionApplicationProposalFoundation,
)
from .governed_knowledge_revision_proposal import (
    GovernedKnowledgeRevisionProposal,
    GovernedKnowledgeRevisionProposalFoundation,
)
from .governed_knowledge_revision_request import (
    GovernedKnowledgeRevisionRequest,
    GovernedKnowledgeRevisionRequestFoundation,
)
from .m369_explicit_human_learning_approval import (
    ApprovedKnowledgeRevisionEvidence,
    AuthorizedGovernedMemoryWriteExecutionEvidence,
    AuthorizedKnowledgeRevisionExecutionEvidence,
    ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
    ExplicitHumanKnowledgeRevisionApprovalResponse,
    ExplicitHumanLearningApprovalResponse,
    HumanLearningApprovalOutcome,
    HumanLearningApprovalReport,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)


class GovernedLearningMemoryWriter(Protocol):
    def remember_governed_learning(self, request: GovernedMemoryWriteRequest): ...

    def apply_governed_knowledge_revision(
        self,
        request: GovernedKnowledgeRevisionRequest,
    ): ...


class ProductiveGovernedLearningOutcome(StrEnum):
    STORED = "stored"
    ALREADY_STORED = "already_stored"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    UNCLEAR = "unclear"
    ABSTAIN = "abstain"
    REVIEW_REQUIRED = "review_required"
    MEMORY_UNAVAILABLE = "memory_unavailable"
    WRITE_FAILED = "write_failed"


@dataclass(frozen=True)
class ProductiveGovernedLearningResult:
    outcome: ProductiveGovernedLearningOutcome
    rationale_codes: tuple[str, ...]
    approval: HumanLearningApprovalReport | None = None
    materialization: ApprovedLearningMemoryMaterializationReport | None = None
    write_request: GovernedMemoryWriteRequest | None = None
    stored_memory_ids: tuple[str, ...] = ()
    writer_call_performed: bool = False
    schema_version: str = "post-m409.1-governed-learning-productive-wiring-v1"
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes:
            raise ValueError("productive governed learning requires rationale")
        if self.grants_authority or self.starts_background_process:
            raise ValueError("productive governed learning cannot expand authority")
        if self.writer_call_performed and self.write_request is None:
            raise ValueError("writer call requires a governed write request")
        wrote = self.outcome in {
            ProductiveGovernedLearningOutcome.STORED,
            ProductiveGovernedLearningOutcome.ALREADY_STORED,
        }
        if self.writer_call_performed is not wrote:
            raise ValueError("writer-call flag must match persistent outcomes")


class ProductiveGovernedLearningWiring:
    """Orchestrate certified approval-to-memory contracts with one official writer."""

    def __init__(
        self,
        memory_gateway: GovernedLearningMemoryWriter | None,
    ) -> None:
        self._memory_gateway = memory_gateway
        self._approval = M369ExplicitHumanLearningApprovalEvidenceFoundation()
        self._materialization = (
            ApprovedLearningMemoryMaterializationProposalFoundation()
        )
        self._write_adapter = GovernedMemoryWriteAdapterFoundation()
        self._revision_proposal = GovernedKnowledgeRevisionProposalFoundation()
        self._revision_application = (
            GovernedKnowledgeRevisionApplicationProposalFoundation()
        )
        self._revision_request = GovernedKnowledgeRevisionRequestFoundation()
        self._pending_memory_write_request: dict[str, GovernedMemoryWriteRequest] = {}
        self._pending_revision: dict[str, GovernedKnowledgeRevisionProposal] = {}

    def execute(
        self,
        evaluation: CuriosityM369LearningEvaluationReport,
        response: ExplicitHumanLearningApprovalResponse,
        *,
        current_turn_text: str,
    ) -> ProductiveGovernedLearningResult:
        current_text = self._normalize(current_turn_text)
        response_text = self._normalize(response.response_text)
        if current_text != response_text:
            return self._result(
                ProductiveGovernedLearningOutcome.ABSTAIN,
                ("current_turn_does_not_match_approval_response",),
            )

        approval = self._approval.evaluate(evaluation, response)
        if approval.outcome is not HumanLearningApprovalOutcome.APPROVED:
            return self._non_approved(approval)

        evidence = approval.approved_evidence
        if evidence is None:
            raise ValueError("approved outcome requires approved learning evidence")

        materialization = self._materialization.propose(evaluation, evidence)
        if (
            materialization.outcome
            is not LearningMemoryMaterializationOutcome.PROPOSAL_READY
        ):
            return self._result(
                ProductiveGovernedLearningOutcome.REVIEW_REQUIRED,
                ("durable_materialization_not_ready",),
                approval=approval,
                materialization=materialization,
            )

        proposal = materialization.proposal
        if proposal is None:
            raise ValueError("proposal-ready materialization requires proposal")
        request = self._write_adapter.adapt(proposal)
        return self._persist_certified_write_request(
            request,
            approval=approval,
            materialization=materialization,
        )

    def execute_certified_write_request(
        self,
        request: GovernedMemoryWriteRequest,
        authorization: AuthorizedGovernedMemoryWriteExecutionEvidence | None = None,
    ) -> ProductiveGovernedLearningResult:
        """Persist one exact certified request only with apply-now evidence."""
        if authorization is None or not self._memory_write_authorization_matches(
            request, authorization
        ):
            return self._result(
                ProductiveGovernedLearningOutcome.REVIEW_REQUIRED,
                ("explicit_memory_write_execution_authorization_required",),
                write_request=request,
            )
        return self._persist_certified_write_request(request)

    @staticmethod
    def _memory_write_authorization_matches(
        request: GovernedMemoryWriteRequest,
        authorization: AuthorizedGovernedMemoryWriteExecutionEvidence,
    ) -> bool:
        return bool(
            authorization.read_only
            and not authorization.write_performed
            and not authorization.memory_persisted
            and not authorization.memory_created
            and not authorization.executes_actions
            and not authorization.grants_authority
            and authorization.memory_write_request_id == request.request_id
            and authorization.materialization_proposal_id
            == request.materialization_proposal_id
            and authorization.idempotency_key == request.idempotency_key
            and authorization.writer_authority == request.writer_authority
            and authorization.writer_component == request.writer_component
            and authorization.writer_method == request.writer_method
        )

    def retain_pending_governed_memory_write_request(
        self,
        session_id: str,
        request: GovernedMemoryWriteRequest,
    ) -> GovernedMemoryWriteRequest:
        """Retain one exact inert governed Memory write request for one session."""
        normalized_session_id = str(session_id).strip()
        if not normalized_session_id:
            raise ValueError("pending governed memory write requires session identity")
        if not (
            request.read_only
            and not request.write_performed
            and not request.persists_results
            and not request.creates_memory
            and not request.executes_actions
            and not request.grants_authority
        ):
            raise ValueError("pending governed memory write request must remain inert")
        self._pending_memory_write_request[normalized_session_id] = request
        return request

    def pending_governed_memory_write_request(
        self,
        session_id: str,
    ) -> GovernedMemoryWriteRequest | None:
        """Return the exact inert Memory write request pending in one session."""
        normalized_session_id = str(session_id).strip()
        if not normalized_session_id:
            return None
        return self._pending_memory_write_request.get(normalized_session_id)

    def evaluate_pending_governed_memory_write_execution_authorization(
        self,
        session_id: str,
        response: ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
    ) -> AuthorizedGovernedMemoryWriteExecutionEvidence | None:
        """Evaluate the exact pending request through the existing M369 authority."""
        request = self.pending_governed_memory_write_request(session_id)
        if request is None:
            return None
        if (
            not response.exact_linkage
            or response.memory_write_request_id != request.request_id
        ):
            return None
        return self._approval.evaluate_governed_memory_write_execution_authorization(
            request,
            response,
        )

    def consume_pending_governed_memory_write_request(
        self,
        session_id: str,
        request: GovernedMemoryWriteRequest,
    ) -> bool:
        """Consume only the exact pending request for one normalized session."""
        normalized_session_id = str(session_id).strip()
        if not normalized_session_id:
            return False
        pending = self._pending_memory_write_request.get(normalized_session_id)
        if pending is None:
            return False
        if (
            pending.request_id != request.request_id
            or pending.materialization_proposal_id
            != request.materialization_proposal_id
            or pending.idempotency_key != request.idempotency_key
            or pending.writer_authority != request.writer_authority
            or pending.writer_component != request.writer_component
            or pending.writer_method != request.writer_method
        ):
            return False
        self._pending_memory_write_request.pop(normalized_session_id, None)
        return True

    def propose_knowledge_revision(
        self,
        target_memory,
        corrective_evidence,
        proposed_content: str,
        session_id: str,
    ) -> GovernedKnowledgeRevisionProposal:
        """Create and retain one inert G13 proposal for human review."""
        normalized_session_id = str(session_id).strip()
        if not normalized_session_id:
            raise ValueError("revision proposal requires session identity")
        proposal = self._revision_proposal.propose(
            target_memory,
            corrective_evidence,
            proposed_content=proposed_content,
        )
        self._pending_revision[normalized_session_id] = proposal
        return proposal

    def pending_revision_proposal(
        self,
        session_id: str,
    ) -> GovernedKnowledgeRevisionProposal | None:
        """Return the exact inert proposal pending in one conversation session."""
        normalized_session_id = str(session_id).strip()
        if not normalized_session_id:
            return None
        return self._pending_revision.get(normalized_session_id)

    def evaluate_pending_knowledge_revision(
        self,
        session_id: str,
        response: ExplicitHumanKnowledgeRevisionApprovalResponse,
    ) -> ApprovedKnowledgeRevisionEvidence | None:
        """Evaluate only the exact G13 proposal pending in this session via G14."""
        proposal = self.pending_revision_proposal(session_id)
        if proposal is None:
            return None
        if (
            not response.exact_linkage
            or response.revision_proposal_id != proposal.proposal_id
        ):
            return None
        return self._approval.evaluate_revision(proposal, response)

    def prepare_approved_knowledge_revision(
        self,
        approved_revision: ApprovedKnowledgeRevisionEvidence,
        *,
        owner: str,
    ) -> GovernedKnowledgeRevisionRequest:
        """Prepare and certify an approved revision without executing Memory."""
        proposal = self._revision_application.propose(
            approved_revision,
            owner=owner,
        )
        return self._revision_request.certify(proposal)

    def execute_certified_revision_request(
        self,
        request: GovernedKnowledgeRevisionRequest,
        authorization: AuthorizedKnowledgeRevisionExecutionEvidence | None = None,
    ):
        """Execute one exact G16 request only with explicit apply-now evidence."""
        if self._memory_gateway is None or authorization is None:
            return None
        if not self._execution_authorization_matches(request, authorization):
            return None
        return self._memory_gateway.apply_governed_knowledge_revision(request)

    @staticmethod
    def _execution_authorization_matches(
        request: GovernedKnowledgeRevisionRequest,
        authorization: AuthorizedKnowledgeRevisionExecutionEvidence,
    ) -> bool:
        return bool(
            authorization.read_only
            and not authorization.write_performed
            and not authorization.replacement_persisted
            and not authorization.supersession_applied
            and not authorization.memory_modified
            and not authorization.executes_actions
            and not authorization.grants_authority
            and authorization.revision_request_id == request.request_id
            and authorization.application_proposal_id == request.application_proposal_id
            and authorization.revision_approval_id == request.revision_approval_id
            and authorization.revision_proposal_id == request.revision_proposal_id
            and authorization.target_memory_id == request.target_memory_id
            and authorization.target_owner == request.target_owner
            and authorization.expected_target_fingerprint
            == request.expected_target_fingerprint
            and authorization.replacement_idempotency_key
            == request.replacement_idempotency_key
        )

    def _persist_certified_write_request(
        self,
        request: GovernedMemoryWriteRequest,
        *,
        approval: HumanLearningApprovalReport | None = None,
        materialization: ApprovedLearningMemoryMaterializationReport | None = None,
    ) -> ProductiveGovernedLearningResult:
        if self._memory_gateway is None:
            return self._result(
                ProductiveGovernedLearningOutcome.MEMORY_UNAVAILABLE,
                ("official_memory_gateway_unavailable",),
                approval=approval,
                materialization=materialization,
                write_request=request,
            )

        try:
            stored = self._memory_gateway.remember_governed_learning(request)
        except Exception:
            return self._result(
                ProductiveGovernedLearningOutcome.WRITE_FAILED,
                ("official_memory_gateway_write_failed",),
                approval=approval,
                materialization=materialization,
                write_request=request,
            )

        stored_count = int(getattr(stored, "stored_count", 0))
        memory_ids = tuple(getattr(stored, "stored_memory_ids", ()))
        outcome = (
            ProductiveGovernedLearningOutcome.STORED
            if stored_count > 0
            else ProductiveGovernedLearningOutcome.ALREADY_STORED
        )
        return self._result(
            outcome,
            (
                "governed_learning_written_once"
                if stored_count > 0
                else "governed_learning_idempotent_existing_memory"
            ,),
            approval=approval,
            materialization=materialization,
            write_request=request,
            stored_memory_ids=memory_ids,
            writer_call_performed=True,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().casefold().split())

    def _non_approved(
        self,
        approval: HumanLearningApprovalReport,
    ) -> ProductiveGovernedLearningResult:
        mapping = {
            HumanLearningApprovalOutcome.REJECTED: (
                ProductiveGovernedLearningOutcome.REJECTED,
                "explicit_human_learning_rejection",
            ),
            HumanLearningApprovalOutcome.DEFERRED: (
                ProductiveGovernedLearningOutcome.DEFERRED,
                "explicit_human_learning_deferral",
            ),
            HumanLearningApprovalOutcome.UNCLEAR: (
                ProductiveGovernedLearningOutcome.UNCLEAR,
                "human_learning_approval_unclear",
            ),
            HumanLearningApprovalOutcome.ABSTAIN: (
                ProductiveGovernedLearningOutcome.ABSTAIN,
                "human_learning_approval_abstained",
            ),
        }
        outcome, rationale = mapping[approval.outcome]
        return self._result(outcome, (rationale,), approval=approval)

    @staticmethod
    def _result(
        outcome: ProductiveGovernedLearningOutcome,
        rationale: tuple[str, ...],
        *,
        approval: HumanLearningApprovalReport | None = None,
        materialization: ApprovedLearningMemoryMaterializationReport | None = None,
        write_request: GovernedMemoryWriteRequest | None = None,
        stored_memory_ids: tuple[str, ...] = (),
        writer_call_performed: bool = False,
    ) -> ProductiveGovernedLearningResult:
        return ProductiveGovernedLearningResult(
            outcome=outcome,
            rationale_codes=rationale,
            approval=approval,
            materialization=materialization,
            write_request=write_request,
            stored_memory_ids=stored_memory_ids,
            writer_call_performed=writer_call_performed,
        )
