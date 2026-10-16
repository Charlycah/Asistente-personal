from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.claims import (
    Claim,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
)
from core.governed_reasoning.explicit_turn_proposition_grounding import (
    ExplicitTurnPropositionGroundingStatus,
    GovernedExplicitTurnPropositionGrounding,
)

_SCHEMA_VERSION = "cih-2g-explicit-turn-transient-claim-projection-v1"


class ExplicitTurnTransientClaimProjectionStatus(StrEnum):
    PROJECTED = "projected"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    INSUFFICIENT = "insufficient"
    SCOPE_MISMATCH = "scope_mismatch"


@dataclass(frozen=True)
class GovernedExplicitTurnTransientClaimProjection:
    status: ExplicitTurnTransientClaimProjectionStatus | str
    claims: tuple[Claim, ...]
    source_reference: str
    scope_reference: str
    source_grounding_fingerprint: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    transient: bool = True
    persists_results: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    registers_claims: bool = False
    registers_rule: bool = False
    authorizes_inference: bool = False
    authorizes_action: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        status = ExplicitTurnTransientClaimProjectionStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "explicit-turn claim projection must preserve "
                "governed reasoning authority"
            )
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError(
                "explicit-turn claim projection requires provenance and scope"
            )
        if (
            len(self.source_grounding_fingerprint) != 64
            or len(self.source_fingerprint) != 64
        ):
            raise ValueError(
                "explicit-turn claim projection fingerprints must be SHA-256"
            )
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("explicit-turn claim projection requires rationale codes")
        if any(
            (
                not self.read_only,
                not self.session_local,
                not self.transient,
                self.persists_results,
                self.establishes_truth,
                self.establishes_falsity,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_world_model,
                self.registers_claims,
                self.registers_rule,
                self.authorizes_inference,
                self.authorizes_action,
                self.uses_provider,
                self.uses_retrieval,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("explicit-turn claim projection violates governed limits")
        if status is ExplicitTurnTransientClaimProjectionStatus.PROJECTED:
            if not self.claims:
                raise ValueError("projected explicit turn requires transient claims")
        elif self.claims:
            raise ValueError("non-projected explicit turn cannot expose partial claims")
        object.__setattr__(self, "status", status)


class GovernedExplicitTurnTransientClaimProjector:
    """Project grounded current-turn propositions into transient human hypotheses."""

    def project(
        self,
        *,
        grounding: GovernedExplicitTurnPropositionGrounding,
        scope_reference: str,
        owner: str,
        created_at: datetime,
    ) -> GovernedExplicitTurnTransientClaimProjection:
        if not scope_reference.strip() or not owner.strip():
            raise ValueError("explicit-turn claim projection requires scope and owner")
        if created_at.tzinfo is None:
            raise ValueError(
                "explicit-turn claim projection timestamp must be timezone-aware"
            )
        if scope_reference != grounding.scope_reference:
            return self._result(
                grounding=grounding,
                scope_reference=scope_reference,
                owner=owner,
                created_at=created_at,
                status=ExplicitTurnTransientClaimProjectionStatus.SCOPE_MISMATCH,
                rationale_codes=("explicit_turn_claim_projection:scope_mismatch",),
            )

        mapped_status = self._grounding_status(grounding.status)
        if mapped_status is not ExplicitTurnTransientClaimProjectionStatus.PROJECTED:
            return self._result(
                grounding=grounding,
                scope_reference=scope_reference,
                owner=owner,
                created_at=created_at,
                status=mapped_status,
                rationale_codes=(
                    "explicit_turn_claim_projection:grounding_"
                    f"{grounding.status.value}",
                ),
            )

        claims = tuple(
            Claim(
                subject=proposition.subject,
                predicate=proposition.predicate,
                object_value=proposition.object_value,
                claim_type=ClaimType.HYPOTHESIS,
                origin=ClaimOrigin.HUMAN,
                status=ClaimStatus.PROPOSED,
                owner=owner,
                created_at=created_at,
                claim_id=self._claim_id(
                    grounding.source_fingerprint,
                    proposition.source_fingerprint,
                    owner,
                    proposition.subject,
                    proposition.predicate,
                    proposition.object_value,
                ),
            )
            for proposition in grounding.propositions
        )
        return self._result(
            grounding=grounding,
            scope_reference=scope_reference,
            owner=owner,
            created_at=created_at,
            status=ExplicitTurnTransientClaimProjectionStatus.PROJECTED,
            rationale_codes=(
                "explicit_turn_claim_projection:explicit_grounding_only",
                "explicit_turn_claim_projection:human_proposed_hypotheses_only",
                "explicit_turn_claim_projection:non_persistent_transient_claims",
            ),
            claims=claims,
        )

    @staticmethod
    def _grounding_status(
        status: ExplicitTurnPropositionGroundingStatus,
    ) -> ExplicitTurnTransientClaimProjectionStatus:
        return {
            ExplicitTurnPropositionGroundingStatus.GROUNDED: (
                ExplicitTurnTransientClaimProjectionStatus.PROJECTED
            ),
            ExplicitTurnPropositionGroundingStatus.AMBIGUOUS: (
                ExplicitTurnTransientClaimProjectionStatus.AMBIGUOUS
            ),
            ExplicitTurnPropositionGroundingStatus.UNSUPPORTED: (
                ExplicitTurnTransientClaimProjectionStatus.UNSUPPORTED
            ),
            ExplicitTurnPropositionGroundingStatus.INSUFFICIENT: (
                ExplicitTurnTransientClaimProjectionStatus.INSUFFICIENT
            ),
        }[status]

    @staticmethod
    def _claim_id(
        grounding_fingerprint: str,
        proposition_fingerprint: str,
        owner: str,
        subject: str,
        predicate: str,
        object_value: str,
    ) -> str:
        payload = "|".join(
            (
                grounding_fingerprint,
                proposition_fingerprint,
                owner.strip().casefold(),
                subject,
                predicate,
                object_value,
            )
        )
        return "explicit-turn-claim-" + sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _result(
        *,
        grounding: GovernedExplicitTurnPropositionGrounding,
        scope_reference: str,
        owner: str,
        created_at: datetime,
        status: ExplicitTurnTransientClaimProjectionStatus,
        rationale_codes: tuple[str, ...],
        claims: tuple[Claim, ...] = (),
    ) -> GovernedExplicitTurnTransientClaimProjection:
        payload = (
            _SCHEMA_VERSION,
            status.value,
            grounding.source_reference,
            grounding.source_fingerprint,
            scope_reference,
            owner.strip().casefold(),
            created_at.isoformat(),
            tuple(
                (claim.claim_id, claim.subject, claim.predicate, claim.object_value)
                for claim in claims
            ),
            rationale_codes,
        )
        return GovernedExplicitTurnTransientClaimProjection(
            status=status,
            claims=claims,
            source_reference=grounding.source_reference,
            scope_reference=scope_reference,
            source_grounding_fingerprint=grounding.source_fingerprint,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
