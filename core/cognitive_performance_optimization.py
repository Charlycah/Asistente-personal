from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_health_monitoring import (
    CognitiveHealthMonitor,
    CognitiveHealthStatus,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class CognitiveOptimizationStatus(str, Enum):
    OPTIMAL = "optimal"
    TUNE = "tune"
    THROTTLE = "throttle"
    STABILIZE = "stabilize"


@dataclass(frozen=True)
class CognitiveOptimizationRecommendation:
    action: str
    priority: int
    expected_benefit: float
    rationale: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        action = self.action.strip()
        rationale = tuple(item.strip() for item in self.rationale if item.strip())
        if not action:
            raise ValueError("optimization recommendation must have an action")
        if not 1 <= self.priority <= 100:
            raise ValueError(
                "optimization priority must be between one and one hundred"
            )
        if not 0.0 <= self.expected_benefit <= 1.0:
            raise ValueError("expected benefit must be between zero and one")
        if len(set(rationale)) != len(rationale):
            raise ValueError("optimization rationale must be unique")
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class CognitiveOptimizationPlan:
    owner: str
    session_id: str
    status: CognitiveOptimizationStatus | str
    baseline_score: float
    recommendations: tuple[CognitiveOptimizationRecommendation, ...]
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        status = CognitiveOptimizationStatus(self.status)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("optimization identity must be complete")
        if not 0.0 <= self.baseline_score <= 1.0:
            raise ValueError("optimization baseline score must be between zero and one")
        if self.created_at.tzinfo is None:
            raise ValueError("optimization time must be timezone-aware")
        if len({item.action for item in self.recommendations}) != len(
            self.recommendations
        ):
            raise ValueError("optimization recommendations must be unique")
        if (
            tuple(
                sorted(
                    self.recommendations, key=lambda item: (-item.priority, item.action)
                )
            )
            != self.recommendations
        ):
            raise ValueError("optimization recommendations must be priority ordered")
        if len(set(references)) != len(references):
            raise ValueError("optimization references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    f"{self.baseline_score:.3f}",
                    *(
                        f"{item.action}:{item.priority}:{item.expected_benefit:.3f}:{','.join(item.rationale)}"
                        for item in self.recommendations
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.plan_id and self.plan_id != expected:
            raise ValueError("optimization plan id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "plan_id", expected)


class CognitivePerformanceOptimizer:
    """Derive advisory performance recommendations from cognitive health."""

    def __init__(self, monitor: CognitiveHealthMonitor) -> None:
        self.monitor = monitor
        self.last_plan: CognitiveOptimizationPlan | None = None

    def optimize(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> CognitiveOptimizationPlan:
        timestamp = now or datetime.now(timezone.utc)
        report = self.monitor.last_report
        if (
            report is None
            or report.owner != owner.strip()
            or report.session_id != session_id.strip()
        ):
            report = self.monitor.assess(
                owner=owner, session_id=session_id, now=timestamp
            )

        recommendations: list[CognitiveOptimizationRecommendation] = []
        dimensions = {item.name: item for item in report.dimensions}
        if report.status is CognitiveHealthStatus.CRITICAL:
            recommendations.append(
                CognitiveOptimizationRecommendation(
                    "stabilize_conflicted_context", 100, 0.95, tuple(report.alerts)
                )
            )
        if report.status is CognitiveHealthStatus.DEGRADED:
            recommendations.append(
                CognitiveOptimizationRecommendation(
                    "reduce_nonessential_cognitive_load", 90, 0.80, ("degraded_health",)
                )
            )
        if (
            dimensions.get("context_coverage")
            and dimensions["context_coverage"].score < 0.75
        ):
            recommendations.append(
                CognitiveOptimizationRecommendation(
                    "improve_context_coverage", 70, 0.65, ("low_context_coverage",)
                )
            )
        if (
            dimensions.get("signal_confidence")
            and dimensions["signal_confidence"].score < 0.75
        ):
            recommendations.append(
                CognitiveOptimizationRecommendation(
                    "increase_signal_quality", 65, 0.60, ("low_signal_confidence",)
                )
            )
        if any(item.startswith("deferred:") for item in report.alerts):
            recommendations.append(
                CognitiveOptimizationRecommendation(
                    "review_deferred_work", 60, 0.55, ("deferred_work_present",)
                )
            )
        if any(item.startswith("constraint:") for item in report.alerts):
            recommendations.append(
                CognitiveOptimizationRecommendation(
                    "preserve_constraints_and_limit_parallelism",
                    80,
                    0.75,
                    ("active_constraints",),
                )
            )
        if not recommendations:
            recommendations.append(
                CognitiveOptimizationRecommendation(
                    "maintain_current_cognitive_profile",
                    10,
                    0.20,
                    ("healthy_baseline",),
                )
            )
        ordered = tuple(
            sorted(recommendations, key=lambda item: (-item.priority, item.action))
        )
        if report.status is CognitiveHealthStatus.CRITICAL:
            status = CognitiveOptimizationStatus.STABILIZE
        elif report.status is CognitiveHealthStatus.DEGRADED:
            status = CognitiveOptimizationStatus.THROTTLE
        elif report.status is CognitiveHealthStatus.WATCH or len(ordered) > 1:
            status = CognitiveOptimizationStatus.TUNE
        else:
            status = CognitiveOptimizationStatus.OPTIMAL
        plan = CognitiveOptimizationPlan(
            owner=owner,
            session_id=session_id,
            status=status,
            baseline_score=report.score,
            recommendations=ordered,
            source_reference_ids=(report.report_id, *report.source_reference_ids),
            created_at=timestamp,
        )
        self.last_plan = plan
        return plan


@dataclass
class CognitivePerformanceOptimizationRuntimeContributor:
    optimizer: CognitivePerformanceOptimizer
    blackboard: UnifiedCognitiveBlackboard
    name: str = "cognitive_performance_optimization"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del text, request
        plan = self.optimizer.optimize(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CANDIDATE,
                key="cognitive_optimization_status",
                value=plan.status.value,
                confidence=plan.baseline_score,
                source_reference_ids=(plan.plan_id, *plan.source_reference_ids),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Optimización cognitiva: "
                f"{plan.status.value}; {len(plan.recommendations)} recomendaciones.",
            ),
            reference_ids=(entry.entry_id, plan.plan_id, *plan.source_reference_ids),
            rationale=(
                "cognitive_health_translated_into_advisory_optimizations",
                "priority_and_expected_benefit_preserved",
                "automatic_tuning_authority_not_acquired",
            ),
        )
