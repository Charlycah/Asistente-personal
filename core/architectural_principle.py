from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.cognitive_cycle import CognitiveCycleManager
from core.collaboration import CollaborationManager
from core.evolution_guard import EvolutionGuardManager
from core.initiative import InitiativeManager
from core.presence import PresenceManager
from core.relationship_memory import RelationshipMemoryManager
from core.routines_habits import RoutineHabitManager
from core.social_regulation import SocialRegulationManager
from core.stable_personality import StablePersonalityManager
from core.trust_explainability import TrustExplainabilityManager


class ArchitecturalPrincipleSignal(str, Enum):
    """Señales del principio arquitectónico rector de la Fase V."""

    M50_CONSUMED = "m50_consumed"
    NON_REPLACEMENT = "non_replacement"
    OPTIONAL_LAYERS = "optional_layers"
    CONTRACT_FIRST = "contract_first"
    PHASE_V_CLOSED = "phase_v_closed"


class ArchitecturalPrincipleStatus(str, Enum):
    """Estado del principio arquitectónico aplicado al turno."""

    CONSOLIDATED = "consolidated"
    ALIGNED = "aligned"
    PARTIAL = "partial"
    VIOLATED = "violated"


@dataclass(frozen=True)
class ArchitecturalPrinciplePolicy:
    """Política de M60 para consolidar la Fase V sin alterar M50."""

    aligned_threshold: float = 0.60
    consolidated_threshold: float = 0.82
    violation_risk_threshold: float = 0.72
    required_layer_count: int = 9

    def __post_init__(self) -> None:
        thresholds = (
            self.aligned_threshold,
            self.consolidated_threshold,
            self.violation_risk_threshold,
        )
        if any(not 0.0 <= threshold <= 1.0 for threshold in thresholds):
            raise ValueError("architectural thresholds must be between 0 and 1")
        if not self.aligned_threshold <= self.consolidated_threshold:
            raise ValueError("architectural thresholds must be ordered")
        if self.required_layer_count <= 0:
            raise ValueError("required layer count must be positive")


@dataclass(frozen=True)
class ArchitecturalPrincipleSnapshot:
    """Snapshot auditable del principio arquitectónico M60."""

    signals: tuple[ArchitecturalPrincipleSignal | str, ...]
    status: ArchitecturalPrincipleStatus | str
    alignment_score: float
    violation_risk: float
    principle_statement: str
    enforced_rules: tuple[str, ...]
    verified_layers: tuple[str, ...]
    missing_layers: tuple[str, ...]
    phase_v_closed: bool
    upstream_snapshot_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("architectural signals must not be empty")
        for signal in self.signals:
            ArchitecturalPrincipleSignal(signal)
        ArchitecturalPrincipleStatus(self.status)
        if not 0.0 <= self.alignment_score <= 1.0:
            raise ValueError("architectural alignment must be between 0 and 1")
        if not 0.0 <= self.violation_risk <= 1.0:
            raise ValueError("architectural risk must be between 0 and 1")
        if not self.principle_statement.strip():
            raise ValueError("architectural principle statement must not be empty")
        if not self.enforced_rules:
            raise ValueError("architectural enforced rules must not be empty")
        if any(not rule.strip() for rule in self.enforced_rules):
            raise ValueError("architectural enforced rules must not be blank")
        if any(not layer.strip() for layer in self.verified_layers):
            raise ValueError("architectural verified layers must not be blank")
        if any(not layer.strip() for layer in self.missing_layers):
            raise ValueError("architectural missing layers must not be blank")
        if any(not snapshot_id.strip() for snapshot_id in self.upstream_snapshot_ids):
            raise ValueError("architectural upstream snapshot ids must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("architectural timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("architectural snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[ArchitecturalPrincipleSignal, ...]:
        return tuple(ArchitecturalPrincipleSignal(signal) for signal in self.signals)

    @property
    def normalized_status(self) -> ArchitecturalPrincipleStatus:
        return ArchitecturalPrincipleStatus(self.status)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Principio arquitectónico M60:",
            f"- Estado: {self.normalized_status.value}",
            f"- Señales: {signals}",
            f"- Alineación: {self.alignment_score:.2f}",
            f"- Riesgo de ruptura: {self.violation_risk:.2f}",
            f"- Fase V cerrada: {str(self.phase_v_closed).lower()}",
            f"- Principio: {self.principle_statement}",
        ]
        lines.extend(f"- Regla aplicada: {rule}" for rule in self.enforced_rules)
        lines.extend(f"- Capa verificada: {layer}" for layer in self.verified_layers)
        lines.extend(f"- Capa faltante: {layer}" for layer in self.missing_layers)
        lines.extend(
            f"- Snapshot upstream: {snapshot_id}"
            for snapshot_id in self.upstream_snapshot_ids
        )
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "status": self.normalized_status.value,
            "alignment_score": self.alignment_score,
            "violation_risk": self.violation_risk,
            "principle_statement": self.principle_statement,
            "enforced_rules": list(self.enforced_rules),
            "verified_layers": list(self.verified_layers),
            "missing_layers": list(self.missing_layers),
            "phase_v_closed": self.phase_v_closed,
            "upstream_snapshot_ids": list(self.upstream_snapshot_ids),
            "created_at": self.created_at.isoformat(),
        }


