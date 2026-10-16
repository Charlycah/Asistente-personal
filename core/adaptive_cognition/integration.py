from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.adaptive_cognition.episodic_memory import EpisodicMemoryManager
from core.adaptive_cognition.executive_coordination import (
    ExecutiveCoordinationManager,
)
from core.adaptive_cognition.executive_planning import ExecutivePlanningManager
from core.adaptive_cognition.knowledge_evolution import KnowledgeEvolutionManager
from core.adaptive_cognition.mental_models import MentalModel, MentalModelManager
from core.adaptive_cognition.meta_reasoning import MetaReasoningManager
from core.adaptive_cognition.reflection_engine import AdaptiveReflectionManager
from core.governed_reasoning import GovernedReasoningResult
from core.scope_guard import ScopeDomain


class AdaptiveCognitionStage(str, Enum):
    EPISODIC_MEMORY = "episodic_memory"
    MENTAL_MODELS = "mental_models"
    META_REASONING = "meta_reasoning"
    REFLECTION = "reflection"
    KNOWLEDGE_EVOLUTION = "knowledge_evolution"
    EXECUTIVE_PLANNING = "executive_planning"
    EXECUTIVE_COORDINATION = "executive_coordination"


class AdaptiveCognitionStageStatus(str, Enum):
    COMPLETED = "completed"
    AVAILABLE = "available"
    NOT_CONFIGURED = "not_configured"
    SKIPPED = "skipped"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class AdaptiveCognitionStageRecord:
    stage: AdaptiveCognitionStage | str
    status: AdaptiveCognitionStageStatus | str
    reference_ids: tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        stage = AdaptiveCognitionStage(self.stage)
        status = AdaptiveCognitionStageStatus(self.status)
        if len(set(self.reference_ids)) != len(self.reference_ids):
            raise ValueError("adaptive cognition references must be unique")
        if any(not item.strip() for item in self.reference_ids):
            raise ValueError("adaptive cognition references must not be blank")
        object.__setattr__(self, "stage", stage)
        object.__setattr__(self, "status", status)

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage.value,
            "status": self.status.value,
            "reference_ids": list(self.reference_ids),
            "note": self.note,
        }


