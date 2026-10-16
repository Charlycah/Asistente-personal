from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.explicit_turn_contextual_claim_grouping import (
    ExplicitTurnContextualGroupingStatus,
    GovernedExplicitTurnContextualClaimGrouping,
)
from core.governed_reasoning.explicit_turn_transient_claim_projection import (
    ExplicitTurnTransientClaimProjectionStatus,
    GovernedExplicitTurnTransientClaimProjection,
)

_SCHEMA_VERSION = "cih-2m-bounded-situational-hypothesis-v1"


def _hypothesis_level():
    from core.cognitive_maturity.epistemic import EpistemicLevel

    return EpistemicLevel.HYPOTHESIS


class BoundedSituationalHypothesisStatus(StrEnum):
    FORMED = "formed"
    INSUFFICIENT = "insufficient"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


class BoundedSituationalHypothesisKind(StrEnum):
    ORGANIZATION_RELATED = "organization_related"


@dataclass(frozen=True)
class GovernedBoundedSituationalHypothesis:
    status: BoundedSituationalHypothesisStatus | str
    hypothesis_id: str
    situational_kind: BoundedSituationalHypothesisKind | str | None
    proposition: str
    source_grouping_fingerprint: str
    source_projection_fingerprint: str
    source_claim_ids: tuple[str, ...]
    semantic_support_claim_ids: tuple[str, ...]
    semantic_basis_codes: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    epistemic_level: object = field(default_factory=_hypothesis_level)
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    transient: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_facts: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    establishes_causality: bool = False
    infers_intent: bool = False
    infers_need: bool = False
    infers_priority: bool = False
    infers_action: bool = False
    creates_claims: bool = False
    registers_claims: bool = False
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
        status = BoundedSituationalHypothesisStatus(self.status)
        kind = (
            None
            if self.situational_kind is None
            else BoundedSituationalHypothesisKind(self.situational_kind)
        )
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("situational hypothesis must preserve reasoning authority")
        if self.epistemic_level is not _hypothesis_level():
            raise ValueError("situational hypothesis must remain a hypothesis")
        if len(self.source_grouping_fingerprint) != 64 or len(
            self.source_projection_fingerprint
        ) != 64 or len(self.source_fingerprint) != 64:
            raise ValueError("situational hypothesis fingerprints must be SHA-256")
        if any((
            not self.read_only,
            not self.session_local,
            not self.transient,
            not self.consultative,
            self.persists_results,
            self.creates_facts,
            self.establishes_truth,
            self.establishes_falsity,
            self.establishes_causality,
            self.infers_intent,
            self.infers_need,
            self.infers_priority,
            self.infers_action,
            self.creates_claims,
            self.registers_claims,
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
        )):
            raise ValueError("situational hypothesis violates governed limits")
        if status is BoundedSituationalHypothesisStatus.FORMED:
            if kind is None or not self.proposition.strip():
                raise ValueError("formed situational hypothesis requires semantics")
            if not self.source_claim_ids or not self.semantic_support_claim_ids:
                raise ValueError("formed situational hypothesis requires lineage")
        elif kind is not None or self.proposition or self.semantic_support_claim_ids:
            raise ValueError("non-formed hypothesis cannot expose semantics")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "situational_kind", kind)


class GovernedBoundedSituationalHypothesisFormer:
    """Form one non-factual organization-related current-turn hypothesis."""

    def form(
        self,
        *,
        grouping: GovernedExplicitTurnContextualClaimGrouping,
        projection: GovernedExplicitTurnTransientClaimProjection,
    ) -> GovernedBoundedSituationalHypothesis:
        if (
            grouping.status is not ExplicitTurnContextualGroupingStatus.GROUPED
            or projection.status
            is not ExplicitTurnTransientClaimProjectionStatus.PROJECTED
        ):
            return self._result(
                grouping,
                projection,
                BoundedSituationalHypothesisStatus.INSUFFICIENT,
            )
        claim_ids = tuple(claim.claim_id for claim in projection.claims)
        if (
            grouping.source_projection_fingerprint != projection.source_fingerprint
            or grouping.member_claim_ids != claim_ids
        ):
            return self._result(
                grouping,
                projection,
                BoundedSituationalHypothesisStatus.UNSUPPORTED,
            )
        support = tuple(
            claim.claim_id
            for claim in projection.claims
            if claim.predicate == "falta_organizar"
        )
        if not support:
            return self._result(
                grouping,
                projection,
                BoundedSituationalHypothesisStatus.UNSUPPORTED,
            )
        return self._result(
            grouping,
            projection,
            BoundedSituationalHypothesisStatus.FORMED,
            situational_kind=BoundedSituationalHypothesisKind.ORGANIZATION_RELATED,
            proposition=(
                "The grouped current-turn claims may describe an "
                "organization-related situation."
            ),
            semantic_support_claim_ids=support,
            semantic_basis_codes=(
                "situational_hypothesis:predicate:falta_organizar",
                "situational_hypothesis:organization_related_candidate",
            ),
            rationale_codes=(
                "situational_hypothesis:grouping_verified",
                "situational_hypothesis:explicit_semantic_support",
                "situational_hypothesis:no_causality_inferred",
                "situational_hypothesis:no_intent_inferred",
                "situational_hypothesis:no_action_inferred",
            ),
        )

    @staticmethod
    def _result(
        grouping: GovernedExplicitTurnContextualClaimGrouping,
        projection: GovernedExplicitTurnTransientClaimProjection,
        status: BoundedSituationalHypothesisStatus,
        *,
        situational_kind: BoundedSituationalHypothesisKind | None = None,
        proposition: str = "",
        semantic_support_claim_ids: tuple[str, ...] = (),
        semantic_basis_codes: tuple[str, ...] = (),
        rationale_codes: tuple[str, ...] = (),
    ) -> GovernedBoundedSituationalHypothesis:
        source_claim_ids = tuple(claim.claim_id for claim in projection.claims)
        if not rationale_codes:
            rationale_codes = (f"situational_hypothesis:{status.value}",)
        payload = (
            _SCHEMA_VERSION,
            status.value,
            situational_kind.value if situational_kind else None,
            proposition,
            grouping.source_fingerprint,
            projection.source_fingerprint,
            source_claim_ids,
            semantic_support_claim_ids,
            semantic_basis_codes,
            rationale_codes,
        )
        digest = sha256(repr(payload).encode("utf-8")).hexdigest()
        return GovernedBoundedSituationalHypothesis(
            status=status,
            hypothesis_id="bounded-situational-hypothesis-" + digest,
            situational_kind=situational_kind,
            proposition=proposition,
            source_grouping_fingerprint=grouping.source_fingerprint,
            source_projection_fingerprint=projection.source_fingerprint,
            source_claim_ids=source_claim_ids,
            semantic_support_claim_ids=semantic_support_claim_ids,
            semantic_basis_codes=semantic_basis_codes,
            rationale_codes=rationale_codes,
            source_fingerprint=digest,
        )
