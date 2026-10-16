from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.cognitive_cycle import CognitiveCycleManager
from core.collaboration import CollaborationManager
from core.initiative import InitiativeManager
from core.presence import PresenceManager
from core.relationship_memory import RelationshipMemoryManager
from core.routines_habits import RoutineHabitManager
from core.social_regulation import SocialRegulationManager
from core.stable_personality import StablePersonalityManager
from core.trust_explainability import TrustExplainabilityManager


class EvolutionSignal(str, Enum):
    """Señales que indican evolución segura sobre la arquitectura M50."""

    M50_ANCHOR = "m50_anchor"
    CONTRACT_PRESERVATION = "contract_preservation"
    OPTIONAL_EXTENSION = "optional_extension"
    BACKWARD_COMPATIBILITY = "backward_compatibility"
    VALIDATION_GATE = "validation_gate"


class EvolutionStatus(str, Enum):
    """Estado operativo de una evolución arquitectónica."""

    SAFE = "safe"
    GUARDED = "guarded"
    NEEDS_REVIEW = "needs_review"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class EvolutionGuardPolicy:
    """Política de M59 para evolucionar sin romper M50 ni la Fase V."""

    guarded_threshold: float = 0.52
    safe_threshold: float = 0.74
    blocked_risk_threshold: float = 0.78
    max_required_checks: int = 6

    def __post_init__(self) -> None:
        thresholds = (
            self.guarded_threshold,
            self.safe_threshold,
            self.blocked_risk_threshold,
        )
        if any(not 0.0 <= threshold <= 1.0 for threshold in thresholds):
            raise ValueError("evolution thresholds must be between 0 and 1")
        if not self.guarded_threshold <= self.safe_threshold:
            raise ValueError("evolution thresholds must be ordered")
        if self.max_required_checks <= 0:
            raise ValueError("evolution required-check limit must be positive")


@dataclass(frozen=True)
class EvolutionGuardSnapshot:
    """Resultado auditable de M59 para evolución arquitectónica segura."""

    signals: tuple[EvolutionSignal | str, ...]
    status: EvolutionStatus | str
    compatibility_score: float
    risk_score: float
    protected_contracts: tuple[str, ...]
    required_checks: tuple[str, ...]
    missing_layers: tuple[str, ...]
    m50_anchor_present: bool
    upstream_snapshot_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("evolution signals must not be empty")
        for signal in self.signals:
            EvolutionSignal(signal)
        EvolutionStatus(self.status)
        if not 0.0 <= self.compatibility_score <= 1.0:
            raise ValueError("evolution compatibility must be between 0 and 1")
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError("evolution risk must be between 0 and 1")
        if not self.protected_contracts:
            raise ValueError("evolution protected contracts must not be empty")
        if any(not contract.strip() for contract in self.protected_contracts):
            raise ValueError("evolution protected contracts must not be blank")
        if not self.required_checks:
            raise ValueError("evolution required checks must not be empty")
        if any(not check.strip() for check in self.required_checks):
            raise ValueError("evolution required checks must not be blank")
        if any(not layer.strip() for layer in self.missing_layers):
            raise ValueError("evolution missing layers must not be blank")
        if any(not snapshot_id.strip() for snapshot_id in self.upstream_snapshot_ids):
            raise ValueError("evolution upstream snapshot ids must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("evolution timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("evolution snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[EvolutionSignal, ...]:
        return tuple(EvolutionSignal(signal) for signal in self.signals)

    @property
    def normalized_status(self) -> EvolutionStatus:
        return EvolutionStatus(self.status)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Evolución arquitectónica M59:",
            f"- Estado: {self.normalized_status.value}",
            f"- Señales: {signals}",
            f"- Compatibilidad: {self.compatibility_score:.2f}",
            f"- Riesgo: {self.risk_score:.2f}",
            f"- Ancla M50 presente: {str(self.m50_anchor_present).lower()}",
        ]
        lines.extend(
            f"- Contrato protegido: {item}" for item in self.protected_contracts
        )
        lines.extend(f"- Chequeo requerido: {item}" for item in self.required_checks)
        lines.extend(f"- Capa faltante: {item}" for item in self.missing_layers)
        lines.extend(
            f"- Snapshot upstream: {item}" for item in self.upstream_snapshot_ids
        )
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "status": self.normalized_status.value,
            "compatibility_score": self.compatibility_score,
            "risk_score": self.risk_score,
            "protected_contracts": list(self.protected_contracts),
            "required_checks": list(self.required_checks),
            "missing_layers": list(self.missing_layers),
            "m50_anchor_present": self.m50_anchor_present,
            "upstream_snapshot_ids": list(self.upstream_snapshot_ids),
            "created_at": self.created_at.isoformat(),
        }


