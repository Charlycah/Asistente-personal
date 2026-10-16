from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    MultisourceKnowledgeGapEvidence,
)

EXPLICIT_INNER_CONTINUITY_IDENTITY = "roby.self.explicit_inner_continuity"


class EpistemicNeedIdentityRelation(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class EpistemicNeedIdentityReference:
    identity: str | None
    source_reference: str
    lineage_kind: str

    def __post_init__(self) -> None:
        if self.identity is not None and not self.identity.strip():
            raise ValueError("epistemic need identity must be explicit or absent")
        if not self.source_reference.strip() or not self.lineage_kind.strip():
            raise ValueError("epistemic need reference requires explicit lineage")


@dataclass(frozen=True)
class EpistemicNeedIdentityMatch:
    relation: EpistemicNeedIdentityRelation
    left_source_reference: str
    right_source_reference: str
    inferred_from_text: bool = False
    used_fuzzy_matching: bool = False
    used_semantic_matching: bool = False


@dataclass(frozen=True)
class SelfEpistemicNeedIdentityProjector:
    read_only: bool = True
    creates_questions: bool = False
    assigns_relevance: bool = False
    creates_goals: bool = False
    creates_acquisition_plans: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    claims_subjective_experience: bool = False

    def project(
        self,
        gap: MultisourceKnowledgeGapEvidence,
    ) -> EpistemicNeedIdentityReference:
        if not isinstance(gap, MultisourceKnowledgeGapEvidence):
            raise TypeError("projector requires MultisourceKnowledgeGapEvidence")
        if gap.source_kind is not EpistemicCuriositySourceKind.REASONING:
            raise ValueError("self-gap must preserve the certified source kind")
        if gap.relevance is not EpistemicCuriosityRelevance.UNKNOWN:
            raise ValueError("identity projection must stop before relevance")
        if gap.subject != "ROBY explicit inner continuity":
            raise ValueError("projector is bounded to explicit inner continuity")
        if not any(
            code == f"inner_continuity_report:{gap.source_reference}"
            for code in gap.evidence_codes
        ):
            raise ValueError("self-gap lacks explicit inner-continuity lineage")
        return EpistemicNeedIdentityReference(
            identity=EXPLICIT_INNER_CONTINUITY_IDENTITY,
            source_reference=gap.source_reference,
            lineage_kind="explicit_inner_continuity_gap",
        )


@dataclass(frozen=True)
class SelfEpistemicNeedIdentityMatcher:
    read_only: bool = True
    creates_questions: bool = False
    assigns_relevance: bool = False
    creates_goals: bool = False
    creates_acquisition_plans: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    claims_subjective_experience: bool = False

    def compare(
        self,
        left: EpistemicNeedIdentityReference,
        right: EpistemicNeedIdentityReference,
    ) -> EpistemicNeedIdentityMatch:
        if not isinstance(left, EpistemicNeedIdentityReference) or not isinstance(
            right, EpistemicNeedIdentityReference
        ):
            raise TypeError("matcher requires explicit epistemic need references")
        if left.identity is None or right.identity is None:
            relation = EpistemicNeedIdentityRelation.ABSTAIN
        elif left.identity == right.identity:
            relation = EpistemicNeedIdentityRelation.MATCH
        else:
            relation = EpistemicNeedIdentityRelation.MISMATCH
        return EpistemicNeedIdentityMatch(
            relation=relation,
            left_source_reference=left.source_reference,
            right_source_reference=right.source_reference,
        )
