from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.cognitive_memory import LearningCategory
from core.cognitive_memory_store import CognitiveMemoryRecord
from core.governed_reasoning.evidence import EvidenceReference


@dataclass(frozen=True)
class GovernedKnowledgeRevisionProposal:
    """Inert proposal to review existing durable governed stable knowledge."""

    proposal_id: str
    target_memory_id: str
    target_category: str
    current_content: str
    proposed_content: str
    corrective_evidence_ids: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "intel-g13-governed-knowledge-revision-proposal-v1"
    canonical_memory_authority: str = "OfficialMemoryGateway"
    read_only: bool = True
    review_required: bool = True
    write_performed: bool = False
    approval_granted: bool = False
    applied: bool = False
    archives_memory: bool = False
    supersedes_memory: bool = False
    persists_replacement: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.proposal_id.startswith("governed-knowledge-revision-proposal-"):
            raise ValueError("revision proposal identifier is invalid")
        if not self.target_memory_id.strip():
            raise ValueError("revision proposal requires target memory identity")
        if self.target_category != LearningCategory.STABLE_KNOWLEDGE.value:
            raise ValueError("revision proposal requires durable stable knowledge")
        if not self.current_content.strip() or not self.proposed_content.strip():
            raise ValueError("revision proposal content must not be blank")
        if self.current_content.strip() == self.proposed_content.strip():
            raise ValueError("revision proposal must describe a content change")
        if not self.corrective_evidence_ids:
            raise ValueError("revision proposal requires corrective evidence")
        if len(self.corrective_evidence_ids) != len(set(self.corrective_evidence_ids)):
            raise ValueError("revision proposal evidence ids must be unique")
        if any(not item.strip() for item in self.corrective_evidence_ids):
            raise ValueError("revision proposal evidence ids must not be blank")
        if len(self.source_fingerprint) != 64:
            raise ValueError("revision proposal fingerprint must be SHA-256")
        if self.canonical_memory_authority != "OfficialMemoryGateway":
            raise ValueError(
                "revision proposal must preserve canonical memory authority"
            )
        if not self.read_only or not self.review_required:
            raise ValueError("revision proposal must remain inert and review-required")
        if any(
            (
                self.write_performed,
                self.approval_granted,
                self.applied,
                self.archives_memory,
                self.supersedes_memory,
                self.persists_replacement,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("revision proposal cannot approve, apply, persist, or act")


class GovernedKnowledgeRevisionProposalFoundation:
    """Propose revision without approving or mutating durable Memory."""

    def propose(
        self,
        target_memory: CognitiveMemoryRecord,
        corrective_evidence: tuple[EvidenceReference, ...],
        *,
        proposed_content: str,
    ) -> GovernedKnowledgeRevisionProposal:
        if target_memory.category is not LearningCategory.STABLE_KNOWLEDGE:
            raise ValueError("revision target must be stable knowledge")
        normalized_proposed = " ".join(proposed_content.strip().split())
        if not normalized_proposed:
            raise ValueError("proposed corrected content must not be blank")
        if not corrective_evidence:
            raise ValueError("revision proposal requires governed corrective evidence")

        evidence_ids = tuple(item.evidence_id for item in corrective_evidence)
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("corrective evidence must be unique")

        target_memory_id = str(target_memory.id)
        fingerprint = sha256(
            repr(
                (
                    target_memory_id,
                    target_memory.category.value,
                    target_memory.content,
                    normalized_proposed,
                    evidence_ids,
                    tuple(item.fingerprint for item in corrective_evidence),
                )
            ).encode("utf-8")
        ).hexdigest()

        return GovernedKnowledgeRevisionProposal(
            proposal_id=f"governed-knowledge-revision-proposal-{fingerprint[:16]}",
            target_memory_id=target_memory_id,
            target_category=target_memory.category.value,
            current_content=target_memory.content,
            proposed_content=normalized_proposed,
            corrective_evidence_ids=evidence_ids,
            source_fingerprint=fingerprint,
        )
