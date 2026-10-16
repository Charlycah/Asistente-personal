from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.collaboration import CollaborationSnapshot
from core.initiative import InitiativeSnapshot
from core.relationship_memory import RelationshipMemorySnapshot
from core.social_regulation import SocialRegulationSnapshot
from core.stable_personality import StablePersonalitySnapshot


class TrustSignal(str, Enum):
    """Señales que aumentan trazabilidad, cautela y confianza operativa."""

    EXPLANATION_REQUEST = "explanation_request"
    VALIDATION = "validation"
    UNCERTAINTY = "uncertainty"
    TRACEABILITY = "traceability"
    RELIABILITY = "reliability"


class TrustPosture(str, Enum):
    """Postura de M58 frente a una respuesta o colaboración."""

    BASELINE = "baseline"
    EXPLAIN = "explain"
    VERIFY = "verify"
    CALIBRATE = "calibrate"
    AUDIT = "audit"


@dataclass(frozen=True)
class TrustExplainabilityPolicy:
    """Política de M58 para explicar sin sobreprometer ni inventar certeza."""

    explain_threshold: float = 0.42
    verify_threshold: float = 0.58
    audit_threshold: float = 0.76
    max_explanation_items: int = 5

    def __post_init__(self) -> None:
        thresholds = (
            self.explain_threshold,
            self.verify_threshold,
            self.audit_threshold,
        )
        if any(not 0.0 <= threshold <= 1.0 for threshold in thresholds):
            raise ValueError("trust thresholds must be between 0 and 1")
        if not self.explain_threshold <= self.verify_threshold:
            raise ValueError("trust thresholds must be ordered")
        if self.verify_threshold > self.audit_threshold:
            raise ValueError("trust audit threshold is too low")
        if self.max_explanation_items <= 0:
            raise ValueError("trust explanation item limit must be positive")


