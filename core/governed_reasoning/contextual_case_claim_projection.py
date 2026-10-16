from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.claims import Claim, ClaimOrigin, ClaimStatus, ClaimType
from core.governed_reasoning.contextual_case_grounding import (
    ContextualCaseGroundingStatus,
    GovernedContextualCaseGrounding,
)
from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleInstantiationSpec,
)

_SCHEMA_VERSION = "post-m409.1-contextual-case-claim-projection-v1"


class ContextualCaseClaimProjectionStatus(StrEnum):
    PROJECTED = "projected"
    INSUFFICIENT = "insufficient"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    SCOPE_MISMATCH = "scope_mismatch"
    PROVENANCE_MISMATCH = "provenance_mismatch"


@dataclass(frozen=True)
class GovernedContextualCaseClaimProjection:
    status: ContextualCaseClaimProjectionStatus | str
    claims: tuple[Claim, ...]
    source_reference: str
    scope_reference: str
    source_case_fingerprint: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists_results: bool = False
    establishes_truth: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    registers_claims: bool = False
    registers_rule: bool = False
    authorizes_inference: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False

    def __post_init__(self) -> None:
        status = ContextualCaseClaimProjectionStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("case claim projection must preserve reasoning authority")
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("case claim projection requires provenance and scope")
        if (
            not self.source_case_fingerprint.strip()
            or not self.source_fingerprint.strip()
        ):
            raise ValueError("case claim projection requires fingerprints")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("case claim projection requires rationale codes")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists_results,
                self.establishes_truth,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_world_model,
                self.registers_claims,
                self.registers_rule,
                self.authorizes_inference,
                self.executes_actions,
                self.grants_authority,
                self.uses_provider,
                self.uses_retrieval,
            )
        ):
            raise ValueError("case claim projection violates governed limits")
        if status is ContextualCaseClaimProjectionStatus.PROJECTED:
            if not self.claims:
                raise ValueError("projected case requires contextual claims")
        elif self.claims:
            raise ValueError("non-projected case cannot expose partial claims")

    @property
    def normalized_status(self) -> ContextualCaseClaimProjectionStatus:
        return ContextualCaseClaimProjectionStatus(self.status)


