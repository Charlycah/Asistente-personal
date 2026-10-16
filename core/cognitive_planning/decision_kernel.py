from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .calibration import (
    CognitiveCalibrationStatus,
    CognitiveKernelCalibration,
    CognitiveKernelCalibrationEngine,
)
from .capability_selection import CognitiveCapabilitySelectionAssessment
from .context_selection import CognitiveContextSelectionAssessment
from .decision_log import CognitiveDecisionLog, CognitiveDecisionLogSnapshot
from .executive_activation import CognitiveExecutiveActivationAssessment
from .explainability import CognitiveDecisionExplainer, CognitiveDecisionExplanation
from .metrics import CognitiveKernelMetricsCollector, CognitiveKernelMetricsSnapshot
from .models import (
    CognitiveIntent,
    CognitivePlan,
    CognitivePlanOutcomeAssessment,
    ContextRequirement,
    EvidenceLevel,
    FreshnessRequirement,
    PlannedResponseDecision,
    ShadowAssessmentStatus,
    ToolRequirement,
)
from .observability import (
    CognitiveKernelObservabilityExport,
    CognitiveKernelObservabilityExporter,
    CognitiveObservabilityProfile,
)
from .policy_resolution import (
    CognitivePolicyResolution,
    CognitivePolicyResolutionEngine,
)
from .trace_analysis import (
    CognitiveTraceAnalysisEngine,
    CognitiveTraceAnalysisSnapshot,
)
from .trace_anomaly import (
    CognitiveTraceAnomalyDetector,
    CognitiveTraceAnomalySnapshot,
)
from .trace_anomaly_consolidation import (
    CognitiveTraceAnomalyConsolidationSnapshot,
    CognitiveTraceAnomalyConsolidator,
)
from .trace_anomaly_lifecycle import (
    CognitiveTraceAnomalyLifecycle,
    CognitiveTraceAnomalyLifecycleSnapshot,
)
from .trace_anomaly_lifecycle_assessment import (
    CognitiveTraceAnomalyLifecycleAssessment,
    CognitiveTraceAnomalyLifecycleAssessor,
)
from .trace_anomaly_lifecycle_comparison import (
    CognitiveTraceAnomalyLifecycleComparator,
    CognitiveTraceAnomalyLifecycleComparison,
)
from .trace_anomaly_lifecycle_guidance import (
    CognitiveTraceAnomalyLifecycleAdvisor,
    CognitiveTraceAnomalyLifecycleGuidance,
)
from .trace_anomaly_lifecycle_query import (
    CognitiveTraceAnomalyLifecycleQuery,
    CognitiveTraceAnomalyLifecycleQueryEngine,
    CognitiveTraceAnomalyLifecycleView,
)
from .trace_anomaly_priority import (
    CognitiveTraceAnomalyPrioritizer,
    CognitiveTraceAnomalyPrioritySnapshot,
)
from .trace_correlation import (
    CognitiveDecisionCorrelation,
    CognitiveTraceCorrelator,
    CognitiveTraceSnapshot,
)
from .trace_query import (
    CognitiveTraceQuery,
    CognitiveTraceQueryEngine,
    CognitiveTraceQueryResult,
    CognitiveTraceRetentionPolicy,
)


class CognitiveRiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CognitiveConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CognitiveDecisionPolicy(StrEnum):
    RESPOND = "respond"
    RESPOND_WITH_CAUTION = "respond_with_caution"
    ABSTAIN_IF_UNVERIFIED = "abstain_if_unverified"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class CognitiveDecisionContext:
    """Canonical, provider-agnostic view of one cognitive decision."""

    intent: CognitiveIntent
    required_context: tuple[ContextRequirement, ...]
    required_tools: tuple[ToolRequirement, ...]
    freshness: FreshnessRequirement
    minimum_evidence: EvidenceLevel
    risk: CognitiveRiskLevel
    confidence: CognitiveConfidenceLevel
    policy: CognitiveDecisionPolicy
    plan: CognitivePlan
    outcome: CognitivePlanOutcomeAssessment | None
    capability: CognitiveCapabilitySelectionAssessment | None
    context: CognitiveContextSelectionAssessment | None
    activation: CognitiveExecutiveActivationAssessment | None
    rationale_codes: tuple[str, ...]
    policy_resolution: CognitivePolicyResolution
    explanation: CognitiveDecisionExplanation
    calibration: CognitiveKernelCalibration
    correlation: CognitiveDecisionCorrelation | None


