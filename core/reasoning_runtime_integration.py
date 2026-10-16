from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from inspect import Parameter, signature

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.governed_reasoning import (
    GovernedReasoningResult,
    GovernedReasoningStatus,
)
from core.llm_provider import LLMRequest
from core.memory_planning_evidence import decode_memory_planning_evidence

GovernedReasoningSource = Callable[..., GovernedReasoningResult | None]


@dataclass(frozen=True)
class ReasoningRuntimeContributor:
    """Project governed reasoning into the current operational turn."""

    source: GovernedReasoningSource
    name: str = "reasoning"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
        continuity_selection: object | None = None,
        continuity_context_surface: object | None = None,
        visual_context_contribution: CognitiveRuntimeContribution | None = None,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
    ) -> CognitiveRuntimeContribution:
        recalled_memory_evidence = tuple(
            item
            for item in decode_memory_planning_evidence(
                request.metadata,
                owner=owner,
            )
            if item.category == "stable_knowledge"
        )
        source_parameters = signature(self.source).parameters
        supports_recalled_memory_evidence = (
            "recalled_memory_evidence" in source_parameters
            or any(
                parameter.kind is Parameter.VAR_KEYWORD
                for parameter in source_parameters.values()
            )
        )
        source_kwargs = {
            "owner": owner,
            "session_id": session_id,
            "text": text,
            "now": now,
        }
        if supports_recalled_memory_evidence:
            source_kwargs["recalled_memory_evidence"] = recalled_memory_evidence
        if "explicit_document_ids" in source_parameters:
            source_kwargs["explicit_document_ids"] = explicit_document_ids
        if "explicit_sources" in source_parameters:
            source_kwargs["explicit_sources"] = explicit_sources
        if "explicit_evidence_references" in source_parameters:
            source_kwargs["explicit_evidence_references"] = (
                explicit_evidence_references
            )
        if (
            "visual_context_contribution" in source_parameters
            or any(
                parameter.kind is Parameter.VAR_KEYWORD
                for parameter in source_parameters.values()
            )
        ):
            source_kwargs["visual_context_contribution"] = visual_context_contribution
        result = self.source(**source_kwargs)
        if result is None:
            return self._skipped("governed_reasoning_unavailable")
        if result.context.query.owner.casefold() != owner.casefold():
            raise ValueError("governed reasoning owner must match runtime owner")

        status = GovernedReasoningStatus(result.status)
        if status is GovernedReasoningStatus.BLOCKED:
            return self._skipped("governed_reasoning_blocked", result.result_id)
        if status is GovernedReasoningStatus.REVIEW_REQUIRED:
            return self._skipped(
                "governed_reasoning_requires_review",
                result.result_id,
            )

        epistemic_reference_ids: tuple[str, ...] = ()
        reference_source = getattr(self.source, "reference_ids", None)
        if callable(reference_source):
            epistemic_reference_ids = tuple(
                reference_source(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        references = tuple(
            dict.fromkeys(
                (
                    result.result_id,
                    result.context.context_id,
                    result.inference_run.run_id,
                    result.conflict_analysis.analysis_id,
                    result.decision.decision_id,
                    result.explanation.answer_id,
                    *epistemic_reference_ids,
                )
            )
        )
        if status is GovernedReasoningStatus.ABSTAINED:
            return CognitiveRuntimeContribution(
                stage=self.name,
                status=CognitiveRuntimeStageStatus.APPLIED,
                prompt_lines=(
                    "El razonamiento gobernado se abstuvo por evidencia insuficiente; "
                    "responder con cautela y declarar la incertidumbre.",
                ),
                reference_ids=references,
                rationale=("governed_reasoning_abstention_applied",),
            )

        if status is GovernedReasoningStatus.DERIVED:
            lines = [
                (
                    "Derivación gobernada consultiva (hipótesis modal): "
                    f"{result.decision.conclusion}"
                ),
                (
                    "Esta derivación es contextual y no factual; no establece "
                    "intención o necesidad del usuario, no selecciona capacidades "
                    "y no autoriza acciones."
                ),
                f"Resumen explicable de la derivación: {result.explanation.summary}",
            ]
            rationale = ("governed_reasoning_derived_context_applied",)
        else:
            lines = [
                f"Conclusión gobernada: {result.decision.conclusion}",
                (
                    "Confianza del razonamiento: "
                    f"{result.decision.confidence_score:.2f} "
                    f"({result.explanation.confidence_label})."
                ),
                f"Resumen explicable: {result.explanation.summary}",
            ]
            rationale = ("governed_reasoning_context_applied",)
        if result.decision.limitations:
            lines.append(
                "Limitaciones gobernadas: " + "; ".join(result.decision.limitations)
            )
        if result.decision.assumptions:
            lines.append(
                "Supuestos gobernados: " + "; ".join(result.decision.assumptions)
            )
        abstraction_context = getattr(self.source, "abstraction_context_lines", None)
        if callable(abstraction_context):
            lines.extend(
                abstraction_context(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        concept_context = getattr(self.source, "concept_context_lines", None)
        if callable(concept_context):
            lines.extend(
                concept_context(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        cross_domain_context = getattr(
            self.source,
            "cross_domain_synthesis_context_lines",
            None,
        )
        if callable(cross_domain_context):
            lines.extend(
                cross_domain_context(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        counterfactual_context = getattr(
            self.source,
            "counterfactual_path_comparison_context_lines",
            None,
        )
        if callable(counterfactual_context):
            lines.extend(
                counterfactual_context(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        analogy_context = getattr(
            self.source,
            "hierarchical_analogy_context_lines",
            None,
        )
        if callable(analogy_context):
            lines.extend(
                analogy_context(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        explanatory_context = getattr(
            self.source,
            "explanatory_model_context_lines",
            None,
        )
        if callable(explanatory_context):
            lines.extend(
                explanatory_context(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        explanatory_revision_context = getattr(
            self.source,
            "explanatory_model_revision_context_lines",
            None,
        )
        if callable(explanatory_revision_context):
            lines.extend(
                explanatory_revision_context(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            )
        if (
            continuity_selection is not None
            and continuity_context_surface is not None
        ):
            lines.extend(
                continuity_context_surface.context_lines(
                    selection=continuity_selection,
                )
            )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=tuple(lines),
            reference_ids=references,
            rationale=rationale,
        )

    def _skipped(
        self,
        rationale: str,
        reference_id: str | None = None,
    ) -> CognitiveRuntimeContribution:
        references = (reference_id,) if reference_id else ()
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.SKIPPED,
            reference_ids=references,
            rationale=(rationale,),
        )
