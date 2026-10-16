from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.presence import PresenceMode, PresenceSnapshot
from core.relationship_memory import RelationshipMemorySnapshot


class InitiativeKind(str, Enum):
    """Tipos de iniciativa que ROBY puede considerar sin ejecutarla."""

    NONE = "none"
    WAIT = "wait"
    ASK_CLARIFICATION = "ask_clarification"
    OFFER_NEXT_STEP = "offer_next_step"
    SUGGEST_ROUTINE = "suggest_routine"
    PROTECT_BOUNDARY = "protect_boundary"


class InitiativeDecision(str, Enum):
    """Decisión final de M53 sobre si ROBY debe intervenir."""

    SUPPRESS = "suppress"
    WAIT = "wait"
    PROPOSE = "propose"
    ASK = "ask"


@dataclass(frozen=True)
class InitiativeCandidate:
    """Posible iniciativa antes de aplicar límites de seguridad relacional."""

    kind: InitiativeKind | str
    confidence: float
    reason: str
    message: str | None = None
    source: str = "controlled_initiative"

    def __post_init__(self) -> None:
        InitiativeKind(self.kind)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("initiative confidence must be between 0 and 1")
        if not self.reason.strip():
            raise ValueError("initiative reason must not be empty")
        if self.message is not None and not self.message.strip():
            raise ValueError("initiative message must not be blank")
        if not self.source.strip():
            raise ValueError("initiative source must not be empty")

    @property
    def normalized_kind(self) -> InitiativeKind:
        return InitiativeKind(self.kind)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.normalized_kind.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "message": self.message,
            "source": self.source,
        }


