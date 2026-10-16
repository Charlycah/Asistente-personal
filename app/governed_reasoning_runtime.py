from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from typing import TYPE_CHECKING

from app.governed_explanatory_model_productive_consumption import (
    GovernedExplanatoryModelProductiveConsumption,
    GovernedExplanatoryModelProductiveConsumptionV1,
)
from app.governed_explanatory_model_revision import (
    GovernedEvidenceDrivenExplanatoryModelRevisionV1,
    GovernedExplanatoryModelRevision,
    GovernedExplanatoryModelRevisionStatus,
)
from app.governed_long_horizon_investigation_rr2_terminal_closure import (
    GovernedInvestigationRR2TerminalClosureResult,
    GovernedInvestigationRR2TerminalClosureStatus,
)
from core.cognitive_maturity import EpistemicEvidenceAdapter
from core.cognitive_memory import LearningCategory
from core.cognitive_memory_recall import (
    CognitiveMemoryRecallItem,
    CognitiveMemoryRecallResult,
)
from core.cognitive_memory_store import CognitiveMemoryRecord
from core.cognitive_runtime_orchestration import CognitiveRuntimeContribution
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
    build_governed_conversation_turn_identity,
)
from core.governed_reasoning import (
    BoundedModalSituationalImplicationStatus,
    BoundedNonRuleDerivationStatus,
    BoundedProductiveSupportInterpretationStatus,
    BoundedSituationalHypothesisKind,
    BoundedSituationalHypothesisStatus,
    ClaimRegistryManager,
    ConflictResolutionManager,
    DecisionRecordManager,
    EvidenceRegistry,
    ExplicitTurnContextualGroupingStatus,
    ExplicitTurnPropositionGroundingStatus,
    ExplicitTurnTransientClaimProjectionStatus,
    GovernedBoundedExplicitTurnPropositionGrounder,
    GovernedBoundedModalSituationalImplicationFoundationV1,
    GovernedBoundedNonRuleDerivationFoundationV1,
    GovernedBoundedProductiveSupportInterpreterV1,
    GovernedBoundedSituationalHypothesisFormer,
    GovernedContextAssembler,
    GovernedExplicitTurnContextualClaimGrouper,
    GovernedExplicitTurnTransientClaimProjector,
    GovernedInferenceEngine,
    GovernedReasoningOrchestrator,
    GovernedReasoningResult,
    GovernedRecalledKnowledgeStructuralProjector,
    GovernedSituationalHypothesisTransientClaimProjector,
    GovernedStructuralKnowledgeTransferMatcher,
    GovernedTargetProblemStructuralProjector,
    GovernedTurnBoundProductiveSituationalClaimBinder,
    InMemoryDecisionRecordRepository,
    InMemoryInferenceRuleRegistry,
    ReasoningQuery,
    SituationalHypothesisTransientClaimProjectionStatus,
    StructuralKnowledgeTransferStatus,
    TurnBoundProductiveSituationalClaimBindingStatus,
)
from core.governed_reasoning.causal_prediction import (
    CausalHypothesis,
    GovernedCausalPredictiveReasoner,
)
from core.governed_reasoning.counterfactual_path_comparison import (
    CounterfactualPathComparisonStatus,
    GovernedCounterfactualPathComparator,
    GovernedCounterfactualPathComparison,
)
from core.governed_reasoning.cross_domain_concept_synthesis import (
    CrossDomainConceptSource,
    CrossDomainConceptSynthesisStatus,
    GovernedCrossDomainConceptSynthesisCandidate,
    GovernedCrossDomainConceptSynthesizer,
)
from core.governed_reasoning.epistemic_sufficiency import (
    GovernedEpistemicSufficiencyAssessment,
    GovernedEpistemicSufficiencyAssessmentFoundationV1,
)
from core.governed_reasoning.explicit_hypothesis_source import (
    GovernedExplicitHypothesisSource,
    GovernedExplicitHypothesisSourceAdapterV1,
    GovernedExplicitHypothesisSourceResult,
)
from core.governed_reasoning.governed_hypothesis_formation import (
    GovernedHypothesisCandidate,
)
from core.governed_reasoning.hierarchical_concept_composition import (
    CanonicalProductiveConceptEpisode,
    GovernedHierarchicalConceptCandidate,
    GovernedHierarchicalConceptComposer,
    HierarchicalConceptCompositionStatus,
)
from core.governed_reasoning.hierarchical_structural_analogy import (
    GovernedHierarchicalStructuralAnalogyCandidate,
    GovernedHierarchicalStructuralAnalogyMatcher,
    HierarchicalStructuralAnalogyStatus,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepener,
    GovernedHypothesisDeepeningReport,
)
from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstruction,
    GovernedLongitudinalIntellectualReconstructionFoundationV1,
    LongitudinalIntellectualCurrentEpistemicView,
)
from core.governed_reasoning.multistage_causal_path import (
    GovernedMultiStageCausalPath,
    GovernedMultiStageCausalPathComposer,
    MultiStageCausalPathStatus,
)
from core.governed_reasoning.productive_abstraction_admission import (
    CanonicalProductiveAbstractionEpisode,
    GovernedProductiveAbstractionAdmission,
    GovernedProductiveAbstractionAdmissionResult,
)
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeObservation,
)
from core.governed_reasoning.reasoning_method_provenance import (
    GovernedReasoningMethodProvenance,
    GovernedReasoningMethodProvenanceFoundationV1,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityAssessmentFoundationV1,
)
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulator,
    ScenarioHypothesis,
)
from core.persistent_world_model import PersistentWorldSnapshot
from core.scope_guard import ScopeDomain

if TYPE_CHECKING:
    from app.governed_explanatory_model_investigation_reentry import (
        GovernedExplanatoryModelInvestigationReentry,
    )

from .productive_temporary_rule_intake import ProductiveTemporaryRuleIntake


@dataclass(frozen=True)
class CanonicalProductiveTerminalResearchIntellectualRealization:
    """Read-only binding of terminal investigation state to reasoning artifacts."""

    episode_id: str
    originating_reasoning_id: str
    world_snapshot_id: str
    stopping_reason: object
    terminal_closure: GovernedInvestigationRR2TerminalClosureResult
    epistemic_assessment: CanonicalProductiveEpistemicAssessmentEpisode | None
    explanatory_model: GovernedExplanatoryModelProductiveConsumption | None
    explanatory_model_revision: GovernedExplanatoryModelRevision | None
    rationale_codes: tuple[str, ...]
    reasons: bool = False
    creates_requirement: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    modifies_memory: bool = False
    creates_learning: bool = False
    starts_background_process: bool = False
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True

    def __post_init__(self) -> None:
        if not all(
            item.strip()
            for item in (
                self.episode_id,
                self.originating_reasoning_id,
                self.world_snapshot_id,
            )
        ):
            raise ValueError("terminal research realization requires exact lineage")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("terminal research realization requires rationale codes")
        if self.canonical_authority != "governed_reasoning" or not self.read_only:
            raise ValueError("terminal research realization must remain read-only")
        if any(
            (
                self.reasons,
                self.creates_requirement,
                self.invokes_planning,
                self.invokes_authorization,
                self.invokes_execution,
                self.modifies_memory,
                self.creates_learning,
                self.starts_background_process,
            )
        ):
            raise ValueError(
                "terminal research realization exposes forbidden authority"
            )


@dataclass(frozen=True)
class CanonicalProductiveReasoningEpisode:
    owner: str
    session_id: str
    turn_id: str
    input_fingerprint: str
    result: GovernedReasoningResult
    source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not all(
            item.strip()
            for item in (
                self.owner,
                self.session_id,
                self.turn_id,
                self.input_fingerprint,
                self.source_fingerprint,
            )
        ):
            raise ValueError("productive reasoning episode requires exact lineage")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("productive reasoning episode must preserve authority")
        if any(
            (
                not self.read_only,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.grants_authority,
            )
        ):
            raise ValueError("productive reasoning episode violates governed limits")


class CanonicalProductiveEpistemicAssessmentStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    REVIEW_REQUIRED = "review_required"
    ASSESSED = "assessed"


