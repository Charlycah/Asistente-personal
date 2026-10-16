from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.claims import Claim, ClaimOrigin, ClaimStatus, ClaimType

_SCHEMA_VERSION = "cih-2u-bounded-modal-situational-implication-v1"
_IMPLICATION_CODE = (
    "bounded_modal_situational_implication:organization_related:"
    "may_have_relevant_support:organization_support:v1"
)


class BoundedModalSituationalImplicationStatus(StrEnum):
    APPLIED = "applied"
    INSUFFICIENT = "insufficient"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class GovernedBoundedModalSituationalImplicationResult:
    status: BoundedModalSituationalImplicationStatus | str
    derived_claim: Claim | None
    source_claim_id: str
    source_claim_fingerprint: str
    implication_code: str
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
        status = BoundedModalSituationalImplicationStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "bounded modal implication must preserve reasoning authority"
            )
        if not self.source_claim_id.strip():
            raise ValueError("bounded modal implication requires source claim identity")
        if len(self.source_claim_fingerprint) != 64:
            raise ValueError("source claim fingerprint must be SHA-256")
        if len(self.source_fingerprint) != 64:
            raise ValueError("bounded modal implication fingerprint must be SHA-256")
        if not self.implication_code.strip():
            raise ValueError("bounded modal implication requires implication code")
        if not self.rationale_codes:
            raise ValueError("bounded modal implication requires rationale")
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
            raise ValueError("bounded modal implication violates governed limits")
        if status is BoundedModalSituationalImplicationStatus.APPLIED:
            self._validate_derived_claim()
        elif self.derived_claim is not None:
            raise ValueError("non-applied bounded implication cannot expose a claim")
        object.__setattr__(self, "status", status)

    def _validate_derived_claim(self) -> None:
        claim = self.derived_claim
        if claim is None:
            raise ValueError("applied bounded implication requires one claim")
        if (
            claim.subject != "current_turn_situation"
            or claim.predicate != "may_have_relevant_support"
            or claim.object_value != "organization_support"
            or claim.normalized_type is not ClaimType.HYPOTHESIS
            or claim.normalized_origin is not ClaimOrigin.SYSTEM
            or claim.normalized_status is not ClaimStatus.PROPOSED
            or claim.confidence is not None
            or claim.evidence_links
            or claim.rule_reference is not None
        ):
            raise ValueError(
                "bounded modal implication must preserve frozen output epistemics"
            )


class GovernedBoundedModalSituationalImplicationFoundationV1:
    """Apply one certified modal situational implication without general inference."""

    def apply(
        self,
        *,
        source_claim: Claim,
    ) -> GovernedBoundedModalSituationalImplicationResult:
        if not self._is_supported_source(source_claim):
            return self._result(
                source_claim=source_claim,
                status=BoundedModalSituationalImplicationStatus.UNSUPPORTED,
            )
        derived_claim = Claim(
            subject="current_turn_situation",
            predicate="may_have_relevant_support",
            object_value="organization_support",
            claim_type=ClaimType.HYPOTHESIS,
            origin=ClaimOrigin.SYSTEM,
            status=ClaimStatus.PROPOSED,
            evidence_links=(),
            confidence=None,
            owner=source_claim.owner,
            rule_reference=None,
            supersedes=None,
            valid_from=None,
            valid_until=None,
            created_at=source_claim.created_at,
            claim_id=self._claim_id(source_claim),
        )
        return self._result(
            source_claim=source_claim,
            status=BoundedModalSituationalImplicationStatus.APPLIED,
            derived_claim=derived_claim,
            rationale_codes=(
                "bounded_modal_implication:source_epistemics_valid",
                "bounded_modal_implication:organization_related_supported",
                "bounded_modal_implication:modal_semantics_preserved",
                "bounded_modal_implication:organization_support_only",
                "bounded_modal_implication:no_truth_promotion",
                "bounded_modal_implication:no_evidence_created",
                "bounded_modal_implication:no_confidence_created",
                "bounded_modal_implication:no_action_authorized",
            ),
        )

    @staticmethod
    def _is_supported_source(source_claim: Claim) -> bool:
        return (
            source_claim.subject == "current_turn_situation"
            and source_claim.predicate == "may_be"
            and source_claim.object_value == "organization_related"
            and source_claim.normalized_type is ClaimType.HYPOTHESIS
            and source_claim.normalized_origin is ClaimOrigin.SYSTEM
            and source_claim.normalized_status is ClaimStatus.PROPOSED
            and source_claim.confidence is None
            and not source_claim.evidence_links
            and source_claim.rule_reference is None
            and source_claim.supersedes is None
            and source_claim.valid_from is None
            and source_claim.valid_until is None
        )

    @staticmethod
    def _claim_id(source_claim: Claim) -> str:
        payload = "|".join(
            (
                _SCHEMA_VERSION,
                source_claim.fingerprint,
                "governed_reasoning",
                "current_turn_situation",
                "may_have_relevant_support",
                "organization_support",
                ClaimType.HYPOTHESIS.value,
                ClaimOrigin.SYSTEM.value,
                ClaimStatus.PROPOSED.value,
                _IMPLICATION_CODE,
            )
        )
        digest = sha256(payload.encode("utf-8")).hexdigest()
        return f"bounded-modal-situational-claim-{digest}"

    @staticmethod
    def _result(
        *,
        source_claim: Claim,
        status: BoundedModalSituationalImplicationStatus,
        derived_claim: Claim | None = None,
        rationale_codes: tuple[str, ...] = (),
    ) -> GovernedBoundedModalSituationalImplicationResult:
        if not rationale_codes:
            rationale_codes = (f"bounded_modal_implication:{status.value}",)
        payload = (
            _SCHEMA_VERSION,
            status.value,
            source_claim.claim_id,
            source_claim.fingerprint,
            _IMPLICATION_CODE,
            derived_claim.claim_id if derived_claim else None,
            derived_claim.fingerprint if derived_claim else None,
            rationale_codes,
        )
        return GovernedBoundedModalSituationalImplicationResult(
            status=status,
            derived_claim=derived_claim,
            source_claim_id=source_claim.claim_id,
            source_claim_fingerprint=source_claim.fingerprint,
            implication_code=_IMPLICATION_CODE,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
