from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256

from core.cognitive_memory import LearningCategory
from core.memory import MemoryItem
from core.memory_consolidation_foundation import ConsolidationTarget

from .approved_learning_memory_materialization import (
    ApprovedLearningScope,
    GovernedMemoryMaterializationProposal,
)


@dataclass(frozen=True)
class GovernedMemoryWriteRequest:
    """Inert request prepared for the existing official memory writer."""

    request_id: str
    materialization_proposal_id: str
    memory_item: MemoryItem
    idempotency_key: str
    learning_category: LearningCategory = LearningCategory.USER_PREFERENCE
    structural_evidence_fingerprint: str = ""
    writer_authority: str = "memory_gateway"
    writer_component: str = "OfficialMemoryGateway"
    writer_method: str = "remember_governed_learning"
    schema_version: str = "post-m409.1-governed-memory-write-request-v1"
    semantic_mapping_supported: bool = True
    idempotent_write_supported: bool = True
    requires_official_memory_gateway: bool = True
    read_only: bool = True
    write_performed: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.request_id.startswith("governed-memory-write-request-"):
            raise ValueError("memory write request identifier is invalid")
        if not self.materialization_proposal_id.startswith(
            "approved-learning-memory-proposal-"
        ):
            raise ValueError(
                "write request requires a governed materialization proposal"
            )
        if not self.idempotency_key.startswith("memory-write-"):
            raise ValueError("memory write request requires idempotency identity")
        if not self.memory_item.content.strip():
            raise ValueError("memory write request content must not be blank")
        if self.writer_authority != "memory_gateway":
            raise ValueError("write request must preserve canonical memory authority")
        if self.writer_component != "OfficialMemoryGateway":
            raise ValueError("write request must target OfficialMemoryGateway")
        if self.writer_method != "remember_governed_learning":
            raise ValueError("write request must target governed learning writer")
        if not self.semantic_mapping_supported or not self.idempotent_write_supported:
            raise ValueError("write request requires certified writer guarantees")
        if not self.requires_official_memory_gateway or not self.read_only:
            raise ValueError("write request must preserve official writer boundary")
        if any(
            (
                self.write_performed,
                self.persists_results,
                self.creates_memory,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("write adapter request must remain inert")


class GovernedMemoryWriteAdapterFoundation:
    """Adapt a certified proposal to a write request without calling the writer."""

    def adapt(
        self,
        proposal: GovernedMemoryMaterializationProposal,
    ) -> GovernedMemoryWriteRequest:
        self._validate_proposal(proposal)
        self._validate_structural_eligibility(proposal)
        idempotency_digest = sha256(
            repr(
                (
                    proposal.proposal_id,
                    proposal.source_fingerprint,
                    proposal.approval_scope.value,
                    proposal.subject,
                    proposal.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        idempotency_key = f"memory-write-{idempotency_digest}"
        metadata = self._metadata(proposal, idempotency_key)
        request_digest = sha256(
            repr(
                (
                    proposal.source_fingerprint,
                    proposal.proposal_id,
                    proposal.value,
                    tuple(sorted(metadata.items())),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedMemoryWriteRequest(
            request_id=f"governed-memory-write-request-{request_digest[:16]}",
            materialization_proposal_id=proposal.proposal_id,
            memory_item=MemoryItem(
                content=proposal.value,
                metadata=metadata,
            ),
            idempotency_key=idempotency_key,
            learning_category=proposal.learning_category,
            structural_evidence_fingerprint=(
                proposal.structural_evidence_fingerprint
            ),
        )

    @staticmethod
    def _validate_structural_eligibility(
        proposal: GovernedMemoryMaterializationProposal,
    ) -> None:
        if proposal.learning_category is not LearningCategory.STABLE_KNOWLEDGE:
            return
        evidence = proposal.structural_eligibility
        if evidence is None or not evidence.supported:
            raise ValueError(
                "stable knowledge write requires structural eligibility"
            )
        if evidence.source_fingerprint != evidence.recompute_fingerprint():
            raise ValueError("structural eligibility fingerprint mismatch")
        if evidence.learned_content_fingerprint != sha256(
            proposal.value.encode("utf-8")
        ).hexdigest():
            raise ValueError("structural eligibility content mismatch")
        if evidence.evaluation_fingerprint != proposal.m369_evaluation_fingerprint:
            raise ValueError("structural eligibility evaluation mismatch")
        if evidence.learning_candidate_id != proposal.learning_candidate_id:
            raise ValueError("structural eligibility candidate mismatch")
        if evidence.scope_reference != proposal.approval_scope.value:
            raise ValueError("structural eligibility scope mismatch")
        if proposal.structural_evidence_fingerprint != evidence.source_fingerprint:
            raise ValueError("structural eligibility provenance mismatch")

    @staticmethod
    def _validate_proposal(
        proposal: GovernedMemoryMaterializationProposal,
    ) -> None:
        if proposal.approval_scope in {
            ApprovedLearningScope.SESSION,
            ApprovedLearningScope.UNSPECIFIED,
        }:
            raise ValueError("durable write request requires explicit durable scope")
        if proposal.target is not ConsolidationTarget.LONG_TERM:
            raise ValueError("write request requires long-term materialization target")
        if proposal.consolidation.persistence_performed:
            raise ValueError("write adapter cannot consume already-persisted proposal")
        if not proposal.requires_official_memory_gateway:
            raise ValueError("proposal must require the official memory gateway")
        if not proposal.read_only or proposal.writes_memory:
            raise ValueError("proposal must remain read-only before writer wiring")
        required = (
            proposal.proposal_id,
            proposal.learning_candidate_id,
            proposal.subject,
            proposal.value,
            proposal.approval_id,
            proposal.approver,
            proposal.human_response_reference,
            proposal.m369_evaluation_fingerprint,
            proposal.human_approval_fingerprint,
            proposal.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("write request requires complete proposal provenance")
        preference_lineage = proposal.preference_candidate_id.strip()
        policy_lineage = proposal.policy_candidate_id.strip()
        if bool(preference_lineage) == bool(policy_lineage):
            raise ValueError(
                "write request requires exactly one governed candidate lineage"
            )
        if not proposal.evidence_ids:
            raise ValueError("write request requires learning evidence lineage")

    @staticmethod
    def _metadata(
        proposal: GovernedMemoryMaterializationProposal,
        idempotency_key: str,
    ) -> dict[str, str]:
        metadata = {
            "source": "approved_learning_materialization",
            "learning_category": proposal.learning_category.value,
            "structural_evidence_fingerprint": (
                proposal.structural_evidence_fingerprint
            ),
            "subject": proposal.subject,
            "approval_scope": proposal.approval_scope.value,
            "confidence": format(proposal.confidence, ".17g"),
            "learning_candidate_id": proposal.learning_candidate_id,
            "materialization_proposal_id": proposal.proposal_id,
            "approval_id": proposal.approval_id,
            "approver": proposal.approver,
            "human_response_reference": proposal.human_response_reference,
            "m369_evaluation_fingerprint": proposal.m369_evaluation_fingerprint,
            "human_approval_fingerprint": proposal.human_approval_fingerprint,
            "evidence_ids": json.dumps(
                proposal.evidence_ids,
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            "materialization_source_fingerprint": proposal.source_fingerprint,
            "idempotency_key": idempotency_key,
            "writer_authority": "memory_gateway",
            "writer_component": "OfficialMemoryGateway",
            "writer_method": "remember_governed_learning",
            "semantic_mapping_supported": "true",
            "idempotent_write_supported": "true",
        }
        if proposal.policy_candidate_id.strip():
            metadata["policy_candidate_id"] = proposal.policy_candidate_id
        else:
            metadata["preference_candidate_id"] = (
                proposal.preference_candidate_id
            )
            metadata["learning_kind"] = proposal.learning_kind.value
        return metadata