@dataclass(frozen=True)
class AdaptiveCognitionCycle:
    reasoning_result_id: str
    stages: tuple[AdaptiveCognitionStageRecord, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cycle_id: str = ""

    def __post_init__(self) -> None:
        if not self.reasoning_result_id.strip() or not self.stages:
            raise ValueError("adaptive cognition cycle requires result and stages")
        if self.created_at.tzinfo is None:
            raise ValueError("adaptive cognition timestamp must be timezone-aware")
        stage_values = tuple(item.stage for item in self.stages)
        if len(set(stage_values)) != len(stage_values):
            raise ValueError("adaptive cognition cycle stages must be unique")
        expected = sha256(
            "|".join(
                (
                    self.reasoning_result_id,
                    ";".join(
                        f"{item.stage.value}:{item.status.value}:"
                        f"{','.join(item.reference_ids)}"
                        for item in self.stages
                    ),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.cycle_id and self.cycle_id != expected:
            raise ValueError("adaptive cognition cycle id is inconsistent")
        object.__setattr__(self, "cycle_id", expected)

    @property
    def requires_review(self) -> bool:
        return any(
            item.status is AdaptiveCognitionStageStatus.REVIEW_REQUIRED
            for item in self.stages
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "cycle_id": self.cycle_id,
            "reasoning_result_id": self.reasoning_result_id,
            "requires_review": self.requires_review,
            "stages": [item.to_dict() for item in self.stages],
            "created_at": self.created_at.isoformat(),
        }


@runtime_checkable
class AdaptiveCognitionCycleRepository(Protocol):
    def add(self, cycle: AdaptiveCognitionCycle) -> None: ...

    def get(self, cycle_id: str) -> AdaptiveCognitionCycle | None: ...

    def list_all(self) -> tuple[AdaptiveCognitionCycle, ...]: ...


class InMemoryAdaptiveCognitionCycleRepository:
    def __init__(self) -> None:
        self._cycles: dict[str, AdaptiveCognitionCycle] = {}

    def add(self, cycle: AdaptiveCognitionCycle) -> None:
        if cycle.cycle_id in self._cycles:
            raise ValueError("adaptive cognition cycle already exists")
        self._cycles[cycle.cycle_id] = cycle

    def get(self, cycle_id: str) -> AdaptiveCognitionCycle | None:
        return self._cycles.get(cycle_id)

    def list_all(self) -> tuple[AdaptiveCognitionCycle, ...]:
        return tuple(self._cycles.values())


@dataclass(frozen=True)
class AdaptiveCognitionPolicy:
    capture_episode: bool = True
    assess_reasoning: bool = True
    reflect_assessment: bool = True
    allow_automatic_knowledge_evolution: bool = False
    allow_automatic_executive_planning: bool = False
    allow_automatic_executive_coordination: bool = False

    def __post_init__(self) -> None:
        forbidden = (
            self.allow_automatic_knowledge_evolution,
            self.allow_automatic_executive_planning,
            self.allow_automatic_executive_coordination,
        )
        if any(forbidden):
            raise ValueError("adaptive cognition cannot automate governed evolution")


class AdaptiveCognitionManager:
    def __init__(
        self,
        *,
        episodic_memory: EpisodicMemoryManager | None = None,
        mental_models: MentalModelManager | None = None,
        meta_reasoning: MetaReasoningManager | None = None,
        adaptive_reflection: AdaptiveReflectionManager | None = None,
        knowledge_evolution: KnowledgeEvolutionManager | None = None,
        executive_planning: ExecutivePlanningManager | None = None,
        executive_coordination: ExecutiveCoordinationManager | None = None,
        repository: AdaptiveCognitionCycleRepository | None = None,
        policy: AdaptiveCognitionPolicy | None = None,
    ) -> None:
        self.episodic_memory = episodic_memory
        self.mental_models = mental_models
        self.meta_reasoning = meta_reasoning
        self.adaptive_reflection = adaptive_reflection
        self.knowledge_evolution = knowledge_evolution
        self.executive_planning = executive_planning
        self.executive_coordination = executive_coordination
        self.repository = repository or InMemoryAdaptiveCognitionCycleRepository()
        self.policy = policy or AdaptiveCognitionPolicy()
        self.last_cycle: AdaptiveCognitionCycle | None = None

    def process_reasoning(
        self,
        text: str,
        result: GovernedReasoningResult,
        *,
        owner: str = "shared",
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
        mental_models: tuple[MentalModel, ...] = (),
        now: datetime | None = None,
    ) -> AdaptiveCognitionCycle:
        stages: list[AdaptiveCognitionStageRecord] = []
        episode = None
        if self.episodic_memory is None:
            stages.append(self._not_configured(AdaptiveCognitionStage.EPISODIC_MEMORY))
        elif self.policy.capture_episode:
            episode = self.episodic_memory.capture_governed_reasoning(
                text, result, owner=owner, domains=domains
            )
            references = () if episode is None else (episode.episode_id,)
            stages.append(
                AdaptiveCognitionStageRecord(
                    AdaptiveCognitionStage.EPISODIC_MEMORY,
                    AdaptiveCognitionStageStatus.COMPLETED,
                    references,
                    "Experience captured without promotion to fact.",
                )
            )
        else:
            stages.append(self._skipped(AdaptiveCognitionStage.EPISODIC_MEMORY))

        stages.append(
            self._availability(AdaptiveCognitionStage.MENTAL_MODELS, self.mental_models)
        )
        assessment = None
        if self.meta_reasoning is None:
            stages.append(self._not_configured(AdaptiveCognitionStage.META_REASONING))
        elif self.policy.assess_reasoning:
            assessment = self.meta_reasoning.assess(
                result, mental_models=mental_models, now=now
            )
            status = (
                AdaptiveCognitionStageStatus.REVIEW_REQUIRED
                if assessment.requires_review
                else AdaptiveCognitionStageStatus.COMPLETED
            )
            stages.append(
                AdaptiveCognitionStageRecord(
                    AdaptiveCognitionStage.META_REASONING,
                    status,
                    (assessment.assessment_id,),
                    "Reasoning evaluated without changing its conclusion.",
                )
            )
        else:
            stages.append(self._skipped(AdaptiveCognitionStage.META_REASONING))

        if self.adaptive_reflection is None:
            stages.append(self._not_configured(AdaptiveCognitionStage.REFLECTION))
        elif assessment is not None and self.policy.reflect_assessment:
            episodes = () if episode is None else (episode,)
            reflection = self.adaptive_reflection.reflect(
                (assessment,),
                episodes=episodes,
                mental_models=mental_models,
                now=now,
            )
            status = (
                AdaptiveCognitionStageStatus.REVIEW_REQUIRED
                if reflection.requires_review
                else AdaptiveCognitionStageStatus.COMPLETED
            )
            stages.append(
                AdaptiveCognitionStageRecord(
                    AdaptiveCognitionStage.REFLECTION,
                    status,
                    (reflection.record_id,),
                    "Reflection remains advisory.",
                )
            )
        else:
            stages.append(self._skipped(AdaptiveCognitionStage.REFLECTION))

        stages.extend(
            (
                self._availability(
                    AdaptiveCognitionStage.KNOWLEDGE_EVOLUTION,
                    self.knowledge_evolution,
                ),
                self._availability(
                    AdaptiveCognitionStage.EXECUTIVE_PLANNING,
                    self.executive_planning,
                ),
                self._availability(
                    AdaptiveCognitionStage.EXECUTIVE_COORDINATION,
                    self.executive_coordination,
                ),
            )
        )
        cycle = AdaptiveCognitionCycle(
            reasoning_result_id=result.result_id,
            stages=tuple(stages),
            created_at=now or datetime.now(timezone.utc),
        )
        self.repository.add(cycle)
        self.last_cycle = cycle
        return cycle

    def readiness(self) -> tuple[AdaptiveCognitionStageRecord, ...]:
        return (
            self._availability(
                AdaptiveCognitionStage.EPISODIC_MEMORY, self.episodic_memory
            ),
            self._availability(
                AdaptiveCognitionStage.MENTAL_MODELS, self.mental_models
            ),
            self._availability(
                AdaptiveCognitionStage.META_REASONING, self.meta_reasoning
            ),
            self._availability(
                AdaptiveCognitionStage.REFLECTION, self.adaptive_reflection
            ),
            self._availability(
                AdaptiveCognitionStage.KNOWLEDGE_EVOLUTION,
                self.knowledge_evolution,
            ),
            self._availability(
                AdaptiveCognitionStage.EXECUTIVE_PLANNING,
                self.executive_planning,
            ),
            self._availability(
                AdaptiveCognitionStage.EXECUTIVE_COORDINATION,
                self.executive_coordination,
            ),
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        return (
            "Cognición adaptativa integrada: experiencia no equivale a hecho.",
            "Evaluación y reflexión no reemplazan decisiones gobernadas.",
            "No evoluciones conocimiento, planes o coordinación automáticamente.",
            "Toda adaptación debe ser trazable, revisable y no ejecutiva.",
        )

    @staticmethod
    def _availability(
        stage: AdaptiveCognitionStage, component: object | None
    ) -> AdaptiveCognitionStageRecord:
        if component is None:
            return AdaptiveCognitionManager._not_configured(stage)
        return AdaptiveCognitionStageRecord(
            stage,
            AdaptiveCognitionStageStatus.AVAILABLE,
            note="Capability configured; explicit invocation remains required.",
        )

    @staticmethod
    def _not_configured(
        stage: AdaptiveCognitionStage,
    ) -> AdaptiveCognitionStageRecord:
        return AdaptiveCognitionStageRecord(
            stage,
            AdaptiveCognitionStageStatus.NOT_CONFIGURED,
            note="Capability is not configured.",
        )

    @staticmethod
    def _skipped(stage: AdaptiveCognitionStage) -> AdaptiveCognitionStageRecord:
        return AdaptiveCognitionStageRecord(
            stage,
            AdaptiveCognitionStageStatus.SKIPPED,
            note="Stage skipped by policy or missing prerequisite.",
        )
