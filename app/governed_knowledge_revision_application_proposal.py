from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .m369_explicit_human_learning_approval import ApprovedKnowledgeRevisionEvidence


@dataclass(frozen=True)
class GovernedKnowledgeRevisionApplicationProposal:
    """Inert proposal describing a future governed Memory revision application."""

    proposal_id: str
    revision_approval_id: str
    revision_proposal_id: str
    target_memory_id: str
    target_owner: str
    target_category: str
    current_content: str
    replacement_content: str
    corrective_evidence_ids: tuple[str, ...]
    revision_proposal_fingerprint: str
    human_approval_fingerprint: str
    source_fingerprint: str
    schema_version: str = "intel-g15-governed-revision-application-proposal-v1"
    canonical_memory_authority: str = "OfficialMemoryGateway"
    read_only: bool = True
    write_performed: bool = False
    replacement_persisted: bool = False
    supersession_applied: bool = False
    archive_performed: bool = False
    memory_modified: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.proposal_id,
            self.revision_approval_id,
            self.revision_proposal_id,
            self.target_memory_id,
            self.target_owner,
            self.target_category,
            self.current_content,
            self.replacement_content,
            self.revision_proposal_fingerprint,
            self.human_approval_fingerprint,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("revision application proposal requires complete lineage")
        if not self.proposal_id.startswith(
            "governed-knowledge-revision-application-proposal-"
        ):
            raise ValueError("revision application proposal identifier is invalid")
        if not self.corrective_evidence_ids:
            raise ValueError(
                "revision application proposal requires corrective evidence"
            )
        if len(self.corrective_evidence_ids) != len(set(self.corrective_evidence_ids)):
            raise ValueError(
                "revision application proposal evidence ids must be unique"
            )
        if any(not item.strip() for item in self.corrective_evidence_ids):
            raise ValueError(
                "revision application proposal evidence ids must not be blank"
            )
        if self.current_content.strip() == self.replacement_content.strip():
            raise ValueError("revision application proposal requires changed content")
        for fingerprint in (
            self.revision_proposal_fingerprint,
            self.human_approval_fingerprint,
            self.source_fingerprint,
        ):
            if len(fingerprint) != 64:
                raise ValueError("revision application fingerprints must be SHA-256")
        if self.canonical_memory_authority != "OfficialMemoryGateway":
            raise ValueError(
                "revision application must preserve canonical Memory authority"
            )
        if not self.read_only or any(
            (
                self.write_performed,
                self.replacement_persisted,
                self.supersession_applied,
                self.archive_performed,
                self.memory_modified,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("revision application proposal must remain inert")


class GovernedKnowledgeRevisionApplicationProposalFoundation:
    """Describe approved revision application without mutating durable Memory."""

    def propose(
        self,
        approved_revision: ApprovedKnowledgeRevisionEvidence,
        *,
        owner: str,
    ) -> GovernedKnowledgeRevisionApplicationProposal:
        normalized_owner = " ".join(owner.strip().split())
        if not normalized_owner:
            raise ValueError("revision application proposal requires Memory owner")
        if not approved_revision.read_only:
            raise ValueError("revision application requires inert approved evidence")
        if any(
            (
                approved_revision.writes_memory,
                approved_revision.modifies_knowledge,
                approved_revision.applies_revision,
                approved_revision.archives_memory,
                approved_revision.supersedes_memory,
                approved_revision.persists_replacement,
                approved_revision.executes_actions,
                approved_revision.grants_authority,
            )
        ):
            raise ValueError("revision application requires non-mutating G14 evidence")

        fingerprint = sha256(
            repr(
                (
                    approved_revision.approval_id,
                    approved_revision.revision_proposal_id,
                    approved_revision.target_memory_id,
                    normalized_owner,
                    approved_revision.target_category,
                    approved_revision.current_content,
                    approved_revision.proposed_content,
                    approved_revision.corrective_evidence_ids,
                    approved_revision.revision_proposal_fingerprint,
                    approved_revision.human_approval_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()

        return GovernedKnowledgeRevisionApplicationProposal(
            proposal_id=(
                "governed-knowledge-revision-application-proposal-"
                f"{fingerprint[:16]}"
            ),
            revision_approval_id=approved_revision.approval_id,
            revision_proposal_id=approved_revision.revision_proposal_id,
            target_memory_id=approved_revision.target_memory_id,
            target_owner=normalized_owner,
            target_category=approved_revision.target_category,
            current_content=approved_revision.current_content,
            replacement_content=approved_revision.proposed_content,
            corrective_evidence_ids=approved_revision.corrective_evidence_ids,
            revision_proposal_fingerprint=(
                approved_revision.revision_proposal_fingerprint
            ),
            human_approval_fingerprint=approved_revision.human_approval_fingerprint,
            source_fingerprint=fingerprint,
        )
