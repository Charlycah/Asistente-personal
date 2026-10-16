from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from core.memory import MemoryItem, MemoryQuery, MemoryStore

from .memory_consolidation import OfficialMemoryGateway, OfficialMemoryStatus


class CanonicalMemoryRole(StrEnum):
    PRIMARY = "primary"
    ADAPTER = "adapter"
    SPECIALIZED = "specialized"
    LEGACY = "legacy"


class CanonicalMemoryOperation(StrEnum):
    RECALL = "recall"
    REMEMBER = "remember"
    STATUS = "status"
    INTERCEPT = "intercept"


@dataclass(frozen=True)
class CanonicalMemoryComponent:
    key: str
    path: str
    role: CanonicalMemoryRole
    operations: tuple[CanonicalMemoryOperation, ...]
    writable: bool
    purpose: str


@dataclass(frozen=True)
class CanonicalMemorySnapshot:
    schema_version: str
    primary: str
    components: tuple[CanonicalMemoryComponent, ...]

    def component_for(self, key: str) -> CanonicalMemoryComponent:
        return next(component for component in self.components if component.key == key)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "primary": self.primary,
            "components": [asdict(component) for component in self.components],
        }


CANONICAL_MEMORY_COMPONENTS: tuple[CanonicalMemoryComponent, ...] = (
    CanonicalMemoryComponent(
        key="memory_gateway",
        path="app.memory_consolidation:OfficialMemoryGateway",
        role=CanonicalMemoryRole.PRIMARY,
        operations=tuple(CanonicalMemoryOperation),
        writable=True,
        purpose="Única autoridad operativa para memoria personal persistente.",
    ),
    CanonicalMemoryComponent(
        key="brain_memory_adapter",
        path="application.brain.official_memory_adapter:OfficialMemoryBrainAdapter",
        role=CanonicalMemoryRole.ADAPTER,
        operations=(CanonicalMemoryOperation.RECALL,),
        writable=False,
        purpose="Vista de sólo lectura de la memoria oficial para BRAIN.",
    ),
    CanonicalMemoryComponent(
        key="episodic_memory",
        path="app.cognitive_episodic_memory:CognitiveEpisodicMemory",
        role=CanonicalMemoryRole.SPECIALIZED,
        operations=(CanonicalMemoryOperation.RECALL, CanonicalMemoryOperation.REMEMBER),
        writable=True,
        purpose="Memoria episódica especializada, subordinada al contrato oficial.",
    ),
    CanonicalMemoryComponent(
        key="executive_working_memory",
        path="app.executive_working_memory:ExecutiveWorkingMemory",
        role=CanonicalMemoryRole.SPECIALIZED,
        operations=(CanonicalMemoryOperation.RECALL, CanonicalMemoryOperation.REMEMBER),
        writable=True,
        purpose="Estado de trabajo ejecutivo de duración limitada.",
    ),
    CanonicalMemoryComponent(
        key="cognitive_memory_integration",
        path="core.cognitive_memory_integration:CognitiveMemoryIntegration",
        role=CanonicalMemoryRole.LEGACY,
        operations=(CanonicalMemoryOperation.RECALL, CanonicalMemoryOperation.REMEMBER),
        writable=True,
        purpose=(
            "Pipeline histórico conservado para compatibilidad, sin autoridad propia."
        ),
    ),
    CanonicalMemoryComponent(
        key="household_memory",
        path="core.household_memory:HouseholdMemoryService",
        role=CanonicalMemoryRole.SPECIALIZED,
        operations=(CanonicalMemoryOperation.RECALL, CanonicalMemoryOperation.REMEMBER),
        writable=True,
        purpose="Memoria doméstica especializada detrás de su capacidad gobernada.",
    ),
)


class CanonicalMemoryFacade(MemoryStore):
    """Single canonical memory contract over the official memory gateway.

    The facade does not merge stores or migrate data. When bound, it delegates
    operational calls to ``OfficialMemoryGateway`` without changing behavior.
    """

    SCHEMA_VERSION = "m342.5"
    PRIMARY = "memory_gateway"

    def __init__(self, gateway: OfficialMemoryGateway | None = None) -> None:
        self._gateway = gateway
        self._validate()

    @property
    def snapshot(self) -> CanonicalMemorySnapshot:
        return CanonicalMemorySnapshot(
            schema_version=self.SCHEMA_VERSION,
            primary=self.PRIMARY,
            components=CANONICAL_MEMORY_COMPONENTS,
        )

    @property
    def bound(self) -> bool:
        return self._gateway is not None

    def remember(self, item: MemoryItem) -> None:
        self._require_gateway().remember(item)

    def recall(self, query: MemoryQuery) -> list[MemoryItem]:
        return self._require_gateway().recall(query)

    def status(self) -> OfficialMemoryStatus:
        return self._require_gateway().status()

    def intercept(self, request, *, now):
        return self._require_gateway().intercept(request, now=now)

    def _require_gateway(self) -> OfficialMemoryGateway:
        if self._gateway is None:
            raise RuntimeError("canonical memory facade is not bound to a gateway")
        return self._gateway

    def _validate(self) -> None:
        keys = [component.key for component in CANONICAL_MEMORY_COMPONENTS]
        if len(keys) != len(set(keys)):
            raise ValueError("canonical memory component keys must be unique")
        primary = [
            component
            for component in CANONICAL_MEMORY_COMPONENTS
            if component.role is CanonicalMemoryRole.PRIMARY
        ]
        if len(primary) != 1 or primary[0].key != self.PRIMARY:
            raise ValueError("canonical memory must declare one official primary")
        for component in CANONICAL_MEMORY_COMPONENTS:
            if not component.operations:
                raise ValueError(f"memory component {component.key} needs operations")
            if (
                not component.writable
                and CanonicalMemoryOperation.REMEMBER in component.operations
            ):
                raise ValueError(
                    f"read-only memory component {component.key} cannot remember"
                )
