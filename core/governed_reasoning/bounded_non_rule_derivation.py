from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.claims import Claim, ClaimOrigin, ClaimStatus, ClaimType

_SCHEMA_VERSION = "cih-2af-bounded-non-rule-derivation-v1"
_DERIVATION_CODE = (
    "bounded_non_rule_derivation:contextual_support_interpretation:"
    "organization_support:v1"
)


class BoundedNonRuleDerivationStatus(StrEnum):
    DERIVED = "derived"
    INSUFFICIENT = "insufficient"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


class BoundedNonRuleDerivationKind(StrEnum):
    CONTEXTUAL_SUPPORT_INTERPRETATION = "contextual_support_interpretation"


@dataclass(frozen=True)
class GovernedBoundedNonRuleDerivation:
    status: BoundedNonRuleDerivationStatus | str
    derived_claim: Claim | None
    source_claim_id: str
    source_claim_fingerprint: str
    derivation_kind: BoundedNonRuleDerivationKind | str
    derivation_code: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    transient: bool = True
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
    authorizes_inference: bool = False
    authorizes_action: bool = False
    executes_actions: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        status = BoundedNonRuleDerivationStatus(self.status)
        kind = BoundedNonRuleDerivationKind(self.derivation_kind)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "bounded non-rule derivation must preserve reasoning authority"
            )
        if not self.source_claim_id.strip():
            raise ValueError(
                "bounded non-rule derivation requires source claim identity"
            )
        if len(self.source_claim_fingerprint) != 64:
            raise ValueError("source claim fingerprint must be SHA-256")
        if len(self.source_fingerprint) != 64:
            raise ValueError("bounded non-rule derivation fingerprint must be SHA-256")
        if not self.derivation_code.strip() or not self.rationale_codes:
            raise ValueError("bounded non-rule derivation requires rationale")
        if any(
            (
                not self.read_only,
                not self.session_local,
                not self.transient,
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
                self.authorizes_inference,
                self.authorizes_action,
                self.executes_actions,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_world_model,
                self.modifies_planning,
                self.uses_provider,
                self.uses_retrieval,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("bounded non-rule derivation violates governed limits")
        if kind is not BoundedNonRuleDerivationKind.CONTEXTUAL_SUPPORT_INTERPRETATION:
            raise ValueError("unsupported bounded non-rule derivation kind")
        if status is BoundedNonRuleDerivationStatus.DERIVED:
            self._validate_derived_claim()
        elif self.derived_claim is not None:
            raise ValueError("non-derived bounded result cannot expose a claim")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "derivation_kind", kind)

    def _validate_derived_claim(self) -> None:
        claim = self.derived_claim
        if claim is None:
            raise ValueError("derived bounded non-rule result requires one claim")
        if (
            claim.subject != "current_turn_situation"
            or claim.predicate != "may_admit_contextual_assistance"
            or claim.object_value != "organization_support"
            or claim.normalized_type is not ClaimType.HYPOTHESIS
            or claim.normalized_origin is not ClaimOrigin.SYSTEM
            or claim.normalized_status is not ClaimStatus.PROPOSED
            or claim.confidence is not None
            or claim.evidence_links
            or claim.rule_reference is not None
            or claim.supersedes is not None
            or claim.valid_from is not None
            or claim.valid_until is not None
        ):
            raise ValueError(
                "bounded non-rule derivation must preserve frozen epistemics"
            )


class GovernedBoundedNonRuleDerivationFoundationV1:
    """Represent one certified non-rule semantic derivation without inference."""

    def derive(self, *, interpreted_claim: Claim) -> GovernedBoundedNonRuleDerivation:
        if not self._is_supported_claim(interpreted_claim):
            return self._result(
                interpreted_claim=interpreted_claim,
                status=BoundedNonRuleDerivationStatus.UNSUPPORTED,
                derived_claim=None,
            )
        return self._result(
            interpreted_claim=interpreted_claim,
            status=BoundedNonRuleDerivationStatus.DERIVED,
            derived_claim=interpreted_claim,
            rationale_codes=(
                "bounded_non_rule_derivation:interpreted_claim_valid",
                "bounded_non_rule_derivation:hypothesis_preserved",
                "bounded_non_rule_derivation:no_rule_inference",
                "bounded_non_rule_derivation:no_evidence_created",
                "bounded_non_rule_derivation:no_action_authorized",
            ),
        )

    @staticmethod
    def _is_supported_claim(claim: Claim) -> bool:
        return (
            claim.subject == "current_turn_situation"
            and claim.predicate == "may_admit_contextual_assistance"
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
        interpreted_claim: Claim,
        status: BoundedNonRuleDerivationStatus,
        derived_claim: Claim | None,
        rationale_codes: tuple[str, ...] = (),
    ) -> GovernedBoundedNonRuleDerivation:
        if not rationale_codes:
            rationale_codes = (f"bounded_non_rule_derivation:{status.value}",)
        payload = (
            _SCHEMA_VERSION,
            "governed_reasoning",
            interpreted_claim.claim_id,
            interpreted_claim.fingerprint,
            BoundedNonRuleDerivationKind.CONTEXTUAL_SUPPORT_INTERPRETATION.value,
            _DERIVATION_CODE,
            status.value,
            derived_claim.claim_id if derived_claim else None,
            derived_claim.fingerprint if derived_claim else None,
            rationale_codes,
        )
        return GovernedBoundedNonRuleDerivation(
            status=status,
            derived_claim=derived_claim,
            source_claim_id=interpreted_claim.claim_id,
            source_claim_fingerprint=interpreted_claim.fingerprint,
            derivation_kind=(
                BoundedNonRuleDerivationKind.CONTEXTUAL_SUPPORT_INTERPRETATION
            ),
            derivation_code=_DERIVATION_CODE,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