class ArchitecturalPrincipleEngine:
    """Motor puro de M60 — principio arquitectónico de convivencia."""

    _PHASE_V_LAYERS = (
        "presence",
        "relationship_memory",
        "initiative",
        "social_regulation",
        "stable_personality",
        "routines_habits",
        "collaboration",
        "trust_explainability",
        "evolution_guard",
    )

    _PRINCIPLE = (
        "La convivencia no reemplaza el ciclo cognitivo M50; "
        "lo consume como ancla y agrega capas opcionales, auditables y "
        "compatibles hacia atrás."
    )

    def __init__(
        self,
        policy: ArchitecturalPrinciplePolicy | None = None,
    ) -> None:
        self.policy = policy or ArchitecturalPrinciplePolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        cognitive_cycle: CognitiveCycleManager | None = None,
        presence: PresenceManager | None = None,
        relationship_memory: RelationshipMemoryManager | None = None,
        initiative: InitiativeManager | None = None,
        social_regulation: SocialRegulationManager | None = None,
        stable_personality: StablePersonalityManager | None = None,
        routines_habits: RoutineHabitManager | None = None,
        collaboration: CollaborationManager | None = None,
        trust_explainability: TrustExplainabilityManager | None = None,
        evolution_guard: EvolutionGuardManager | None = None,
        history_size: int = 0,
        now: datetime | None = None,
    ) -> ArchitecturalPrincipleSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("architectural timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("architectural text must not be empty")

        layers = {
            "presence": presence,
            "relationship_memory": relationship_memory,
            "initiative": initiative,
            "social_regulation": social_regulation,
            "stable_personality": stable_personality,
            "routines_habits": routines_habits,
            "collaboration": collaboration,
            "trust_explainability": trust_explainability,
            "evolution_guard": evolution_guard,
        }
        verified_layers = tuple(name for name, layer in layers.items() if layer)
        missing_layers = tuple(name for name, layer in layers.items() if layer is None)
        upstream_snapshot_ids = self._upstream_snapshot_ids(layers)
        signals = self._signals_for(text, cognitive_cycle, missing_layers)
        alignment_score = self._alignment_for(
            signals,
            cognitive_cycle,
            verified_layers,
            upstream_snapshot_ids,
            history_size,
        )
        violation_risk = self._risk_for(signals, cognitive_cycle, missing_layers)
        phase_v_closed = (
            cognitive_cycle is not None
            and len(verified_layers) >= self.policy.required_layer_count
            and not missing_layers
            and violation_risk < self.policy.violation_risk_threshold
        )
        status = self._status_for(alignment_score, violation_risk, phase_v_closed)

        return ArchitecturalPrincipleSnapshot(
            signals=signals,
            status=status,
            alignment_score=alignment_score,
            violation_risk=violation_risk,
            principle_statement=self._PRINCIPLE,
            enforced_rules=self._rules_for(phase_v_closed),
            verified_layers=verified_layers,
            missing_layers=missing_layers,
            phase_v_closed=phase_v_closed,
            upstream_snapshot_ids=upstream_snapshot_ids,
            created_at=timestamp,
        )

    def _signals_for(
        self,
        text: str,
        cognitive_cycle: CognitiveCycleManager | None,
        missing_layers: tuple[str, ...],
    ) -> tuple[ArchitecturalPrincipleSignal, ...]:
        normalized = text.lower()
        signals: list[ArchitecturalPrincipleSignal] = []
        if cognitive_cycle is not None or "m50" in normalized:
            signals.append(ArchitecturalPrincipleSignal.M50_CONSUMED)
        if any(word in normalized for word in ("no reemplaza", "consume", "ancla")):
            signals.append(ArchitecturalPrincipleSignal.NON_REPLACEMENT)
        if any(word in normalized for word in ("opcional", "capa", "capas")):
            signals.append(ArchitecturalPrincipleSignal.OPTIONAL_LAYERS)
        if any(
            word in normalized for word in ("contrato", "arquitectura", "compatible")
        ):
            signals.append(ArchitecturalPrincipleSignal.CONTRACT_FIRST)
        if any(word in normalized for word in ("fase v", "cerramos", "terminamos")):
            signals.append(ArchitecturalPrincipleSignal.PHASE_V_CLOSED)
        if (
            not missing_layers
            and ArchitecturalPrincipleSignal.PHASE_V_CLOSED not in signals
        ):
            signals.append(ArchitecturalPrincipleSignal.PHASE_V_CLOSED)
        if not signals:
            signals.append(ArchitecturalPrincipleSignal.CONTRACT_FIRST)
        return tuple(dict.fromkeys(signals))

    def _alignment_for(
        self,
        signals: tuple[ArchitecturalPrincipleSignal, ...],
        cognitive_cycle: CognitiveCycleManager | None,
        verified_layers: tuple[str, ...],
        upstream_snapshot_ids: tuple[str, ...],
        history_size: int,
    ) -> float:
        score = 0.24 + min(len(signals) * 0.075, 0.30)
        if cognitive_cycle is not None:
            score += 0.18
        score += min(len(verified_layers) * 0.035, 0.32)
        score += min(len(upstream_snapshot_ids) * 0.01, 0.08)
        score += min(history_size * 0.02, 0.06)
        return min(score, 1.0)

    def _risk_for(
        self,
        signals: tuple[ArchitecturalPrincipleSignal, ...],
        cognitive_cycle: CognitiveCycleManager | None,
        missing_layers: tuple[str, ...],
    ) -> float:
        risk = 0.46 + min(len(missing_layers) * 0.04, 0.30)
        if cognitive_cycle is not None:
            risk -= 0.18
        if ArchitecturalPrincipleSignal.NON_REPLACEMENT in signals:
            risk -= 0.08
        if ArchitecturalPrincipleSignal.OPTIONAL_LAYERS in signals:
            risk -= 0.06
        if ArchitecturalPrincipleSignal.CONTRACT_FIRST in signals:
            risk -= 0.07
        if ArchitecturalPrincipleSignal.PHASE_V_CLOSED in signals:
            risk -= 0.04
        return min(max(risk, 0.0), 1.0)

    def _status_for(
        self,
        alignment_score: float,
        violation_risk: float,
        phase_v_closed: bool,
    ) -> ArchitecturalPrincipleStatus:
        if violation_risk >= self.policy.violation_risk_threshold:
            return ArchitecturalPrincipleStatus.VIOLATED
        if phase_v_closed and alignment_score >= self.policy.consolidated_threshold:
            return ArchitecturalPrincipleStatus.CONSOLIDATED
        if alignment_score >= self.policy.aligned_threshold:
            return ArchitecturalPrincipleStatus.ALIGNED
        return ArchitecturalPrincipleStatus.PARTIAL

    def _rules_for(self, phase_v_closed: bool) -> tuple[str, ...]:
        rules = [
            "M50 remains the cognitive-cycle anchor.",
            "Phase V layers consume M50 instead of replacing it.",
            "New capabilities are optional dependencies in CognitivePipeline.",
            "Snapshots remain auditable through system_prompt_lines().",
            "Backward compatibility is part of the architectural contract.",
        ]
        if phase_v_closed:
            rules.append("M60 closes Phase V as an architectural consolidation.")
        return tuple(rules)

    def _upstream_snapshot_ids(
        self,
        layers: dict[str, object | None],
    ) -> tuple[str, ...]:
        snapshot_ids: list[str] = []
        for layer in layers.values():
            snapshot = getattr(layer, "last_snapshot", None)
            snapshot_id = getattr(snapshot, "snapshot_id", None)
            if isinstance(snapshot_id, str) and snapshot_id.strip():
                snapshot_ids.append(snapshot_id)
        return tuple(snapshot_ids)


class ArchitecturalPrincipleManager:
    """Fachada estable para M60.

    M60 no agrega una nueva capacidad funcional aislada. Declara y verifica el
    principio rector que cierra Fase V: convivencia como capa superior que
    consume M50, preserva contratos y permite evolución compatible.
    """

    def __init__(
        self,
        engine: ArchitecturalPrincipleEngine | None = None,
    ) -> None:
        self.engine = engine or ArchitecturalPrincipleEngine()
        self._snapshots: list[ArchitecturalPrincipleSnapshot] = []

    @property
    def history(self) -> tuple[ArchitecturalPrincipleSnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> ArchitecturalPrincipleSnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    def observe_turn(
        self,
        text: str,
        *,
        cognitive_cycle: CognitiveCycleManager | None = None,
        presence: PresenceManager | None = None,
        relationship_memory: RelationshipMemoryManager | None = None,
        initiative: InitiativeManager | None = None,
        social_regulation: SocialRegulationManager | None = None,
        stable_personality: StablePersonalityManager | None = None,
        routines_habits: RoutineHabitManager | None = None,
        collaboration: CollaborationManager | None = None,
        trust_explainability: TrustExplainabilityManager | None = None,
        evolution_guard: EvolutionGuardManager | None = None,
        now: datetime | None = None,
    ) -> ArchitecturalPrincipleSnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            cognitive_cycle=cognitive_cycle,
            presence=presence,
            relationship_memory=relationship_memory,
            initiative=initiative,
            social_regulation=social_regulation,
            stable_personality=stable_personality,
            routines_habits=routines_habits,
            collaboration=collaboration,
            trust_explainability=trust_explainability,
            evolution_guard=evolution_guard,
            history_size=len(self._snapshots),
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Principio arquitectónico M60: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