@dataclass(frozen=True)
class CanonicalProductiveEpistemicAssessmentEpisode:
    assessment_episode_id: str
    status: CanonicalProductiveEpistemicAssessmentStatus | str
    owner: str
    session_id: str
    turn_id: str
    reasoning_episode_fingerprint: str
    hypothesis_source_result: GovernedExplicitHypothesisSourceResult
    world_snapshot_id: str
    productive_reference_id: str | None
    deepening: GovernedHypothesisDeepeningReport | None
    sufficiency: GovernedEpistemicSufficiencyAssessment | None
    quality: GovernedReasoningQualityAssessment | None
    method_provenance: GovernedReasoningMethodProvenance | None
    method_outcome: GovernedReasoningMethodOutcomeObservation | None
    source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        status = CanonicalProductiveEpistemicAssessmentStatus(self.status)
        if not self.assessment_episode_id.startswith(
            "productive-epistemic-assessment-"
        ):
            raise ValueError("productive epistemic assessment id is invalid")
        if not all(
            item.strip()
            for item in (
                self.owner,
                self.session_id,
                self.turn_id,
                self.reasoning_episode_fingerprint,
                self.world_snapshot_id,
                self.source_fingerprint,
            )
        ):
            raise ValueError("productive epistemic assessment requires lineage")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("productive epistemic assessment must preserve authority")
        if any(
            (
                not self.read_only,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("productive epistemic assessment violates limits")
        complete = (
            self.productive_reference_id is not None
            and self.deepening is not None
            and self.sufficiency is not None
            and self.quality is not None
            and self.method_provenance is not None
            and self.method_outcome is not None
        )
        if status is CanonicalProductiveEpistemicAssessmentStatus.ASSESSED:
            if not complete:
                raise ValueError("assessed epistemic episode requires full chain")
        elif any(
            item is not None
            for item in (
                self.productive_reference_id,
                self.deepening,
                self.sufficiency,
                self.quality,
                self.method_provenance,
                self.method_outcome,
            )
        ):
            raise ValueError("non-assessed epistemic episode cannot carry chain")
        object.__setattr__(self, "status", status)


class CanonicalProductiveReasoningSource:
    """Project the official turn-scoped governed episode into cognitive runtime."""

    def __init__(
        self,
        gateway: "OfficialGovernedReasoningRuntimeGateway",
        ordinary_turn_multisource_reachability_adapter: object | None = None,
    ) -> None:
        self.gateway = gateway
        self.ordinary_turn_multisource_reachability_adapter = (
            ordinary_turn_multisource_reachability_adapter
        )

    def __call__(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
        recalled_memory_evidence=(),
        visual_context_contribution: CognitiveRuntimeContribution | None = None,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
    ) -> GovernedReasoningResult:
        has_explicit_selection = bool(
            explicit_document_ids or explicit_sources or explicit_evidence_references
        )
        if has_explicit_selection:
            adapter = self.ordinary_turn_multisource_reachability_adapter
            if not callable(getattr(adapter, "admit_and_reason", None)):
                raise RuntimeError(
                    "explicit multisource selection requires the certified "
                    "ordinary-turn convergence seam"
                )
            result = adapter.admit_and_reason(
                text=text,
                owner=owner,
                explicit_document_ids=explicit_document_ids,
                explicit_sources=explicit_sources,
                explicit_evidence_references=explicit_evidence_references,
                visual_context_contribution=visual_context_contribution,
                now=now,
            )
            if result is None:
                raise RuntimeError(
                    "explicit multisource convergence unexpectedly abstained"
                )
            return result

        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        episode = self.gateway.productive_episode(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if episode is None:
            episode = self.gateway.evaluate_productive_episode(
                owner=owner,
                session_id=session_id,
                text=text,
                now=now,
                turn_id=identity.turn_id,
                scope_reference=session_id,
                observe_productive_intake=False,
                recalled_memory_evidence=recalled_memory_evidence,
                visual_context_contribution=visual_context_contribution,
            )
        return episode.result

    def reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose exact same-turn selective epistemic references, when present."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        epistemic = self.gateway.productive_epistemic_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        abstraction = self.gateway.productive_abstraction_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        concept = self.gateway.productive_concept_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        analogy = self.gateway.productive_hierarchical_analogy_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        explanatory = self.gateway.productive_explanatory_model_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        inquiry = self.gateway.productive_explanatory_investigation_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        revision = self.gateway.productive_explanatory_model_revision_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        cross_domain = self.gateway.productive_cross_domain_synthesis_reference_ids(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        counterfactual = (
            self.gateway.productive_counterfactual_path_comparison_reference_ids(
                owner=owner,
                session_id=session_id,
                turn_id=identity.turn_id,
            )
        )
        return tuple(
            dict.fromkeys(
                (
                    *epistemic,
                    *abstraction,
                    *concept,
                    *analogy,
                    *explanatory,
                    *inquiry,
                    *revision,
                    *cross_domain,
                    *counterfactual,
                )
            )
        )

    def abstraction_context_lines(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose same-turn abstraction read-only to cognitive runtime."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        episode = self.gateway.productive_abstraction_episode(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if episode is None:
            return ()
        candidate = episode.abstraction_candidate
        return (
            (
                "Abstracción relacional gobernada disponible: "
                f"{candidate.invariant_relation} → {candidate.invariant_outcome}."
            ),
            (
                "Usarla sólo como contexto consultivo y revisable; "
                "no establece verdad ni autoriza aprendizaje, transferencia o acción."
            ),
        )

    def concept_context_lines(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose same-turn hierarchical concept read-only to cognitive runtime."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        episode = self.gateway.productive_concept_episode(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if episode is None:
            return ()
        candidate = episode.concept_candidate
        component_summary = "; ".join(
            f"{item.relation} → {item.outcome}" for item in candidate.components
        )
        return (
            f"Concepto jerárquico gobernado disponible: {component_summary}.",
            (
                "Usarlo sólo como contexto conceptual consultivo y revisable; "
                "no establece verdad ni autoriza memoria, aprendizaje, "
                "transferencia o acción."
            ),
        )

    def cross_domain_synthesis_context_lines(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose same-turn cross-domain synthesis as consultative context."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        candidate = self.gateway.productive_cross_domain_synthesis_candidate(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if candidate is None:
            return ()
        return (
            (
                "Síntesis conceptual interdominio gobernada disponible: "
                f"{candidate.source_domain_reference} ↔ "
                f"{candidate.target_domain_reference}, con "
                f"{len(candidate.correspondences)} correspondencias estructurales."
            ),
            (
                "Usarla sólo como contexto consultivo y revisable; la analogía "
                "interdominio no establece verdad, causalidad, inferencia, "
                "transferencia, aprendizaje ni acción."
            ),
        )

    def hierarchical_analogy_context_lines(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose same-turn hierarchical analogy as consultative context."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        candidate = self.gateway.productive_hierarchical_analogy_candidate(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if candidate is None:
            return ()
        pairs = "; ".join(
            f"{item.relation} → {item.outcome}"
            for item in candidate.component_correspondences
        )
        return (
            f"Analogía jerárquica gobernada disponible: {pairs}.",
            (
                "Usarla sólo como comparación estructural consultiva y revisable; "
                "no establece verdad ni autoriza inferencia, aprendizaje, "
                "transferencia o acción."
            ),
        )

    def counterfactual_path_comparison_context_lines(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose same-turn counterfactual path comparison consultatively."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        comparison = self.gateway.productive_counterfactual_path_comparison(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if (
            comparison is None
            or comparison.status
            is not CounterfactualPathComparisonStatus.COMPARISON_CANDIDATE
        ):
            return ()
        return (
            (
                "Comparación contrafactual gobernada disponible: "
                f"{len(comparison.path_ids)} trayectorias explícitas sobre "
                f"baseline {comparison.baseline_snapshot_id}, con "
                f"{len(comparison.divergences)} divergencias."
            ),
            (
                "Usarla sólo como contexto consultivo y revisable; no establece "
                "verdad ni causalidad, no elige una trayectoria verdadera y no "
                "autoriza planificación, aprendizaje, transferencia o acción."
            ),
        )

    def explanatory_model_context_lines(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose same-turn ordinary multi-hypothesis model consultatively."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        consumption = self.gateway.productive_explanatory_model_consumption(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        return consumption.context_lines() if consumption is not None else ()

    def explanatory_model_revision_context_lines(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> tuple[str, ...]:
        """Expose same-turn evidence-driven model revision consultatively."""
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(request, now)
        revision = self.gateway.productive_explanatory_model_revision(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        return revision.context_lines() if revision is not None else ()


@dataclass(frozen=True)
class CanonicalNovelSynthesisGovernedHypothesisAdmission:
    synthesis_source_fingerprint: str
    source_domain_reference: str
    target_domain_reference: str
    source_concept_episode_id: str
    target_concept_episode_id: str
    hypothesis_candidate: GovernedHypothesisCandidate
    rationale_codes: tuple[str, ...]
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    synthesis_origin: bool = True
    registers_synthesis_as_evidence: bool = False
    invokes_planning: bool = False
    invokes_investigation: bool = False
    invokes_execution: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    starts_background_process: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.synthesis_source_fingerprint,
            self.source_domain_reference,
            self.target_domain_reference,
            self.source_concept_episode_id,
            self.target_concept_episode_id,
        )
        if any(not value.strip() for value in required):
            raise ValueError("novel synthesis hypothesis admission requires lineage")
        if len(self.synthesis_source_fingerprint) != 64:
            raise ValueError(
                "novel synthesis hypothesis admission requires fingerprint"
            )
        if not self.rationale_codes:
            raise ValueError("novel synthesis hypothesis admission requires rationale")
        if self.hypothesis_candidate.evidence_ids:
            raise ValueError("synthesis must not count as evidence for itself")
        if self.hypothesis_candidate.source_claim_fingerprint != (
            self.synthesis_source_fingerprint
        ):
            raise ValueError("novel synthesis hypothesis lineage mismatch")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("novel synthesis hypothesis authority mismatch")
        if any(
            (
                not self.read_only,
                not self.synthesis_origin,
                self.registers_synthesis_as_evidence,
                self.invokes_planning,
                self.invokes_investigation,
                self.invokes_execution,
                self.creates_memory,
                self.creates_learning_candidate,
                self.starts_background_process,
                self.grants_authority,
            )
        ):
            raise ValueError("novel synthesis hypothesis admission violates limits")


class GovernedCreativeCandidateCriticalDispositionStatus(StrEnum):
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedCreativeCandidateCriticalDisposition:
    disposition_id: str
    status: GovernedCreativeCandidateCriticalDispositionStatus | str
    synthesis_source_fingerprint: str
    hypothesis_candidate_id: str
    hypothesis_source_claim_fingerprint: str
    critical_evaluation_reference_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    independent_evidence_required: bool = True
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    derived_assessment: bool = True
    registers_as_evidence: bool = False
    establishes_truth: bool = False
    establishes_causality: bool = False
    creates_proposal: bool = False
    invokes_planning: bool = False
    invokes_execution: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        status = GovernedCreativeCandidateCriticalDispositionStatus(self.status)
        if not self.disposition_id.startswith("creative-candidate-disposition-"):
            raise ValueError("creative candidate disposition id is invalid")
        if len(self.synthesis_source_fingerprint) != 64:
            raise ValueError("creative candidate disposition requires fingerprint")
        if not all(
            value.strip()
            for value in (
                self.hypothesis_candidate_id,
                self.hypothesis_source_claim_fingerprint,
            )
        ):
            raise ValueError(
                "creative candidate disposition requires hypothesis lineage"
            )
        if (
            self.hypothesis_source_claim_fingerprint
            != self.synthesis_source_fingerprint
        ):
            raise ValueError("creative candidate disposition lineage mismatch")
        if not self.rationale_codes:
            raise ValueError("creative candidate disposition requires rationale")
        if (
            status
            is not GovernedCreativeCandidateCriticalDispositionStatus.REVIEW_REQUIRED
        ):
            raise ValueError("creative candidate disposition status is unsupported")
        if self.critical_evaluation_reference_ids:
            raise ValueError(
                "unsupported creative candidate cannot claim evaluation refs"
            )
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("creative candidate disposition authority mismatch")
        if any(
            (
                not self.independent_evidence_required,
                not self.read_only,
                not self.derived_assessment,
                self.registers_as_evidence,
                self.establishes_truth,
                self.establishes_causality,
                self.creates_proposal,
                self.invokes_planning,
                self.invokes_execution,
                self.creates_memory,
                self.creates_learning,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("creative candidate disposition violates governed limits")
        object.__setattr__(self, "status", status)


@dataclass(frozen=True)
class GovernedInvestigationEpisodeBudgetIntrospectionView:
    episode_id: str
    originating_reasoning_id: str
    source_reference: str
    world_snapshot_id: str
    requirement_ids: tuple[str, ...]
    plan_ids: tuple[str, ...]
    authorization_ids: tuple[str, ...]
    execution_ids: tuple[str, ...]
    local_execution_ids: tuple[str, ...]
    reentry_ids: tuple[str, ...]
    consumed_acquisitions: int
    max_acquisitions: int
    remaining_acquisitions: int
    current_step: int
    status: object
    stopping_reason: object


@dataclass(frozen=True)
class GovernedReasoningRuntimeSnapshot:
    evaluations: int
    last_owner: str | None
    last_status: str | None
    last_confidence: float | None
    last_requires_human_review: bool


def build_default_governed_reasoning_orchestrator() -> GovernedReasoningOrchestrator:
    """Build a safe empty orchestrator that abstains until knowledge is registered."""
    return GovernedReasoningOrchestrator(
        context_assembler=GovernedContextAssembler(
            claim_registry=ClaimRegistryManager(),
            evidence_registry=EvidenceRegistry(),
        ),
        inference_engine=GovernedInferenceEngine(InMemoryInferenceRuleRegistry()),
        conflict_manager=ConflictResolutionManager(),
        decision_manager=DecisionRecordManager(InMemoryDecisionRecordRepository()),
        pre_inference_observer=EpistemicEvidenceAdapter().observe_claims,
    )


class OfficialGovernedReasoningRuntimeGateway:
    """Official observable facade over ROBY's governed reasoning pipeline."""

    _STATUS_TRIGGERS = (
        "estado del runtime de razonamiento gobernado",
        "estado de razonamiento gobernado",
    )
    _AUDIT_TRIGGERS = (
        "auditá runtime de razonamiento gobernado",
        "audita runtime de razonamiento gobernado",
        "evaluá runtime de razonamiento gobernado",
        "evalua runtime de razonamiento gobernado",
    )

    def __init__(
        self,
        orchestrator: GovernedReasoningOrchestrator | None = None,
    ) -> None:
        self.orchestrator = (
            orchestrator or build_default_governed_reasoning_orchestrator()
        )
        registry = self.orchestrator.inference_engine.registry
        if not isinstance(registry, InMemoryInferenceRuleRegistry):
            raise TypeError(
                "productive temporary rule intake requires canonical in-memory registry"
            )
        self.productive_temporary_rule_intake = ProductiveTemporaryRuleIntake(registry)
        self.recalled_knowledge_structural_projector = (
            GovernedRecalledKnowledgeStructuralProjector()
        )
        self.target_problem_structural_projector = (
            GovernedTargetProblemStructuralProjector()
        )
        self.structural_knowledge_transfer_matcher = (
            GovernedStructuralKnowledgeTransferMatcher()
        )
        self._productive_recalled_knowledge_references: dict[
            tuple[str, str, str], tuple[str, ...]
        ] = {}
        self.productive_abstraction_admission = GovernedProductiveAbstractionAdmission()
        self.hierarchical_concept_composer = GovernedHierarchicalConceptComposer()
        self.hierarchical_structural_analogy_matcher = (
            GovernedHierarchicalStructuralAnalogyMatcher()
        )
        self.cross_domain_concept_synthesizer = GovernedCrossDomainConceptSynthesizer()
        self.multistage_causal_path_composer = GovernedMultiStageCausalPathComposer()
        self.counterfactual_path_comparator = GovernedCounterfactualPathComparator()
        self._productive_abstraction_results: dict[
            tuple[str, str, str], GovernedProductiveAbstractionAdmissionResult
        ] = {}
        self._productive_concept_episodes: dict[
            tuple[str, str, str], CanonicalProductiveConceptEpisode
        ] = {}
        self._productive_abstractions_by_scope: dict[
            tuple[str, str, str],
            dict[tuple[str, str], CanonicalProductiveAbstractionEpisode],
        ] = {}
        self._productive_concept_history_by_scope: dict[
            tuple[str, str, str], CanonicalProductiveConceptEpisode
        ] = {}
        self._productive_hierarchical_analogies: dict[
            tuple[str, str, str], GovernedHierarchicalStructuralAnalogyCandidate
        ] = {}
        self._productive_concepts_by_domain: dict[
            tuple[str, str, str], CanonicalProductiveConceptEpisode
        ] = {}
        self._productive_cross_domain_syntheses: dict[
            tuple[str, str, str], GovernedCrossDomainConceptSynthesisCandidate
        ] = {}
        self._productive_multistage_causal_paths: dict[
            tuple[str, str, str], GovernedMultiStageCausalPath
        ] = {}
        self._productive_counterfactual_path_comparisons: dict[
            tuple[str, str, str], GovernedCounterfactualPathComparison
        ] = {}
        self._evaluations = 0
        self._last_owner: str | None = None
        self._last_result: GovernedReasoningResult | None = None
        self._productive_episodes: dict[
            tuple[str, str], CanonicalProductiveReasoningEpisode
        ] = {}
        self._productive_epistemic_episodes: dict[
            tuple[str, str, str], CanonicalProductiveEpistemicAssessmentEpisode
        ] = {}
        self._ordinary_scenario_hypotheses: dict[
            tuple[str, str, str], dict[tuple[str, ...], ScenarioHypothesis]
        ] = {}
        self._ordinary_causal_hypotheses: dict[
            tuple[str, str, str], dict[tuple[str, ...], CausalHypothesis]
        ] = {}
        self._productive_explanatory_models: dict[
            tuple[str, str, str], GovernedExplanatoryModelProductiveConsumption
        ] = {}
        self.explanatory_model_revision = (
            GovernedEvidenceDrivenExplanatoryModelRevisionV1()
        )
        self._productive_explanatory_model_revisions: dict[
            tuple[str, str, str], GovernedExplanatoryModelRevision
        ] = {}
        from app.governed_explanatory_model_investigation_reentry import (
            GovernedExplanatoryModelInvestigationReentryV1,
        )

        self.explanatory_model_investigation_reentry = (
            GovernedExplanatoryModelInvestigationReentryV1()
        )
        self._productive_explanatory_investigation_reentries: dict[
            tuple[str, str, str], GovernedExplanatoryModelInvestigationReentry
        ] = {}

    def terminal_research_intellectual_realization(
        self,
        *,
        terminal_closure: GovernedInvestigationRR2TerminalClosureResult,
        epistemic_assessment: (
            CanonicalProductiveEpistemicAssessmentEpisode | None
        ) = None,
        explanatory_model: GovernedExplanatoryModelProductiveConsumption | None = None,
        explanatory_model_revision: GovernedExplanatoryModelRevision | None = None,
    ) -> CanonicalProductiveTerminalResearchIntellectualRealization:
        """Project a closed investigation and existing reasoning artifacts read-only."""
        if (
            terminal_closure.status
            is not GovernedInvestigationRR2TerminalClosureStatus.CLOSED
            or not terminal_closure.episode_closed
            or terminal_closure.stopping_reason is None
        ):
            raise ValueError(
                "terminal research realization requires closed investigation"
            )
        if (
            epistemic_assessment is not None
            and epistemic_assessment.world_snapshot_id
            != terminal_closure.world_snapshot_id
        ):
            raise ValueError("epistemic assessment world snapshot lineage mismatch")
        if (
            explanatory_model_revision is not None
            and explanatory_model_revision.world_snapshot_id
            != terminal_closure.world_snapshot_id
        ):
            raise ValueError("explanatory revision world snapshot lineage mismatch")
        return CanonicalProductiveTerminalResearchIntellectualRealization(
            episode_id=terminal_closure.episode_id,
            originating_reasoning_id=terminal_closure.originating_reasoning_id,
            world_snapshot_id=terminal_closure.world_snapshot_id,
            stopping_reason=terminal_closure.stopping_reason,
            terminal_closure=terminal_closure,
            epistemic_assessment=epistemic_assessment,
            explanatory_model=explanatory_model,
            explanatory_model_revision=explanatory_model_revision,
            rationale_codes=terminal_closure.rationale_codes,
        )

    @property
    def snapshot(self) -> GovernedReasoningRuntimeSnapshot:
        result = self._last_result
        return GovernedReasoningRuntimeSnapshot(
            evaluations=self._evaluations,
            last_owner=self._last_owner,
            last_status=(result.status.value if result is not None else None),
            last_confidence=(
                result.decision.confidence_score if result is not None else None
            ),
            last_requires_human_review=(
                result.requires_human_review if result is not None else False
            ),
        )

    def productive_episode(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> CanonicalProductiveReasoningEpisode | None:
        episode = self._productive_episodes.get(
            (owner.strip().casefold(), session_id.strip())
        )
        if episode is None or episode.turn_id != turn_id.strip():
            return None
        return episode

    def productive_abstraction_episode(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> CanonicalProductiveAbstractionEpisode | None:
        result = self._productive_abstraction_results.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )
        return result.episode if result is not None else None

    def productive_abstraction_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        episode = self.productive_abstraction_episode(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if episode is None:
            return ()
        return (episode.episode_id, episode.source_fingerprint)

    def productive_concept_episode(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> CanonicalProductiveConceptEpisode | None:
        return self._productive_concept_episodes.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_concept_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        episode = self.productive_concept_episode(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if episode is None:
            return ()
        return (
            episode.episode_id,
            episode.concept_candidate.concept_id,
            episode.source_fingerprint,
        )

    def productive_cross_domain_synthesis_candidate(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedCrossDomainConceptSynthesisCandidate | None:
        return self._productive_cross_domain_syntheses.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_cross_domain_synthesis_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        candidate = self.productive_cross_domain_synthesis_candidate(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if candidate is None:
            return ()
        return (
            candidate.source_concept_episode_id,
            candidate.target_concept_episode_id,
            candidate.source_fingerprint,
        )

    def admit_novel_synthesis_as_governed_hypothesis(
        self,
        *,
        synthesis: GovernedCrossDomainConceptSynthesisCandidate,
        proposition: str,
    ) -> CanonicalNovelSynthesisGovernedHypothesisAdmission:
        """Give an existing synthesis candidate tentative hypothesis identity only."""
        if (
            synthesis.status
            is not CrossDomainConceptSynthesisStatus.SYNTHESIS_CANDIDATE
        ):
            raise ValueError("novel hypothesis admission requires synthesis candidate")
        if (
            synthesis.canonical_authority != "governed_reasoning"
            or not synthesis.read_only
        ):
            raise ValueError("novel hypothesis admission requires governed synthesis")
        if any(
            (
                synthesis.establishes_truth,
                synthesis.establishes_causality,
                synthesis.authorizes_inference,
                synthesis.creates_memory,
                synthesis.creates_learning,
                synthesis.executes_transfer,
                synthesis.registers_rule,
                synthesis.executes_actions,
                synthesis.grants_authority,
            )
        ):
            raise ValueError(
                "novel hypothesis admission rejects authoritative synthesis"
            )
        normalized_proposition = proposition.strip()
        if not normalized_proposition:
            raise ValueError(
                "novel hypothesis admission requires tentative proposition"
            )

        candidate_fingerprint = sha256(
            "|".join(
                (
                    "novel-synthesis-governed-hypothesis",
                    synthesis.source_fingerprint,
                    normalized_proposition,
                )
            ).encode("utf-8")
        ).hexdigest()
        hypothesis_candidate = GovernedHypothesisCandidate(
            candidate_id=f"governed-hypothesis-candidate-{candidate_fingerprint[:20]}",
            proposition=normalized_proposition,
            source_claim_id=(
                f"cross-domain-synthesis-{synthesis.source_fingerprint[:20]}"
            ),
            source_claim_type="synthesis_candidate",
            source_claim_fingerprint=synthesis.source_fingerprint,
            evidence_ids=(),
            rationale_codes=(
                "novel_synthesis:hypothesis_identity_only",
                "novel_synthesis:synthesis_is_not_evidence",
                "novel_synthesis:independent_evidence_required",
            ),
        )
        return CanonicalNovelSynthesisGovernedHypothesisAdmission(
            synthesis_source_fingerprint=synthesis.source_fingerprint,
            source_domain_reference=synthesis.source_domain_reference,
            target_domain_reference=synthesis.target_domain_reference,
            source_concept_episode_id=synthesis.source_concept_episode_id,
            target_concept_episode_id=synthesis.target_concept_episode_id,
            hypothesis_candidate=hypothesis_candidate,
            rationale_codes=(
                "novel_synthesis:governed_reasoning_lineage_preserved",
                "novel_synthesis:tentative_hypothesis_only",
                "novel_synthesis:no_new_authority",
            ),
        )

    def evaluate_creative_candidate_critical_disposition(
        self,
        *,
        admission: CanonicalNovelSynthesisGovernedHypothesisAdmission,
    ) -> GovernedCreativeCandidateCriticalDisposition:
        """Keep a novel synthesis tentative until independent evidence exists."""
        if admission.canonical_authority != "governed_reasoning":
            raise ValueError(
                "creative candidate disposition requires reasoning authority"
            )
        if not admission.read_only or not admission.synthesis_origin:
            raise ValueError(
                "creative candidate disposition requires governed admission"
            )
        if admission.registers_synthesis_as_evidence:
            raise ValueError(
                "creative candidate disposition rejects synthetic evidence"
            )
        candidate = admission.hypothesis_candidate
        if candidate.evidence_ids:
            raise ValueError(
                "creative candidate disposition requires independent evidence"
            )
        if candidate.source_claim_fingerprint != admission.synthesis_source_fingerprint:
            raise ValueError("creative candidate disposition lineage mismatch")

        fingerprint = sha256(
            "|".join(
                (
                    "creative-candidate-critical-disposition",
                    admission.synthesis_source_fingerprint,
                    candidate.candidate_id,
                    candidate.source_claim_fingerprint,
                    "review-required",
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedCreativeCandidateCriticalDisposition(
            disposition_id=f"creative-candidate-disposition-{fingerprint[:24]}",
            status=GovernedCreativeCandidateCriticalDispositionStatus.REVIEW_REQUIRED,
            synthesis_source_fingerprint=admission.synthesis_source_fingerprint,
            hypothesis_candidate_id=candidate.candidate_id,
            hypothesis_source_claim_fingerprint=candidate.source_claim_fingerprint,
            critical_evaluation_reference_ids=(),
            rationale_codes=(
                "creative_candidate:tentative_hypothesis_preserved",
                "creative_candidate:independent_evidence_required",
                "creative_candidate:proposal_boundary_not_entered",
            ),
        )

    def bind_productive_cross_domain_concept(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        domain_reference: str,
        concept_episode: CanonicalProductiveConceptEpisode,
    ) -> GovernedCrossDomainConceptSynthesisCandidate | None:
        """Admit explicit domain provenance without weakening concept scope."""
        if not domain_reference.strip():
            raise ValueError("cross-domain productive binding requires domain")
        if concept_episode.owner.casefold() != owner.strip().casefold() or (
            concept_episode.session_id != session_id.strip()
        ):
            raise ValueError("cross-domain productive binding lineage mismatch")
        domain_key = (
            owner.strip().casefold(),
            session_id.strip(),
            domain_reference.strip().casefold(),
        )
        self._productive_concepts_by_domain[domain_key] = concept_episode
        other_keys = tuple(
            sorted(
                key
                for key in self._productive_concepts_by_domain
                if key[:2] == domain_key[:2] and key[2] != domain_key[2]
            )
        )
        if not other_keys:
            return None
        source_episode = self._productive_concepts_by_domain[other_keys[-1]]
        candidate = self.cross_domain_concept_synthesizer.synthesize(
            source=CrossDomainConceptSource(
                domain_reference=other_keys[-1][2],
                concept_episode=source_episode,
            ),
            target=CrossDomainConceptSource(
                domain_reference=domain_reference,
                concept_episode=concept_episode,
            ),
        )
        if candidate.status is not (
            CrossDomainConceptSynthesisStatus.SYNTHESIS_CANDIDATE
        ):
            return None
        key = (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        self._productive_cross_domain_syntheses[key] = candidate
        return candidate

    def productive_hierarchical_analogy_candidate(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedHierarchicalStructuralAnalogyCandidate | None:
        return self._productive_hierarchical_analogies.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_hierarchical_analogy_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        candidate = self.productive_hierarchical_analogy_candidate(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if candidate is None:
            return ()
        return (
            candidate.source_concept_episode_id,
            candidate.target_concept_episode_id,
            candidate.source_fingerprint,
        )

    def _compare_productive_concept_if_ready(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        concept_episode: CanonicalProductiveConceptEpisode,
    ) -> GovernedHierarchicalStructuralAnalogyCandidate | None:
        scope_key = (
            owner.strip().casefold(),
            session_id.strip(),
            concept_episode.scope_reference,
        )
        previous = self._productive_concept_history_by_scope.get(scope_key)
        self._productive_concept_history_by_scope[scope_key] = concept_episode
        if previous is None or previous.episode_id == concept_episode.episode_id:
            return None
        candidate = self.hierarchical_structural_analogy_matcher.match(
            source=previous,
            target=concept_episode,
            scope_reference=concept_episode.scope_reference,
        )
        if (
            candidate.status
            is not HierarchicalStructuralAnalogyStatus.ANALOGY_CANDIDATE
        ):
            return None
        key = (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        self._productive_hierarchical_analogies[key] = candidate
        return candidate

    def bind_productive_concept_candidate(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        candidate: GovernedHierarchicalConceptCandidate,
    ) -> CanonicalProductiveConceptEpisode | None:
        """Bind an already-governed HCC candidate without recomposition."""
        if candidate.status not in {
            HierarchicalConceptCompositionStatus.REVIEW_REQUIRED,
            HierarchicalConceptCompositionStatus.CONTESTED,
        }:
            return None
        source_fingerprint = sha256(
            repr(
                (
                    owner.strip().casefold(),
                    session_id.strip(),
                    turn_id.strip(),
                    candidate.concept_id,
                    candidate.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        episode = CanonicalProductiveConceptEpisode(
            episode_id=f"productive-concept:{source_fingerprint[:16]}",
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            scope_reference=candidate.scope_reference,
            concept_candidate=candidate,
            source_abstraction_episode_ids=candidate.constituent_episode_ids,
            source_fingerprint=source_fingerprint,
        )
        key = (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        existing = self._productive_concept_episodes.get(key)
        if existing is not None and existing != episode:
            raise ValueError("productive concept episode is immutable per turn")
        self._productive_concept_episodes[key] = episode
        self._compare_productive_concept_if_ready(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            concept_episode=episode,
        )
        return episode

    def _compose_productive_concept_if_ready(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        abstraction_episode: CanonicalProductiveAbstractionEpisode,
    ) -> CanonicalProductiveConceptEpisode | None:
        """Compose two genuinely distinct ordinary abstractions in one scope."""
        candidate = abstraction_episode.abstraction_candidate
        family_key = (
            candidate.invariant_relation,
            candidate.invariant_outcome,
        )
        scope_key = (
            owner.strip().casefold(),
            session_id.strip(),
            abstraction_episode.scope_reference,
        )
        families = self._productive_abstractions_by_scope.setdefault(scope_key, {})
        families[family_key] = abstraction_episode
        if len(families) < self.hierarchical_concept_composer.MINIMUM_COMPONENTS:
            return None

        other_keys = tuple(sorted(key for key in families if key != family_key))
        if not other_keys:
            return None
        episodes = (
            families[other_keys[0]],
            abstraction_episode,
        )
        concept = self.hierarchical_concept_composer.compose(
            episodes=episodes,
            scope_reference=abstraction_episode.scope_reference,
        )
        return self.bind_productive_concept_candidate(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            candidate=concept,
        )

    def _compose_bounded_situational_productive_binding(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        text: str,
        now: datetime,
        scope_reference: str | None,
    ):
        effective_scope = scope_reference or session_id
        source_reference = f"conversation:{session_id}/turn:{turn_id}"
        grounding = GovernedBoundedExplicitTurnPropositionGrounder().ground(
            text,
            source_reference=source_reference,
            scope_reference=effective_scope,
        )
        if grounding.status is not ExplicitTurnPropositionGroundingStatus.GROUNDED:
            return None
        projection = GovernedExplicitTurnTransientClaimProjector().project(
            grounding=grounding,
            scope_reference=effective_scope,
            owner=owner,
            created_at=now,
        )
        if (
            projection.status
            is not ExplicitTurnTransientClaimProjectionStatus.PROJECTED
        ):
            return None
        grouping = GovernedExplicitTurnContextualClaimGrouper().group(
            projection=projection
        )
        if grouping.status is not ExplicitTurnContextualGroupingStatus.GROUPED:
            return None
        hypothesis = GovernedBoundedSituationalHypothesisFormer().form(
            grouping=grouping,
            projection=projection,
        )
        if (
            hypothesis.status is not BoundedSituationalHypothesisStatus.FORMED
            or hypothesis.situational_kind
            is not BoundedSituationalHypothesisKind.ORGANIZATION_RELATED
        ):
            return None
        claim_projection = (
            GovernedSituationalHypothesisTransientClaimProjector().project(
                hypothesis=hypothesis,
                owner=owner,
                created_at=now,
            )
        )
        if (
            claim_projection.status
            is not SituationalHypothesisTransientClaimProjectionStatus.PROJECTED
            or claim_projection.claim is None
        ):
            return None
        implication = GovernedBoundedModalSituationalImplicationFoundationV1().apply(
            source_claim=claim_projection.claim
        )
        if (
            implication.status is not BoundedModalSituationalImplicationStatus.APPLIED
            or implication.derived_claim is None
        ):
            return None
        binding = GovernedTurnBoundProductiveSituationalClaimBinder().bind(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            source_claim=implication.derived_claim,
        )
        if binding.status is not TurnBoundProductiveSituationalClaimBindingStatus.BOUND:
            return None
        return binding

    @staticmethod
    def _compose_bounded_productive_non_rule_derivation(situational_binding):
        if situational_binding is None or situational_binding.source_claim is None:
            return None
        interpretation = GovernedBoundedProductiveSupportInterpreterV1().interpret(
            source_claim=situational_binding.source_claim
        )
        if (
            interpretation.status
            is not BoundedProductiveSupportInterpretationStatus.INTERPRETED
            or interpretation.interpreted_claim is None
        ):
            return None
        derivation = GovernedBoundedNonRuleDerivationFoundationV1().derive(
            interpreted_claim=interpretation.interpreted_claim
        )
        if derivation.status is not BoundedNonRuleDerivationStatus.DERIVED:
            return None
        return derivation

    def evaluate_productive_episode(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
        turn_id: str,
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
        scope_reference: str | None = None,
        observe_productive_intake: bool = True,
        recalled_memory_evidence=(),
        visual_context_contribution: CognitiveRuntimeContribution | None = None,
    ) -> CanonicalProductiveReasoningEpisode:
        existing = self.productive_episode(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if existing is not None:
            return existing
        situational_binding = self._compose_bounded_situational_productive_binding(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            text=text,
            now=now,
            scope_reference=scope_reference,
        )
        bounded_transient_claims = (
            (situational_binding.source_claim,)
            if situational_binding is not None
            and situational_binding.source_claim is not None
            else ()
        )
        bounded_non_rule_derivation = (
            self._compose_bounded_productive_non_rule_derivation(situational_binding)
        )
        bounded_non_rule_derivations = (
            (bounded_non_rule_derivation,)
            if bounded_non_rule_derivation is not None
            else ()
        )
        result = self._evaluate_with_recalled_structural_knowledge(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            text=text,
            now=now,
            domains=domains,
            scope_reference=scope_reference,
            observe_productive_intake=observe_productive_intake,
            recalled_memory_evidence=tuple(recalled_memory_evidence),
            visual_context_contribution=visual_context_contribution,
            bounded_transient_claims=bounded_transient_claims,
            bounded_non_rule_derivations=bounded_non_rule_derivations,
        )
        if scope_reference is not None and observe_productive_intake:
            intake = self.productive_temporary_rule_intake.last_result
            grounding = intake.semantic_grounding if intake is not None else None
            if grounding is not None:
                abstraction = self.productive_abstraction_admission.observe(
                    grounding,
                    session_id=session_id,
                    turn_id=turn_id,
                    scope_reference=scope_reference,
                )
                self._productive_abstraction_results[
                    (owner.strip().casefold(), session_id.strip(), turn_id.strip())
                ] = abstraction
                if abstraction.episode is not None:
                    self._compose_productive_concept_if_ready(
                        owner=owner,
                        session_id=session_id,
                        turn_id=turn_id,
                        abstraction_episode=abstraction.episode,
                    )
        input_fingerprint = sha256(
            repr(
                (
                    owner.casefold(),
                    session_id,
                    turn_id,
                    text.strip(),
                    tuple(recalled_memory_evidence),
                    (
                        tuple(visual_context_contribution.reference_ids)
                        if visual_context_contribution is not None
                        else ()
                    ),
                    (
                        situational_binding.binding_fingerprint
                        if situational_binding is not None
                        else None
                    ),
                )
            ).encode("utf-8")
        ).hexdigest()
        source_fingerprint = sha256(
            repr((turn_id, input_fingerprint, result.result_id)).encode("utf-8")
        ).hexdigest()
        episode = CanonicalProductiveReasoningEpisode(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            input_fingerprint=input_fingerprint,
            result=result,
            source_fingerprint=source_fingerprint,
        )
        self._productive_episodes[(owner.casefold(), session_id)] = episode
        return episode

    def productive_recalled_knowledge_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        """Expose successful same-turn governed recalled-knowledge reuse lineage."""
        return self._productive_recalled_knowledge_references.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip()),
            (),
        )

    def _evaluate_with_recalled_structural_knowledge(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        text: str,
        now: datetime,
        domains: tuple[ScopeDomain | str, ...],
        scope_reference: str | None,
        observe_productive_intake: bool,
        recalled_memory_evidence,
        bounded_transient_claims=(),
        bounded_non_rule_derivations=(),
        visual_context_contribution: CognitiveRuntimeContribution | None = None,
    ) -> GovernedReasoningResult:
        stable = tuple(
            item
            for item in recalled_memory_evidence
            if getattr(item, "category", "") == "stable_knowledge"
        )
        if scope_reference is None or not stable:
            return self.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
                additional_transient_claims=bounded_transient_claims,
                bounded_non_rule_derivations=bounded_non_rule_derivations,
                visual_context_contribution=visual_context_contribution,
            )

        recall_items = []
        evidence_by_memory_id: dict[int, object] = {}
        for evidence in stable[
            : self.recalled_knowledge_structural_projector.MAX_RECALLED_ITEMS
        ]:
            _, separator, raw_memory_id = str(evidence.memory_id).rpartition(":")
            candidate_id = raw_memory_id if separator else str(evidence.memory_id)
            if not candidate_id.isdigit():
                continue
            memory_id = int(candidate_id)
            memory = CognitiveMemoryRecord(
                id=memory_id,
                content=evidence.content,
                category=LearningCategory.STABLE_KNOWLEDGE,
                confidence=evidence.confidence,
                reason=evidence.provenance,
                tags=("governed_learning", "human_approved", "stable_knowledge"),
                metadata={"g12_source_scope": evidence.scope},
                created_at=now.isoformat(),
            )
            recall_items.append(
                CognitiveMemoryRecallItem(
                    memory=memory,
                    score=evidence.recall_score,
                    matched_signals=("governed_memory_planning_evidence",),
                )
            )
            evidence_by_memory_id[memory_id] = evidence

        if not recall_items:
            return self.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
                additional_transient_claims=bounded_transient_claims,
                bounded_non_rule_derivations=bounded_non_rule_derivations,
                visual_context_contribution=visual_context_contribution,
            )

        recalled_projection = self.recalled_knowledge_structural_projector.project(
            recall_result=CognitiveMemoryRecallResult(
                should_use_memory=True,
                items=tuple(recall_items),
                reason="already_selected_governed_memory_evidence",
            ),
            scope_reference=scope_reference,
        )
        if not recalled_projection.items:
            return self.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
                additional_transient_claims=bounded_transient_claims,
                bounded_non_rule_derivations=bounded_non_rule_derivations,
                visual_context_contribution=visual_context_contribution,
            )

        target = self.target_problem_structural_projector.project(
            text=text,
            source_reference=f"conversation:{session_id}/turn:{turn_id}",
            scope_reference=scope_reference,
        )
        transfer = self.structural_knowledge_transfer_matcher.match_target_problem(
            target=target,
            known=tuple(item.grounding for item in recalled_projection.items),
            scope_reference=scope_reference,
        )
        if (
            transfer.normalized_status
            is not StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
            or len(transfer.matched_source_fingerprints) != 1
        ):
            return self.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
                additional_transient_claims=bounded_transient_claims,
                bounded_non_rule_derivations=bounded_non_rule_derivations,
                visual_context_contribution=visual_context_contribution,
            )

        matched_fingerprint = transfer.matched_source_fingerprints[0]
        source = next(
            (
                item
                for item in recalled_projection.items
                if item.grounding.source_fingerprint == matched_fingerprint
            ),
            None,
        )
        if source is None:
            return self.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
                additional_transient_claims=bounded_transient_claims,
                bounded_non_rule_derivations=bounded_non_rule_derivations,
                visual_context_contribution=visual_context_contribution,
            )
        source_evidence = evidence_by_memory_id.get(source.memory_id)
        if source_evidence is None:
            return self.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
                additional_transient_claims=bounded_transient_claims,
                bounded_non_rule_derivations=bounded_non_rule_derivations,
                visual_context_contribution=visual_context_contribution,
            )

        # Reuse the existing productive temporary-rule boundary for canonical
        # admission and explicit-case claim projection. The recalled item is
        # still review-required, temporary and non-authoritative.
        self.observe_productive_temporary_rule_intake(
            owner=owner,
            text=source_evidence.content,
            now=now,
            scope_reference=scope_reference,
            domains=domains,
        )
        intake = self.observe_productive_temporary_rule_intake(
            owner=owner,
            text=text,
            now=now,
            scope_reference=scope_reference,
            domains=domains,
        )
        projections = intake.projections or (
            (intake.projection,) if intake.projection is not None else ()
        )
        transient_claims = tuple(
            claim for projection in projections for claim in projection.claims
        )
        if intake.admission is None or not transient_claims:
            return self.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=False,
                additional_transient_claims=bounded_transient_claims,
                bounded_non_rule_derivations=bounded_non_rule_derivations,
                visual_context_contribution=visual_context_contribution,
            )

        result = self.reason(
            ReasoningQuery(text=text, owner=owner, domains=domains, as_of=now),
            now=now,
            scope_reference=scope_reference,
            transient_claims=transient_claims + tuple(bounded_transient_claims),
            non_rule_derivations=tuple(bounded_non_rule_derivations),
            visual_context_contribution=visual_context_contribution,
        )
        self._productive_recalled_knowledge_references[
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        ] = (
            recalled_projection.source_fingerprint,
            source.source_fingerprint,
            target.source_fingerprint,
            transfer.source_fingerprint,
            intake.admission.rule.fingerprint,
            *(projection.source_fingerprint for projection in projections),
        )
        return result

    def productive_multistage_causal_path(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedMultiStageCausalPath | None:
        return self._productive_multistage_causal_paths.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_multistage_causal_path_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        path = self.productive_multistage_causal_path(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if path is None or path.status is not MultiStageCausalPathStatus.PATH_CANDIDATE:
            return ()
        return (
            path.path_id,
            path.baseline_snapshot_id,
            *path.relation_ids,
            path.source_fingerprint,
        )

    def bind_productive_multistage_causal_path(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        baseline: PersistentWorldSnapshot,
        hypotheses: tuple[CausalHypothesis, ...],
    ) -> GovernedMultiStageCausalPath:
        path = self.multistage_causal_path_composer.compose(
            owner=owner,
            session_id=session_id,
            baseline=baseline,
            hypotheses=hypotheses,
        )
        self._productive_multistage_causal_paths[
            (
                owner.strip().casefold(),
                session_id.strip(),
                turn_id.strip(),
            )
        ] = path
        return path

    def productive_counterfactual_path_comparison(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedCounterfactualPathComparison | None:
        return self._productive_counterfactual_path_comparisons.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_counterfactual_path_comparison_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        comparison = self.productive_counterfactual_path_comparison(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if (
            comparison is None
            or comparison.status
            is not CounterfactualPathComparisonStatus.COMPARISON_CANDIDATE
        ):
            return ()
        return (
            comparison.comparison_id,
            comparison.baseline_snapshot_id,
            *comparison.path_ids,
            *(
                relation_id
                for _, relation_ids in comparison.relation_lineage
                for relation_id in relation_ids
            ),
            comparison.source_fingerprint,
        )

    def bind_productive_counterfactual_path_comparison(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        paths: tuple[GovernedMultiStageCausalPath, ...],
    ) -> GovernedCounterfactualPathComparison:
        if any(
            path.owner.strip().casefold() != owner.strip().casefold()
            or path.session_id.strip() != session_id.strip()
            for path in paths
        ):
            raise ValueError(
                "counterfactual productive binding requires owner/session lineage"
            )
        comparison = self.counterfactual_path_comparator.compare(paths)
        self._productive_counterfactual_path_comparisons[
            (
                owner.strip().casefold(),
                session_id.strip(),
                turn_id.strip(),
            )
        ] = comparison
        return comparison

    def productive_explanatory_model_consumption(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedExplanatoryModelProductiveConsumption | None:
        return self._productive_explanatory_models.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_explanatory_model_revision(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedExplanatoryModelRevision | None:
        return self._productive_explanatory_model_revisions.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_explanatory_model_revision_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        revision = self.productive_explanatory_model_revision(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if (
            revision is None
            or revision.status is not GovernedExplanatoryModelRevisionStatus.REVISED
            or revision.revised_model_id is None
            or revision.evidence_id is None
        ):
            return ()
        return (
            revision.revision_id,
            revision.previous_model_id,
            revision.revised_model_id,
            revision.reentry_id,
            revision.requirement_id,
            revision.evidence_id,
            revision.source_fingerprint,
        )

    def bind_productive_explanatory_model_revision(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        source_turn_id: str,
        reentry,
        revised_report: GovernedHypothesisDeepeningReport,
    ) -> GovernedExplanatoryModelRevision:
        previous = self.productive_explanatory_model_consumption(
            owner=owner,
            session_id=session_id,
            turn_id=source_turn_id,
        )
        if previous is None:
            raise ValueError("explanatory model revision requires exact source model")
        revision = self.explanatory_model_revision.consume(
            previous,
            reentry,
            revised_report,
        )
        key = (
            owner.strip().casefold(),
            session_id.strip(),
            turn_id.strip(),
        )
        self._productive_explanatory_model_revisions[key] = revision
        return revision

    def productive_explanatory_investigation_reentry(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedExplanatoryModelInvestigationReentry | None:
        return self._productive_explanatory_investigation_reentries.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def investigation_episode_budget_introspection(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> GovernedInvestigationEpisodeBudgetIntrospectionView | None:
        reentry = self.productive_explanatory_investigation_reentry(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if reentry is None or reentry.investigation_entry is None:
            return None
        state = reentry.investigation_entry.episode_state
        if state is None:
            return None
        return GovernedInvestigationEpisodeBudgetIntrospectionView(
            episode_id=state.episode_id,
            originating_reasoning_id=state.originating_reasoning_id,
            source_reference=state.source_reference,
            world_snapshot_id=state.world_snapshot_id,
            requirement_ids=state.requirement_ids,
            plan_ids=state.plan_ids,
            authorization_ids=state.authorization_ids,
            execution_ids=state.execution_ids,
            local_execution_ids=state.local_execution_ids,
            reentry_ids=state.reentry_ids,
            consumed_acquisitions=state.consumed_acquisitions,
            max_acquisitions=state.max_acquisitions,
            remaining_acquisitions=state.remaining_acquisitions,
            current_step=state.current_step,
            status=state.status,
            stopping_reason=state.stopping_reason,
        )

    def productive_explanatory_investigation_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        reentry = self.productive_explanatory_investigation_reentry(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if reentry is None or reentry.investigation_entry is None:
            return ()
        return (
            reentry.reentry_id,
            reentry.requirement.requirement_id,
            reentry.investigation_entry.episode_id or "",
            reentry.source_fingerprint,
        )

    def productive_explanatory_model_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        consumption = self.productive_explanatory_model_consumption(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
        )
        if consumption is None:
            return ()
        model = consumption.model
        return (
            model.model_id,
            model.source_report_id,
            model.discrimination_report_id,
            model.source_fingerprint,
        )

    @staticmethod
    def _scenario_semantic_key(hypothesis: ScenarioHypothesis) -> tuple[str, ...]:
        return (
            hypothesis.proposition.strip().casefold(),
            hypothesis.world_domain.strip().casefold(),
            hypothesis.fact_key.strip().casefold(),
            hypothesis.assumed_value.strip().casefold(),
            hypothesis.temporal_scope.strip().casefold(),
        )

    @staticmethod
    def _causal_semantic_key(hypothesis: CausalHypothesis) -> tuple[str, ...]:
        return (
            hypothesis.proposition.strip().casefold(),
            hypothesis.cause_domain.strip().casefold(),
            hypothesis.cause_key.strip().casefold(),
            hypothesis.cause_value.strip().casefold(),
            hypothesis.effect_domain.strip().casefold(),
            hypothesis.effect_key.strip().casefold(),
            hypothesis.effect_value.strip().casefold(),
            hypothesis.temporal_scope.strip().casefold(),
        )

    def _compose_ordinary_multi_hypothesis_if_ready(
        self,
        *,
        episode: CanonicalProductiveReasoningEpisode,
        reached: GovernedExplicitHypothesisSourceResult,
        world: PersistentWorldSnapshot,
    ) -> GovernedExplanatoryModelProductiveConsumption | None:
        scope_key = (
            episode.owner.strip().casefold(),
            episode.session_id.strip(),
            world.snapshot_id,
        )
        deepener = GovernedHypothesisDeepener()
        if reached.scenario_hypotheses:
            history = self._ordinary_scenario_hypotheses.setdefault(scope_key, {})
            current = reached.scenario_hypotheses[0]
            history[self._scenario_semantic_key(current)] = current
            if len(history) < 2:
                return None
            hypotheses = tuple(history[key] for key in sorted(history))
            report = GovernedScenarioSimulator().simulate(world, hypotheses)
            deepening = deepener.deepen_scenarios_safely(report)
        elif reached.causal_hypotheses:
            history = self._ordinary_causal_hypotheses.setdefault(scope_key, {})
            current = reached.causal_hypotheses[0]
            history[self._causal_semantic_key(current)] = current
            if len(history) < 2:
                return None
            hypotheses = tuple(history[key] for key in sorted(history))
            report = GovernedCausalPredictiveReasoner().analyze(world, hypotheses)
            deepening = deepener.deepen_causal_predictions_safely(report)
        else:
            return None

        consumption = GovernedExplanatoryModelProductiveConsumptionV1().consume(
            deepening
        )
        if consumption.context_lines() == ():
            return None
        key = (
            episode.owner.strip().casefold(),
            episode.session_id.strip(),
            episode.turn_id.strip(),
        )
        self._productive_explanatory_models[key] = consumption
        reentry = self.explanatory_model_investigation_reentry.consume(
            consumption,
            originating_reasoning_id=episode.result.result_id,
        )
        self._productive_explanatory_investigation_reentries[key] = reentry
        return consumption

    def compose_productive_longitudinal_intellectual_reconstruction(
        self,
        *,
        recalled_antecedent_reference: str,
        recalled_antecedent_fingerprint: str,
        recalled_evidence_references: tuple[str, ...],
        current_epistemic_assessment: (
            LongitudinalIntellectualCurrentEpistemicView | None
        ),
        epistemic_delta: object | None,
        open_state_references: tuple[str, ...],
    ) -> GovernedLongitudinalIntellectualReconstruction:
        """Delegate bounded longitudinal reconstruction to its core authority."""
        return GovernedLongitudinalIntellectualReconstructionFoundationV1().reconstruct(
            recalled_antecedent_reference=recalled_antecedent_reference,
            recalled_antecedent_fingerprint=recalled_antecedent_fingerprint,
            recalled_evidence_references=recalled_evidence_references,
            current_epistemic_assessment=current_epistemic_assessment,
            epistemic_delta=epistemic_delta,
            open_state_references=open_state_references,
        )

    def bind_productive_epistemic_assessment(
        self,
        episode: CanonicalProductiveReasoningEpisode,
        source: GovernedExplicitHypothesisSource,
        *,
        world: PersistentWorldSnapshot,
    ) -> CanonicalProductiveEpistemicAssessmentEpisode:
        """Bind one selective epistemic chain to one exact productive turn."""
        key = (
            episode.owner.casefold(),
            episode.session_id,
            episode.turn_id,
        )
        existing = self._productive_epistemic_episodes.get(key)
        if existing is not None:
            if (
                existing.hypothesis_source_result.source_fingerprint_input
                != source.source_fingerprint
                or existing.world_snapshot_id != world.snapshot_id
            ):
                raise ValueError(
                    "productive epistemic assessment already bound to turn"
                )
            return existing

        reached = self.evaluate_explicit_hypothesis_source(source, world=world)
        if reached.status.value == "not_applicable":
            return self._store_productive_epistemic_empty(
                key,
                episode,
                reached,
                CanonicalProductiveEpistemicAssessmentStatus.NOT_APPLICABLE,
            )
        if reached.status.value == "review_required":
            return self._store_productive_epistemic_empty(
                key,
                episode,
                reached,
                CanonicalProductiveEpistemicAssessmentStatus.REVIEW_REQUIRED,
            )

        self._compose_ordinary_multi_hypothesis_if_ready(
            episode=episode,
            reached=reached,
            world=world,
        )

        if reached.scenario_report is not None:
            productive_reference = reached.scenario_report.simulation_id
            deepening = GovernedHypothesisDeepener().deepen_scenarios_safely(
                reached.scenario_report
            )
        elif reached.causal_report is not None:
            productive_reference = reached.causal_report.analysis_id
            deepening = GovernedHypothesisDeepener().deepen_causal_predictions_safely(
                reached.causal_report
            )
        else:
            raise ValueError("eligible hypothesis source lacks canonical report")

        sufficiency = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(
            deepening
        )
        quality = GovernedReasoningQualityAssessmentFoundationV1().assess(
            deepening,
            sufficiency,
        )
        provenance = GovernedReasoningMethodProvenanceFoundationV1().derive(
            deepening,
            sufficiency=sufficiency,
            quality=quality,
        )
        outcome = GovernedReasoningMethodOutcomeObservation.from_artifacts(
            provenance,
            quality,
            sufficiency,
        )
        fingerprint = sha256(
            repr(
                (
                    episode.source_fingerprint,
                    source.source_fingerprint,
                    world.snapshot_id,
                    productive_reference,
                    deepening.report_id,
                    sufficiency.assessment_id,
                    quality.assessment_id,
                    provenance.provenance_id,
                    outcome.observation_id,
                )
            ).encode("utf-8")
        ).hexdigest()
        result = CanonicalProductiveEpistemicAssessmentEpisode(
            assessment_episode_id=(
                f"productive-epistemic-assessment-{fingerprint[:24]}"
            ),
            status=CanonicalProductiveEpistemicAssessmentStatus.ASSESSED,
            owner=episode.owner,
            session_id=episode.session_id,
            turn_id=episode.turn_id,
            reasoning_episode_fingerprint=episode.source_fingerprint,
            hypothesis_source_result=reached,
            world_snapshot_id=world.snapshot_id,
            productive_reference_id=productive_reference,
            deepening=deepening,
            sufficiency=sufficiency,
            quality=quality,
            method_provenance=provenance,
            method_outcome=outcome,
            source_fingerprint=fingerprint,
        )
        self._productive_epistemic_episodes[key] = result
        return result

    def productive_epistemic_episode(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> CanonicalProductiveEpistemicAssessmentEpisode | None:
        """Return only the exact same-turn bound epistemic episode."""
        return self._productive_epistemic_episodes.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )

    def productive_epistemic_reference_ids(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> tuple[str, ...]:
        """Expose only references certified for the exact productive turn."""
        result = self._productive_epistemic_episodes.get(
            (owner.strip().casefold(), session_id.strip(), turn_id.strip())
        )
        if (
            result is None
            or result.status
            is not CanonicalProductiveEpistemicAssessmentStatus.ASSESSED
            or result.productive_reference_id is None
        ):
            return ()
        return (result.productive_reference_id,)

    def _store_productive_epistemic_empty(
        self,
        key: tuple[str, str, str],
        episode: CanonicalProductiveReasoningEpisode,
        reached: GovernedExplicitHypothesisSourceResult,
        status: CanonicalProductiveEpistemicAssessmentStatus,
    ) -> CanonicalProductiveEpistemicAssessmentEpisode:
        fingerprint = sha256(
            repr(
                (
                    episode.source_fingerprint,
                    reached.source_fingerprint,
                    reached.world_snapshot_id,
                    status.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        result = CanonicalProductiveEpistemicAssessmentEpisode(
            assessment_episode_id=(
                f"productive-epistemic-assessment-{fingerprint[:24]}"
            ),
            status=status,
            owner=episode.owner,
            session_id=episode.session_id,
            turn_id=episode.turn_id,
            reasoning_episode_fingerprint=episode.source_fingerprint,
            hypothesis_source_result=reached,
            world_snapshot_id=reached.world_snapshot_id,
            productive_reference_id=None,
            deepening=None,
            sufficiency=None,
            quality=None,
            method_provenance=None,
            method_outcome=None,
            source_fingerprint=fingerprint,
        )
        self._productive_epistemic_episodes[key] = result
        return result

    def evaluate_explicit_hypothesis_source(
        self,
        source: GovernedExplicitHypothesisSource,
        *,
        world: PersistentWorldSnapshot,
    ) -> GovernedExplicitHypothesisSourceResult:
        """Reach existing scenario/causal foundations through reasoning authority."""
        return GovernedExplicitHypothesisSourceAdapterV1().evaluate(
            source,
            world,
        )

    def reason(
        self,
        query: ReasoningQuery,
        *,
        now: datetime | None = None,
        scope_reference: str | None = None,
        transient_claims=(),
        non_rule_derivations=(),
        visual_context_contribution: CognitiveRuntimeContribution | None = None,
    ) -> GovernedReasoningResult:
        result = self.orchestrator.reason(
            query,
            now=now,
            scope_reference=scope_reference,
            transient_claims=tuple(transient_claims),
            non_rule_derivations=tuple(non_rule_derivations),
            visual_context_contribution=visual_context_contribution,
        )
        self._evaluations += 1
        self._last_owner = query.owner
        self._last_result = result
        return result

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_governed_reasoning_runtime_status_completed",
            )
        if any(trigger in normalized for trigger in self._AUDIT_TRIGGERS):
            return GovernedOperationalInterception(
                response_text="\n".join(
                    (
                        "Auditoría del Governed Reasoning Runtime:",
                        "- Evidencia, claims e inferencias: separados.",
                        "- Conflictos e incertidumbre: evaluados explícitamente.",
                        "- Abstención: obligatoria ante contexto insuficiente.",
                        "- Revisión humana: preservada cuando corresponde.",
                        "- Acciones operacionales: no autorizadas por inferencia.",
                        "- Proveedores externos: no invocados por la auditoría.",
                    )
                ),
                rationale="official_governed_reasoning_runtime_audit_completed",
            )
        return None

    def observe_productive_temporary_rule_intake(
        self,
        *,
        owner: str,
        text: str,
        now: datetime,
        scope_reference: str,
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
    ):
        return self.productive_temporary_rule_intake.observe(
            owner=owner,
            text=text,
            scope_reference=scope_reference,
            domains=domains,
            now=now,
        )

    def evaluate_text(
        self,
        *,
        owner: str,
        text: str,
        now: datetime,
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
        scope_reference: str | None = None,
        observe_productive_intake: bool = True,
        additional_transient_claims=(),
        bounded_non_rule_derivations=(),
        visual_context_contribution: CognitiveRuntimeContribution | None = None,
    ) -> GovernedReasoningResult:
        transient_claims = ()
        if scope_reference is not None and observe_productive_intake:
            intake = self.observe_productive_temporary_rule_intake(
                owner=owner,
                text=text,
                scope_reference=scope_reference,
                domains=domains,
                now=now,
            )
            projections = intake.projections or (
                (intake.projection,) if intake.projection is not None else ()
            )
            transient_claims = tuple(
                claim for projection in projections for claim in projection.claims
            )
        return self.reason(
            ReasoningQuery(text=text, owner=owner, domains=domains, as_of=now),
            now=now,
            scope_reference=scope_reference,
            transient_claims=transient_claims + tuple(additional_transient_claims),
            non_rule_derivations=tuple(bounded_non_rule_derivations),
            visual_context_contribution=visual_context_contribution,
        )

    def _status_response(self) -> str:
        snapshot = self.snapshot
        confidence = (
            f"{snapshot.last_confidence:.2f}"
            if snapshot.last_confidence is not None
            else "ninguna"
        )
        return "\n".join(
            (
                "Estado del Governed Reasoning Runtime:",
                f"- Evaluaciones gobernadas: {snapshot.evaluations}",
                f"- Último estado: {snapshot.last_status or 'ninguno'}",
                f"- Última confianza: {confidence}",
                (
                    "- Revisión humana pendiente: "
                    f"{'sí' if snapshot.last_requires_human_review else 'no'}"
                ),
                "- Modo: trazable, abstencionista y no operacional.",
            )
        )
