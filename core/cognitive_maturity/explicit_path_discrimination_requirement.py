from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)

AUTHORIZED_PROVENANCE = (
    "governed_explicit_path_discrimination_requirement_declaration"
)


@dataclass(frozen=True)
class ExplicitPathDiscriminationRequirementDeclaration:
    epistemic_need_identity: str
    path_a_capability_name: str
    path_a_declared_evidence_output: str
    path_b_capability_name: str
    path_b_declared_evidence_output: str
    requirement_identity: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    inferred_from_text: bool = False
    inferred_from_metadata: bool = False
    used_fuzzy_matching: bool = False
    used_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False

    def __post_init__(self) -> None:
        explicit_values = (
            self.epistemic_need_identity,
            self.path_a_capability_name,
            self.path_a_declared_evidence_output,
            self.path_b_capability_name,
            self.path_b_declared_evidence_output,
            self.requirement_identity,
            self.provenance_authority,
        )
        if any(not value.strip() for value in explicit_values):
            raise ValueError(
                "path discrimination declaration requires explicit identity"
            )
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError(
                "path discrimination declaration requires evidence codes"
            )
        if any(
            (
                self.inferred_from_text,
                self.inferred_from_metadata,
                self.used_fuzzy_matching,
                self.used_semantic_matching,
                self.uses_llm,
                self.uses_retrieval,
            )
        ):
            raise ValueError(
                "path discrimination requirement must not be inferred"
            )


@dataclass(frozen=True)
class ExplicitPathDiscriminationRequirement:
    path_a_eligibility: GovernedSelectionEligibility
    path_b_eligibility: GovernedSelectionEligibility
    epistemic_need_identity: str
    epistemic_need_source_reference: str
    epistemic_need_lineage_kind: str
    requirement_identity: str
    provenance_authority: str
    evidence_codes: tuple[str, ...]
    read_only: bool = True
    derivational: bool = True


@dataclass(frozen=True)
class ExplicitPathDiscriminationRequirementAdmission:
    read_only: bool = True
    derivational: bool = True
    mutates_eligibility: bool = False
    mutates_suitability: bool = False
    mutates_resolution_binding: bool = False
    queries_capability_registry: bool = False
    mutates_capability_registry: bool = False
    queries_official_runtime: bool = False
    mutates_official_runtime: bool = False
    creates_runtime_capability_graph: bool = False
    creates_runtime_readiness_evidence: bool = False
    creates_eligibility: bool = False
    reconstructs_eligibility: bool = False
    infers_discrimination_requirement: bool = False
    uses_fuzzy_matching: bool = False
    uses_semantic_matching: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    acquires_discriminating_evidence: bool = False
    evaluates_discriminating_evidence: bool = False
    scores_sources: bool = False
    compares_sources: bool = False
    ranks_sources: bool = False
    prefers_sources: bool = False
    filters_sources: bool = False
    selects_sources: bool = False
    selects_capabilities: bool = False
    plans_acquisition: bool = False
    authorizes_acquisition: bool = False
    acquires_evidence: bool = False
    certifies_truth: bool = False
    grants_authority: bool = False
    creates_questions: bool = False
    assigns_question_worthiness: bool = False
    assigns_relevance: bool = False
    invokes_curiosity: bool = False
    creates_goals: bool = False
    invokes_initiative: bool = False
    invokes_conversation: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    executes_actions: bool = False
    claims_subjective_experience: bool = False
    claims_consciousness: bool = False

    def admit(
        self,
        path_a: GovernedSelectionEligibility,
        path_b: GovernedSelectionEligibility,
        declaration: ExplicitPathDiscriminationRequirementDeclaration,
    ) -> ExplicitPathDiscriminationRequirement | None:
        if not isinstance(path_a, GovernedSelectionEligibility):
            raise TypeError("path_a must be GovernedSelectionEligibility")
        if not isinstance(path_b, GovernedSelectionEligibility):
            raise TypeError("path_b must be GovernedSelectionEligibility")
        if not isinstance(
            declaration,
            ExplicitPathDiscriminationRequirementDeclaration,
        ):
            raise TypeError(
                "declaration must be an explicit path discrimination requirement"
            )
        if not path_a.eligible_for_selection or not path_b.eligible_for_selection:
            return None
        if not self._same_need(path_a, path_b):
            return None
        if self._path_identity(path_a) == self._path_identity(path_b):
            return None
        if declaration.epistemic_need_identity != self._need_identity(path_a):
            return None
        if not self._declaration_matches_pair(declaration, path_a, path_b):
            return None
        if declaration.provenance_authority != AUTHORIZED_PROVENANCE:
            return None

        suitability = path_a.suitability
        return ExplicitPathDiscriminationRequirement(
            path_a_eligibility=path_a,
            path_b_eligibility=path_b,
            epistemic_need_identity=suitability.epistemic_need_identity,
            epistemic_need_source_reference=(
                suitability.epistemic_need_source_reference
            ),
            epistemic_need_lineage_kind=suitability.epistemic_need_lineage_kind,
            requirement_identity=declaration.requirement_identity,
            provenance_authority=declaration.provenance_authority,
            evidence_codes=declaration.evidence_codes,
        )

    @staticmethod
    def _need_identity(path: GovernedSelectionEligibility) -> str:
        return path.suitability.epistemic_need_identity

    @staticmethod
    def _same_need(
        path_a: GovernedSelectionEligibility,
        path_b: GovernedSelectionEligibility,
    ) -> bool:
        a = path_a.suitability
        b = path_b.suitability
        return all(
            (
                a.epistemic_need_identity == b.epistemic_need_identity,
                a.epistemic_need_source_reference
                == b.epistemic_need_source_reference,
                a.epistemic_need_lineage_kind == b.epistemic_need_lineage_kind,
            )
        )

    @staticmethod
    def _path_identity(
        path: GovernedSelectionEligibility,
    ) -> tuple[str, str]:
        suitability = path.suitability
        return (
            suitability.capability_name,
            suitability.declared_evidence_output,
        )

    @classmethod
    def _declaration_matches_pair(
        cls,
        declaration: ExplicitPathDiscriminationRequirementDeclaration,
        path_a: GovernedSelectionEligibility,
        path_b: GovernedSelectionEligibility,
    ) -> bool:
        declared_pair = {
            (
                declaration.path_a_capability_name,
                declaration.path_a_declared_evidence_output,
            ),
            (
                declaration.path_b_capability_name,
                declaration.path_b_declared_evidence_output,
            ),
        }
        actual_pair = {
            cls._path_identity(path_a),
            cls._path_identity(path_b),
        }
        return declared_pair == actual_pair
