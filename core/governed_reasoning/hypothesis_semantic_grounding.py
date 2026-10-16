from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
    GovernedExplicitHypothesisSource,
)
from core.governed_reasoning.governed_hypothesis_formation import (
    GovernedHypothesisCandidate,
)


class HypothesisStructuredSemanticsKind(StrEnum):
    SCENARIO = "scenario"
    CAUSAL = "causal"


@dataclass(frozen=True)
class GovernedHypothesisStructuredSemantics:
    """Explicit semantics with provenance; never inferred from candidate text."""

    candidate_id: str
    candidate_fingerprint: str
    proposition: str
    kind: HypothesisStructuredSemanticsKind | str
    source_reference: str
    source_fingerprint: str
    provenance_authority: str
    world_domain: str | None = None
    fact_key: str | None = None
    assumed_value: str | None = None
    cause_domain: str | None = None
    cause_key: str | None = None
    cause_value: str | None = None
    effect_domain: str | None = None
    effect_key: str | None = None
    effect_value: str | None = None
    temporal_scope: str = "current"
    evidence_codes: tuple[str, ...] = ()
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    inferred_from_text: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    persists_results: bool = False
    creates_facts: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        kind = HypothesisStructuredSemanticsKind(self.kind)
        required = (
            self.candidate_id,
            self.candidate_fingerprint,
            self.proposition,
            self.source_reference,
            self.source_fingerprint,
            self.provenance_authority,
            self.temporal_scope,
        )
        if any(not value.strip() for value in required):
            raise ValueError("structured hypothesis semantics lineage cannot be blank")
        if len(self.candidate_fingerprint) != 64:
            raise ValueError("structured semantics require candidate fingerprint")
        if len(self.source_fingerprint) != 64:
            raise ValueError("structured semantics require source fingerprint")
        if self.temporal_scope not in {"current", "future"}:
            raise ValueError("structured semantics temporal scope is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("structured semantics must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                self.inferred_from_text,
                self.uses_llm,
                self.uses_retrieval,
                self.persists_results,
                self.creates_facts,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("structured hypothesis semantics violate governed limits")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("structured semantics evidence codes cannot be blank")
        self._validate_shape(kind)
        object.__setattr__(self, "kind", kind)

    def _validate_shape(self, kind: HypothesisStructuredSemanticsKind) -> None:
        scenario = (self.world_domain, self.fact_key, self.assumed_value)
        causal = (
            self.cause_domain,
            self.cause_key,
            self.cause_value,
            self.effect_domain,
            self.effect_key,
            self.effect_value,
        )
        if kind is HypothesisStructuredSemanticsKind.SCENARIO:
            if any(item is None or not item.strip() for item in scenario):
                raise ValueError("scenario semantics require world domain/key/value")
            if any(item is not None for item in causal):
                raise ValueError("scenario semantics cannot contain causal fields")
            return
        if any(item is None or not item.strip() for item in causal):
            raise ValueError("causal semantics require cause/effect domain/key/value")
        if any(item is not None for item in scenario):
            raise ValueError("causal semantics cannot contain scenario fields")


class GovernedHypothesisSemanticGroundingFoundationV1:
    """Admit explicit structured semantics for one exact formed hypothesis candidate."""

    def admit(
        self,
        candidate: GovernedHypothesisCandidate,
        semantics: GovernedHypothesisStructuredSemantics,
    ) -> GovernedExplicitHypothesisSource:
        if semantics.candidate_id != candidate.candidate_id:
            raise ValueError("structured semantics candidate identity does not match")
        if semantics.candidate_fingerprint != candidate.source_claim_fingerprint:
            raise ValueError("structured semantics candidate lineage does not match")
        if semantics.proposition.strip() != candidate.proposition.strip():
            raise ValueError(
                "structured semantics proposition does not match candidate"
            )

        kind = HypothesisStructuredSemanticsKind(semantics.kind)
        source_fingerprint = sha256(
            repr(
                (
                    candidate.candidate_id,
                    candidate.source_claim_fingerprint,
                    semantics.source_reference,
                    semantics.source_fingerprint,
                    semantics.provenance_authority,
                    kind.value,
                    semantics.world_domain,
                    semantics.fact_key,
                    semantics.assumed_value,
                    semantics.cause_domain,
                    semantics.cause_key,
                    semantics.cause_value,
                    semantics.effect_domain,
                    semantics.effect_key,
                    semantics.effect_value,
                    semantics.temporal_scope,
                    semantics.evidence_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        source_id = (
            "explicit-hypothesis-source-grounded-"
            f"{source_fingerprint[:16]}"
        )
        return GovernedExplicitHypothesisSource(
            source_id=source_id,
            kind=ExplicitHypothesisSourceKind(kind.value),
            proposition=candidate.proposition,
            source_reference=semantics.source_reference,
            source_fingerprint=source_fingerprint,
            world_domain=semantics.world_domain,
            fact_key=semantics.fact_key,
            assumed_value=semantics.assumed_value,
            cause_domain=semantics.cause_domain,
            cause_key=semantics.cause_key,
            cause_value=semantics.cause_value,
            effect_domain=semantics.effect_domain,
            effect_key=semantics.effect_key,
            effect_value=semantics.effect_value,
            temporal_scope=semantics.temporal_scope,
            evidence_codes=tuple(
                dict.fromkeys(
                    (
                        *candidate.rationale_codes,
                        *semantics.evidence_codes,
                        f"semantic_provenance:{semantics.provenance_authority}",
                        f"semantic_source:{semantics.source_reference}",
                        f"semantic_source_fingerprint:{semantics.source_fingerprint}",
                    )
                )
            ),
        )