@dataclass(frozen=True)
class TrustExplainabilitySnapshot:
    """Resultado auditable de M58 para confianza y explicabilidad."""

    signals: tuple[TrustSignal | str, ...]
    posture: TrustPosture | str
    confidence_score: float
    explainability_score: float
    rationale: str
    explanation_items: tuple[str, ...]
    uncertainty_notes: tuple[str, ...]
    relationship_snapshot_id: str | None = None
    initiative_snapshot_id: str | None = None
    social_regulation_snapshot_id: str | None = None
    personality_snapshot_id: str | None = None
    collaboration_snapshot_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("trust signals must not be empty")
        for signal in self.signals:
            TrustSignal(signal)
        TrustPosture(self.posture)
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("trust confidence must be between 0 and 1")
        if not 0.0 <= self.explainability_score <= 1.0:
            raise ValueError("trust explainability must be between 0 and 1")
        if not self.rationale.strip():
            raise ValueError("trust rationale must not be empty")
        if not self.explanation_items:
            raise ValueError("trust explanation items must not be empty")
        if any(not item.strip() for item in self.explanation_items):
            raise ValueError("trust explanation items must not be blank")
        if any(not note.strip() for note in self.uncertainty_notes):
            raise ValueError("trust uncertainty notes must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("trust timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("trust snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[TrustSignal, ...]:
        return tuple(TrustSignal(signal) for signal in self.signals)

    @property
    def normalized_posture(self) -> TrustPosture:
        return TrustPosture(self.posture)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Confianza y explicabilidad M58:",
            f"- Postura: {self.normalized_posture.value}",
            f"- Señales: {signals}",
            f"- Confianza calibrada: {self.confidence_score:.2f}",
            f"- Explicabilidad: {self.explainability_score:.2f}",
            f"- Racional: {self.rationale}",
        ]
        lines.extend(f"- Explicar: {item}" for item in self.explanation_items)
        lines.extend(f"- Incertidumbre: {note}" for note in self.uncertainty_notes)
        if self.relationship_snapshot_id is not None:
            lines.append(f"- Relación asociada: {self.relationship_snapshot_id}")
        if self.initiative_snapshot_id is not None:
            lines.append(f"- Iniciativa asociada: {self.initiative_snapshot_id}")
        if self.social_regulation_snapshot_id is not None:
            lines.append(
                f"- Regulación social asociada: {self.social_regulation_snapshot_id}"
            )
        if self.personality_snapshot_id is not None:
            lines.append(f"- Personalidad asociada: {self.personality_snapshot_id}")
        if self.collaboration_snapshot_id is not None:
            lines.append(f"- Colaboración asociada: {self.collaboration_snapshot_id}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "posture": self.normalized_posture.value,
            "confidence_score": self.confidence_score,
            "explainability_score": self.explainability_score,
            "rationale": self.rationale,
            "explanation_items": list(self.explanation_items),
            "uncertainty_notes": list(self.uncertainty_notes),
            "relationship_snapshot_id": self.relationship_snapshot_id,
            "initiative_snapshot_id": self.initiative_snapshot_id,
            "social_regulation_snapshot_id": self.social_regulation_snapshot_id,
            "personality_snapshot_id": self.personality_snapshot_id,
            "collaboration_snapshot_id": self.collaboration_snapshot_id,
            "created_at": self.created_at.isoformat(),
        }


class TrustExplainabilityEngine:
    """Motor puro de M58 — Confianza y Explicabilidad."""

    def __init__(self, policy: TrustExplainabilityPolicy | None = None) -> None:
        self.policy = policy or TrustExplainabilityPolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        relationship: RelationshipMemorySnapshot | None = None,
        initiative: InitiativeSnapshot | None = None,
        social_regulation: SocialRegulationSnapshot | None = None,
        personality: StablePersonalitySnapshot | None = None,
        collaboration: CollaborationSnapshot | None = None,
        history_size: int = 0,
        now: datetime | None = None,
    ) -> TrustExplainabilitySnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("trust timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("trust text must not be empty")

        signals = self._signals_for(text, history_size)
        confidence_score = self._confidence_for(
            signals,
            relationship,
            social_regulation,
            personality,
            collaboration,
            history_size,
        )
        explainability_score = self._explainability_for(
            signals,
            initiative,
            collaboration,
        )
        posture = self._posture_for(signals, confidence_score, explainability_score)
        rationale = self._rationale_for(signals, posture)
        explanation_items = self._explanation_items_for(signals, posture)
        uncertainty_notes = self._uncertainty_notes_for(signals, posture)

        return TrustExplainabilitySnapshot(
            signals=signals,
            posture=posture,
            confidence_score=confidence_score,
            explainability_score=explainability_score,
            rationale=rationale,
            explanation_items=explanation_items[: self.policy.max_explanation_items],
            uncertainty_notes=uncertainty_notes,
            relationship_snapshot_id=(
                relationship.snapshot_id if relationship is not None else None
            ),
            initiative_snapshot_id=(
                initiative.snapshot_id if initiative is not None else None
            ),
            social_regulation_snapshot_id=(
                social_regulation.snapshot_id if social_regulation is not None else None
            ),
            personality_snapshot_id=(
                personality.snapshot_id if personality is not None else None
            ),
            collaboration_snapshot_id=(
                collaboration.snapshot_id if collaboration is not None else None
            ),
            created_at=timestamp,
        )

    def _signals_for(self, text: str, history_size: int) -> tuple[TrustSignal, ...]:
        normalized = text.lower()
        signals: list[TrustSignal] = []
        if any(word in normalized for word in ("explica", "por qué", "porque")):
            signals.append(TrustSignal.EXPLANATION_REQUEST)
        if any(word in normalized for word in ("ruff", "pytest", "valid", "check")):
            signals.append(TrustSignal.VALIDATION)
        if any(word in normalized for word in ("no estoy seguro", "duda", "riesgo")):
            signals.append(TrustSignal.UNCERTAINTY)
        if any(word in normalized for word in ("traza", "auditable", "contrato")):
            signals.append(TrustSignal.TRACEABILITY)
        if any(word in normalized for word in ("confianza", "estable", "regresión")):
            signals.append(TrustSignal.RELIABILITY)
        if history_size > 0 and TrustSignal.TRACEABILITY not in signals:
            signals.append(TrustSignal.TRACEABILITY)
        if not signals:
            signals.append(TrustSignal.RELIABILITY)
        return tuple(dict.fromkeys(signals))

    def _confidence_for(
        self,
        signals: tuple[TrustSignal, ...],
        relationship: RelationshipMemorySnapshot | None,
        social_regulation: SocialRegulationSnapshot | None,
        personality: StablePersonalitySnapshot | None,
        collaboration: CollaborationSnapshot | None,
        history_size: int,
    ) -> float:
        score = 0.30 + min(len(signals) * 0.06, 0.24)
        score += min(history_size * 0.04, 0.16)
        if TrustSignal.VALIDATION in signals:
            score += 0.14
        if TrustSignal.UNCERTAINTY in signals:
            score -= 0.10
        if relationship is not None:
            score += relationship.familiarity_score * 0.08
        if social_regulation is not None:
            score += social_regulation.confidence * 0.10
        if personality is not None:
            score += personality.consistency_score * 0.08
        if collaboration is not None:
            score += collaboration.continuity_score * 0.08
        return max(0.0, min(1.0, score))

    def _explainability_for(
        self,
        signals: tuple[TrustSignal, ...],
        initiative: InitiativeSnapshot | None,
        collaboration: CollaborationSnapshot | None,
    ) -> float:
        score = 0.28 + min(len(signals) * 0.08, 0.32)
        if TrustSignal.EXPLANATION_REQUEST in signals:
            score += 0.16
        if TrustSignal.TRACEABILITY in signals:
            score += 0.12
        if initiative is not None:
            score += initiative.candidate.confidence * 0.06
        if collaboration is not None:
            score += collaboration.progress_score * 0.08
        return max(0.0, min(1.0, score))

    def _posture_for(
        self,
        signals: tuple[TrustSignal, ...],
        confidence_score: float,
        explainability_score: float,
    ) -> TrustPosture:
        if TrustSignal.UNCERTAINTY in signals:
            return TrustPosture.CALIBRATE
        if (
            TrustSignal.VALIDATION in signals
            and explainability_score >= self.policy.audit_threshold
        ):
            return TrustPosture.AUDIT
        if confidence_score >= self.policy.verify_threshold:
            return TrustPosture.VERIFY
        if explainability_score >= self.policy.explain_threshold:
            return TrustPosture.EXPLAIN
        return TrustPosture.BASELINE

    def _rationale_for(
        self,
        signals: tuple[TrustSignal, ...],
        posture: TrustPosture,
    ) -> str:
        if posture is TrustPosture.AUDIT:
            return "la interacción requiere trazabilidad verificable y cierre auditable"
        if TrustSignal.UNCERTAINTY in signals:
            return "la confianza debe calibrarse porque hay incertidumbre explícita"
        if TrustSignal.EXPLANATION_REQUEST in signals:
            return "el usuario pidió entender el fundamento de la respuesta"
        if TrustSignal.VALIDATION in signals:
            return "la confianza se apoya en validaciones observables"
        return "mantener confianza estable sin sobreactuar la explicación"

    def _explanation_items_for(
        self,
        signals: tuple[TrustSignal, ...],
        posture: TrustPosture,
    ) -> tuple[str, ...]:
        items = [
            "Distinguir hechos observados de inferencias.",
            "Explicar decisiones relevantes sin revelar razonamiento interno "
            "innecesario.",
            "Mantener promesas dentro de capacidades verificables.",
        ]
        if TrustSignal.VALIDATION in signals:
            items.append("Citar o mencionar validaciones ejecutadas cuando existan.")
        if TrustSignal.TRACEABILITY in signals or posture is TrustPosture.AUDIT:
            items.append(
                "Conservar trazabilidad de módulos, snapshots y contratos usados."
            )
        if TrustSignal.UNCERTAINTY in signals:
            items.append("Declarar incertidumbre y límites antes de concluir.")
        return tuple(items)

    def _uncertainty_notes_for(
        self,
        signals: tuple[TrustSignal, ...],
        posture: TrustPosture,
    ) -> tuple[str, ...]:
        notes: list[str] = []
        if TrustSignal.UNCERTAINTY in signals:
            notes.append("No convertir dudas en afirmaciones absolutas.")
        if posture is TrustPosture.AUDIT:
            notes.append("No afirmar validaciones que no hayan sido ejecutadas.")
        if TrustSignal.EXPLANATION_REQUEST in signals:
            notes.append("Explicar de forma breve y orientada al usuario.")
        return tuple(notes)


class TrustExplainabilityManager:
    """Fachada estable para M58.

    M58 calibra confianza y explicabilidad sobre la convivencia acumulada. No
    reemplaza decisiones previas: las vuelve más auditables y honestas para
    guiar respuestas con límites claros.
    """

    def __init__(self, engine: TrustExplainabilityEngine | None = None) -> None:
        self.engine = engine or TrustExplainabilityEngine()
        self._snapshots: list[TrustExplainabilitySnapshot] = []

    @property
    def history(self) -> tuple[TrustExplainabilitySnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> TrustExplainabilitySnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def observe_turn(
        self,
        text: str,
        *,
        relationship: RelationshipMemorySnapshot | None = None,
        initiative: InitiativeSnapshot | None = None,
        social_regulation: SocialRegulationSnapshot | None = None,
        personality: StablePersonalitySnapshot | None = None,
        collaboration: CollaborationSnapshot | None = None,
        now: datetime | None = None,
    ) -> TrustExplainabilitySnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            relationship=relationship,
            initiative=initiative,
            social_regulation=social_regulation,
            personality=personality,
            collaboration=collaboration,
            history_size=len(self._snapshots),
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Confianza y explicabilidad M58: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
