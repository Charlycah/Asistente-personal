from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.global_context_fusion import (
    GlobalContextFusionEngine,
    GlobalContextFusionStatus,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class CognitiveHealthStatus(str, Enum):
    HEALTHY = "healthy"
    WATCH = "watch"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass(frozen=True)
class CognitiveHealthDimension:
    name: str
    score: float
    observations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        name = self.name.strip()
        observations = tuple(item.strip() for item in self.observations if item.strip())
        if not name:
            raise ValueError("cognitive health dimension must have a name")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("cognitive health score must be between zero and one")
        if len(set(observations)) != len(observations):
            raise ValueError("cognitive health observations must be unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "observations", observations)


@dataclass(frozen=True)
class CognitiveHealthReport:
    owner: str
    session_id: str
    status: CognitiveHealthStatus | str
    score: float
    dimensions: tuple[CognitiveHealthDimension, ...]
    alerts: tuple[str, ...] = ()
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    report_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        status = CognitiveHealthStatus(self.status)
        alerts = tuple(item.strip() for item in self.alerts if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("cognitive health identity must be complete")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("cognitive health score must be between zero and one")
        if self.created_at.tzinfo is None:
            raise ValueError("cognitive health time must be timezone-aware")
        if len({item.name for item in self.dimensions}) != len(self.dimensions):
            raise ValueError("cognitive health dimensions must be unique")
        if len(set(alerts)) != len(alerts):
            raise ValueError("cognitive health alerts must be unique")
        if len(set(references)) != len(references):
            raise ValueError("cognitive health references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    f"{self.score:.3f}",
                    *(
                        f"{item.name}:{item.score:.3f}:{','.join(item.observations)}"
                        for item in self.dimensions
                    ),
                    *alerts,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.report_id and self.report_id != expected:
            raise ValueError("cognitive health report id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "alerts", alerts)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "report_id", expected)


class CognitiveHealthMonitor:
    """Assess whole-system cognitive health without changing system behavior."""

    def __init__(self, fusion: GlobalContextFusionEngine) -> None:
        self.fusion = fusion
        self.last_report: CognitiveHealthReport | None = None

    def assess(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> CognitiveHealthReport:
        timestamp = now or datetime.now(timezone.utc)
        context = self.fusion.last_context
        if (
            context is None
            or context.owner != owner.strip()
            or context.session_id != session_id.strip()
        ):
            context = self.fusion.fuse(
                owner=owner, session_id=session_id, now=timestamp
            )

        coverage = min(1.0, len(context.domains) / 4.0) if context.domains else 0.25
        confidence = (
            sum(item.confidence for item in context.domains) / len(context.domains)
            if context.domains
            else 0.5
        )
        coherence = {
            GlobalContextFusionStatus.EMPTY: 0.65,
            GlobalContextFusionStatus.COHERENT: 1.0,
            GlobalContextFusionStatus.CONSTRAINED: 0.65,
            GlobalContextFusionStatus.CONFLICTED: 0.25,
        }[context.status]
        availability = 1.0
        if context.deferred_actions:
            availability -= min(0.5, len(context.deferred_actions) * 0.1)
        if context.constraints:
            availability -= min(0.4, len(context.constraints) * 0.1)
        availability = max(0.0, availability)

        dimensions = (
            CognitiveHealthDimension("context_coverage", coverage),
            CognitiveHealthDimension("signal_confidence", confidence),
            CognitiveHealthDimension(
                "context_coherence",
                coherence,
                (context.status.value,),
            ),
            CognitiveHealthDimension(
                "cognitive_availability",
                availability,
                tuple((*context.constraints, *context.deferred_actions)),
            ),
        )
        score = round(sum(item.score for item in dimensions) / len(dimensions), 3)
        alert_items: list[str] = []
        if context.status is GlobalContextFusionStatus.CONFLICTED:
            alert_items.append("context_conflict_detected")
        alert_items.extend(f"constraint:{item}" for item in context.constraints)
        alert_items.extend(f"deferred:{item}" for item in context.deferred_actions)
        alerts = tuple(dict.fromkeys(alert_items))
        if context.status is GlobalContextFusionStatus.CONFLICTED or score < 0.45:
            status = CognitiveHealthStatus.CRITICAL
        elif score < 0.65:
            status = CognitiveHealthStatus.DEGRADED
        elif alerts or score < 0.85:
            status = CognitiveHealthStatus.WATCH
        else:
            status = CognitiveHealthStatus.HEALTHY
        report = CognitiveHealthReport(
            owner=owner,
            session_id=session_id,
            status=status,
            score=score,
            dimensions=dimensions,
            alerts=alerts,
            source_reference_ids=(context.context_id, *context.source_reference_ids),
            created_at=timestamp,
        )
        self.last_report = report
        return report


@dataclass
class CognitiveHealthMonitoringRuntimeContributor:
    monitor: CognitiveHealthMonitor
    blackboard: UnifiedCognitiveBlackboard
    name: str = "cognitive_health_monitoring"

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
        report = self.monitor.assess(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.HEALTH,
                key="cognitive_health_status",
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
                "Salud cognitiva: "
                f"{report.status.value}; puntuación {report.score:.3f}.",
            ),
            reference_ids=(
                entry.entry_id,
                report.report_id,
                *report.source_reference_ids,
            ),
            rationale=(
                "global_context_health_assessed",
                "conflicts_constraints_and_availability_observed",
                "health_diagnostic_published",
                "corrective_authority_not_acquired",
            ),
        )
