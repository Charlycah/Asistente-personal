from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .assessment import (
    ExternalEvidenceAssessment,
    ExternalEvidenceAssessmentStatus,
)
from .models import ExternalIntelligenceEnvelope
from .verification import ExternalIntelligenceVerification


class ExternalEvidenceStance(str, Enum):
    SUPPORT = "support"
    CONTRADICT = "contradict"


class ExternalEvidenceCorroborationStatus(str, Enum):
    CORROBORATED = "corroborated"
    CONTRADICTED = "contradicted"
    MIXED = "mixed"
    INSUFFICIENT = "insufficient"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ExternalEvidenceCorroborationItem:
    proposition_id: str
    envelope: ExternalIntelligenceEnvelope
    verification: ExternalIntelligenceVerification
    assessment: ExternalEvidenceAssessment
    stance: ExternalEvidenceStance | str

    def __post_init__(self) -> None:
        proposition_id = self.proposition_id.strip()
        stance = ExternalEvidenceStance(self.stance)
        if not proposition_id:
            raise ValueError("external corroboration item requires proposition id")
        if self.verification.envelope_id != self.envelope.envelope_id:
            raise ValueError("external corroboration verification lineage mismatch")
        if self.assessment.envelope_id != self.envelope.envelope_id:
            raise ValueError("external corroboration assessment lineage mismatch")
        if self.assessment.verification_id != self.verification.verification_id:
            raise ValueError("external corroboration assessment verification mismatch")
        object.__setattr__(self, "proposition_id", proposition_id)
        object.__setattr__(self, "stance", stance)


@dataclass(frozen=True)
class ExternalEvidenceCorroboration:
    proposition_id: str
    status: ExternalEvidenceCorroborationStatus | str
    supporting_envelopes: tuple[str, ...]
    contradicting_envelopes: tuple[str, ...]
    independent_actors: tuple[str, ...]
    aggregate_confidence: float
    checks: tuple[str, ...]
    limitations: tuple[str, ...]
    rationale: tuple[str, ...]
    corroboration_id: str = ""

    def __post_init__(self) -> None:
        proposition_id = self.proposition_id.strip()
        status = ExternalEvidenceCorroborationStatus(self.status)
        supports = tuple(self.supporting_envelopes)
        contradicts = tuple(self.contradicting_envelopes)
        actors = tuple(self.independent_actors)
        checks = tuple(item.strip() for item in self.checks)
        limitations = tuple(item.strip() for item in self.limitations)
        rationale = tuple(item.strip() for item in self.rationale)
        if not proposition_id:
            raise ValueError("external corroboration requires proposition id")
        if not 0.0 <= self.aggregate_confidence <= 1.0:
            raise ValueError(
                "external corroboration confidence must be between 0 and 1"
            )
        if not checks or any(not item for item in checks):
            raise ValueError("external corroboration requires explicit checks")
        if any(not item for item in limitations):
            raise ValueError("external corroboration limitations must not be blank")
        if not rationale or any(not item for item in rationale):
            raise ValueError("external corroboration requires rationale")
        payload = "|".join(
            (
                proposition_id,
                status.value,
                ",".join(supports),
                ",".join(contradicts),
                ",".join(actors),
                f"{self.aggregate_confidence:.6f}",
                *checks,
                *limitations,
                *rationale,
            )
        )
        expected = sha256(payload.encode()).hexdigest()
        if self.corroboration_id and self.corroboration_id != expected:
            raise ValueError("external corroboration id is inconsistent")
        object.__setattr__(self, "proposition_id", proposition_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "supporting_envelopes", supports)
        object.__setattr__(self, "contradicting_envelopes", contradicts)
        object.__setattr__(self, "independent_actors", actors)
        object.__setattr__(self, "checks", checks)
        object.__setattr__(self, "limitations", limitations)
        object.__setattr__(self, "rationale", rationale)
        object.__setattr__(self, "corroboration_id", expected)

    @property
    def truth_certified(self) -> bool:
        return False

    @property
    def cognitive_authority_granted(self) -> bool:
        return False


class GovernedExternalEvidenceCorroborator:
    """Corroborates explicit stances without inferring semantic truth."""

    CORROBORATOR_ID = "external_intelligence_evidence_corroborator"

    @property
    def corroborator_id(self) -> str:
        return self.CORROBORATOR_ID

    def corroborate(
        self,
        items: tuple[ExternalEvidenceCorroborationItem, ...],
    ) -> ExternalEvidenceCorroboration:
        if not items:
            raise ValueError("external corroboration requires evidence items")
        proposition_ids = {item.proposition_id for item in items}
        if len(proposition_ids) != 1:
            raise ValueError("external corroboration items must share proposition")
        if len({item.envelope.envelope_id for item in items}) != len(items):
            raise ValueError("external corroboration evidence must be unique")

        proposition_id = items[0].proposition_id
        usable = tuple(
            item
            for item in items
            if item.assessment.status is not ExternalEvidenceAssessmentStatus.REJECTED
        )
        rejected = tuple(
            item
            for item in items
            if item.assessment.status is ExternalEvidenceAssessmentStatus.REJECTED
        )
        supports = tuple(
            item for item in usable if item.stance is ExternalEvidenceStance.SUPPORT
        )
        contradicts = tuple(
            item
            for item in usable
            if item.stance is ExternalEvidenceStance.CONTRADICT
        )
        actors = tuple(
            sorted({item.envelope.provenance.actor_id for item in usable})
        )
        checks = [
            "all_items_share_explicit_proposition",
            "all_lineages_are_consistent",
            "stances_are_explicit_not_semantically_inferred",
            "majority_does_not_certify_truth",
            "external_evidence_has_no_cognitive_authority",
        ]
        limitations = ["corroboration_does_not_certify_truth"]

        if rejected and not usable:
            status = ExternalEvidenceCorroborationStatus.REJECTED
            confidence = 0.0
            limitations.append("all_evidence_is_rejected")
        elif len(usable) < 2 or len(actors) < 2:
            status = ExternalEvidenceCorroborationStatus.INSUFFICIENT
            confidence = self._mean_confidence(usable)
            limitations.append("independent_corroboration_is_insufficient")
        elif supports and contradicts:
            status = ExternalEvidenceCorroborationStatus.MIXED
            confidence = self._mean_confidence(usable)
            limitations.append("credible_evidence_is_in_conflict")
        elif supports:
            status = ExternalEvidenceCorroborationStatus.CORROBORATED
            confidence = self._mean_confidence(supports)
            checks.append("multiple_independent_actors_support_proposition")
        else:
            status = ExternalEvidenceCorroborationStatus.CONTRADICTED
            confidence = self._mean_confidence(contradicts)
            checks.append("multiple_independent_actors_contradict_proposition")

        return ExternalEvidenceCorroboration(
            proposition_id=proposition_id,
            status=status,
            supporting_envelopes=tuple(
                item.envelope.envelope_id for item in supports
            ),
            contradicting_envelopes=tuple(
                item.envelope.envelope_id for item in contradicts
            ),
            independent_actors=actors,
            aggregate_confidence=confidence,
            checks=tuple(checks),
            limitations=tuple(limitations),
            rationale=(
                "corroboration_compares_explicit_stances_only",
                "independence_is_actor_identity_not_semantic_independence",
                "confidence_is_aggregate_not_certainty",
                "roby_retains_interpretation_and_decision",
            ),
        )

    @staticmethod
    def _mean_confidence(
        items: tuple[ExternalEvidenceCorroborationItem, ...],
    ) -> float:
        if not items:
            return 0.0
        return sum(item.assessment.confidence for item in items) / len(items)
