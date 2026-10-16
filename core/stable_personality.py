from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.presence import PresenceSnapshot
from core.relationship_memory import RelationshipMemorySnapshot
from core.social_regulation import SocialDistance, SocialRegulationSnapshot, SocialTone


class PersonalityTrait(str, Enum):
    """Rasgos estables que ROBY preserva entre turnos de convivencia."""

    CALM = "calm"
    PRECISE = "precise"
    SUPPORTIVE = "supportive"
    RESPECTFUL = "respectful"
    CONSISTENT = "consistent"


class PersonalityExpression(str, Enum):
    """Forma observable de expresar la personalidad sin cambiar identidad."""

    NEUTRAL = "neutral"
    WARM = "warm"
    CAREFUL = "careful"
    REPAIRING = "repairing"
    DIRECT = "direct"


@dataclass(frozen=True)
class StablePersonalityPolicy:
    """Política de estabilidad para modular expresión sin mutar personalidad."""

    baseline_traits: tuple[PersonalityTrait | str, ...] = (
        PersonalityTrait.CALM,
        PersonalityTrait.PRECISE,
        PersonalityTrait.SUPPORTIVE,
        PersonalityTrait.RESPECTFUL,
        PersonalityTrait.CONSISTENT,
    )
    minimum_consistency: float = 0.72
    familiarity_warmth_threshold: float = 0.62
    low_trust_care_threshold: float = 0.32

    def __post_init__(self) -> None:
        if not self.baseline_traits:
            raise ValueError("stable personality traits must not be empty")
        for trait in self.baseline_traits:
            PersonalityTrait(trait)
        if not 0.0 <= self.minimum_consistency <= 1.0:
            raise ValueError("minimum consistency must be between 0 and 1")
        if not 0.0 <= self.familiarity_warmth_threshold <= 1.0:
            raise ValueError("warmth threshold must be between 0 and 1")
        if not 0.0 <= self.low_trust_care_threshold <= 1.0:
            raise ValueError("care threshold must be between 0 and 1")

    @property
    def normalized_traits(self) -> tuple[PersonalityTrait, ...]:
        return tuple(PersonalityTrait(trait) for trait in self.baseline_traits)


@dataclass(frozen=True)
class StablePersonalitySnapshot:
    """Resultado auditable de M55 para un turno de convivencia."""

    expression: PersonalityExpression | str
    active_traits: tuple[PersonalityTrait | str, ...]
    consistency_score: float
    reason: str
    guidance: tuple[str, ...]
    presence_snapshot_id: str | None = None
    relationship_snapshot_id: str | None = None
    social_regulation_snapshot_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        PersonalityExpression(self.expression)
        if not self.active_traits:
            raise ValueError("stable personality active traits must not be empty")
        for trait in self.active_traits:
            PersonalityTrait(trait)
        if not 0.0 <= self.consistency_score <= 1.0:
            raise ValueError("personality consistency must be between 0 and 1")
        if not self.reason.strip():
            raise ValueError("stable personality reason must not be empty")
        if not self.guidance:
            raise ValueError("stable personality guidance must not be empty")
        if any(not line.strip() for line in self.guidance):
            raise ValueError("stable personality guidance lines must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("stable personality timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("stable personality snapshot id must not be empty")

    @property
    def normalized_expression(self) -> PersonalityExpression:
        return PersonalityExpression(self.expression)

    @property
    def normalized_traits(self) -> tuple[PersonalityTrait, ...]:
        return tuple(PersonalityTrait(trait) for trait in self.active_traits)

    def system_prompt_lines(self) -> tuple[str, ...]:
        traits = ", ".join(trait.value for trait in self.normalized_traits)
        lines = [
            "Personalidad estable M55:",
            f"- Expresión: {self.normalized_expression.value}",
            f"- Rasgos activos: {traits}",
            f"- Consistencia: {self.consistency_score:.2f}",
            f"- Motivo: {self.reason}",
        ]
        lines.extend(f"- Guía: {item}" for item in self.guidance)
        if self.presence_snapshot_id is not None:
            lines.append(f"- Presencia asociada: {self.presence_snapshot_id}")
        if self.relationship_snapshot_id is not None:
            lines.append(f"- Relación asociada: {self.relationship_snapshot_id}")
        if self.social_regulation_snapshot_id is not None:
            lines.append(
                f"- Regulación social asociada: {self.social_regulation_snapshot_id}"
            )
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "expression": self.normalized_expression.value,
            "active_traits": [trait.value for trait in self.normalized_traits],
            "consistency_score": self.consistency_score,
            "reason": self.reason,
            "guidance": list(self.guidance),
            "presence_snapshot_id": self.presence_snapshot_id,
            "relationship_snapshot_id": self.relationship_snapshot_id,
            "social_regulation_snapshot_id": self.social_regulation_snapshot_id,
            "created_at": self.created_at.isoformat(),
        }


