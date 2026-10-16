from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.bounded_situational_hypothesis import (
    BoundedSituationalHypothesisKind,
    BoundedSituationalHypothesisStatus,
    GovernedBoundedSituationalHypothesis,
)
from core.governed_reasoning.claims import Claim, ClaimOrigin, ClaimStatus, ClaimType

_SCHEMA_VERSION = "cih-2o-situational-hypothesis-transient-claim-projection-v1"


class SituationalHypothesisTransientClaimProjectionStatus(StrEnum):
    PROJECTED = "projected"
    INSUFFICIENT = "insufficient"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class GovernedSituationalHypothesisTransientClaimProjection:
    status: SituationalHypothesisTransientClaimProjectionStatus | str
    claim: Claim | None
    source_hypothesis_id: str
    source_hypothesis_fingerprint: str
    source_grouping_fingerprint: str
    source_projection_fingerprint: str
    source_claim_ids: tuple[str, ...]
    semantic_support_claim_ids: tuple[str, ...]
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    transient: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_claims: bool = True
    registers_claims: bool = False
    creates_evidence: bool = False
    registers_evidence: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    establishes_causality: bool = False
    infers_intent: bool = False
    infers_need: bool = False
    infers_priority: bool = False
    infers_action: bool = False
    registers_rules: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False
    authorizes_inference: bool = False
    authorizes_action: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        status = SituationalHypothesisTransientClaimProjectionStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "situational claim projection must preserve reasoning authority"
            )
        if not self.source_hypothesis_id.strip():
            raise ValueError(
                "situational claim projection requires hypothesis identity"
            )
        if any(
            len(value) != 64
            for value in (
                self.source_hypothesis_fingerprint,
                self.source_grouping_fingerprint,
                self.source_projection_fingerprint,
                self.source_fingerprint,
            )
        ):
            raise ValueError(
                "situational claim projection fingerprints must be SHA-256"
            )
        if not self.rationale_codes:
            raise ValueError("situational claim projection requires rationale")
        if any(
            (
                not self.read_only,
                not self.session_local,
                not self.transient,
                not self.consultative,
                self.persists_results,
                not self.creates_claims,
                self.registers_claims,
                self.creates_evidence,
                self.registers_evidence,
                self.establishes_truth,
                self.establishes_falsity,
                self.establishes_causality,
                self.infers_intent,
                self.infers_need,
                self.infers_priority,
                self.infers_action,
                self.registers_rules,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_world_model,
                self.modifies_planning,
                self.uses_provider,
                self.uses_retrieval,
                self.authorizes_inference,
                self.authorizes_action,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("situational claim projection violates governed limits")
        if status is SituationalHypothesisTransientClaimProjectionStatus.PROJECTED:
            if self.claim is None:
                raise ValueError("projected situational hypothesis requires one claim")
            if self.claim.normalized_type is not ClaimType.HYPOTHESIS:
                raise ValueError(
                    "situational projection claim must remain a hypothesis"
                )
            if self.claim.normalized_origin is not ClaimOrigin.SYSTEM:
                raise ValueError("situational projection claim must have system origin")
            if self.claim.normalized_status is not ClaimStatus.PROPOSED:
                raise ValueError("situational projection claim must remain proposed")
        elif self.claim is not None:
            raise ValueError("non-projected situational result cannot expose a claim")
        object.__setattr__(self, "status", status)


class GovernedSituationalHypothesisTransientClaimProjector:
    """Project one bounded situational hypothesis into one transient Claim object."""

    def project(
        self,
        *,
        hypothesis: GovernedBoundedSituationalHypothesis,
        owner: str,
        created_at: datetime,
    ) -> GovernedSituationalHypothesisTransientClaimProjection:
        if not owner.strip():
            raise ValueError("situational claim projection owner must not be blank")
        if created_at.tzinfo is None:
            raise ValueError(
                "situational claim projection timestamp must be timezone-aware"
            )
        if hypothesis.status is not BoundedSituationalHypothesisStatus.FORMED:
            return self._result(
                hypothesis=hypothesis,
                status=self._status_for(hypothesis.status),
            )
        if (
            hypothesis.canonical_authority != "governed_reasoning"
            or hypothesis.situational_kind
            is not BoundedSituationalHypothesisKind.ORGANIZATION_RELATED
            or hypothesis.establishes_truth
            or hypothesis.establishes_falsity
            or hypothesis.establishes_causality
            or hypothesis.authorizes_inference
            or hypothesis.authorizes_action
            or hypothesis.executes_actions
            or hypothesis.grants_authority
        ):
            return self._result(
                hypothesis=hypothesis,
                status=SituationalHypothesisTransientClaimProjectionStatus.UNSUPPORTED,
            )
        claim_id = self._claim_id(hypothesis.source_fingerprint, owner)
        claim = Claim(
            subject="current_turn_situation",
            predicate="may_be",
            object_value="organization_related",
            claim_type=ClaimType.HYPOTHESIS,
            origin=ClaimOrigin.SYSTEM,
            status=ClaimStatus.PROPOSED,
            evidence_links=(),
            confidence=None,
            owner=owner,
            rule_reference=None,
            supersedes=None,
            valid_from=None,
            valid_until=None,
            created_at=created_at,
            claim_id=claim_id,
        )
        return self._result(
            hypothesis=hypothesis,
            status=SituationalHypothesisTransientClaimProjectionStatus.PROJECTED,
            claim=claim,
            rationale_codes=(
                "situational_claim_projection:formed_hypothesis",
                "situational_claim_projection:modal_semantics_preserved",
                "situational_claim_projection:system_hypothesis",
                "situational_claim_projection:transient_only",
                "situational_claim_projection:no_evidence_created",
                "situational_claim_projection:no_rule_created",
                "situational_claim_projection:no_truth_promotion",
                "situational_claim_projection:no_inference_authorized",
            ),
        )

    @staticmethod
    def _status_for(
        status: BoundedSituationalHypothesisStatus,
    ) -> SituationalHypothesisTransientClaimProjectionStatus:
        return {
            BoundedSituationalHypothesisStatus.INSUFFICIENT: (
                SituationalHypothesisTransientClaimProjectionStatus.INSUFFICIENT
            ),
            BoundedSituationalHypothesisStatus.AMBIGUOUS: (
                SituationalHypothesisTransientClaimProjectionStatus.AMBIGUOUS
            ),
            BoundedSituationalHypothesisStatus.UNSUPPORTED: (
                SituationalHypothesisTransientClaimProjectionStatus.UNSUPPORTED
            ),
        }[status]

    @staticmethod
    def _claim_id(hypothesis_fingerprint: str, owner: str) -> str:
        payload = "|".join(
            (
                _SCHEMA_VERSION,
                hypothesis_fingerprint,
                owner.strip().casefold(),
                "current_turn_situation",
                "may_be",
                "organization_related",
            )
        )
        return (
            "situational-hypothesis-claim-"
            + sha256(payload.encode("utf-8")).hexdigest()
        )

    @staticmethod
    def _result(
        *,
        hypothesis: GovernedBoundedSituationalHypothesis,
        status: SituationalHypothesisTransientClaimProjectionStatus,
        claim: Claim | None = None,
        rationale_codes: tuple[str, ...] = (),
    ) -> GovernedSituationalHypothesisTransientClaimProjection:
        if not rationale_codes:
            rationale_codes = (f"situational_claim_projection:{status.value}",)
        payload = (
            _SCHEMA_VERSION,
            status.value,
            hypothesis.hypothesis_id,
            hypothesis.source_fingerprint,
            hypothesis.source_grouping_fingerprint,
            hypothesis.source_projection_fingerprint,
            hypothesis.source_claim_ids,
            hypothesis.semantic_support_claim_ids,
            claim.claim_id if claim else None,
            claim.fingerprint if claim else None,
            rationale_codes,
        )
        return GovernedSituationalHypothesisTransientClaimProjection(
            status=status,
            claim=claim,
            source_hypothesis_id=hypothesis.hypothesis_id,
            source_hypothesis_fingerprint=hypothesis.source_fingerprint,
            source_grouping_fingerprint=hypothesis.source_grouping_fingerprint,
            source_projection_fingerprint=hypothesis.source_projection_fingerprint,
            source_claim_ids=hypothesis.source_claim_ids,
            semantic_support_claim_ids=hypothesis.semantic_support_claim_ids,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
