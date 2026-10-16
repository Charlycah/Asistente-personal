from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.explicit_turn_transient_claim_projection import (
    ExplicitTurnTransientClaimProjectionStatus,
    GovernedExplicitTurnTransientClaimProjection,
)

_SCHEMA_VERSION = "cih-2k-explicit-turn-contextual-claim-grouping-v1"


class ExplicitTurnContextualGroupingStatus(StrEnum):
    GROUPED = "grouped"
    INSUFFICIENT = "insufficient"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    SCOPE_MISMATCH = "scope_mismatch"


class ExplicitTurnContextualRelation(StrEnum):
    CO_PRESENT_IN_CURRENT_TURN = "co_present_in_current_turn"


@dataclass(frozen=True)
class GovernedExplicitTurnContextualClaimGrouping:
    status: ExplicitTurnContextualGroupingStatus | str
    relation: ExplicitTurnContextualRelation | str | None
    member_claim_ids: tuple[str, ...]
    source_reference: str
    scope_reference: str
    source_grounding_fingerprint: str
    source_projection_fingerprint: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    transient: bool = True
    persists_results: bool = False
    creates_claims: bool = False
    registers_claims: bool = False
    registers_rule: bool = False
    creates_evidence: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    establishes_causality: bool = False
    infers_intent: bool = False
    infers_need: bool = False
    infers_priority: bool = False
    infers_goal: bool = False
    infers_action: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    authorizes_inference: bool = False
    authorizes_action: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        status = ExplicitTurnContextualGroupingStatus(self.status)
        relation = (
            None
            if self.relation is None
            else ExplicitTurnContextualRelation(self.relation)
        )
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "explicit-turn contextual grouping must preserve governed "
                "reasoning authority"
            )
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError(
                "explicit-turn contextual grouping requires provenance and scope"
            )
        fingerprints = (
            self.source_grounding_fingerprint,
            self.source_projection_fingerprint,
            self.source_fingerprint,
        )
        if any(len(item) != 64 for item in fingerprints):
            raise ValueError(
                "explicit-turn contextual grouping fingerprints must be SHA-256"
            )
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError(
                "explicit-turn contextual grouping requires rationale codes"
            )
        if any(
            (
                not self.read_only,
                not self.session_local,
                not self.transient,
                self.persists_results,
                self.creates_claims,
                self.registers_claims,
                self.registers_rule,
                self.creates_evidence,
                self.establishes_truth,
                self.establishes_falsity,
                self.establishes_causality,
                self.infers_intent,
                self.infers_need,
                self.infers_priority,
                self.infers_goal,
                self.infers_action,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_world_model,
                self.authorizes_inference,
                self.authorizes_action,
                self.uses_provider,
                self.uses_retrieval,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError(
                "explicit-turn contextual grouping violates governed limits"
            )
        if status is ExplicitTurnContextualGroupingStatus.GROUPED:
            if (
                relation
                is not ExplicitTurnContextualRelation.CO_PRESENT_IN_CURRENT_TURN
            ):
                raise ValueError(
                    "grouped explicit turn requires current-turn co-presence"
                )
            if len(self.member_claim_ids) < 2:
                raise ValueError("grouped explicit turn requires multiple claims")
            if any(not claim_id.strip() for claim_id in self.member_claim_ids):
                raise ValueError("grouped explicit turn requires valid claim ids")
            if len(set(self.member_claim_ids)) != len(self.member_claim_ids):
                raise ValueError("grouped explicit turn requires unique claim ids")
        elif relation is not None or self.member_claim_ids:
            raise ValueError(
                "non-grouped explicit turn cannot expose relation or members"
            )
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "relation", relation)


class GovernedExplicitTurnContextualClaimGrouper:
    """Represent provenance-only co-presence among one projection's claims."""

    def group(
        self,
        *,
        projection: GovernedExplicitTurnTransientClaimProjection,
    ) -> GovernedExplicitTurnContextualClaimGrouping:
        mapped_status = self._projection_status(projection.status)
        if mapped_status is not ExplicitTurnContextualGroupingStatus.GROUPED:
            return self._result(
                projection=projection,
                status=mapped_status,
                rationale_codes=(
                    "explicit_turn_grouping:projection_"
                    f"{projection.status.value}",
                ),
            )

        member_claim_ids = tuple(claim.claim_id for claim in projection.claims)
        if len(member_claim_ids) < 2:
            return self._result(
                projection=projection,
                status=ExplicitTurnContextualGroupingStatus.INSUFFICIENT,
                rationale_codes=(
                    "explicit_turn_grouping:multiple_claims_required",
                ),
            )
        if any(not claim_id.strip() for claim_id in member_claim_ids):
            raise ValueError("explicit-turn contextual grouping requires claim ids")
        if len(set(member_claim_ids)) != len(member_claim_ids):
            raise ValueError(
                "explicit-turn contextual grouping rejects duplicate claim ids"
            )

        return self._result(
            projection=projection,
            status=ExplicitTurnContextualGroupingStatus.GROUPED,
            relation=ExplicitTurnContextualRelation.CO_PRESENT_IN_CURRENT_TURN,
            member_claim_ids=member_claim_ids,
            rationale_codes=(
                "explicit_turn_grouping:source_projection_projected",
                "explicit_turn_grouping:multiple_claims_present",
                "explicit_turn_grouping:co_presence_only",
                "explicit_turn_grouping:no_semantic_relation_inferred",
            ),
        )

    @staticmethod
    def _projection_status(
        status: ExplicitTurnTransientClaimProjectionStatus,
    ) -> ExplicitTurnContextualGroupingStatus:
        return {
            ExplicitTurnTransientClaimProjectionStatus.PROJECTED: (
                ExplicitTurnContextualGroupingStatus.GROUPED
            ),
            ExplicitTurnTransientClaimProjectionStatus.INSUFFICIENT: (
                ExplicitTurnContextualGroupingStatus.INSUFFICIENT
            ),
            ExplicitTurnTransientClaimProjectionStatus.AMBIGUOUS: (
                ExplicitTurnContextualGroupingStatus.AMBIGUOUS
            ),
            ExplicitTurnTransientClaimProjectionStatus.UNSUPPORTED: (
                ExplicitTurnContextualGroupingStatus.UNSUPPORTED
            ),
            ExplicitTurnTransientClaimProjectionStatus.SCOPE_MISMATCH: (
                ExplicitTurnContextualGroupingStatus.SCOPE_MISMATCH
            ),
        }[status]

    @staticmethod
    def _result(
        *,
        projection: GovernedExplicitTurnTransientClaimProjection,
        status: ExplicitTurnContextualGroupingStatus,
        rationale_codes: tuple[str, ...],
        relation: ExplicitTurnContextualRelation | None = None,
        member_claim_ids: tuple[str, ...] = (),
    ) -> GovernedExplicitTurnContextualClaimGrouping:
        payload = (
            _SCHEMA_VERSION,
            status.value,
            relation.value if relation is not None else None,
            projection.source_reference,
            projection.scope_reference,
            projection.source_grounding_fingerprint,
            projection.source_fingerprint,
            member_claim_ids,
            rationale_codes,
        )
        return GovernedExplicitTurnContextualClaimGrouping(
            status=status,
            relation=relation,
            member_claim_ids=member_claim_ids,
            source_reference=projection.source_reference,
            scope_reference=projection.scope_reference,
            source_grounding_fingerprint=projection.source_grounding_fingerprint,
            source_projection_fingerprint=projection.source_fingerprint,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