class EvolutionGuardEngine:
    """Motor puro de M59 — evolución segura sobre M50."""

    _LAYER_NAMES = (
        "presence",
        "relationship_memory",
        "initiative",
        "social_regulation",
        "stable_personality",
        "routines_habits",
        "collaboration",
        "trust_explainability",
    )

    def __init__(self, policy: EvolutionGuardPolicy | None = None) -> None:
        self.policy = policy or EvolutionGuardPolicy()

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
        history_size: int = 0,
        now: datetime | None = None,
    ) -> EvolutionGuardSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("evolution timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("evolution text must not be empty")

        layers = {
            "presence": presence,
            "relationship_memory": relationship_memory,
            "initiative": initiative,
            "social_regulation": social_regulation,
            "stable_personality": stable_personality,
            "routines_habits": routines_habits,
            "collaboration": collaboration,
            "trust_explainability": trust_explainability,
        }
        missing_layers = tuple(name for name, layer in layers.items() if layer is None)
        upstream_snapshot_ids = self._upstream_snapshot_ids(layers)
        signals = self._signals_for(text, cognitive_cycle, missing_layers)
        compatibility_score = self._compatibility_for(
            signals,
            cognitive_cycle,
            missing_layers,
            upstream_snapshot_ids,
            history_size,
        )
        risk_score = self._risk_for(signals, cognitive_cycle, missing_layers)
        status = self._status_for(compatibility_score, risk_score, cognitive_cycle)

        return EvolutionGuardSnapshot(
            signals=signals,
            status=status,
            compatibility_score=compatibility_score,
            risk_score=risk_score,
            protected_contracts=self._protected_contracts_for(),
            required_checks=self._required_checks_for(signals),
            missing_layers=missing_layers,
            m50_anchor_present=cognitive_cycle is not None,
            upstream_snapshot_ids=upstream_snapshot_ids,
            created_at=timestamp,
        )

    def _signals_for(
        self,
        text: str,
        cognitive_cycle: CognitiveCycleManager | None,
        missing_layers: tuple[str, ...],
    ) -> tuple[EvolutionSignal, ...]:
        normalized = text.lower()
        signals: list[EvolutionSignal] = []
        if cognitive_cycle is not None or "m50" in normalized:
            signals.append(EvolutionSignal.M50_ANCHOR)
        if any(word in normalized for word in ("contrato", "arquitectura", "romper")):
            signals.append(EvolutionSignal.CONTRACT_PRESERVATION)
        if any(word in normalized for word in ("opcional", "extensión", "capa")):
            signals.append(EvolutionSignal.OPTIONAL_EXTENSION)
        if any(
            word in normalized
            for word in ("compatibilidad", "regresión", "regresiones")
        ):
            signals.append(EvolutionSignal.BACKWARD_COMPATIBILITY)
        if any(
            word in normalized for word in ("ruff", "pytest", "validación", "tests")
        ):
            signals.append(EvolutionSignal.VALIDATION_GATE)
        if not missing_layers and EvolutionSignal.BACKWARD_COMPATIBILITY not in signals:
            signals.append(EvolutionSignal.BACKWARD_COMPATIBILITY)
        if not signals:
            signals.append(EvolutionSignal.CONTRACT_PRESERVATION)
        return tuple(dict.fromkeys(signals))

    def _compatibility_for(
        self,
        signals: tuple[EvolutionSignal, ...],
        cognitive_cycle: CognitiveCycleManager | None,
        missing_layers: tuple[str, ...],
        upstream_snapshot_ids: tuple[str, ...],
        history_size: int,
    ) -> float:
        score = 0.30 + min(len(signals) * 0.08, 0.32)
        if cognitive_cycle is not None:
            score += 0.18
        score += max(0.0, (len(self._LAYER_NAMES) - len(missing_layers)) * 0.025)
        score += min(len(upstream_snapshot_ids) * 0.015, 0.10)
        score += min(history_size * 0.03, 0.09)
        return min(score, 1.0)

    def _risk_for(
        self,
        signals: tuple[EvolutionSignal, ...],
        cognitive_cycle: CognitiveCycleManager | None,
        missing_layers: tuple[str, ...],
    ) -> float:
        risk = 0.42 + min(len(missing_layers) * 0.045, 0.28)
        if cognitive_cycle is not None:
            risk -= 0.18
        if EvolutionSignal.CONTRACT_PRESERVATION in signals:
            risk -= 0.07
        if EvolutionSignal.VALIDATION_GATE in signals:
            risk -= 0.08
        if EvolutionSignal.OPTIONAL_EXTENSION in signals:
            risk -= 0.05
        return min(max(risk, 0.0), 1.0)

    def _status_for(
        self,
        compatibility_score: float,
        risk_score: float,
        cognitive_cycle: CognitiveCycleManager | None,
    ) -> EvolutionStatus:
        if cognitive_cycle is None or risk_score >= self.policy.blocked_risk_threshold:
            return EvolutionStatus.BLOCKED
        if compatibility_score >= self.policy.safe_threshold and risk_score <= 0.30:
            return EvolutionStatus.SAFE
        if compatibility_score >= self.policy.guarded_threshold:
            return EvolutionStatus.GUARDED
        return EvolutionStatus.NEEDS_REVIEW

    def _protected_contracts_for(self) -> tuple[str, ...]:
        return (
            "M50 CognitiveCycleManager remains the orchestration anchor.",
            "CognitivePipeline accepts new layers only as optional dependencies.",
            "Existing public result fields remain backward compatible.",
            "Managers expose snapshots through stable system_prompt_lines().",
        )

    def _required_checks_for(
        self,
        signals: tuple[EvolutionSignal, ...],
    ) -> tuple[str, ...]:
        checks = [
            "Run ruff check . before accepting the milestone.",
            "Run pytest before declaring the milestone closed.",
            "Keep M50-M59 integration tests green.",
            "Avoid destructive refactors of existing managers.",
        ]
        if EvolutionSignal.CONTRACT_PRESERVATION in signals:
            checks.append("Verify constructor and result compatibility.")
        if EvolutionSignal.BACKWARD_COMPATIBILITY in signals:
            checks.append("Confirm previous milestone tests still pass.")
        return tuple(checks[: self.policy.max_required_checks])

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


class EvolutionGuardManager:
    """Fachada estable para M59.

    M59 no crea una nueva arquitectura. Protege la arquitectura M50 y permite
    que futuras capas evolucionen como extensiones opcionales, auditables y
    compatibles hacia atrás.
    """

    def __init__(self, engine: EvolutionGuardEngine | None = None) -> None:
        self.engine = engine or EvolutionGuardEngine()
        self._snapshots: list[EvolutionGuardSnapshot] = []

    @property
    def history(self) -> tuple[EvolutionGuardSnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> EvolutionGuardSnapshot | None:
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
        now: datetime | None = None,
    ) -> EvolutionGuardSnapshot:
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
            history_size=len(self._snapshots),
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Evolución arquitectónica M59: sin evaluación aún.",)
        return self.last_snapshot.system_prompt_lines()
