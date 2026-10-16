from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_health_monitoring import CognitiveHealthStatus
from core.cognitive_performance_optimization import (
    CognitiveOptimizationStatus,
    CognitivePerformanceOptimizer,
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


class WholeSystemIntegrationStatus(str, Enum):
    READY = "ready"
    CONSTRAINED = "constrained"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class WholeSystemComponentState:
    component: str
    status: str
    reference_id: str

    def __post_init__(self) -> None:
        component = self.component.strip()
        status = self.status.strip()
        reference_id = self.reference_id.strip()
        if not component or not status or not reference_id:
            raise ValueError("whole-system component state must be complete")
        object.__setattr__(self, "component", component)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "reference_id", reference_id)


@dataclass(frozen=True)
class WholeSystemIntegrationReport:
    owner: str
    session_id: str
    status: WholeSystemIntegrationStatus | str
    operational_ready: bool
    score: float
    components: tuple[WholeSystemComponentState, ...]
    constraints: tuple[str, ...] = ()
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    report_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        status = WholeSystemIntegrationStatus(self.status)
        constraints = tuple(item.strip() for item in self.constraints if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("whole-system integration identity must be complete")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "whole-system integration score must be between zero and one"
            )
        if self.created_at.tzinfo is None:
            raise ValueError("whole-system integration time must be timezone-aware")
        if len({item.component for item in self.components}) != len(self.components):
            raise ValueError("whole-system components must be unique")
        if len(set(constraints)) != len(constraints):
            raise ValueError("whole-system constraints must be unique")
        if len(set(references)) != len(references):
            raise ValueError("whole-system references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    str(self.operational_ready),
                    f"{self.score:.3f}",
                    *(
                        f"{item.component}:{item.status}:{item.reference_id}"
                        for item in self.components
                    ),
                    *constraints,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.report_id and self.report_id != expected:
            raise ValueError("whole-system integration report id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "constraints", constraints)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "report_id", expected)


class WholeSystemIntegrator:
    """Consolidate M201-M209 into one governed end-to-end readiness report."""

    def __init__(self, optimizer: CognitivePerformanceOptimizer) -> None:
        self.optimizer = optimizer
        self.last_report: WholeSystemIntegrationReport | None = None

    def integrate(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> WholeSystemIntegrationReport:
        timestamp = now or datetime.now(timezone.utc)
        plan = self.optimizer.optimize(
            owner=owner, session_id=session_id, now=timestamp
        )
        monitor = self.optimizer.monitor
        health = monitor.last_report
        context = monitor.fusion.last_context
        if health is None or context is None:  # pragma: no cover - guarded by optimizer
            raise RuntimeError("whole-system integration requires health and context")

        components = (
            WholeSystemComponentState(
                "m201_blackboard", "available", context.source_reference_ids[-1]
            ),
            WholeSystemComponentState(
                "m202_global_state", "available", context.source_reference_ids[0]
            ),
            WholeSystemComponentState(
                "m203_event_bus", "available", context.context_id
            ),
            WholeSystemComponentState(
                "m204_coordination", "available", context.context_id
            ),
            WholeSystemComponentState(
                "m205_scheduler", "available", context.context_id
            ),
            WholeSystemComponentState(
                "m206_arbitration", "available", context.context_id
            ),
            WholeSystemComponentState(
                "m207_context_fusion", context.status.value, context.context_id
            ),
            WholeSystemComponentState(
                "m208_health", health.status.value, health.report_id
            ),
            WholeSystemComponentState(
                "m209_optimization", plan.status.value, plan.plan_id
            ),
        )
        constraints = tuple(dict.fromkeys((*context.constraints, *health.alerts)))
        if health.status is CognitiveHealthStatus.CRITICAL:
            status = WholeSystemIntegrationStatus.BLOCKED
        elif health.status is CognitiveHealthStatus.DEGRADED or plan.status in {
            CognitiveOptimizationStatus.THROTTLE,
            CognitiveOptimizationStatus.STABILIZE,
        }:
            status = WholeSystemIntegrationStatus.DEGRADED
        elif constraints or plan.status is CognitiveOptimizationStatus.TUNE:
            status = WholeSystemIntegrationStatus.CONSTRAINED
        else:
            status = WholeSystemIntegrationStatus.READY
        report = WholeSystemIntegrationReport(
            owner=owner,
            session_id=session_id,
            status=status,
            operational_ready=status
            in {
                WholeSystemIntegrationStatus.READY,
                WholeSystemIntegrationStatus.CONSTRAINED,
            },
            score=health.score,
            components=components,
            constraints=constraints,
            source_reference_ids=tuple(
                dict.fromkeys(
                    (
                        plan.plan_id,
                        health.report_id,
                        context.context_id,
                        *plan.source_reference_ids,
                    )
                )
            ),
            created_at=timestamp,
        )
        self.last_report = report
        return report


@dataclass
class WholeSystemIntegrationRuntimeContributor:
    integrator: WholeSystemIntegrator
    blackboard: UnifiedCognitiveBlackboard
    name: str = "whole_system_integration"

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
        report = self.integrator.integrate(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.HEALTH,
                key="whole_system_integration_status",
                value=report.status.value,
                confidence=report.score,
                source_reference_ids=(report.report_id, *report.source_reference_ids),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Integración total: "
                f"{report.status.value}; disponibilidad={report.operational_ready}.",
            ),
            reference_ids=(
                entry.entry_id,
                report.report_id,
                *report.source_reference_ids,
            ),
            rationale=(
                "m201_to_m209_consolidated_end_to_end",
                "health_constraints_and_optimization_preserved",
                "execution_authority_remains_governed_elsewhere",
            ),
        )