class StablePersonalityEngine:
    """Motor puro de M55 — Personalidad Estable."""

    def __init__(self, policy: StablePersonalityPolicy | None = None) -> None:
        self.policy = policy or StablePersonalityPolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        social_regulation: SocialRegulationSnapshot | None = None,
        now: datetime | None = None,
    ) -> StablePersonalitySnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("stable personality timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("stable personality text must not be empty")

        expression = self._expression_for(relationship, social_regulation)
        consistency_score = self._consistency_for(relationship, social_regulation)
        reason = self._reason_for(expression, social_regulation)
        guidance = self._guidance_for(expression, social_regulation)

        return StablePersonalitySnapshot(
            expression=expression,
            active_traits=self.policy.normalized_traits,
            consistency_score=consistency_score,
            reason=reason,
            guidance=guidance,
            presence_snapshot_id=(
                presence.snapshot_id if presence is not None else None
            ),
            relationship_snapshot_id=(
                relationship.snapshot_id if relationship is not None else None
            ),
            social_regulation_snapshot_id=(
                social_regulation.snapshot_id if social_regulation is not None else None
            ),
            created_at=timestamp,
        )

    def _expression_for(
        self,
        relationship: RelationshipMemorySnapshot | None,
        social_regulation: SocialRegulationSnapshot | None,
    ) -> PersonalityExpression:
        if social_regulation is not None:
            tone = social_regulation.normalized_tone
            if tone is SocialTone.REPAIRING:
                return PersonalityExpression.REPAIRING
            if tone is SocialTone.CAREFUL:
                return PersonalityExpression.CAREFUL
            if tone is SocialTone.BOUNDARY_RESPECTING:
                return PersonalityExpression.DIRECT
            if (
                tone is SocialTone.SUPPORTIVE
                and social_regulation.normalized_distance is SocialDistance.FAMILIAR
            ):
                return PersonalityExpression.WARM
        if (
            relationship is not None
            and relationship.continuity_score
            >= self.policy.familiarity_warmth_threshold
            and relationship.trust_score > self.policy.low_trust_care_threshold
        ):
            return PersonalityExpression.WARM
        if (
            relationship is not None
            and relationship.trust_score <= self.policy.low_trust_care_threshold
        ):
            return PersonalityExpression.CAREFUL
        return PersonalityExpression.NEUTRAL

    def _consistency_for(
        self,
        relationship: RelationshipMemorySnapshot | None,
        social_regulation: SocialRegulationSnapshot | None,
    ) -> float:
        score = self.policy.minimum_consistency
        if relationship is not None:
            score += relationship.trust_score * 0.12
            score += relationship.continuity_score * 0.08
        if social_regulation is not None:
            score += social_regulation.confidence * 0.08
            if social_regulation.normalized_tone in {
                SocialTone.REPAIRING,
                SocialTone.BOUNDARY_RESPECTING,
            }:
                score -= 0.04
        return max(0.0, min(1.0, score))

    def _reason_for(
        self,
        expression: PersonalityExpression,
        social_regulation: SocialRegulationSnapshot | None,
    ) -> str:
        if expression is PersonalityExpression.REPAIRING:
            return "la personalidad conserva calma y precisión durante reparación"
        if expression is PersonalityExpression.CAREFUL:
            return "la personalidad reduce intensidad sin perder consistencia"
        if expression is PersonalityExpression.DIRECT:
            return "la personalidad respeta límites de forma clara y estable"
        if expression is PersonalityExpression.WARM:
            return "la personalidad expresa familiaridad sin cambiar identidad"
        if social_regulation is None:
            return "la personalidad usa su línea base estable"
        return "la personalidad acompaña la regulación social del turno"

    def _guidance_for(
        self,
        expression: PersonalityExpression,
        social_regulation: SocialRegulationSnapshot | None,
    ) -> tuple[str, ...]:
        guidance = [
            "Mantener calma, precisión y respeto aunque cambie el contexto.",
            "No simular emociones ni intimidad que no estén justificadas.",
            "Preservar continuidad de estilo entre turnos y milestones.",
        ]
        if expression is PersonalityExpression.WARM:
            guidance.append("Usar cercanía moderada sin perder sobriedad técnica.")
        if expression is PersonalityExpression.CAREFUL:
            guidance.append("Bajar intensidad y priorizar seguridad relacional.")
        if expression is PersonalityExpression.REPAIRING:
            guidance.append("Responder con reparación concreta y sin defensividad.")
        if expression is PersonalityExpression.DIRECT:
            guidance.append("Ser claro y reversible al respetar el límite del usuario.")
        if social_regulation is not None:
            guidance.append("No contradecir la guía activa de regulación social M54.")
        return tuple(guidance)


class StablePersonalityManager:
    """Fachada estable para M55.

    M55 fija una identidad expresiva consistente para ROBY. No sustituye M54 ni
    decide acciones; modula cómo se manifiestan los rasgos estables dentro del
    pipeline cognitivo y de convivencia.
    """

    def __init__(self, engine: StablePersonalityEngine | None = None) -> None:
        self.engine = engine or StablePersonalityEngine()
        self._snapshots: list[StablePersonalitySnapshot] = []

    @property
    def history(self) -> tuple[StablePersonalitySnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> StablePersonalitySnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def observe_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        social_regulation: SocialRegulationSnapshot | None = None,
        now: datetime | None = None,
    ) -> StablePersonalitySnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            presence=presence,
            relationship=relationship,
            social_regulation=social_regulation,
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Personalidad estable M55: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
