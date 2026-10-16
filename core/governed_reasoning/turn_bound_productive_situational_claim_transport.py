from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.claims import Claim, ClaimOrigin, ClaimStatus, ClaimType

_SCHEMA_VERSION = "cih-2w-turn-bound-productive-situational-claim-binding-v1"


class TurnBoundProductiveSituationalClaimBindingStatus(StrEnum):
    BOUND = "bound"
    INSUFFICIENT = "insufficient"
    UNSUPPORTED = "unsupported"
    SCOPE_MISMATCH = "scope_mismatch"


@dataclass(frozen=True)
class GovernedTurnBoundProductiveSituationalClaimBinding:
    status: TurnBoundProductiveSituationalClaimBindingStatus | str
    owner: str
    session_id: str
    turn_id: str
    source_claim: Claim | None
    source_claim_id: str
    source_claim_fingerprint: str
    binding_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    transient: bool = True
    session_local: bool = True
    turn_bound: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_claims: bool = False
    registers_claims: bool = False
    creates_evidence: bool = False
    registers_evidence: bool = False
    registers_rules: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    establishes_causality: bool = False
    infers_intent: bool = False
    infers_need: bool = False
    infers_priority: bool = False
    infers_action: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    authorizes_action: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        status = TurnBoundProductiveSituationalClaimBindingStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("turn-bound binding must preserve reasoning authority")
        if not all(
            item.strip() for item in (self.owner, self.session_id, self.turn_id)
        ):
            raise ValueError("turn-bound binding requires owner/session/turn lineage")
        if len(self.binding_fingerprint) != 64:
            raise ValueError("turn-bound binding fingerprint must be SHA-256")
        if not self.rationale_codes:
            raise ValueError("turn-bound binding requires rationale")
        if any(
            (
                not self.read_only,
                not self.transient,
                not self.session_local,
                not self.turn_bound,
                not self.consultative,
                self.persists_results,
                self.creates_claims,
                self.registers_claims,
                self.creates_evidence,
                self.registers_evidence,
                self.registers_rules,
                self.establishes_truth,
                self.establishes_falsity,
                self.establishes_causality,
                self.infers_intent,
                self.infers_need,
                self.infers_priority,
                self.infers_action,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_world_model,
                self.modifies_planning,
                self.authorizes_action,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("turn-bound binding violates governed limits")
        if status is TurnBoundProductiveSituationalClaimBindingStatus.BOUND:
            if self.source_claim is None:
                raise ValueError("bound situational claim binding requires one claim")
            if (
                self.source_claim.claim_id != self.source_claim_id
                or self.source_claim.fingerprint != self.source_claim_fingerprint
            ):
                raise ValueError("turn-bound binding requires exact claim lineage")
        elif self.source_claim is not None:
            raise ValueError("non-bound situational binding cannot expose a claim")
        object.__setattr__(self, "status", status)


@dataclass(frozen=True)
class GovernedTurnBoundProductiveSituationalClaimBinder:
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    transient: bool = True
    persists_results: bool = False
    registers_claims: bool = False
    executes_actions: bool = False

    def bind(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        source_claim: Claim,
    ) -> GovernedTurnBoundProductiveSituationalClaimBinding:
        owner_key = owner.strip()
        session_key = session_id.strip()
        turn_key = turn_id.strip()
        if not owner_key or not session_key or not turn_key:
            raise ValueError("turn-bound binding requires owner/session/turn lineage")
        if source_claim.owner.strip().casefold() != owner_key.casefold():
            return self._result(
                status=TurnBoundProductiveSituationalClaimBindingStatus.SCOPE_MISMATCH,
                owner=owner_key,
                session_id=session_key,
                turn_id=turn_key,
                source_claim=None,
                source_claim_id=source_claim.claim_id,
                source_claim_fingerprint=source_claim.fingerprint,
                rationale_codes=("turn_bound_binding:owner_mismatch",),
            )
        if not self._supported(source_claim):
            return self._result(
                status=TurnBoundProductiveSituationalClaimBindingStatus.UNSUPPORTED,
                owner=owner_key,
                session_id=session_key,
                turn_id=turn_key,
                source_claim=None,
                source_claim_id=source_claim.claim_id,
                source_claim_fingerprint=source_claim.fingerprint,
                rationale_codes=("turn_bound_binding:unsupported_claim_shape",),
            )
        return self._result(
            status=TurnBoundProductiveSituationalClaimBindingStatus.BOUND,
            owner=owner_key,
            session_id=session_key,
            turn_id=turn_key,
            source_claim=source_claim,
            source_claim_id=source_claim.claim_id,
            source_claim_fingerprint=source_claim.fingerprint,
            rationale_codes=(
                "turn_bound_binding:exact_cih_2u_claim",
                "turn_bound_binding:same_owner",
                "turn_bound_binding:same_session_turn",
                "turn_bound_binding:transient_only",
            ),
        )

    @staticmethod
    def _supported(claim: Claim) -> bool:
        return (
            claim.subject == "current_turn_situation"
            and claim.predicate == "may_have_relevant_support"
            and claim.object_value == "organization_support"
            and claim.normalized_type is ClaimType.HYPOTHESIS
            and claim.normalized_origin is ClaimOrigin.SYSTEM
            and claim.normalized_status is ClaimStatus.PROPOSED
            and claim.confidence is None
            and not claim.evidence_links
            and claim.rule_reference is None
            and claim.supersedes is None
            and claim.valid_from is None
            and claim.valid_until is None
        )

    @staticmethod
    def _result(
        *,
        status: TurnBoundProductiveSituationalClaimBindingStatus,
        owner: str,
        session_id: str,
        turn_id: str,
        source_claim: Claim | None,
        source_claim_id: str,
        source_claim_fingerprint: str,
        rationale_codes: tuple[str, ...],
    ) -> GovernedTurnBoundProductiveSituationalClaimBinding:
        payload = (
            _SCHEMA_VERSION,
            "governed_reasoning",
            owner.casefold(),
            session_id,
            turn_id,
            source_claim_id,
            source_claim_fingerprint,
            status.value,
        )
        fingerprint = sha256(repr(payload).encode("utf-8")).hexdigest()
        return GovernedTurnBoundProductiveSituationalClaimBinding(
            status=status,
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            source_claim=source_claim,
            source_claim_id=source_claim_id,
            source_claim_fingerprint=source_claim_fingerprint,
            binding_fingerprint=fingerprint,
            rationale_codes=rationale_codes,
        )