@dataclass(frozen=True)
class InitiativeSnapshot:
    """Resultado auditable de M53 para un turno de convivencia."""

    decision: InitiativeDecision | str
    candidate: InitiativeCandidate
    should_intervene: bool
    intervention_text: str | None
    restraint_reason: str | None = None
    presence_snapshot_id: str | None = None
    relationship_snapshot_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        InitiativeDecision(self.decision)
        if self.should_intervene and not self.intervention_text:
            raise ValueError("initiative intervention text is required")
        if not self.should_intervene and self.intervention_text is not None:
            raise ValueError("suppressed initiative cannot include intervention text")
        if self.restraint_reason is not None and not self.restraint_reason.strip():
            raise ValueError("initiative restraint reason must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("initiative snapshot timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("initiative snapshot id must not be empty")

    @property
    def normalized_decision(self) -> InitiativeDecision:
        return InitiativeDecision(self.decision)

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Iniciativa controlada M53:",
            f"- Decisión: {self.normalized_decision.value}",
            f"- Tipo: {self.candidate.normalized_kind.value}",
            f"- Confianza: {self.candidate.confidence:.2f}",
        ]
        if self.should_intervene and self.intervention_text is not None:
            lines.append(f"- Intervención sugerida: {self.intervention_text}")
        elif self.restraint_reason is not None:
            lines.append(f"- Motivo de contención: {self.restraint_reason}")
        if self.presence_snapshot_id is not None:
            lines.append(f"- Presencia asociada: {self.presence_snapshot_id}")
        if self.relationship_snapshot_id is not None:
            lines.append(f"- Relación asociada: {self.relationship_snapshot_id}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "decision": self.normalized_decision.value,
            "candidate": self.candidate.to_dict(),
            "should_intervene": self.should_intervene,
            "intervention_text": self.intervention_text,
            "restraint_reason": self.restraint_reason,
            "presence_snapshot_id": self.presence_snapshot_id,
            "relationship_snapshot_id": self.relationship_snapshot_id,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class InitiativePolicy:
    """Política determinística de intervención prudente."""

    propose_threshold: float = 0.68
    ask_threshold: float = 0.58
    minimum_trust_to_propose: float = 0.30
    minimum_presence_to_propose: float = 0.25

    def __post_init__(self) -> None:
        if not 0.0 <= self.ask_threshold <= self.propose_threshold <= 1.0:
            raise ValueError("initiative thresholds must be ordered")
        if not 0.0 <= self.minimum_trust_to_propose <= 1.0:
            raise ValueError("initiative trust threshold must be between 0 and 1")
        if not 0.0 <= self.minimum_presence_to_propose <= 1.0:
            raise ValueError("initiative presence threshold must be between 0 and 1")


class InitiativeEngine:
    """Motor puro de M53 — Iniciativa Controlada."""

    _NEXT_STEP_PATTERNS = (
        "seguimos",
        "continuamos",
        "arrancamos",
        "empezamos",
        "despues me pasas el zip",
        "después me pasas el zip",
        "mismo metodo",
        "mismo método",
    )
    _CLARIFICATION_PATTERNS = (
        "no se",
        "no sé",
        "duda",
        "quizas",
        "quizás",
        "tal vez",
        "?",
    )
    _ROUTINE_PATTERNS = (
        "commit",
        "ruff",
        "pytest",
        "validamos",
        "zip",
    )
    _BOUNDARY_PATTERNS = (
        "no hagas",
        "no quiero",
        "sin romper",
        "no toques",
        "espera",
    )

    def __init__(self, policy: InitiativePolicy | None = None) -> None:
        self.policy = policy or InitiativePolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        now: datetime | None = None,
    ) -> InitiativeSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("initiative timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("initiative text must not be empty")

        candidate = self._candidate_for(text, presence, relationship)
        decision, should_intervene, restraint = self._decide(
            candidate,
            presence,
            relationship,
        )
        intervention_text = candidate.message if should_intervene else None

        return InitiativeSnapshot(
            decision=decision,
            candidate=candidate,
            should_intervene=should_intervene,
            intervention_text=intervention_text,
            restraint_reason=restraint,
            presence_snapshot_id=(
                presence.snapshot_id if presence is not None else None
            ),
            relationship_snapshot_id=(
                relationship.snapshot_id if relationship is not None else None
            ),
            created_at=timestamp,
        )

    def _candidate_for(
        self,
        text: str,
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
    ) -> InitiativeCandidate:
        normalized = text.lower()
        if self._contains_any(normalized, self._BOUNDARY_PATTERNS):
            return InitiativeCandidate(
                InitiativeKind.PROTECT_BOUNDARY,
                0.90,
                "explicit_boundary_requires_restraint",
                "Mantener el límite indicado y evitar acciones no solicitadas.",
            )
        if self._contains_any(normalized, self._NEXT_STEP_PATTERNS):
            confidence = 0.64 + self._continuity_bonus(presence, relationship)
            return InitiativeCandidate(
                InitiativeKind.OFFER_NEXT_STEP,
                min(1.0, confidence),
                "project_continuity_supports_next_step_offer",
                "Puedo proponer el siguiente paso y dejarlo listo para validar.",
            )
        if self._contains_any(normalized, self._ROUTINE_PATTERNS):
            confidence = 0.56 + self._continuity_bonus(presence, relationship)
            return InitiativeCandidate(
                InitiativeKind.SUGGEST_ROUTINE,
                min(1.0, confidence),
                "known_workflow_supports_routine_suggestion",
                "Conviene cerrar con ruff, pytest y commit antes de avanzar.",
            )
        if self._contains_any(normalized, self._CLARIFICATION_PATTERNS):
            return InitiativeCandidate(
                InitiativeKind.ASK_CLARIFICATION,
                0.62,
                "ambiguity_supports_single_clarifying_question",
                "Necesito una precisión mínima antes de avanzar.",
            )
        return InitiativeCandidate(
            InitiativeKind.WAIT,
            0.40,
            "no_stable_initiative_signal_detected",
            None,
        )

    def _decide(
        self,
        candidate: InitiativeCandidate,
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
    ) -> tuple[InitiativeDecision, bool, str | None]:
        kind = candidate.normalized_kind
        if kind is InitiativeKind.PROTECT_BOUNDARY:
            return (
                InitiativeDecision.WAIT,
                False,
                "explicit_boundary_prevents_unsolicited_initiative",
            )
        if kind is InitiativeKind.WAIT:
            return InitiativeDecision.WAIT, False, "no_action_needed"

        trust = relationship.trust_score if relationship is not None else 0.0
        continuity = presence.continuity_score if presence is not None else 0.0
        if trust < self.policy.minimum_trust_to_propose:
            return InitiativeDecision.SUPPRESS, False, "relationship_trust_too_low"
        if continuity < self.policy.minimum_presence_to_propose:
            return InitiativeDecision.SUPPRESS, False, "presence_continuity_too_low"
        if presence is not None and presence.normalized_mode is PresenceMode.RECOVERING:
            return InitiativeDecision.WAIT, False, "presence_is_recovering"

        if kind is InitiativeKind.ASK_CLARIFICATION:
            if candidate.confidence >= self.policy.ask_threshold:
                return InitiativeDecision.ASK, True, None
            return InitiativeDecision.WAIT, False, "clarification_confidence_too_low"

        if candidate.confidence >= self.policy.propose_threshold:
            return InitiativeDecision.PROPOSE, True, None
        return InitiativeDecision.WAIT, False, "initiative_confidence_too_low"

    @staticmethod
    def _continuity_bonus(
        presence: PresenceSnapshot | None,
        relationship: RelationshipMemorySnapshot | None,
    ) -> float:
        presence_score = presence.continuity_score if presence is not None else 0.0
        relationship_score = (
            relationship.continuity_score if relationship is not None else 0.0
        )
        familiarity_score = (
            relationship.familiarity_score if relationship is not None else 0.0
        )
        return (
            presence_score * 0.12 + relationship_score * 0.10 + familiarity_score * 0.08
        )

    @staticmethod
    def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
        return any(pattern in text for pattern in patterns)


class InitiativeManager:
    """Fachada estable para M53.

    M53 decide si ROBY puede tomar iniciativa conversacional. No ejecuta
    acciones externas, no agenda tareas, no llama herramientas y no reemplaza
    el ciclo cognitivo. Solo produce una recomendación auditable para capas
    superiores.
    """

    def __init__(self, engine: InitiativeEngine | None = None) -> None:
        self.engine = engine or InitiativeEngine()
        self._snapshots: list[InitiativeSnapshot] = []

    @property
    def history(self) -> tuple[InitiativeSnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> InitiativeSnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def observe_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        relationship: RelationshipMemorySnapshot | None = None,
        now: datetime | None = None,
    ) -> InitiativeSnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            presence=presence,
            relationship=relationship,
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Iniciativa controlada M53: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
