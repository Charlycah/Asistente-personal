from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.attention import AttentionManager
from core.identity import ROBYIdentity
from core.mental_state import ROBYMentalState
from core.planning import Plan, PlanningManager
from core.reasoning import ReasoningManager, ReasoningResult
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class LearningSignalKind(str, Enum):
    """Tipo de señal experiencial que ROBY puede aprender."""

    USER_FEEDBACK = "user_feedback"
    ROUTINE = "routine"
    PREFERENCE = "preference"
    REMINDER = "reminder"
    PLAN_OUTCOME = "plan_outcome"
    CORRECTION = "correction"
    OBSERVATION = "observation"


class LearningStrength(str, Enum):
    """Fuerza de una experiencia aprendida."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class LearningSignal:
    """Señal de experiencia capturada durante la convivencia.

    M47 no aprende datos de internet. Captura señales sobre hábitos,
    preferencias, correcciones y resultados para mejorar futuras decisiones.
    """

    description: str
    kind: LearningSignalKind | str = LearningSignalKind.OBSERVATION
    person: str | None = None
    source: str = "conversation"
    confidence: float = 0.7
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signal_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("learning signal description must not be empty")
        if self.person is not None and not self.person.strip():
            raise ValueError("learning signal person must not be empty")
        if not self.source.strip():
            raise ValueError("learning signal source must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("learning signal confidence must be between 0 and 1")
        if self.occurred_at.tzinfo is None:
            raise ValueError("learning signal timestamp must be timezone-aware")
        if not self.signal_id.strip():
            raise ValueError("learning signal id must not be empty")
        LearningSignalKind(self.kind)

    @property
    def normalized_kind(self) -> LearningSignalKind:
        return LearningSignalKind(self.kind)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.signal_id,
            "description": self.description,
            "kind": self.normalized_kind.value,
            "person": self.person,
            "source": self.source,
            "confidence": self.confidence,
            "occurred_at": self.occurred_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class LearnedExperience:
    """Experiencia consolidada que puede guiar futuras decisiones de ROBY."""

    lesson: str
    kind: LearningSignalKind | str = LearningSignalKind.OBSERVATION
    person: str | None = None
    strength: LearningStrength | str = LearningStrength.MEDIUM
    confidence: float = 0.7
    evidence: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    experience_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.lesson.strip():
            raise ValueError("learned experience lesson must not be empty")
        if self.person is not None and not self.person.strip():
            raise ValueError("learned experience person must not be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("learned experience confidence must be between 0 and 1")
        if self.created_at.tzinfo is None:
            raise ValueError("learned experience timestamp must be timezone-aware")
        if not self.experience_id.strip():
            raise ValueError("learned experience id must not be empty")
        LearningSignalKind(self.kind)
        LearningStrength(self.strength)

    @property
    def normalized_kind(self) -> LearningSignalKind:
        return LearningSignalKind(self.kind)

    @property
    def normalized_strength(self) -> LearningStrength:
        return LearningStrength(self.strength)

    def strengthened(self, evidence: str | None = None) -> LearnedExperience:
        next_confidence = min(1.0, round(self.confidence + 0.1, 2))
        strength = self.normalized_strength
        if next_confidence >= 0.85:
            strength = LearningStrength.HIGH
        elif next_confidence >= 0.55:
            strength = LearningStrength.MEDIUM
        new_evidence = self.evidence
        if evidence:
            new_evidence = (*new_evidence, evidence)
        return replace(
            self,
            confidence=next_confidence,
            strength=strength,
            evidence=new_evidence,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.experience_id,
            "lesson": self.lesson,
            "kind": self.normalized_kind.value,
            "person": self.person,
            "strength": self.normalized_strength.value,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class LearningContext:
    """Contexto explícito para transformar una señal en aprendizaje."""

    signal: LearningSignal
    identity: ROBYIdentity | None = None
    mental_state: ROBYMentalState | None = None
    attention: AttentionManager | None = None
    working_memory: WorkingMemoryManager | None = None
    reasoning: ReasoningManager | None = None
    reasoning_result: ReasoningResult | None = None
    planning: PlanningManager | None = None
    plan: Plan | None = None

    @property
    def latest_reasoning(self) -> ReasoningResult | None:
        if self.reasoning_result is not None:
            return self.reasoning_result
        if self.reasoning is None:
            return None
        return self.reasoning.last_result

    @property
    def latest_plan(self) -> Plan | None:
        if self.plan is not None:
            return self.plan
        if self.planning is None:
            return None
        return self.planning.last_plan


class ExperientialLearningEngine:
    """Motor M47 para convertir convivencia en aprendizaje seguro."""

    def learn(self, context: LearningContext) -> LearnedExperience:
        signal = context.signal
        lesson = self._lesson_for(context)
        strength = self._strength_for(signal)
        confidence = self._confidence_for(context)
        evidence = self._evidence_for(context)
        experience = LearnedExperience(
            lesson=lesson,
            kind=signal.normalized_kind,
            person=signal.person,
            strength=strength,
            confidence=confidence,
            evidence=evidence,
            metadata={"source": signal.source, **signal.metadata},
        )
        self._store_experience_in_workspace(context, experience)
        return experience

    def _lesson_for(self, context: LearningContext) -> str:
        signal = context.signal
        prefix = "ROBY observó"
        if signal.person:
            prefix = f"ROBY aprendió algo sobre {signal.person}"
        if signal.normalized_kind is LearningSignalKind.PREFERENCE:
            return f"{prefix}: preferencia detectada: {signal.description}"
        if signal.normalized_kind is LearningSignalKind.ROUTINE:
            return f"{prefix}: rutina detectada: {signal.description}"
        if signal.normalized_kind is LearningSignalKind.REMINDER:
            return f"{prefix}: patrón de recordatorio: {signal.description}"
        if signal.normalized_kind is LearningSignalKind.CORRECTION:
            return f"{prefix}: corrección a aplicar: {signal.description}"
        if signal.normalized_kind is LearningSignalKind.PLAN_OUTCOME:
            return f"{prefix}: resultado de plan: {signal.description}"
        return f"{prefix}: {signal.description}"

    def _strength_for(self, signal: LearningSignal) -> LearningStrength:
        if signal.confidence >= 0.85:
            return LearningStrength.HIGH
        if signal.confidence >= 0.55:
            return LearningStrength.MEDIUM
        return LearningStrength.LOW

    def _confidence_for(self, context: LearningContext) -> float:
        confidence = context.signal.confidence
        if context.identity is not None:
            confidence += 0.03
        if context.mental_state is not None:
            confidence += 0.02
        if context.attention is not None and context.attention.current_focus:
            confidence += 0.03
        if context.latest_reasoning is not None:
            confidence += 0.04
        if context.latest_plan is not None:
            confidence += 0.04
        return min(1.0, round(confidence, 2))

    def _evidence_for(self, context: LearningContext) -> tuple[str, ...]:
        evidence = [context.signal.description]
        if context.latest_reasoning is not None:
            evidence.append(context.latest_reasoning.conclusion)
        if context.latest_plan is not None:
            evidence.append(context.latest_plan.goal.description)
        return tuple(evidence)

    def _store_experience_in_workspace(
        self,
        context: LearningContext,
        experience: LearnedExperience,
    ) -> None:
        if context.working_memory is None:
            return
        context.working_memory.memory.remember(
            f"Aprendizaje activo: {experience.lesson}",
            kind=WorkingMemoryKind.FACT,
            source="learning",
            priority=10,
            confidence=experience.confidence,
            metadata={"experience_id": experience.experience_id},
        )


class ExperientialLearningManager:
    """Fachada M47 para acumular experiencias aprendidas."""

    def __init__(
        self,
        engine: ExperientialLearningEngine | None = None,
        *,
        capacity: int = 50,
    ) -> None:
        if capacity <= 0:
            raise ValueError("learning capacity must be greater than zero")
        self.engine = engine or ExperientialLearningEngine()
        self.capacity = capacity
        self.experiences: tuple[LearnedExperience, ...] = ()
        self.last_experience: LearnedExperience | None = None

    def learn(self, context: LearningContext) -> LearnedExperience:
        experience = self.engine.learn(context)
        self.last_experience = self._merge_or_append(experience)
        return self.last_experience

    def observe(
        self,
        description: str,
        *,
        kind: LearningSignalKind | str = LearningSignalKind.OBSERVATION,
        person: str | None = None,
        source: str = "conversation",
        confidence: float = 0.7,
        **context_kwargs: object,
    ) -> LearnedExperience:
        signal = LearningSignal(
            description=description,
            kind=kind,
            person=person,
            source=source,
            confidence=confidence,
        )
        return self.learn(LearningContext(signal=signal, **context_kwargs))

    def relevant_for(self, person: str | None = None) -> tuple[LearnedExperience, ...]:
        if person is None:
            return self.experiences
        return tuple(
            experience for experience in self.experiences if experience.person == person
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = ["Aprendizaje experiencial de ROBY:"]
        if not self.experiences:
            lines.append("- Sin experiencias aprendidas activas")
            return tuple(lines)
        for experience in self.experiences[:5]:
            target = f" sobre {experience.person}" if experience.person else ""
            lines.append(
                f"- {experience.normalized_strength.value}{target}: {experience.lesson}"
            )
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "capacity": self.capacity,
            "last_experience": (
                self.last_experience.to_dict()
                if self.last_experience is not None
                else None
            ),
            "experiences": [experience.to_dict() for experience in self.experiences],
        }

    def _merge_or_append(
        self,
        experience: LearnedExperience,
    ) -> LearnedExperience:
        merged = []
        selected = experience
        found = False
        for existing in self.experiences:
            same_lesson = existing.lesson == experience.lesson
            same_person = existing.person == experience.person
            same_kind = existing.normalized_kind is experience.normalized_kind
            if same_lesson and same_person and same_kind:
                selected = existing.strengthened(experience.evidence[0])
                merged.append(selected)
                found = True
            else:
                merged.append(existing)
        if not found:
            merged.insert(0, experience)
        self.experiences = tuple(merged[: self.capacity])
        return selected
