from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .governed_knowledge_revision_application_proposal import (
    GovernedKnowledgeRevisionApplicationProposal,
)


@dataclass(frozen=True)
class GovernedKnowledgeRevisionRequest:
    """Certified inert request for the existing official Memory authority."""

    request_id: str
    application_proposal_id: str
    revision_approval_id: str
    revision_proposal_id: str
    target_memory_id: str
    target_owner: str
    target_category: str
    expected_current_content: str
    replacement_content: str
    corrective_evidence_ids: tuple[str, ...]
    revision_proposal_fingerprint: str
    human_approval_fingerprint: str
    application_proposal_fingerprint: str
    expected_target_fingerprint: str
    replacement_idempotency_key: str
    writer_authority: str = "memory_gateway"
    writer_component: str = "OfficialMemoryGateway"
    writer_method: str = "apply_governed_knowledge_revision"
    schema_version: str = "intel-g16-governed-knowledge-revision-request-v1"
    requires_official_memory_gateway: bool = True
    requires_atomic_revision: bool = True
    preserves_prior_version: bool = True
    read_only: bool = True
    write_performed: bool = False
    replacement_persisted: bool = False
    supersession_applied: bool = False
    memory_modified: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.request_id,
            self.application_proposal_id,
            self.revision_approval_id,
            self.revision_proposal_id,
            self.target_memory_id,
            self.target_owner,
            self.target_category,
            self.expected_current_content,
            self.replacement_content,
            self.revision_proposal_fingerprint,
            self.human_approval_fingerprint,
            self.application_proposal_fingerprint,
            self.expected_target_fingerprint,
            self.replacement_idempotency_key,
        )
        if any(not value.strip() for value in required):
            raise ValueError("revision request requires complete governed lineage")
        if not self.request_id.startswith("governed-knowledge-revision-request-"):
            raise ValueError("revision request identifier is invalid")
        if not self.application_proposal_id.startswith(
            "governed-knowledge-revision-application-proposal-"
        ):
            raise ValueError("revision request requires G15 application proposal")
        if not self.corrective_evidence_ids:
            raise ValueError("revision request requires corrective evidence")
        if len(self.corrective_evidence_ids) != len(set(self.corrective_evidence_ids)):
            raise ValueError("revision request evidence ids must be unique")
        if any(not item.strip() for item in self.corrective_evidence_ids):
            raise ValueError("revision request evidence ids must not be blank")
        if self.expected_current_content.strip() == self.replacement_content.strip():
            raise ValueError("revision request requires changed replacement content")
        for fingerprint in (
            self.revision_proposal_fingerprint,
            self.human_approval_fingerprint,
            self.application_proposal_fingerprint,
            self.expected_target_fingerprint,
        ):
            if len(fingerprint) != 64:
                raise ValueError("revision request fingerprints must be SHA-256")
        if not self.replacement_idempotency_key.startswith(
            "knowledge-revision-replacement-"
        ):
            raise ValueError("revision request requires replacement idempotency")
        if self.writer_authority != "memory_gateway":
            raise ValueError("revision request must preserve Memory authority")
        if self.writer_component != "OfficialMemoryGateway":
            raise ValueError("revision request must target OfficialMemoryGateway")
        if self.writer_method != "apply_governed_knowledge_revision":
            raise ValueError("revision request must target governed revision method")
        if not all(
            (
                self.requires_official_memory_gateway,
                self.requires_atomic_revision,
                self.preserves_prior_version,
                self.read_only,
            )
        ):
            raise ValueError("revision request must preserve governed boundaries")
        if any(
            (
                self.write_performed,
                self.replacement_persisted,
                self.supersession_applied,
                self.memory_modified,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("certified revision request must remain inert")


class GovernedKnowledgeRevisionRequestFoundation:
    """Certify G15 application intent without executing a Memory revision."""

    def certify(
        self,
        proposal: GovernedKnowledgeRevisionApplicationProposal,
    ) -> GovernedKnowledgeRevisionRequest:
        self._validate_proposal(proposal)

        target_fingerprint = sha256(
            repr(
                (
                    proposal.target_owner,
                    proposal.target_memory_id,
                    proposal.target_category,
                    proposal.current_content,
                )
            ).encode("utf-8")
        ).hexdigest()

        replacement_digest = sha256(
            repr(
                (
                    proposal.proposal_id,
                    proposal.source_fingerprint,
                    target_fingerprint,
                    proposal.replacement_content,
                )
            ).encode("utf-8")
        ).hexdigest()
        replacement_idempotency_key = (
            f"knowledge-revision-replacement-{replacement_digest}"
        )

        request_digest = sha256(
            repr(
                (
                    proposal.proposal_id,
                    proposal.revision_approval_id,
                    proposal.revision_proposal_id,
                    proposal.source_fingerprint,
                    target_fingerprint,
                    replacement_idempotency_key,
                )
            ).encode("utf-8")
        ).hexdigest()

        return GovernedKnowledgeRevisionRequest(
            request_id=f"governed-knowledge-revision-request-{request_digest[:16]}",
            application_proposal_id=proposal.proposal_id,
            revision_approval_id=proposal.revision_approval_id,
            revision_proposal_id=proposal.revision_proposal_id,
            target_memory_id=proposal.target_memory_id,
            target_owner=proposal.target_owner,
            target_category=proposal.target_category,
            expected_current_content=proposal.current_content,
            replacement_content=proposal.replacement_content,
            corrective_evidence_ids=proposal.corrective_evidence_ids,
            revision_proposal_fingerprint=proposal.revision_proposal_fingerprint,
            human_approval_fingerprint=proposal.human_approval_fingerprint,
            application_proposal_fingerprint=proposal.source_fingerprint,
            expected_target_fingerprint=target_fingerprint,
            replacement_idempotency_key=replacement_idempotency_key,
        )

    @staticmethod
    def _validate_proposal(
        proposal: GovernedKnowledgeRevisionApplicationProposal,
    ) -> None:
        if proposal.canonical_memory_authority != "OfficialMemoryGateway":
            raise ValueError("G15 proposal targets wrong Memory authority")
        if not proposal.read_only:
            raise ValueError("G15 proposal must remain read-only")
        if any(
            (
                proposal.write_performed,
                proposal.replacement_persisted,
                proposal.supersession_applied,
                proposal.archive_performed,
                proposal.memory_modified,
                proposal.executes_actions,
                proposal.grants_authority,
            )
        ):
            raise ValueError("G15 proposal must be inert before certification")