class GovernedContextualCaseClaimProjector:
    """Project certified case conditions into non-authoritative contextual claims."""

    def project(
        self,
        *,
        spec: ContextualRuleInstantiationSpec,
        case_grounding: GovernedContextualCaseGrounding,
        scope_reference: str,
        owner: str,
        created_at: datetime,
    ) -> GovernedContextualCaseClaimProjection:
        if not scope_reference.strip() or not owner.strip():
            raise ValueError("case claim projection requires scope and owner")
        if created_at.tzinfo is None:
            raise ValueError("case claim projection timestamp must be timezone-aware")
        if scope_reference != spec.scope_reference or scope_reference != (
            case_grounding.scope_reference
        ):
            return self._result(
                spec=spec,
                case_grounding=case_grounding,
                scope_reference=scope_reference,
                owner=owner,
                created_at=created_at,
                status=ContextualCaseClaimProjectionStatus.SCOPE_MISMATCH,
                rationale_codes=("case_claim_projection:scope_mismatch",),
            )
        if case_grounding.source_rule_candidate_id != spec.rule_candidate_id:
            return self._result(
                spec=spec,
                case_grounding=case_grounding,
                scope_reference=scope_reference,
                owner=owner,
                created_at=created_at,
                status=ContextualCaseClaimProjectionStatus.PROVENANCE_MISMATCH,
                rationale_codes=("case_claim_projection:rule_provenance_mismatch",),
            )
        mapped_status = self._case_status(case_grounding.normalized_status)
        if mapped_status is not ContextualCaseClaimProjectionStatus.PROJECTED:
            return self._result(
                spec=spec,
                case_grounding=case_grounding,
                scope_reference=scope_reference,
                owner=owner,
                created_at=created_at,
                status=mapped_status,
                rationale_codes=(
                    "case_claim_projection:case_"
                    f"{case_grounding.normalized_status.value}",
                ),
            )

        bindings = {item.role_id: item for item in case_grounding.bindings}
        if set(bindings) != set(spec.roles) or len(bindings) != len(spec.roles):
            return self._result(
                spec=spec,
                case_grounding=case_grounding,
                scope_reference=scope_reference,
                owner=owner,
                created_at=created_at,
                status=ContextualCaseClaimProjectionStatus.INSUFFICIENT,
                rationale_codes=("case_claim_projection:required_role_unbound",),
            )
        condition_indexes = tuple(range(len(spec.conditions)))
        if (
            "case_grounding:prerequisite_availability_deferred"
            in case_grounding.rationale_codes
        ):
            condition_indexes = (0,)
        claims = tuple(
            Claim(
                subject=bindings[item.role_id].entity_reference,
                predicate=item.predicate_id,
                object_value=self._resolve_object_value(item, bindings),
                claim_type=ClaimType.HYPOTHESIS,
                origin=ClaimOrigin.HUMAN,
                status=ClaimStatus.PROPOSED,
                owner=owner,
                created_at=created_at,
                claim_id=self._claim_id(
                    case_grounding.source_fingerprint,
                    item.role_id,
                    item.predicate_id,
                    self._resolve_object_value(item, bindings),
                ),
            )
            for index, item in enumerate(spec.conditions)
            if index in condition_indexes
        )
        return self._result(
            spec=spec,
            case_grounding=case_grounding,
            scope_reference=scope_reference,
            owner=owner,
            created_at=created_at,
            status=ContextualCaseClaimProjectionStatus.PROJECTED,
            rationale_codes=(
                "case_claim_projection:explicit_case_conditions_only",
                (
                    "case_claim_projection:deferred_rule_result_condition_excluded"
                    if len(condition_indexes) < len(spec.conditions)
                    else "case_claim_projection:all_explicit_conditions_projected"
                ),
                "case_claim_projection:claims_remain_proposed_hypotheses",
            ),
            claims=claims,
        )

    @staticmethod
    def _resolve_object_value(item, bindings) -> str:
        if item.object_role_id is not None:
            return bindings[item.object_role_id].entity_reference
        if item.object_value is None:
            raise ValueError("case claim projection requires concrete object value")
        return item.object_value

    @staticmethod
    def _case_status(
        status: ContextualCaseGroundingStatus,
    ) -> ContextualCaseClaimProjectionStatus:
        return {
            ContextualCaseGroundingStatus.GROUNDED:
                ContextualCaseClaimProjectionStatus.PROJECTED,
            ContextualCaseGroundingStatus.AMBIGUOUS:
                ContextualCaseClaimProjectionStatus.AMBIGUOUS,
            ContextualCaseGroundingStatus.INSUFFICIENT:
                ContextualCaseClaimProjectionStatus.INSUFFICIENT,
            ContextualCaseGroundingStatus.UNSUPPORTED:
                ContextualCaseClaimProjectionStatus.UNSUPPORTED,
            ContextualCaseGroundingStatus.SCOPE_MISMATCH:
                ContextualCaseClaimProjectionStatus.SCOPE_MISMATCH,
        }[status]

    @staticmethod
    def _claim_id(
        source_fingerprint: str,
        role_id: str,
        predicate_id: str,
        object_value: str,
    ) -> str:
        payload = "|".join(
            (source_fingerprint, role_id, predicate_id, object_value)
        )
        return "ctx-case-claim-" + sha256(payload.encode("utf-8")).hexdigest()

    def _result(
        self,
        *,
        spec: ContextualRuleInstantiationSpec,
        case_grounding: GovernedContextualCaseGrounding,
        scope_reference: str,
        owner: str,
        created_at: datetime,
        status: ContextualCaseClaimProjectionStatus,
        rationale_codes: tuple[str, ...],
        claims: tuple[Claim, ...] = (),
    ) -> GovernedContextualCaseClaimProjection:
        payload = (
            _SCHEMA_VERSION,
            status.value,
            spec.rule_candidate_id,
            case_grounding.source_fingerprint,
            case_grounding.source_reference,
            scope_reference,
            owner,
            created_at.isoformat(),
            tuple(
                (claim.claim_id, claim.subject, claim.predicate, claim.object_value)
                for claim in claims
            ),
            rationale_codes,
        )
        return GovernedContextualCaseClaimProjection(
            status=status,
            claims=claims,
            source_reference=case_grounding.source_reference,
            scope_reference=scope_reference,
            source_case_fingerprint=case_grounding.source_fingerprint,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            rationale_codes=rationale_codes,
        )