class CognitiveDecisionKernel:
    """Consolidate planner artifacts without routing or executing anything."""

    def __init__(
        self,
        policy_resolution_engine: CognitivePolicyResolutionEngine | None = None,
        decision_explainer: CognitiveDecisionExplainer | None = None,
        calibration_engine: CognitiveKernelCalibrationEngine | None = None,
        metrics_collector: CognitiveKernelMetricsCollector | None = None,
        observability_exporter: CognitiveKernelObservabilityExporter | None = None,
        decision_log: CognitiveDecisionLog | None = None,
        trace_correlator: CognitiveTraceCorrelator | None = None,
        trace_retention_policy: CognitiveTraceRetentionPolicy | None = None,
        trace_query_engine: CognitiveTraceQueryEngine | None = None,
        trace_analysis_engine: CognitiveTraceAnalysisEngine | None = None,
        trace_anomaly_detector: CognitiveTraceAnomalyDetector | None = None,
        trace_anomaly_consolidator: CognitiveTraceAnomalyConsolidator | None = None,
        trace_anomaly_prioritizer: CognitiveTraceAnomalyPrioritizer | None = None,
        trace_anomaly_lifecycle: CognitiveTraceAnomalyLifecycle | None = None,
        trace_anomaly_lifecycle_query_engine: (
            CognitiveTraceAnomalyLifecycleQueryEngine | None
        ) = None,
        trace_anomaly_lifecycle_assessor: (
            CognitiveTraceAnomalyLifecycleAssessor | None
        ) = None,
        trace_anomaly_lifecycle_advisor: (
            CognitiveTraceAnomalyLifecycleAdvisor | None
        ) = None,
        trace_anomaly_lifecycle_comparator: (
            CognitiveTraceAnomalyLifecycleComparator | None
        ) = None,
    ) -> None:
        self.policy_resolution_engine = (
            policy_resolution_engine or CognitivePolicyResolutionEngine()
        )
        self.decision_explainer = decision_explainer or CognitiveDecisionExplainer()
        self.calibration_engine = (
            calibration_engine or CognitiveKernelCalibrationEngine()
        )
        self.metrics_collector = metrics_collector or CognitiveKernelMetricsCollector()
        self.observability_exporter = (
            observability_exporter or CognitiveKernelObservabilityExporter()
        )
        self.decision_log = decision_log or CognitiveDecisionLog()
        self.trace_retention_policy = (
            trace_retention_policy or CognitiveTraceRetentionPolicy()
        )
        self.trace_correlator = trace_correlator or CognitiveTraceCorrelator(
            capacity=self.trace_retention_policy.capacity
        )
        self.trace_query_engine = trace_query_engine or CognitiveTraceQueryEngine(
            maximum_query_results=self.trace_retention_policy.maximum_query_results
        )
        self.trace_analysis_engine = (
            trace_analysis_engine or CognitiveTraceAnalysisEngine()
        )
        self.trace_anomaly_detector = (
            trace_anomaly_detector or CognitiveTraceAnomalyDetector()
        )
        self.trace_anomaly_prioritizer = (
            trace_anomaly_prioritizer or CognitiveTraceAnomalyPrioritizer()
        )
        self.trace_anomaly_consolidator = (
            trace_anomaly_consolidator or CognitiveTraceAnomalyConsolidator()
        )
        self.trace_anomaly_lifecycle = (
            trace_anomaly_lifecycle or CognitiveTraceAnomalyLifecycle()
        )
        self.trace_anomaly_lifecycle_query_engine = (
            trace_anomaly_lifecycle_query_engine
            or CognitiveTraceAnomalyLifecycleQueryEngine()
        )
        self.trace_anomaly_lifecycle_assessor = (
            trace_anomaly_lifecycle_assessor
            or CognitiveTraceAnomalyLifecycleAssessor()
        )
        self.trace_anomaly_lifecycle_advisor = (
            trace_anomaly_lifecycle_advisor
            or CognitiveTraceAnomalyLifecycleAdvisor()
        )
        self.trace_anomaly_lifecycle_comparator = (
            trace_anomaly_lifecycle_comparator
            or CognitiveTraceAnomalyLifecycleComparator()
        )

    @property
    def metrics_snapshot(self) -> CognitiveKernelMetricsSnapshot:
        return self.metrics_collector.snapshot

    def reset_metrics(self) -> None:
        self.metrics_collector.reset()

    @property
    def decision_log_snapshot(self) -> CognitiveDecisionLogSnapshot:
        return self.decision_log.snapshot

    def clear_decision_log(self) -> None:
        self.decision_log.clear()

    @property
    def trace_snapshot(self) -> CognitiveTraceSnapshot:
        return self.trace_correlator.snapshot

    def clear_traces(self) -> None:
        self.trace_correlator.clear()

    def query_traces(
        self,
        query: CognitiveTraceQuery | None = None,
    ) -> CognitiveTraceQueryResult:
        safe_query = query or CognitiveTraceQuery()
        return self.trace_query_engine.query(
            self.trace_snapshot.correlations,
            self.decision_log_snapshot.events,
            safe_query,
        )

    def analyze_traces(
        self,
        query: CognitiveTraceQuery | None = None,
    ) -> CognitiveTraceAnalysisSnapshot:
        return self.trace_analysis_engine.analyze(
            self.trace_snapshot.correlations,
            self.decision_log_snapshot.events,
            query,
        )

    def detect_trace_anomalies(
        self,
        query: CognitiveTraceQuery | None = None,
    ) -> CognitiveTraceAnomalySnapshot:
        return self.trace_anomaly_detector.detect(self.analyze_traces(query))

    def prioritize_trace_anomalies(
        self,
        query: CognitiveTraceQuery | None = None,
        *,
        history: tuple[CognitiveTraceAnomalySnapshot, ...] = (),
    ) -> CognitiveTraceAnomalyPrioritySnapshot:
        return self.trace_anomaly_prioritizer.prioritize(
            self.detect_trace_anomalies(query), history
        )

    def consolidate_trace_anomalies(
        self,
        snapshots: tuple[CognitiveTraceAnomalyPrioritySnapshot, ...],
    ) -> CognitiveTraceAnomalyConsolidationSnapshot:
        return self.trace_anomaly_consolidator.consolidate(snapshots)

    def update_trace_anomaly_lifecycle(
        self,
        consolidation: CognitiveTraceAnomalyConsolidationSnapshot,
    ) -> CognitiveTraceAnomalyLifecycleSnapshot:
        return self.trace_anomaly_lifecycle.ingest(consolidation)

    @property
    def trace_anomaly_lifecycle_snapshot(
        self,
    ) -> CognitiveTraceAnomalyLifecycleSnapshot:
        return self.trace_anomaly_lifecycle.snapshot

    def acknowledge_trace_anomaly(
        self, code: str
    ) -> CognitiveTraceAnomalyLifecycleSnapshot:
        return self.trace_anomaly_lifecycle.acknowledge(code)

    def resolve_trace_anomaly(
        self, code: str
    ) -> CognitiveTraceAnomalyLifecycleSnapshot:
        return self.trace_anomaly_lifecycle.resolve(code)

    def clear_trace_anomaly_lifecycle(self) -> None:
        self.trace_anomaly_lifecycle.clear()

    def query_trace_anomaly_lifecycle(
        self,
        query: CognitiveTraceAnomalyLifecycleQuery | None = None,
    ) -> CognitiveTraceAnomalyLifecycleView:
        return self.trace_anomaly_lifecycle_query_engine.query(
            self.trace_anomaly_lifecycle_snapshot, query
        )

    def assess_trace_anomaly_lifecycle(
        self,
        comparison: CognitiveTraceAnomalyLifecycleComparison,
    ) -> CognitiveTraceAnomalyLifecycleAssessment:
        return self.trace_anomaly_lifecycle_assessor.assess(comparison)

    def advise_trace_anomaly_lifecycle(
        self,
        assessment: CognitiveTraceAnomalyLifecycleAssessment,
    ) -> CognitiveTraceAnomalyLifecycleGuidance:
        return self.trace_anomaly_lifecycle_advisor.advise(assessment)

    def compare_trace_anomaly_lifecycle(
        self,
        previous: CognitiveTraceAnomalyLifecycleSnapshot,
        current: CognitiveTraceAnomalyLifecycleSnapshot | None = None,
    ) -> CognitiveTraceAnomalyLifecycleComparison:
        return self.trace_anomaly_lifecycle_comparator.compare(
            previous, current or self.trace_anomaly_lifecycle_snapshot
        )

    def export_observability(
        self,
        decision: CognitiveDecisionContext | None = None,
        *,
        profile: CognitiveObservabilityProfile = CognitiveObservabilityProfile.SUMMARY,
    ) -> CognitiveKernelObservabilityExport:
        calibration = None if decision is None else decision.calibration
        explanation = None if decision is None else decision.explanation
        return self.observability_exporter.export(
            self.metrics_snapshot,
            calibration=calibration,
            explanation=explanation,
            profile=profile,
        )

    def consolidate(
        self,
        plan: CognitivePlan,
        *,
        outcome: CognitivePlanOutcomeAssessment | None = None,
        capability: CognitiveCapabilitySelectionAssessment | None = None,
        context: CognitiveContextSelectionAssessment | None = None,
        activation: CognitiveExecutiveActivationAssessment | None = None,
    ) -> CognitiveDecisionContext:
        risk = self._risk(plan)
        confidence = self._confidence(
            plan,
            outcome=outcome,
            capability=capability,
            context=context,
            activation=activation,
        )
        try:
            resolution = self.policy_resolution_engine.resolve(
                plan,
                risk=risk.value,
                confidence=confidence.value,
                outcome=outcome,
                capability=capability,
                context=context,
                activation=activation,
            )
        except Exception:
            resolution = CognitivePolicyResolution(
                policy=CognitiveDecisionPolicy.FALLBACK.value,
                decisive_rule="resolution_engine_failure",
                conflict_codes=("resolution_engine_failure",),
                rationale_codes=(
                    "policy_resolution:fallback",
                    "policy_rule:resolution_engine_failure",
                ),
                fallback_required=True,
            )
        policy = CognitiveDecisionPolicy(resolution.policy)
        try:
            explanation = self.decision_explainer.explain(
                plan,
                resolution,
                risk=risk.value,
                confidence=confidence.value,
                outcome=outcome,
                capability=capability,
                context=context,
                activation=activation,
            )
        except Exception:
            explanation = CognitiveDecisionExplanation(
                schema_version="rp22.02",
                decision=policy.value,
                decisive_rule=resolution.decisive_rule,
                evaluated_rules=(),
                conflict_codes=resolution.conflict_codes,
                evidence_codes=("explanation_engine_failure",),
                narrative=(
                    "Kernel explanation unavailable; canonical decision preserved."
                ),
                fallback_required=resolution.fallback_required,
            )
        try:
            calibration = self.calibration_engine.calibrate(
                plan,
                resolution,
                outcome=outcome,
                activation=activation,
            )
        except Exception:
            calibration = CognitiveKernelCalibration(
                schema_version="rp22.03",
                status=CognitiveCalibrationStatus.INCOMPLETE,
                plan_policy_aligned=False,
                policy_execution_aligned=None,
                outcome_aligned=None,
                divergence_codes=("calibration_engine_failure",),
                observation_codes=("calibration:unavailable",),
                score=0.0,
            )
        rationale = list(plan.rationale_codes)
        rationale.extend(resolution.rationale_codes)
        rationale.extend(
            (
                f"kernel_risk:{risk.value}",
                f"kernel_confidence:{confidence.value}",
            )
        )
        rationale.append(f"kernel_policy:{policy.value}")
        try:
            correlation = self.trace_correlator.correlate(
                activation_present=activation is not None,
                outcome_present=outcome is not None,
            )
        except Exception:
            correlation = None
        decision = CognitiveDecisionContext(
            intent=plan.intent,
            required_context=plan.required_context,
            required_tools=plan.required_tools,
            freshness=plan.freshness,
            minimum_evidence=plan.minimum_evidence,
            risk=risk,
            confidence=confidence,
            policy=policy,
            plan=plan,
            outcome=outcome,
            capability=capability,
            context=context,
            activation=activation,
            rationale_codes=tuple(dict.fromkeys(rationale)),
            policy_resolution=resolution,
            explanation=explanation,
            calibration=calibration,
            correlation=correlation,
        )
        try:
            self.metrics_collector.observe(resolution, calibration)
        except Exception:
            pass
        try:
            self.decision_log.record(
                plan,
                resolution,
                calibration,
                risk=risk.value,
                confidence=confidence.value,
                correlation=correlation,
            )
        except Exception:
            pass
        return decision

    @staticmethod
    def _risk(plan: CognitivePlan) -> CognitiveRiskLevel:
        if plan.response_decision is PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED:
            return CognitiveRiskLevel.HIGH
        if plan.freshness is FreshnessRequirement.CURRENT:
            return CognitiveRiskLevel.MODERATE
        if plan.intent is CognitiveIntent.ACTION:
            return CognitiveRiskLevel.MODERATE
        return CognitiveRiskLevel.LOW

    @staticmethod
    def _confidence(
        plan: CognitivePlan,
        *,
        outcome: CognitivePlanOutcomeAssessment | None,
        capability: CognitiveCapabilitySelectionAssessment | None,
        context: CognitiveContextSelectionAssessment | None,
        activation: CognitiveExecutiveActivationAssessment | None,
    ) -> CognitiveConfidenceLevel:
        if outcome is not None and outcome.status is ShadowAssessmentStatus.UNSATISFIED:
            return CognitiveConfidenceLevel.LOW
        if context is not None and context.status is ShadowAssessmentStatus.UNSATISFIED:
            return CognitiveConfidenceLevel.LOW
        if capability is not None and not capability.compatible:
            return CognitiveConfidenceLevel.LOW
        if activation is not None and activation.fallback_required:
            return CognitiveConfidenceLevel.MEDIUM
        if outcome is not None and outcome.status is ShadowAssessmentStatus.SATISFIED:
            return CognitiveConfidenceLevel.HIGH
        concrete_tools = tuple(
            tool for tool in plan.required_tools if tool is not ToolRequirement.NONE
        )
        if len(concrete_tools) == 1 and plan.rationale_codes:
            return CognitiveConfidenceLevel.HIGH
        return CognitiveConfidenceLevel.MEDIUM
