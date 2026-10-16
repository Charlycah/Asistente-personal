from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.initiative import InitiativeDecision, InitiativeSnapshot
from core.presence import PresenceMode, PresenceSnapshot
from core.relationship_memory import RelationshipMemorySnapshot


class SocialTone(str, Enum):
    """Tono social recomendado para convivir sin invadir."""

    NEUTRAL = "neutral"
    CAREFUL = "careful"
    SUPPORTIVE = "supportive"
    BOUNDARY_RESPECTING = "boundary_respecting"
    REPAIRING = "repairing"


class SocialDistance(str, Enum):
    """Distancia relacional que ROBY debe mantener en el turno."""

    RESERVED = "reserved"
    BALANCED = "balanced"
    FAMILIAR = "familiar"


class SocialRegulationAction(str, Enum):
    """Acción regulatoria sugerida antes de responder."""

    NONE = "none"
    ACKNOWLEDGE = "acknowledge"
    RESPECT_BOUNDARY = "respect_boundary"
    REDUCE_INITIATIVE = "reduce_initiative"
    REPAIR_TRUST = "repair_trust"
    CONFIRM_NEXT_STEP = "confirm_next_step"


@dataclass(frozen=True)
class SocialRegulationPolicy:
    """Política determinística para modular tono, distancia e iniciativa."""

    high_trust_threshold: float = 0.68
    low_trust_threshold: float = 0.28
    familiar_continuity_threshold: float = 0.62
    low_continuity_threshold: float = 0.25

    def __post_init__(self) -> None:
        if not 0.0 <= self.low_trust_threshold <= self.high_trust_threshold <= 1.0:
            raise ValueError("social trust thresholds must be ordered")
        if not 0.0 <= self.low_continuity_threshold <= 1.0:
            raise ValueError("social continuity threshold must be between 0 and 1")
        if not 0.0 <= self.familiar_continuity_threshold <= 1.0:
            raise ValueError("social familiarity threshold must be between 0 and 1")


@dataclass(frozen=True)
class SocialRegulationSnapshot:
    """Resultado auditable de M54 para un turno de convivencia."""

    tone: SocialTone | str
    distance: SocialDistance | str
    action: SocialRegulationAction | str
    confidence: float
    reason: str
    guidance: tuple[str, ...]
    presence_snapshot_id: str | None = None
    relationship_snapshot_id: str | None = None
    initiative_snapshot_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        SocialTone(self.tone)
        SocialDistance(self.distance)
        SocialRegulationAction(self.action)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("social regulation confidence must be between 0 and 1")
        if not self.reason.strip():
            raise ValueError("social regulation reason must not be empty")
        if not self.guidance:
            raise ValueError("social regulation guidance must not be empty")
        if any(not line.strip() for line in self.guidance):
            raise ValueError("social regulation guidance lines must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("social regulation timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("social regulation snapshot id must not be empty")

    @property
    def normalized_tone(self) -> SocialTone:
        return SocialTone(self.tone)

    @property
    def normalized_distance(self) -> SocialDistance:
        return SocialDistance(self.distance)

    @property
    def normalized_action(self) -> SocialRegulationAction:
        return SocialRegulationAction(self.action)

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Regulación social M54:",
            f"- Tono: {self.normalized_tone.value}",
            f"- Distancia: {self.normalized_distance.value}",
            f"- Acción: {self.normalized_action.value}",
            f"- Confianza: {self.confidence:.2f}",
            f"- Motivo: {self.reason}",
        ]
        lines.extend(f"- Guía: {item}" for item in self.guidance)
        if self.presence_snapshot_id is not None:
            lines.append(f"- Presencia asociada: {self.presence_snapshot_id}")
        if self.relationship_snapshot_id is not None:
            lines.append(f"- Relación asociada: {self.relationship_snapshot_id}")
        if self.initiative_snapshot_id is not None:
            lines.append(f"- Iniciativa asociada: {self.initiative_snapshot_id}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "tone": self.normalized_tone.value,
            "distance": self.normalized_distance.value,
            "action": self.normalized_action.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "guidance": list(self.guidance),
            "presence_snapshot_id": self.presence_snapshot_id,
            "relationship_snapshot_id": self.relationship_snapshot_id,
            "initiative_snapshot_id": self.initiative_snapshot_id,
            "created_at": self.created_at.isoformat(),
        }


