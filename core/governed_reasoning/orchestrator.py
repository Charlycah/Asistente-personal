from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.governed_reasoning.bounded_non_rule_derivation import (
    BoundedNonRuleDerivationStatus,
    GovernedBoundedNonRuleDerivation,
)
from core.governed_reasoning.claims import Claim
from core.governed_reasoning.conflicts import (
    ConflictAnalysis,
    ConflictResolutionManager,
)
from core.governed_reasoning.context import (
    ContextAssemblyStatus,
    GovernedContextAssembler,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.governed_reasoning.decisions import (
    DecisionRecord,
    DecisionRecordManager,
)
from core.governed_reasoning.explanations import (
    ExplainableAnswer,
    ExplainableAnswerRenderer,
    ExplanationLevel,
)
from core.governed_reasoning.inference import (
    GovernedInferenceEngine,
    InferenceRun,
    InferenceStatus,
)
from core.governed_reasoning.visual_evidence_relation import (
    GovernedVisualEvidenceRelationEvaluator,
)
from core.scope_guard import ScopeDomain


class GovernedReasoningStatus(str, Enum):
    COMPLETED = "completed"
    DERIVED = "derived"
    ABSTAINED = "abstained"
    BLOCKED = "blocked"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedReasoningPolicy:
    explanation_level: ExplanationLevel | str = ExplanationLevel.STANDARD
    max_citations: int = 20
    abstention_text: str = "Insufficient governed evidence to reach a conclusion."
    blocked_text: str = "The query is outside the permitted reasoning scope."

    def __post_init__(self) -> None:
        ExplanationLevel(self.explanation_level)
        if self.max_citations <= 0:
            raise ValueError("maximum citations must be positive")
        if not self.abstention_text.strip() or not self.blocked_text.strip():
            raise ValueError("governed reasoning policy text must not be empty")


@dataclass(frozen=True)
class GovernedReasoningResult:
    status: GovernedReasoningStatus | str
    context: ReasoningContextBundle
    inference_run: InferenceRun
    conflict_analysis: ConflictAnalysis
    decision: DecisionRecord
    explanation: ExplainableAnswer
    non_rule_derivations: tuple[GovernedBoundedNonRuleDerivation, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result_id: str = ""

    def __post_init__(self) -> None:
        GovernedReasoningStatus(self.status)
        if self.created_at.tzinfo is None:
            raise ValueError("governed reasoning timestamp must be timezone-aware")
        expected = sha256(
            "|".join(
                (
                    GovernedReasoningStatus(self.status).value,
                    self.context.context_id,
                    self.inference_run.run_id,
                    self.conflict_analysis.analysis_id,
                    self.decision.decision_id,
                    self.explanation.answer_id,
                    ",".join(
                        item.source_fingerprint
                        for item in self.non_rule_derivations
                    ),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.result_id and self.result_id != expected:
            raise ValueError("governed reasoning result id is inconsistent")
        object.__setattr__(self, "result_id", expected)

    @property
    def requires_human_review(self) -> bool:
        return self.status is GovernedReasoningStatus.REVIEW_REQUIRED

    def snapshot(self) -> dict[str, object]:
        return {
            "result_id": self.result_id,
            "status": GovernedReasoningStatus(self.status).value,
            "context_id": self.context.context_id,
            "decision_id": self.decision.decision_id,
            "answer_id": self.explanation.answer_id,
            "confidence": self.decision.confidence_score,
            "requires_human_review": self.requires_human_review,
            "non_rule_derivation_count": len(self.non_rule_derivations),
        }


class GovernedReasoningOrchestrator:
    def __init__(
        self,
        *,
        context_assembler: GovernedContextAssembler,
        inference_engine: GovernedInferenceEngine,
        conflict_manager: ConflictResolutionManager,
        decision_manager: DecisionRecordManager,
        explanation_renderer: ExplainableAnswerRenderer | None = None,
        policy: GovernedReasoningPolicy | None = None,
        pre_inference_observer: Callable[[tuple[object, ...]], object] | None = None,
    ) -> None:
        self.context_assembler = context_assembler
        self.inference_engine = inference_engine
        self.conflict_manager = conflict_manager
        self.decision_manager = decision_manager
        self.explanation_renderer = explanation_renderer or ExplainableAnswerRenderer()
        self.policy = policy or GovernedReasoningPolicy()
        self.pre_inference_observer = pre_inference_observer

    def reason(
        self,
        query: ReasoningQuery,
        *,
        now: datetime | None = None,
        scope_reference: str | None = None,
        transient_claims: tuple[Claim, ...] = (),
        non_rule_derivations: tuple[GovernedBoundedNonRuleDerivation, ...] = (),
        visual_context_contribution: CognitiveRuntimeContribution | None = None,
    ) -> GovernedReasoningResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("governed reasoning timestamp must be timezone-aware")
        context = self.context_assembler.assemble(query, now=timestamp)
        if transient_claims:
            by_id = {claim.claim_id: claim for claim in context.claims}
            for claim in transient_claims:
                by_id.setdefault(claim.claim_id, claim)
            transient_status = context.status
            if context.normalized_status is ContextAssemblyStatus.INSUFFICIENT:
                transient_status = ContextAssemblyStatus.READY
            context = replace(
                context,
                status=transient_status,
                claims=tuple(by_id.values()),
                context_id="",
            )
        if (
            visual_context_contribution is not None
            and visual_context_contribution.stage == "visual_context"
            and visual_context_contribution.status
            is CognitiveRuntimeStageStatus.APPLIED
            and context.evidence
        ):
            assessment = GovernedVisualEvidenceRelationEvaluator().evaluate(
                proposition_id=context.query.query_id,
                owner=query.owner,
                visual=visual_context_contribution,
                evidence=context.evidence,
            )
            context = replace(
                context,
                derived_assessments=(
                    *context.derived_assessments,
                    assessment,
                ),
                context_id="",
            )
        if self.pre_inference_observer is not None:
            try:
                self.pre_inference_observer(context.claims)
            except Exception:
                pass
        scope = {"scope_reference": scope_reference}
        inference_run = self.inference_engine.infer(context, now=timestamp, **scope)
        conflict_analysis = self.conflict_manager.analyze(
            context.claims,
            inference_run=inference_run,
            now=timestamp,
        )
        valid_non_rule_derivations = tuple(
            item
            for item in non_rule_derivations
            if item.status is BoundedNonRuleDerivationStatus.DERIVED
            and item.derived_claim is not None
        )
        status = self._status(
            context,
            inference_run,
            conflict_analysis,
            valid_non_rule_derivations,
        )
        conclusion = self._conclusion(
            status,
            context,
            inference_run,
            valid_non_rule_derivations,
        )
        limitations = self._limitations(status, context, conflict_analysis)
        decision = self.decision_manager.record(
            context,
            conflict_analysis,
            conclusion=conclusion,
            inference_run=inference_run,
            non_rule_derivations=valid_non_rule_derivations,
            limitations=limitations,
            created_at=timestamp,
        )
        explanation = self.explanation_renderer.render(
            decision,
            level=self.policy.explanation_level,
            max_citations=self.policy.max_citations,
        )
        return GovernedReasoningResult(
            status=status,
            context=context,
            inference_run=inference_run,
            conflict_analysis=conflict_analysis,
            decision=decision,
            explanation=explanation,
            non_rule_derivations=valid_non_rule_derivations,
            created_at=timestamp,
        )

    def _status(
        self,
        context: ReasoningContextBundle,
        inference_run: InferenceRun,
        conflicts: ConflictAnalysis,
        non_rule_derivations: tuple[GovernedBoundedNonRuleDerivation, ...] = (),
    ) -> GovernedReasoningStatus:
        if context.normalized_status is ContextAssemblyStatus.BLOCKED:
            return GovernedReasoningStatus.BLOCKED
        if context.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED:
            return GovernedReasoningStatus.REVIEW_REQUIRED
        if conflicts.requires_review or any(
            result.normalized_status is InferenceStatus.REVIEW_REQUIRED
            for result in inference_run.results
        ):
            return GovernedReasoningStatus.REVIEW_REQUIRED
        if context.normalized_status is ContextAssemblyStatus.INSUFFICIENT:
            return GovernedReasoningStatus.ABSTAINED
        if inference_run.applied_claims:
            return GovernedReasoningStatus.COMPLETED
        if non_rule_derivations:
            return GovernedReasoningStatus.DERIVED
        return GovernedReasoningStatus.ABSTAINED

    def _conclusion(
        self,
        status: GovernedReasoningStatus,
        context: ReasoningContextBundle,
        inference_run: InferenceRun,
        non_rule_derivations: tuple[GovernedBoundedNonRuleDerivation, ...] = (),
    ) -> str:
        if status is GovernedReasoningStatus.BLOCKED:
            return self.policy.blocked_text
        if status is GovernedReasoningStatus.ABSTAINED:
            return self.policy.abstention_text
        if status is GovernedReasoningStatus.DERIVED:
            claims = tuple(
                item.derived_claim
                for item in non_rule_derivations
                if item.derived_claim is not None
            )
            if claims:
                return "; ".join(
                    f"{item.subject} {item.predicate} {item.object_value}"
                    for item in claims
                )
            return self.policy.abstention_text
        claims = inference_run.applied_claims
        if claims:
            return "; ".join(
                f"{item.subject} {item.predicate} {item.object_value}"
                for item in claims
            )
        if context.claims:
            item = context.claims[0]
            return f"{item.subject} {item.predicate} {item.object_value}"
        return self.policy.abstention_text

    @staticmethod
    def _limitations(
        status: GovernedReasoningStatus,
        context: ReasoningContextBundle,
        conflicts: ConflictAnalysis,
    ) -> tuple[str, ...]:
        limitations: list[str] = []
        if status is GovernedReasoningStatus.ABSTAINED:
            limitations.append("insufficient applicable governed inference")
        if status is GovernedReasoningStatus.BLOCKED:
            limitations.append("scope guard blocked the query")
        if status is GovernedReasoningStatus.REVIEW_REQUIRED:
            limitations.append("human review is required before relying on the result")
        if conflicts.conflicts:
            limitations.append("conflicting claims were detected")
        if not context.evidence:
            limitations.append("no evidence reference was selected")
        return tuple(limitations)


class GovernedReasoningManager:
    def __init__(
        self,
        orchestrator: GovernedReasoningOrchestrator,
        *,
        owner: str = "shared",
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
    ) -> None:
        if not owner.strip():
            raise ValueError("governed reasoning owner must not be empty")
        self.orchestrator = orchestrator
        self.owner = owner
        self.domains = tuple(ScopeDomain(item) for item in domains)
        self.last_result: GovernedReasoningResult | None = None

    def observe_turn(
        self,
        text: str,
        *,
        now: datetime | None = None,
    ) -> GovernedReasoningResult:
        timestamp = now or datetime.now(timezone.utc)
        query = ReasoningQuery(
            text,
            owner=self.owner,
            domains=self.domains,
            as_of=timestamp,
        )
        self.last_result = self.orchestrator.reason(query, now=timestamp)
        return self.last_result

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = (
            "Razonamiento gobernado: distingue evidencia, claims e inferencias.",
            "No conviertas inferencias en hechos ni acciones autorizadas.",
        )
        if self.last_result is None:
            return lines
        return lines + (
            "Último razonamiento gobernado: "
            f"{GovernedReasoningStatus(self.last_result.status).value}.",
            f"Confianza registrada: {self.last_result.decision.confidence_score:.2f}.",
        )
