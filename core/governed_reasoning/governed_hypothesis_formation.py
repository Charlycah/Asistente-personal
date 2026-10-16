from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.claims import Claim, ClaimType
from core.governed_reasoning.context import (
    ContextAssemblyStatus,
    ReasoningContextBundle,
)


class GovernedHypothesisFormationStatus(StrEnum):
    FORMED = "formed"
    INSUFFICIENT_ALTERNATIVES = "insufficient_alternatives"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedHypothesisCandidate:
    """One tentative proposition derived only from governed reasoning lineage."""

    candidate_id: str
    proposition: str
    source_claim_id: str
    source_claim_type: str
    source_claim_fingerprint: str
    evidence_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    epistemic_level: EpistemicLevel = EpistemicLevel.HYPOTHESIS
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    persists_results: bool = False
    creates_facts: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.candidate_id,
            self.proposition,
            self.source_claim_id,
            self.source_claim_type,
            self.source_claim_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("hypothesis candidate lineage cannot be blank")
        if not self.candidate_id.startswith("governed-hypothesis-candidate-"):
            raise ValueError("hypothesis candidate identifier is invalid")
        if len(self.source_claim_fingerprint) != 64:
            raise ValueError("hypothesis candidate requires claim fingerprint")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("hypothesis candidate requires rationale")
        if any(not item.strip() for item in self.evidence_ids):
            raise ValueError("hypothesis candidate evidence ids cannot be blank")
        if self.epistemic_level is not EpistemicLevel.HYPOTHESIS:
            raise ValueError("formed candidates must remain hypotheses")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("hypothesis formation must preserve reasoning authority")
        if not self.read_only or any(
            (
                self.persists_results,
                self.creates_facts,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_world_model,
                self.modifies_planning,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("hypothesis candidate violates governed limits")


@dataclass(frozen=True)
class GovernedHypothesisFormationReport:
    report_id: str
    status: GovernedHypothesisFormationStatus
    owner: str
    subject: str
    unknown_element: str
    question: str
    goal_reference: str
    reasoning_context_id: str
    reasoning_query_id: str
    candidates: tuple[GovernedHypothesisCandidate, ...]
    context_evidence_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "intellectual-evolution-hypothesis-formation-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_facts: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        required = (
            self.report_id,
            self.owner,
            self.subject,
            self.unknown_element,
            self.question,
            self.goal_reference,
            self.reasoning_context_id,
            self.reasoning_query_id,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("hypothesis formation lineage cannot be blank")
        if not self.report_id.startswith("governed-hypothesis-formation-"):
            raise ValueError("hypothesis formation report identifier is invalid")
        if len(self.source_fingerprint) != 64:
            raise ValueError("hypothesis formation requires SHA-256 lineage")
        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("hypothesis formation cannot repeat candidates")
        if self.status is GovernedHypothesisFormationStatus.FORMED:
            if len(self.candidates) < 2:
                raise ValueError("formed hypothesis set requires alternatives")
        elif len(self.candidates) >= 2:
            raise ValueError("non-formed report cannot expose full alternatives")
        if not self.rationale_codes:
            raise ValueError("hypothesis formation requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("hypothesis formation must preserve reasoning authority")
        if not self.read_only or not self.consultative or any(
            (
                self.persists_results,
                self.creates_facts,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("hypothesis formation violates governed limits")


class GovernedHypothesisFormationFoundationV1:
    """Form tentative alternatives only from already-governed reasoning claims."""

    _ELIGIBLE_CONTEXT_TYPES = {
        ClaimType.HYPOTHESIS,
        ClaimType.ASSUMPTION,
    }
    _ELIGIBLE_DERIVED_TYPES = {ClaimType.RULE_RESULT}

    def form(
        self,
        *,
        owner: str,
        subject: str,
        unknown_element: str,
        question: str,
        goal_reference: str,
        context: ReasoningContextBundle,
        derived_claims: tuple[Claim, ...] = (),
    ) -> GovernedHypothesisFormationReport:
        clean = tuple(
            value.strip()
            for value in (
                owner,
                subject,
                unknown_element,
                question,
                goal_reference,
            )
        )
        if any(not value for value in clean):
            raise ValueError("hypothesis formation input cannot be blank")
        owner_value, subject_value, unknown_value, question_value, goal_value = clean
        if context.query.owner.casefold() != owner_value.casefold():
            raise ValueError("hypothesis formation owner lineage does not match")
        if context.query.text.strip() != question_value:
            raise ValueError("hypothesis formation question lineage does not match")

        context_claims = tuple(
            claim
            for claim in context.claims
            if claim.normalized_type in self._ELIGIBLE_CONTEXT_TYPES
        )
        derived = tuple(
            claim
            for claim in derived_claims
            if claim.normalized_type in self._ELIGIBLE_DERIVED_TYPES
        )
        source_claims = self._dedupe_claims((*context_claims, *derived))
        candidates = tuple(self._candidate(item) for item in source_claims)

        if (
            context.normalized_status
            in {ContextAssemblyStatus.REVIEW_REQUIRED, ContextAssemblyStatus.BLOCKED}
        ):
            status = GovernedHypothesisFormationStatus.REVIEW_REQUIRED
            candidates = ()
            rationale = (
                "hypothesis_formation:reasoning_context_requires_review",
                "hypothesis_formation:no_semantic_inference",
            )
        elif len(candidates) < 2:
            status = GovernedHypothesisFormationStatus.INSUFFICIENT_ALTERNATIVES
            rationale = (
                "hypothesis_formation:fewer_than_two_governed_alternatives",
                "hypothesis_formation:no_semantic_inference",
            )
        else:
            status = GovernedHypothesisFormationStatus.FORMED
            rationale = (
                "hypothesis_formation:governed_alternatives_formed",
                "hypothesis_formation:existing_reasoning_claims_reused",
                "hypothesis_formation:no_semantic_inference",
            )

        evidence_ids = tuple(item.evidence_id for item in context.evidence)
        fingerprint = sha256(
            repr(
                (
                    owner_value.casefold(),
                    subject_value,
                    unknown_value,
                    question_value,
                    goal_value,
                    context.context_id,
                    context.query.query_id,
                    tuple(item.candidate_id for item in candidates),
                    evidence_ids,
                    rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHypothesisFormationReport(
            report_id=f"governed-hypothesis-formation-{fingerprint[:24]}",
            status=status,
            owner=owner_value,
            subject=subject_value,
            unknown_element=unknown_value,
            question=question_value,
            goal_reference=goal_value,
            reasoning_context_id=context.context_id,
            reasoning_query_id=context.query.query_id,
            candidates=candidates,
            context_evidence_ids=evidence_ids,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _dedupe_claims(claims: tuple[Claim, ...]) -> tuple[Claim, ...]:
        by_fingerprint: dict[str, Claim] = {}
        for claim in claims:
            by_fingerprint.setdefault(claim.fingerprint, claim)
        return tuple(
            by_fingerprint[key]
            for key in sorted(by_fingerprint)
        )

    @staticmethod
    def _candidate(claim: Claim) -> GovernedHypothesisCandidate:
        proposition = " ".join(
            (
                claim.subject.strip(),
                claim.predicate.strip(),
                claim.object_value.strip(),
            )
        )
        fingerprint = sha256(
            repr(
                (
                    claim.claim_id,
                    claim.fingerprint,
                    proposition,
                    tuple(link.evidence_id for link in claim.evidence_links),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHypothesisCandidate(
            candidate_id=f"governed-hypothesis-candidate-{fingerprint[:24]}",
            proposition=proposition,
            source_claim_id=claim.claim_id,
            source_claim_type=claim.normalized_type.value,
            source_claim_fingerprint=claim.fingerprint,
            evidence_ids=tuple(link.evidence_id for link in claim.evidence_links),
            rationale_codes=(
                "hypothesis_candidate:projected_from_governed_claim",
                f"hypothesis_candidate:source_type:{claim.normalized_type.value}",
            ),
        )
