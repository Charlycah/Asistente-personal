from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class CognitiveCapabilityState(StrEnum):
    """Operational maturity assigned without activating a capability."""

    CONTRACT_ONLY = "contract_only"
    ISOLATED = "isolated"
    SHADOW = "shadow"
    CONSULTATIVE = "consultative"
    OPERATIONAL_LIMITED = "operational_limited"
    USER_VISIBLE = "user_visible"
    SUPERSEDED = "superseded"


class CognitiveAuthority(StrEnum):
    ENTRY = "entry"
    CONTEXT = "context"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    REASONING = "reasoning"
    PLANNING = "planning"
    DECISION = "decision"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    GOVERNANCE = "governance"
    OBSERVABILITY = "observability"


@dataclass(frozen=True)
class CognitiveCapabilityRecord:
    key: str
    target: str
    authority: CognitiveAuthority
    state: CognitiveCapabilityState
    canonical: bool
    notes: str


@dataclass(frozen=True)
class CognitiveTurnEvent:
    sequence: int
    stage: str
    component: str
    state: CognitiveCapabilityState
    detail: str = ""


@dataclass(frozen=True)
class CognitiveTurnTrace:
    turn_id: str
    origin: str
    session_id: str | None
    started_at: datetime
    completed: bool
    events: tuple[CognitiveTurnEvent, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["started_at"] = self.started_at.isoformat()
        return payload


@dataclass(frozen=True)
class CognitiveOperationalInventorySnapshot:
    schema_version: str
    capabilities: tuple[CognitiveCapabilityRecord, ...]
    turns: tuple[CognitiveTurnTrace, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "capabilities": [asdict(item) for item in self.capabilities],
            "turns": [item.as_dict() for item in self.turns],
        }


COGNITIVE_CAPABILITY_INVENTORY: tuple[CognitiveCapabilityRecord, ...] = (
    CognitiveCapabilityRecord(
        "conversation_entry",
        "app.official_conversation_gateway:OfficialConversationGateway",
        CognitiveAuthority.ENTRY,
        CognitiveCapabilityState.USER_VISIBLE,
        True,
        "Frontera oficial de todos los turnos interactivos.",
    ),
    CognitiveCapabilityRecord(
        "context_continuity",
        "app.context_continuity_runtime:OfficialContextContinuityRuntimeGateway",
        CognitiveAuthority.CONTEXT,
        CognitiveCapabilityState.OPERATIONAL_LIMITED,
        True,
        "Mantiene continuidad contextual dentro del runtime oficial.",
    ),
    CognitiveCapabilityRecord(
        "memory_gateway",
        "app.memory_consolidation:OfficialMemoryGateway",
        CognitiveAuthority.MEMORY,
        CognitiveCapabilityState.OPERATIONAL_LIMITED,
        True,
        "Frontera oficial de memoria; subsistemas especializados permanecen detrás.",
    ),
    CognitiveCapabilityRecord(
        "knowledge_runtime",
        "app.knowledge_runtime:OfficialKnowledgeRuntimeGateway",
        CognitiveAuthority.KNOWLEDGE,
        CognitiveCapabilityState.CONSULTATIVE,
        True,
        "Expone conocimiento al grafo oficial sin autoridad de ejecución.",
    ),
    CognitiveCapabilityRecord(
        "governed_reasoning",
        "app.governed_reasoning_runtime:OfficialGovernedReasoningRuntimeGateway",
        CognitiveAuthority.REASONING,
        CognitiveCapabilityState.OPERATIONAL_LIMITED,
        True,
        "Razonamiento gobernado usado por la composición extremo a extremo.",
    ),
    CognitiveCapabilityRecord(
        "executive_planning",
        "app.executive_conversation_planner:ExecutiveConversationPlanner",
        CognitiveAuthority.PLANNING,
        CognitiveCapabilityState.CONSULTATIVE,
        True,
        "Planificación ejecutiva integrada como fuente cognitiva.",
    ),
    CognitiveCapabilityRecord(
        "cognitive_planner_shadow",
        "app.cognitive_planner_shadow_runtime:CognitivePlannerShadowRuntime",
        CognitiveAuthority.PLANNING,
        CognitiveCapabilityState.SHADOW,
        False,
        "Evalúa planificación sin alterar la respuesta ni ejecutar acciones.",
    ),
    CognitiveCapabilityRecord(
        "executive_director",
        "app.executive_cognitive_director:ExecutiveCognitiveDirector",
        CognitiveAuthority.DECISION,
        CognitiveCapabilityState.CONSULTATIVE,
        True,
        "Coordina señales ejecutivas; no sustituye la frontera de ejecución.",
    ),
    CognitiveCapabilityRecord(
        "unified_cognitive_coordination",
        "app.unified_cognitive_coordination:UnifiedCognitiveCoordinator",
        CognitiveAuthority.DECISION,
        CognitiveCapabilityState.OPERATIONAL_LIMITED,
        True,
        "Coordina fuentes cognitivas dentro del runtime oficial.",
    ),
    CognitiveCapabilityRecord(
        "capability_orchestrator",
        "app.unified_capability_orchestrator:UnifiedCapabilityOrchestrator",
        CognitiveAuthority.EXECUTION,
        CognitiveCapabilityState.USER_VISIBLE,
        True,
        "Orquesta capacidades registradas mediante el grafo oficial.",
    ),
    CognitiveCapabilityRecord(
        "governed_capability_routing",
        "app.governed_capability_routing_runtime:OfficialGovernedCapabilityRoutingRuntimeGateway",
        CognitiveAuthority.GOVERNANCE,
        CognitiveCapabilityState.OPERATIONAL_LIMITED,
        True,
        "Aplica gobierno al enrutamiento de capacidades.",
    ),
    CognitiveCapabilityRecord(
        "adaptive_cognition",
        "app.adaptive_cognition_runtime:OfficialAdaptiveCognitionRuntimeGateway",
        CognitiveAuthority.REFLECTION,
        CognitiveCapabilityState.CONSULTATIVE,
        True,
        "Adapta cognición a partir del razonamiento gobernado.",
    ),
    CognitiveCapabilityRecord(
        "cognitive_core_resident",
        "app.cognitive_core_runtime:CognitiveCoreRuntime",
        CognitiveAuthority.REFLECTION,
        CognitiveCapabilityState.OPERATIONAL_LIMITED,
        True,
        "Residente cognitivo observable por el runtime oficial.",
    ),
    CognitiveCapabilityRecord(
        "runtime_observability",
        "app.unified_runtime_observability:UnifiedRuntimeObservability",
        CognitiveAuthority.OBSERVABILITY,
        CognitiveCapabilityState.OPERATIONAL_LIMITED,
        True,
        "Vista de sólo lectura del estado operacional canónico.",
    ),
)


class CognitiveOperationalObserver:
    """In-memory, read-only observer for the official conversation boundary."""

    SCHEMA_VERSION = "m342.1"

    def __init__(self, *, max_turns: int = 100) -> None:
        if max_turns < 1:
            raise ValueError("max_turns must be positive")
        self._max_turns = max_turns
        self._turns: list[CognitiveTurnTrace] = []
        self._active: dict[str, CognitiveTurnTrace] = {}
        self._next_turn = 1

    @property
    def snapshot(self) -> CognitiveOperationalInventorySnapshot:
        active = tuple(self._active.values())
        return CognitiveOperationalInventorySnapshot(
            schema_version=self.SCHEMA_VERSION,
            capabilities=COGNITIVE_CAPABILITY_INVENTORY,
            turns=tuple(self._turns) + active,
        )

    def begin_turn(
        self,
        *,
        origin: str,
        session_id: str | None,
        now: datetime | None = None,
    ) -> str:
        turn_id = f"turn-{self._next_turn:06d}"
        self._next_turn += 1
        timestamp = _timestamp(now)
        event = CognitiveTurnEvent(
            sequence=1,
            stage="entry",
            component="conversation_entry",
            state=CognitiveCapabilityState.USER_VISIBLE,
            detail="turn accepted by official conversation boundary",
        )
        self._active[turn_id] = CognitiveTurnTrace(
            turn_id=turn_id,
            origin=origin,
            session_id=session_id,
            started_at=timestamp,
            completed=False,
            events=(event,),
        )
        return turn_id

    def complete_turn(self, turn_id: str, *, session_id: str | None) -> None:
        trace = self._active.pop(turn_id)
        event = CognitiveTurnEvent(
            sequence=len(trace.events) + 1,
            stage="response",
            component="conversation_entry",
            state=CognitiveCapabilityState.USER_VISIBLE,
            detail="turn returned without observer intervention",
        )
        self._append(
            CognitiveTurnTrace(
                turn_id=trace.turn_id,
                origin=trace.origin,
                session_id=session_id or trace.session_id,
                started_at=trace.started_at,
                completed=True,
                events=trace.events + (event,),
            )
        )

    def fail_turn(self, turn_id: str, error: BaseException) -> None:
        trace = self._active.pop(turn_id)
        event = CognitiveTurnEvent(
            sequence=len(trace.events) + 1,
            stage="error",
            component="conversation_entry",
            state=CognitiveCapabilityState.OPERATIONAL_LIMITED,
            detail=type(error).__name__,
        )
        self._append(
            CognitiveTurnTrace(
                turn_id=trace.turn_id,
                origin=trace.origin,
                session_id=trace.session_id,
                started_at=trace.started_at,
                completed=False,
                events=trace.events + (event,),
            )
        )

    def _append(self, trace: CognitiveTurnTrace) -> None:
        self._turns.append(trace)
        if len(self._turns) > self._max_turns:
            del self._turns[: len(self._turns) - self._max_turns]


def _timestamp(value: datetime | None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("cognitive observation time must be timezone-aware")
    return timestamp
