from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

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
from core.whole_system_integration import (
    WholeSystemIntegrationReport,
    WholeSystemIntegrationStatus,
    WholeSystemIntegrator,
)


class CognitiveResiliencePosture(str, Enum):
    ROBUST = "robust"
    GUARDED = "guarded"
    DEGRADED = "degraded"
    CONTAINED = "contained"


class CognitiveFailureDomain(str, Enum):
    CONTEXT = "context"
    COORDINATION = "coordination"
    SCHEDULING = "scheduling"
    HEALTH = "health"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"


@dataclass(frozen=True)
class CognitiveResilienceSafeguard:
    safeguard: str
    domain: CognitiveFailureDomain | str
    priority: int
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        safeguard = self.safeguard.strip()
        domain = CognitiveFailureDomain(self.domain)
        rationale = tuple(item.strip() for item in self.rationale if item.strip())
        if not safeguard:
            raise ValueError("cognitive resilience safeguard must not be blank")
        if not 1 <= self.priority <= 100:
            raise ValueError("cognitive resilience priority must be between 1 and 100")
        if not rationale:
            raise ValueError("cognitive resilience rationale must not be empty")
        if len(set(rationale)) != len(rationale):
            raise ValueError("cognitive resilience rationale must be unique")
        object.__setattr__(self, "safeguard", safeguard)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class CognitiveResilienceAssessment:
    owner: str
    session_id: str
    posture: CognitiveResiliencePosture | str
    resilience_score: float
    failure_domains: tuple[CognitiveFailureDomain | str, ...]
    safeguards: tuple[CognitiveResilienceSafeguard, ...]
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        posture = CognitiveResiliencePosture(self.posture)
        domains = tuple(CognitiveFailureDomain(item) for item in self.failure_domains)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("cognitive resilience identity must be complete")
        if not 0.0 <= self.resilience_score <= 1.0:
            raise ValueError("cognitive resilience score must be between zero and one")
        if self.created_at.tzinfo is None:
            raise ValueError("cognitive resilience time must be timezone-aware")
        if len(set(domains)) != len(domains):
            raise ValueError("cognitive resilience failure domains must be unique")
        safeguards = tuple(item.safeguard for item in self.safeguards)
        if len(set(safeguards)) != len(safeguards):
            raise ValueError("cognitive resilience safeguards must be unique")
        if len(set(references)) != len(references):
            raise ValueError("cognitive resilience references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    posture.value,
                    f"{self.resilience_score:.3f}",
                    *(item.value for item in domains),
                    *(
                        f"{item.safeguard}:{item.domain.value}:{item.priority}:"
                        f"{','.join(item.rationale)}"
                        for item in self.safeguards
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("cognitive resilience assessment id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "posture", posture)
        object.__setattr__(self, "failure_domains", domains)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "assessment_id", expected)


class CognitiveResilienceFramework:
    """Derive a governed resilience posture without executing recovery actions."""

    _COMPONENT_DOMAINS = {
        "m203_event_bus": CognitiveFailureDomain.COORDINATION,
        "m204_coordination": CognitiveFailureDomain.COORDINATION,
        "m205_scheduler": CognitiveFailureDomain.SCHEDULING,
        "m206_arbitration": CognitiveFailureDomain.COORDINATION,
        "m207_context_fusion": CognitiveFailureDomain.CONTEXT,
        "m208_health": CognitiveFailureDomain.HEALTH,
        "m209_optimization": CognitiveFailureDomain.PERFORMANCE,
    }

    def __init__(self, integrator: WholeSystemIntegrator) -> None:
        self.integrator = integrator
        self.last_assessment: CognitiveResilienceAssessment | None = None

    def assess(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> CognitiveResilienceAssessment:
        timestamp = now or datetime.now(timezone.utc)
        report = self.integrator.integrate(
            owner=owner, session_id=session_id, now=timestamp
        )
        assessment = self.assess_report(report)
        self.last_assessment = assessment
        return assessment

    def assess_report(
        self, report: WholeSystemIntegrationReport
    ) -> CognitiveResilienceAssessment:
        domains = self._failure_domains(report)
        safeguards = self._safeguards(report, domains)
        posture = self._posture(report)
        penalty = min(0.35, 0.05 * len(domains) + 0.02 * len(report.constraints))
        score = max(0.0, min(1.0, report.score - penalty))
        return CognitiveResilienceAssessment(
            owner=report.owner,
            session_id=report.session_id,
            posture=posture,
            resilience_score=score,
            failure_domains=domains,
            safeguards=safeguards,
            source_reference_ids=(report.report_id, *report.source_reference_ids),
            created_at=report.created_at,
        )

    @classmethod
    def _failure_domains(
        cls, report: WholeSystemIntegrationReport
    ) -> tuple[CognitiveFailureDomain, ...]:
        domains: list[CognitiveFailureDomain] = []
        for component in report.components:
            if component.status not in {"available", "ready", "healthy", "optimal"}:
                domains.append(
                    cls._COMPONENT_DOMAINS.get(
                        component.component, CognitiveFailureDomain.INTEGRATION
                    )
                )
        if report.constraints:
            domains.append(CognitiveFailureDomain.INTEGRATION)
        if report.status is WholeSystemIntegrationStatus.BLOCKED:
            domains.append(CognitiveFailureDomain.HEALTH)
        return tuple(dict.fromkeys(domains))

    @staticmethod
    def _posture(report: WholeSystemIntegrationReport) -> CognitiveResiliencePosture:
        if report.status is WholeSystemIntegrationStatus.BLOCKED:
            return CognitiveResiliencePosture.CONTAINED
        if report.status is WholeSystemIntegrationStatus.DEGRADED:
            return CognitiveResiliencePosture.DEGRADED
        if report.status is WholeSystemIntegrationStatus.CONSTRAINED:
            return CognitiveResiliencePosture.GUARDED
        return CognitiveResiliencePosture.ROBUST

    @staticmethod
    def _safeguards(
        report: WholeSystemIntegrationReport,
        domains: tuple[CognitiveFailureDomain, ...],
    ) -> tuple[CognitiveResilienceSafeguard, ...]:
        safeguards: list[CognitiveResilienceSafeguard] = []
        for domain in domains:
            action, priority = {
                CognitiveFailureDomain.CONTEXT: ("preserve_last_coherent_context", 85),
                CognitiveFailureDomain.COORDINATION: ("isolate_conflicting_work", 90),
                CognitiveFailureDomain.SCHEDULING: ("bound_cognitive_concurrency", 80),
                CognitiveFailureDomain.HEALTH: (
                    "contain_unhealthy_cognitive_path",
                    100,
                ),
                CognitiveFailureDomain.PERFORMANCE: (
                    "protect_critical_cognitive_budget",
                    75,
                ),
                CognitiveFailureDomain.INTEGRATION: (
                    "retain_governed_safe_baseline",
                    95,
                ),
            }[domain]
            safeguards.append(
                CognitiveResilienceSafeguard(
                    safeguard=action,
                    domain=domain,
                    priority=priority,
                    rationale=(f"failure_domain:{domain.value}",),
                )
            )
        if not safeguards:
            safeguards.append(
                CognitiveResilienceSafeguard(
                    safeguard="maintain_resilience_baseline",
                    domain=CognitiveFailureDomain.INTEGRATION,
                    priority=10,
                    rationale=("whole_system_ready",),
                )
            )
        return tuple(
            sorted(safeguards, key=lambda item: (-item.priority, item.safeguard))
        )


@dataclass
class CognitiveResilienceRuntimeContributor:
    framework: CognitiveResilienceFramework
    blackboard: UnifiedCognitiveBlackboard
    name: str = "cognitive_resilience_framework"

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
        assessment = self.framework.assess(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.HEALTH,
                key="cognitive_resilience_posture",
                value=assessment.posture.value,
                confidence=assessment.resilience_score,
                source_reference_ids=(
                    assessment.assessment_id,
                    *assessment.source_reference_ids,
                ),
                created_at=now,
            )
        )
        domain_summary = (
            ",".join(item.value for item in assessment.failure_domains) or "none"
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Resiliencia cognitiva: "
                f"{assessment.posture.value}; dominios={domain_summary}.",
            ),
            reference_ids=(
                entry.entry_id,
                assessment.assessment_id,
                *assessment.source_reference_ids,
            ),
            rationale=(
                "whole_system_resilience_posture_derived",
                "failure_domains_and_safeguards_traceable",
                "no_degradation_or_recovery_authority_acquired",
            ),
        )
