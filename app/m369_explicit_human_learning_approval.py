from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from .approved_learning_memory_materialization import (
    ApprovedLearningEvidence,
    ApprovedLearningScope,
)
from .approved_learning_memory_write_adapter import GovernedMemoryWriteRequest
from .curiosity_m369_learning_evaluation import (
    CuriosityLearningKind,
    CuriosityM369EvaluationOutcome,
    CuriosityM369LearningEvaluationReport,
)
from .governed_knowledge_revision_proposal import GovernedKnowledgeRevisionProposal


class HumanLearningApprovalOutcome(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    UNCLEAR = "unclear"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class ExplicitHumanLearningApprovalResponse:
    approval_request_id: str
    evaluation_report_id: str
    learning_candidate_id: str
    preference_candidate_id: str
    human_response_reference: str
    response_text: str
    approver: str
    scope: ApprovedLearningScope
    exact_linkage: bool = True
    learning_kind: CuriosityLearningKind = CuriosityLearningKind.PREFERENCE

    def __post_init__(self) -> None:
        required = (
            self.approval_request_id,
            self.evaluation_report_id,
            self.learning_candidate_id,
            self.preference_candidate_id,
            self.human_response_reference,
            self.response_text,
            self.approver,
        )
        if any(not value.strip() for value in required):
            raise ValueError("human learning approval requires complete provenance")


@dataclass(frozen=True)
class ExplicitHumanKnowledgeRevisionApprovalResponse:
    approval_request_id: str
    revision_proposal_id: str
    human_response_reference: str
    response_text: str
    approver: str
    exact_linkage: bool = True

    def __post_init__(self) -> None:
        required = (
            self.approval_request_id,
            self.revision_proposal_id,
            self.human_response_reference,
            self.response_text,
            self.approver,
        )
        if any(not value.strip() for value in required):
            raise ValueError("human revision approval requires complete provenance")


@dataclass(frozen=True)
class ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse:
    authorization_request_id: str
    memory_write_request_id: str
    human_response_reference: str
    response_text: str
    approver: str
    exact_linkage: bool = True

    def __post_init__(self) -> None:
        required = (
            self.authorization_request_id,
            self.memory_write_request_id,
            self.human_response_reference,
            self.response_text,
            self.approver,
        )
        if any(not value.strip() for value in required):
            raise ValueError(
                "human memory write execution authorization requires "
                "complete provenance"
            )


@dataclass(frozen=True)
class AuthorizedGovernedMemoryWriteExecutionEvidence:
    authorization_id: str
    memory_write_request_id: str
    materialization_proposal_id: str
    idempotency_key: str
    writer_authority: str
    writer_component: str
    writer_method: str
    human_response_reference: str
    approver: str
    execution_authorization_fingerprint: str
    read_only: bool = True
    write_performed: bool = False
    memory_persisted: bool = False
    memory_created: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.authorization_id,
            self.memory_write_request_id,
            self.materialization_proposal_id,
            self.idempotency_key,
            self.writer_authority,
            self.writer_component,
            self.writer_method,
            self.human_response_reference,
            self.approver,
            self.execution_authorization_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError(
                "memory write execution authorization requires complete provenance"
            )
        if (
            self.writer_authority != "memory_gateway"
            or self.writer_component != "OfficialMemoryGateway"
            or self.writer_method != "remember_governed_learning"
        ):
            raise ValueError(
                "memory write execution authorization must preserve official writer"
            )
        if not self.read_only or any(
            (
                self.write_performed,
                self.memory_persisted,
                self.memory_created,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError(
                "memory write execution authorization evidence must remain inert"
            )


@dataclass(frozen=True)
class ExplicitHumanKnowledgeRevisionExecutionAuthorizationResponse:
    authorization_request_id: str
    revision_request_id: str
    human_response_reference: str
    response_text: str
    approver: str
    exact_linkage: bool = True

    def __post_init__(self) -> None:
        required = (
            self.authorization_request_id,
            self.revision_request_id,
            self.human_response_reference,
            self.response_text,
            self.approver,
        )
        if any(not value.strip() for value in required):
            raise ValueError(
                "human revision execution authorization requires complete provenance"
            )


@dataclass(frozen=True)
class AuthorizedKnowledgeRevisionExecutionEvidence:
    authorization_id: str
    revision_request_id: str
    application_proposal_id: str
    revision_approval_id: str
    revision_proposal_id: str
    target_memory_id: str
    target_owner: str
    expected_target_fingerprint: str
    replacement_idempotency_key: str
    human_response_reference: str
    approver: str
    execution_authorization_fingerprint: str
    read_only: bool = True
    write_performed: bool = False
    replacement_persisted: bool = False
    supersession_applied: bool = False
    memory_modified: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.authorization_id,
            self.revision_request_id,
            self.application_proposal_id,
            self.revision_approval_id,
            self.revision_proposal_id,
            self.target_memory_id,
            self.target_owner,
            self.expected_target_fingerprint,
            self.replacement_idempotency_key,
            self.human_response_reference,
            self.approver,
            self.execution_authorization_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("execution authorization requires complete provenance")
        if not self.read_only or any(
            (
                self.write_performed,
                self.replacement_persisted,
                self.supersession_applied,
                self.memory_modified,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("execution authorization evidence must remain inert")


@dataclass(frozen=True)
class ApprovedKnowledgeRevisionEvidence:
    approval_id: str
    revision_proposal_id: str
    target_memory_id: str
    target_category: str
    current_content: str
    proposed_content: str
    corrective_evidence_ids: tuple[str, ...]
    revision_proposal_fingerprint: str
    human_response_reference: str
    approver: str
    human_approval_fingerprint: str
    read_only: bool = True
    writes_memory: bool = False
    modifies_knowledge: bool = False
    applies_revision: bool = False
    archives_memory: bool = False
    supersedes_memory: bool = False
    persists_replacement: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.approval_id,
            self.revision_proposal_id,
            self.target_memory_id,
            self.target_category,
            self.current_content,
            self.proposed_content,
            self.revision_proposal_fingerprint,
            self.human_response_reference,
            self.approver,
            self.human_approval_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("approved revision evidence requires complete provenance")
        if not self.corrective_evidence_ids:
            raise ValueError("approved revision evidence requires corrective evidence")
        if not self.read_only or any(
            (
                self.writes_memory,
                self.modifies_knowledge,
                self.applies_revision,
                self.archives_memory,
                self.supersedes_memory,
                self.persists_replacement,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("approved revision evidence violates governed limits")


@dataclass(frozen=True)
class HumanLearningApprovalReport:
    report_id: str
    outcome: HumanLearningApprovalOutcome
    evaluation_report_id: str
    learning_candidate_id: str
    preference_candidate_id: str
    approval_request_id: str
    human_response_reference: str
    approver: str
    scope: ApprovedLearningScope
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    approved_evidence: ApprovedLearningEvidence | None = None
    schema_version: str = "post-m409.1-m369-human-learning-approval-v1"
    read_only: bool = True
    persists_results: bool = False
    writes_learning: bool = False
    writes_memory: bool = False
    modifies_knowledge: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("m369-human-learning-approval-"):
            raise ValueError("human learning approval report identifier is invalid")
        if not self.rationale_codes:
            raise ValueError("human learning approval report requires rationale")
        approved = self.outcome is HumanLearningApprovalOutcome.APPROVED
        if (self.approved_evidence is not None) is not approved:
            raise ValueError("approved evidence presence must match approval outcome")
        if not self.read_only or any(
            (
                self.persists_results,
                self.writes_learning,
                self.writes_memory,
                self.modifies_knowledge,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("human learning approval violates governed limits")


class M369ExplicitHumanLearningApprovalEvidenceFoundation:
    """Interpret only bounded explicit approval replies with exact M369 linkage."""

    _APPROVED = {
        "si",
        "sí",
        "si, aprendelo",
        "sí, aprendelo",
        "si, recordalo",
        "sí, recordalo",
        "de acuerdo",
        "aprobado",
    }
    _REJECTED = {
        "no",
        "no, no lo aprendas",
        "no lo aprendas",
        "no, no lo recuerdes",
        "rechazado",
    }
    _DEFERRED = {
        "despues",
        "después",
        "mas tarde",
        "más tarde",
        "luego",
        "despues vemos",
        "después vemos",
    }
    _UNCLEAR = {
        "puede ser",
        "quizas",
        "quizás",
        "tal vez",
        "creo que si",
        "creo que sí",
        "puede que si",
        "puede que sí",
    }

    def classify_explicit_response(
        self, response_text: str
    ) -> HumanLearningApprovalOutcome:
        """Classify an explicit reply using the existing M369 approval vocabulary."""
        normalized = self._normalize(response_text)
        if normalized in self._APPROVED:
            return HumanLearningApprovalOutcome.APPROVED
        if normalized in self._REJECTED:
            return HumanLearningApprovalOutcome.REJECTED
        if normalized in self._DEFERRED:
            return HumanLearningApprovalOutcome.DEFERRED
        if normalized in self._UNCLEAR:
            return HumanLearningApprovalOutcome.UNCLEAR
        return HumanLearningApprovalOutcome.ABSTAIN

    def evaluate(
        self,
        evaluation: CuriosityM369LearningEvaluationReport,
        response: ExplicitHumanLearningApprovalResponse,
    ) -> HumanLearningApprovalReport:
        fingerprint = self._fingerprint(evaluation, response)
        if not self._exactly_linked(evaluation, response):
            return self._report(
                response,
                fingerprint,
                HumanLearningApprovalOutcome.ABSTAIN,
                ("exact_learning_approval_linkage_required",),
            )
        if evaluation.outcome is not CuriosityM369EvaluationOutcome.REVIEW_REQUIRED:
            return self._report(
                response,
                fingerprint,
                HumanLearningApprovalOutcome.ABSTAIN,
                ("m369_review_required_source_required",),
            )
        decision = evaluation.safe_learning_decision
        if decision is None or not decision.review_authorized:
            return self._report(
                response,
                fingerprint,
                HumanLearningApprovalOutcome.ABSTAIN,
                ("m369_review_authorization_required",),
            )

        outcome = self.classify_explicit_response(response.response_text)
        if outcome is HumanLearningApprovalOutcome.APPROVED:
            return self._approved_report(evaluation, response, fingerprint)
        if outcome is HumanLearningApprovalOutcome.REJECTED:
            return self._report(
                response,
                fingerprint,
                outcome,
                ("explicit_human_learning_rejection",),
            )
        if outcome is HumanLearningApprovalOutcome.DEFERRED:
            return self._report(
                response,
                fingerprint,
                outcome,
                ("explicit_human_learning_deferral",),
            )
        if outcome is HumanLearningApprovalOutcome.UNCLEAR:
            return self._report(
                response,
                fingerprint,
                outcome,
                ("human_learning_response_not_explicit_enough",),
            )
        return self._report(
            response,
            fingerprint,
            HumanLearningApprovalOutcome.ABSTAIN,
            ("unsupported_or_non_explicit_learning_approval_response",),
        )

    def evaluate_revision(
        self,
        proposal: GovernedKnowledgeRevisionProposal,
        response: ExplicitHumanKnowledgeRevisionApprovalResponse,
    ) -> ApprovedKnowledgeRevisionEvidence | None:
        if not (
            response.exact_linkage
            and proposal.review_required
            and response.revision_proposal_id == proposal.proposal_id
        ):
            return None
        if self.classify_explicit_response(response.response_text) is not (
            HumanLearningApprovalOutcome.APPROVED
        ):
            return None

        fingerprint = sha256(
            repr(
                (
                    proposal.source_fingerprint,
                    proposal.proposal_id,
                    response.approval_request_id,
                    response.revision_proposal_id,
                    response.human_response_reference,
                    response.response_text,
                    response.approver,
                    response.exact_linkage,
                )
            ).encode("utf-8")
        ).hexdigest()
        return ApprovedKnowledgeRevisionEvidence(
            approval_id=f"m369-human-revision-approved-{fingerprint[:16]}",
            revision_proposal_id=proposal.proposal_id,
            target_memory_id=proposal.target_memory_id,
            target_category=proposal.target_category,
            current_content=proposal.current_content,
            proposed_content=proposal.proposed_content,
            corrective_evidence_ids=proposal.corrective_evidence_ids,
            revision_proposal_fingerprint=proposal.source_fingerprint,
            human_response_reference=response.human_response_reference,
            approver=response.approver,
            human_approval_fingerprint=fingerprint,
        )

    def evaluate_governed_memory_write_execution_authorization(
        self,
        request: GovernedMemoryWriteRequest,
        response: ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
    ) -> AuthorizedGovernedMemoryWriteExecutionEvidence | None:
        """Authorize one exact governed Memory write request without executing it."""
        if not (
            response.exact_linkage
            and response.memory_write_request_id == request.request_id
            and request.read_only
            and not request.write_performed
            and not request.persists_results
            and not request.creates_memory
            and not request.executes_actions
            and not request.grants_authority
            and request.writer_authority == "memory_gateway"
            and request.writer_component == "OfficialMemoryGateway"
            and request.writer_method == "remember_governed_learning"
        ):
            return None

        normalized = self._normalize(response.response_text)
        if normalized not in {
            "si, guardar ahora",
            "sí, guardar ahora",
            "autorizo guardar esta memoria",
            "autorizo guardar este aprendizaje",
            "proceder con este request",
            "si, ejecutar esta escritura",
            "sí, ejecutar esta escritura",
        }:
            return None

        fingerprint = sha256(
            repr(
                (
                    request.request_id,
                    request.materialization_proposal_id,
                    request.idempotency_key,
                    request.writer_authority,
                    request.writer_component,
                    request.writer_method,
                    response.authorization_request_id,
                    response.human_response_reference,
                    response.response_text,
                    response.approver,
                    response.exact_linkage,
                )
            ).encode("utf-8")
        ).hexdigest()
        return AuthorizedGovernedMemoryWriteExecutionEvidence(
            authorization_id=(
                f"m369-human-memory-write-execution-authorized-{fingerprint[:16]}"
            ),
            memory_write_request_id=request.request_id,
            materialization_proposal_id=request.materialization_proposal_id,
            idempotency_key=request.idempotency_key,
            writer_authority=request.writer_authority,
            writer_component=request.writer_component,
            writer_method=request.writer_method,
            human_response_reference=response.human_response_reference,
            approver=response.approver,
            execution_authorization_fingerprint=fingerprint,
        )

    def evaluate_revision_execution_authorization(
        self,
        request,
        response: ExplicitHumanKnowledgeRevisionExecutionAuthorizationResponse,
    ) -> AuthorizedKnowledgeRevisionExecutionEvidence | None:
        """Authorize applying one exact certified G16 request, without executing it."""
        if not (
            response.exact_linkage
            and response.revision_request_id == request.request_id
            and request.read_only
            and not request.write_performed
            and not request.replacement_persisted
            and not request.supersession_applied
            and not request.memory_modified
            and not request.executes_actions
            and not request.grants_authority
        ):
            return None
        normalized = self._normalize(response.response_text)
        if normalized not in {
            "si, aplicar ahora",
            "sí, aplicar ahora",
            "autorizo aplicar esta revision",
            "autorizo aplicar esta revisión",
            "proceder con este request",
            "si, ejecutar esta revision",
            "sí, ejecutar esta revisión",
        }:
            return None

        fingerprint = sha256(
            repr(
                (
                    request.request_id,
                    request.application_proposal_id,
                    request.revision_approval_id,
                    request.revision_proposal_id,
                    request.target_memory_id,
                    request.target_owner,
                    request.expected_target_fingerprint,
                    request.replacement_idempotency_key,
                    response.authorization_request_id,
                    response.human_response_reference,
                    response.response_text,
                    response.approver,
                    response.exact_linkage,
                )
            ).encode("utf-8")
        ).hexdigest()
        return AuthorizedKnowledgeRevisionExecutionEvidence(
            authorization_id=(
                f"m369-human-revision-execution-authorized-{fingerprint[:16]}"
            ),
            revision_request_id=request.request_id,
            application_proposal_id=request.application_proposal_id,
            revision_approval_id=request.revision_approval_id,
            revision_proposal_id=request.revision_proposal_id,
            target_memory_id=request.target_memory_id,
            target_owner=request.target_owner,
            expected_target_fingerprint=request.expected_target_fingerprint,
            replacement_idempotency_key=request.replacement_idempotency_key,
            human_response_reference=response.human_response_reference,
            approver=response.approver,
            execution_authorization_fingerprint=fingerprint,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().casefold().strip(" .!?¿¡").split())

    @staticmethod
    def _exactly_linked(
        evaluation: CuriosityM369LearningEvaluationReport,
        response: ExplicitHumanLearningApprovalResponse,
    ) -> bool:
        typed_candidate = evaluation.preference_candidate
        typed_candidate_id = (
            typed_candidate.preference_id if typed_candidate is not None else ""
        )
        return bool(
            response.exact_linkage
            and evaluation.learning_candidate_id
            and typed_candidate is not None
            and response.evaluation_report_id == evaluation.report_id
            and response.learning_candidate_id == evaluation.learning_candidate_id
            and response.preference_candidate_id == typed_candidate_id
        )

    def _approved_report(
        self,
        evaluation: CuriosityM369LearningEvaluationReport,
        response: ExplicitHumanLearningApprovalResponse,
        fingerprint: str,
    ) -> HumanLearningApprovalReport:
        approval_id = f"m369-human-learning-approved-{fingerprint[:16]}"
        evidence = ApprovedLearningEvidence(
            approval_id=approval_id,
            evaluation_report_id=evaluation.report_id,
            learning_candidate_id=response.learning_candidate_id,
            preference_candidate_id=response.preference_candidate_id,
            human_response_reference=response.human_response_reference,
            approver=response.approver,
            scope=response.scope,
            source_fingerprint=fingerprint,
            learning_kind=response.learning_kind,
        )
        return self._report(
            response,
            fingerprint,
            HumanLearningApprovalOutcome.APPROVED,
            ("explicit_human_learning_approval", "exact_m369_linkage_preserved"),
            evidence,
        )

    @staticmethod
    def _fingerprint(
        evaluation: CuriosityM369LearningEvaluationReport,
        response: ExplicitHumanLearningApprovalResponse,
    ) -> str:
        return sha256(
            repr(
                (
                    evaluation.source_fingerprint,
                    evaluation.report_id,
                    response.approval_request_id,
                    response.evaluation_report_id,
                    response.learning_candidate_id,
                    response.preference_candidate_id,
                    response.human_response_reference,
                    response.response_text,
                    response.approver,
                    response.scope.value,
                    response.exact_linkage,
                )
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _report(
        response: ExplicitHumanLearningApprovalResponse,
        fingerprint: str,
        outcome: HumanLearningApprovalOutcome,
        rationale: tuple[str, ...],
        evidence: ApprovedLearningEvidence | None = None,
    ) -> HumanLearningApprovalReport:
        return HumanLearningApprovalReport(
            report_id=f"m369-human-learning-approval-{fingerprint[:16]}",
            outcome=outcome,
            evaluation_report_id=response.evaluation_report_id,
            learning_candidate_id=response.learning_candidate_id,
            preference_candidate_id=response.preference_candidate_id,
            approval_request_id=response.approval_request_id,
            human_response_reference=response.human_response_reference,
            approver=response.approver,
            scope=response.scope,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
            approved_evidence=evidence,
        )
