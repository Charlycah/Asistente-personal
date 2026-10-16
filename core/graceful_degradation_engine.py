from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_resilience_framework import (
    CognitiveResilienceAssessment,
    CognitiveResilienceFramework,
    CognitiveResiliencePosture,
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


class CognitiveDegradationMode(str, Enum):
    FULL = "full"
    CONSERVATIVE = "conservative"
    ESSENTIAL = "essential"
    CONTAINED = "contained"


class CognitiveCapabilityDisposition(str, Enum):
    PRESERVE = "preserve"
    LIMIT = "limit"
    SUSPEND = "suspend"


@dataclass(frozen=True)
class CognitiveCapabilityPolicy:
    capability: str
    disposition: CognitiveCapabilityDisposition | str
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        capability = self.capability.strip()
        disposition = CognitiveCapabilityDisposition(self.disposition)
        rationale = tuple(item.strip() for item in self.rationale if item.strip())
        if not capability:
            raise ValueError("cognitive degradation capability must not be blank")
        if not rationale:
            raise ValueError("cognitive degradation rationale must not be empty")
        if len(set(rationale)) != len(rationale):
            raise ValueError("cognitive degradation rationale must be unique")
        object.__setattr__(self, "capability", capability)
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class CognitiveDegradationDecision:
    owner: str
    session_id: str
    mode: CognitiveDegradationMode | str
    policies: tuple[CognitiveCapabilityPolicy, ...]
    triggers: tuple[str, ...]
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        mode = CognitiveDegradationMode(self.mode)
        triggers = tuple(item.strip() for item in self.triggers if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("cognitive degradation identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("cognitive degradation time must be timezone-aware")
        capabilities = tuple(item.capability for item in self.policies)
        if len(set(capabilities)) != len(capabilities):
            raise ValueError("cognitive degradation capabilities must be unique")
        if len(set(triggers)) != len(triggers):
            raise ValueError("cognitive degradation triggers must be unique")
        if len(set(references)) != len(references):
            raise ValueError("cognitive degradation references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    mode.value,
                    *(
                        f"{item.capability}:{item.disposition.value}:"
                        f"{','.join(item.rationale)}"
                        for item in self.policies
                    ),
                    *triggers,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("cognitive degradation decision id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "triggers", triggers)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "decision_id", expected)


class GracefulDegradationEngine:
    """Activate bounded cognitive service modes without attempting recovery."""

    _CAPABILITIES = (
        "conversation_continuity",
        "governed_reasoning",
        "memory_enrichment",
        "executive_planning",
        "background_cognition",
        "tool_expansion",
    )

    def __init__(self, framework: CognitiveResilienceFramework) -> None:
        self.framework = framework
        self.last_decision: CognitiveDegradationDecision | None = None

    def activate(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> CognitiveDegradationDecision:
        assessment = self.framework.assess(owner=owner, session_id=session_id, now=now)
        decision = self.activate_assessment(assessment)
        self.last_decision = decision
        return decision

    def activate_assessment(
        self, assessment: CognitiveResilienceAssessment
    ) -> CognitiveDegradationDecision:
        mode = self._mode(assessment)
        triggers = self._triggers(assessment)
        policies = tuple(
            CognitiveCapabilityPolicy(
                capability=capability,
                disposition=self._disposition(capability, mode, assessment),
                rationale=(
                    f"degradation_mode:{mode.value}",
                    f"resilience_posture:{assessment.posture.value}",
                ),
            )
            for capability in self._CAPABILITIES
        )
        return CognitiveDegradationDecision(
            owner=assessment.owner,
            session_id=assessment.session_id,
            mode=mode,
            policies=policies,
            triggers=triggers,
            source_reference_ids=(
                assessment.assessment_id,
                *assessment.source_reference_ids,
            ),
            created_at=assessment.created_at,
        )

    @staticmethod
    def _mode(assessment: CognitiveResilienceAssessment) -> CognitiveDegradationMode:
        return {
            CognitiveResiliencePosture.ROBUST: CognitiveDegradationMode.FULL,
            CognitiveResiliencePosture.GUARDED: CognitiveDegradationMode.CONSERVATIVE,
            CognitiveResiliencePosture.DEGRADED: CognitiveDegradationMode.ESSENTIAL,
            CognitiveResiliencePosture.CONTAINED: CognitiveDegradationMode.CONTAINED,
        }[assessment.posture]

    @staticmethod
    def _triggers(assessment: CognitiveResilienceAssessment) -> tuple[str, ...]:
        triggers = [f"posture:{assessment.posture.value}"]
        triggers.extend(
            f"failure_domain:{domain.value}" for domain in assessment.failure_domains
        )
        return tuple(triggers)

    @staticmethod
    def _disposition(
        capability: str,
        mode: CognitiveDegradationMode,
        assessment: CognitiveResilienceAssessment,
    ) -> CognitiveCapabilityDisposition:
        del assessment
        if capability == "conversation_continuity":
            return CognitiveCapabilityDisposition.PRESERVE
        if mode is CognitiveDegradationMode.FULL:
            return CognitiveCapabilityDisposition.PRESERVE
        if mode is CognitiveDegradationMode.CONSERVATIVE:
            return (
                CognitiveCapabilityDisposition.LIMIT
                if capability in {"background_cognition", "tool_expansion"}
                else CognitiveCapabilityDisposition.PRESERVE
            )
        if mode is CognitiveDegradationMode.ESSENTIAL:
            return (
                CognitiveCapabilityDisposition.PRESERVE
                if capability in {"governed_reasoning", "memory_enrichment"}
                else CognitiveCapabilityDisposition.SUSPEND
            )
        return CognitiveCapabilityDisposition.SUSPEND


@dataclass
class GracefulDegradationRuntimeContributor:
    engine: GracefulDegradationEngine
    blackboard: UnifiedCognitiveBlackboard
    name: str = "graceful_degradation_engine"

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
        decision = self.engine.activate(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key="cognitive_degradation_mode",
                value=decision.mode.value,
                confidence=1.0,
                source_reference_ids=(
                    decision.decision_id,
                    *decision.source_reference_ids,
                ),
                created_at=now,
            )
        )
        limited = (
            ",".join(
                item.capability
                for item in decision.policies
                if item.disposition is not CognitiveCapabilityDisposition.PRESERVE
            )
            or "none"
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                f"Degradación cognitiva: {decision.mode.value}; limitada={limited}.",
            ),
            reference_ids=(
                entry.entry_id,
                decision.decision_id,
                *decision.source_reference_ids,
            ),
            rationale=(
                "resilience_posture_translated_to_service_mode",
                "critical_conversation_continuity_preserved",
                "no_fault_recovery_authority_acquired",
            ),
        )