class SocialRegulationEngine:
    """Motor puro de M54 — Regulación Social."""

    _BOUNDARY_PATTERNS = (
        "no hagas",
        "no quiero",
        "no toques",
        "espera",
        "sin cambiar",
        "sin romper",
    )
    _REPAIR_PATTERNS = (
        "falló",
        "fallo",
        "error",
        "rompiste",
        "no funciona",
        "arreglamos",
    )
    _ACKNOWLEDGE_PATTERNS = (
        "gracias",
        "perfecto",
        "excelente",
        "bien",
        "listo",
    )

    def __init__(self, policy: SocialRegulationPolicy | None = None) -> None:
        self.policy = policy or SocialRegulationPolicy()

    def regulate_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        initiative: InitiativeSnapshot | None = None,
        now: datetime | None = None,
    ) -> SocialRegulationSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("social regulation timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("social regulation text must not be empty")

        normalized = text.lower()
        tone = self._tone_for(normalized, presence, relationship, initiative)
        distance = self._distance_for(presence, relationship, initiative)
        action = self._action_for(normalized, presence, relationship, initiative)
        confidence = self._confidence_for(presence, relationship, initiative)
        reason = self._reason_for(action, tone, distance)
        guidance = self._guidance_for(tone, distance, action, initiative)

        return SocialRegulationSnapshot(
            tone=tone,
            distance=distance,
            action=action,
            confidence=confidence,
            reason=reason,
            guidance=guidance,
            presence_snapshot_id=(
                presence.snapshot_id if presence is not None else None
            ),
            relationship_snapshot_id=(
                relationship.snapshot_id if relationship is not None else None
            ),
            initiative_snapshot_id=(
                initiative.snapshot_id if initiative is not None else None
            ),
            created_at=timestamp,
        )

    def _tone_for(
        self,
        text: str,
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
        initiative: InitiativeSnapshot | None,
    ) -> SocialTone:
        if self._contains_any(text, self._BOUNDARY_PATTERNS):
            return SocialTone.BOUNDARY_RESPECTING
        if self._contains_any(text, self._REPAIR_PATTERNS):
            return SocialTone.REPAIRING
        if (
            relationship is not None
            and relationship.trust_score < self.policy.low_trust_threshold
        ):
            return SocialTone.CAREFUL
        if presence is not None and presence.normalized_mode is PresenceMode.RECOVERING:
            return SocialTone.CAREFUL
        if initiative is not None and initiative.should_intervene:
            return SocialTone.SUPPORTIVE
        if self._contains_any(text, self._ACKNOWLEDGE_PATTERNS):
            return SocialTone.SUPPORTIVE
        return SocialTone.NEUTRAL

    def _distance_for(
        self,
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
        initiative: InitiativeSnapshot | None,
    ) -> SocialDistance:
        if (
            initiative is not None
            and initiative.normalized_decision is InitiativeDecision.SUPPRESS
        ):
            return SocialDistance.RESERVED
        if (
            presence is not None
            and presence.continuity_score < self.policy.low_continuity_threshold
        ):
            return SocialDistance.RESERVED
        if relationship is None:
            return SocialDistance.RESERVED
        if relationship.trust_score < self.policy.low_trust_threshold:
            return SocialDistance.RESERVED
        if (
            relationship.trust_score >= self.policy.high_trust_threshold
            and relationship.continuity_score
            >= self.policy.familiar_continuity_threshold
        ):
            return SocialDistance.FAMILIAR
        return SocialDistance.BALANCED

    def _action_for(
        self,
        text: str,
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
        initiative: InitiativeSnapshot | None,
    ) -> SocialRegulationAction:
        if self._contains_any(text, self._BOUNDARY_PATTERNS):
            return SocialRegulationAction.RESPECT_BOUNDARY
        if self._contains_any(text, self._REPAIR_PATTERNS):
            return SocialRegulationAction.REPAIR_TRUST
        if initiative is not None:
            if initiative.normalized_decision is InitiativeDecision.SUPPRESS:
                return SocialRegulationAction.REDUCE_INITIATIVE
            if initiative.should_intervene:
                return SocialRegulationAction.CONFIRM_NEXT_STEP
        if (
            relationship is not None
            and relationship.trust_score < self.policy.low_trust_threshold
        ):
            return SocialRegulationAction.REDUCE_INITIATIVE
        if presence is not None and presence.normalized_mode is PresenceMode.RECOVERING:
            return SocialRegulationAction.ACKNOWLEDGE
        return SocialRegulationAction.ACKNOWLEDGE

    @staticmethod
    def _confidence_for(
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
        initiative: InitiativeSnapshot | None,
    ) -> float:
        score = 0.50
        if presence is not None:
            score += presence.continuity_score * 0.18
        if relationship is not None:
            score += relationship.trust_score * 0.16
            score += relationship.familiarity_score * 0.08
        if initiative is not None:
            score += initiative.candidate.confidence * 0.08
        return min(1.0, score)

    @staticmethod
    def _reason_for(
        action: SocialRegulationAction,
        tone: SocialTone,
        distance: SocialDistance,
    ) -> str:
        return f"{action.value}_with_{tone.value}_tone_and_{distance.value}_distance"

    @staticmethod
    def _guidance_for(
        tone: SocialTone,
        distance: SocialDistance,
        action: SocialRegulationAction,
        initiative: InitiativeSnapshot | None,
    ) -> tuple[str, ...]:
        guidance = [
            "Mantener una respuesta proporcional al vínculo y al turno actual.",
            "No aumentar familiaridad ni autonomía sin señales suficientes.",
        ]
        if tone is SocialTone.BOUNDARY_RESPECTING:
            guidance.append(
                "Reconocer el límite del usuario y no avanzar por cuenta propia."
            )
        if tone is SocialTone.REPAIRING:
            guidance.append(
                "Priorizar reparación, claridad y ausencia de defensividad."
            )
        if distance is SocialDistance.FAMILIAR:
            guidance.append(
                "Usar continuidad compartida sin asumir intimidad excesiva."
            )
        if action is SocialRegulationAction.CONFIRM_NEXT_STEP:
            guidance.append("Proponer el próximo paso de forma reversible y auditable.")
        if (
            initiative is not None
            and initiative.should_intervene
            and action is not SocialRegulationAction.CONFIRM_NEXT_STEP
        ):
            guidance.append("Moderar la iniciativa aunque exista una propuesta previa.")
        return tuple(guidance)

    @staticmethod
    def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
        return any(pattern in text for pattern in patterns)


class SocialRegulationManager:
    """Fachada estable para M54.

    M54 regula tono, distancia social e iniciativa antes de responder. No llama
    herramientas, no modifica memoria externa y no reemplaza el ciclo cognitivo;
    solo entrega guía social auditable a las capas superiores.
    """

    def __init__(self, engine: SocialRegulationEngine | None = None) -> None:
        self.engine = engine or SocialRegulationEngine()
        self._snapshots: list[SocialRegulationSnapshot] = []

    @property
    def history(self) -> tuple[SocialRegulationSnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> SocialRegulationSnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def observe_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        initiative: InitiativeSnapshot | None = None,
        now: datetime | None = None,
    ) -> SocialRegulationSnapshot:
        snapshot = self.engine.regulate_turn(
            text,
            presence=presence,
            relationship=relationship,
            initiative=initiative,
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Regulación social M54: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
