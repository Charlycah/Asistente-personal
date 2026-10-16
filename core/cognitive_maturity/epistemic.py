from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.governed_reasoning import Claim, ClaimStatus, ClaimType


class EpistemicLevel(str, Enum):
    FACT = "fact"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    UNKNOWN = "unknown"

    @property
    def public_lead(self) -> str:
        return {
            EpistemicLevel.FACT: "Según la evidencia disponible,",
            EpistemicLevel.INFERENCE: "A partir de la evidencia, infiero que",
            EpistemicLevel.HYPOTHESIS: "Es posible que",
            EpistemicLevel.UNKNOWN: (
                "No tengo evidencia suficiente para afirmar que"
            ),
        }[self]


@dataclass(frozen=True)
class EpistemicAssessment:
    level: EpistemicLevel
    claim_id: str
    source_claim_type: ClaimType
    source_claim_status: ClaimStatus
    rationale_codes: tuple[str, ...]
    public_lead: str
    allows_fact_statement: bool
    fact_promotion_requires_review: bool

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("epistemic assessment claim id must not be blank")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("epistemic assessment requires rationale codes")
        if not self.public_lead.strip():
            raise ValueError("epistemic assessment public lead must not be blank")
        if self.allows_fact_statement is not (self.level is EpistemicLevel.FACT):
            raise ValueError("only epistemic facts may allow factual presentation")
        if self.fact_promotion_requires_review is self.allows_fact_statement:
            raise ValueError("non-facts must require review before fact promotion")


class EpistemicClassifier:
    """Read-only presentation classification over governed M78 claims."""

    _UNCERTAIN_STATUSES = {
        ClaimStatus.DISPUTED,
        ClaimStatus.REFUTED,
        ClaimStatus.STALE,
        ClaimStatus.SUPERSEDED,
        ClaimStatus.REVIEW_REQUIRED,
    }
    _STATUS_RATIONALES = {
        ClaimStatus.DISPUTED: "claim_disputed",
        ClaimStatus.REFUTED: "claim_refuted",
        ClaimStatus.STALE: "claim_stale",
        ClaimStatus.SUPERSEDED: "claim_superseded",
        ClaimStatus.REVIEW_REQUIRED: "claim_review_required",
    }

    def classify(self, claim: Claim) -> EpistemicAssessment:
        claim_type = claim.normalized_type
        claim_status = claim.normalized_status

        if claim_status in self._UNCERTAIN_STATUSES:
            return self._assessment(
                claim,
                EpistemicLevel.UNKNOWN,
                self._STATUS_RATIONALES[claim_status],
            )
        if claim_type in {ClaimType.FACT, ClaimType.OBSERVATION}:
            if claim_status in {ClaimStatus.SUPPORTED, ClaimStatus.CORROBORATED}:
                return self._assessment(
                    claim,
                    EpistemicLevel.FACT,
                    "source_backed_claim_supported",
                )
            return self._assessment(
                claim,
                EpistemicLevel.UNKNOWN,
                "factual_claim_not_supported",
            )
        if claim_type is ClaimType.RULE_RESULT:
            return self._assessment(
                claim,
                EpistemicLevel.INFERENCE,
                "governed_rule_result_is_derived",
            )
        if claim_type in {ClaimType.ASSUMPTION, ClaimType.HYPOTHESIS}:
            return self._assessment(
                claim,
                EpistemicLevel.HYPOTHESIS,
                "claim_requires_confirmation",
            )
        return self._assessment(
            claim,
            EpistemicLevel.UNKNOWN,
            "absence_conflict_or_unknown_basis",
        )

    @staticmethod
    def _assessment(
        claim: Claim,
        level: EpistemicLevel,
        rationale: str,
    ) -> EpistemicAssessment:
        allows_fact_statement = level is EpistemicLevel.FACT
        return EpistemicAssessment(
            level=level,
            claim_id=claim.claim_id,
            source_claim_type=claim.normalized_type,
            source_claim_status=claim.normalized_status,
            rationale_codes=(rationale,),
            public_lead=level.public_lead,
            allows_fact_statement=allows_fact_statement,
            fact_promotion_requires_review=not allows_fact_statement,
        )

