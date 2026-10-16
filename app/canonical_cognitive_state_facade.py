from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Protocol

from core.cognitive_state_contract import (
    CognitiveState,
    CognitiveStateUpdate,
)


class CognitiveStateAuthority(Protocol):
    def snapshot(self) -> CognitiveState: ...

    def update(self, changes: CognitiveStateUpdate) -> CognitiveState: ...

    def reset(self) -> CognitiveState: ...


class CanonicalCognitiveStateRole(StrEnum):
    PRIMARY = "primary"
    ADAPTER = "adapter"
    SPECIALIZED = "specialized"
    OBSERVER = "observer"
    LEGACY = "legacy"


class CanonicalCognitiveStateOperation(StrEnum):
    READ = "read"
    UPDATE = "update"
    RESET = "reset"
    DERIVE = "derive"
    OBSERVE = "observe"


@dataclass(frozen=True)
class CanonicalCognitiveStateComponent:
    key: str
    path: str
    role: CanonicalCognitiveStateRole
    operations: tuple[CanonicalCognitiveStateOperation, ...]
    writable: bool
    purpose: str


@dataclass(frozen=True)
class CanonicalCognitiveStateSnapshot:
    schema_version: str
    primary: str
    components: tuple[CanonicalCognitiveStateComponent, ...]

    def component_for(self, key: str) -> CanonicalCognitiveStateComponent:
        return next(component for component in self.components if component.key == key)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "primary": self.primary,
            "components": [asdict(component) for component in self.components],
        }


CANONICAL_COGNITIVE_STATE_COMPONENTS: tuple[
    CanonicalCognitiveStateComponent, ...
] = (
    CanonicalCognitiveStateComponent(
        key="cognitive_state_contract",
        path="core.cognitive_state_contract:CognitiveStateManager",
        role=CanonicalCognitiveStateRole.PRIMARY,
        operations=(
            CanonicalCognitiveStateOperation.READ,
            CanonicalCognitiveStateOperation.UPDATE,
            CanonicalCognitiveStateOperation.RESET,
        ),
        writable=True,
        purpose="Única autoridad para el estado cognitivo mínimo persistible.",
    ),
    CanonicalCognitiveStateComponent(
        key="persistent_cognitive_state",
        path="core.persistent_cognitive_state:PersistentCognitiveState",
        role=CanonicalCognitiveStateRole.ADAPTER,
        operations=(CanonicalCognitiveStateOperation.READ,),
        writable=False,
        purpose="Representación persistente histórica subordinada al contrato oficial.",
    ),
    CanonicalCognitiveStateComponent(
        key="global_cognitive_state",
        path="core.global_cognitive_state:GlobalCognitiveState",
        role=CanonicalCognitiveStateRole.SPECIALIZED,
        operations=(CanonicalCognitiveStateOperation.DERIVE,),
        writable=False,
        purpose="Proyección global derivada para coordinación entre dominios.",
    ),
    CanonicalCognitiveStateComponent(
        key="mental_state",
        path="core.mental_state:ROBYMentalState",
        role=CanonicalCognitiveStateRole.SPECIALIZED,
        operations=(CanonicalCognitiveStateOperation.DERIVE,),
        writable=False,
        purpose="Estado mental conversacional histórico sin autoridad persistente.",
    ),
    CanonicalCognitiveStateComponent(
        key="continuous_cognitive_loop_state",
        path="app.continuous_internal_cognitive_loop:ContinuousCognitiveState",
        role=CanonicalCognitiveStateRole.OBSERVER,
        operations=(CanonicalCognitiveStateOperation.OBSERVE,),
        writable=False,
        purpose="Instantánea residente observacional del bucle cognitivo interno.",
    ),
    CanonicalCognitiveStateComponent(
        key="cognitive_world_model",
        path="app.cognitive_world_model:CognitiveWorldModelSnapshot",
        role=CanonicalCognitiveStateRole.SPECIALIZED,
        operations=(CanonicalCognitiveStateOperation.DERIVE,),
        writable=False,
        purpose="Modelo del mundo especializado, no sustituto del estado canónico.",
    ),
    CanonicalCognitiveStateComponent(
        key="executive_working_memory",
        path="app.executive_working_memory:ExecutiveWorkingMemorySnapshot",
        role=CanonicalCognitiveStateRole.SPECIALIZED,
        operations=(CanonicalCognitiveStateOperation.DERIVE,),
        writable=False,
        purpose="Estado ejecutivo transitorio subordinado al contrato canónico.",
    ),
    CanonicalCognitiveStateComponent(
        key="legacy_cognitive_state",
        path="core.mental_state",
        role=CanonicalCognitiveStateRole.LEGACY,
        operations=(CanonicalCognitiveStateOperation.READ,),
        writable=False,
        purpose="Contratos históricos conservados para compatibilidad interna.",
    ),
)


class CanonicalCognitiveStateFacade:
    """Single contract over the official cognitive-state authority.

    The facade does not merge state stores, infer updates, or synchronize
    historical representations. When bound, it delegates explicit operations
    to the existing cognitive-state manager without changing their semantics.
    """

    SCHEMA_VERSION = "m342.8"
    PRIMARY = "cognitive_state_contract"

    def __init__(self, authority: CognitiveStateAuthority | None = None) -> None:
        self._authority = authority
        self._validate()

    @property
    def snapshot(self) -> CanonicalCognitiveStateSnapshot:
        return CanonicalCognitiveStateSnapshot(
            schema_version=self.SCHEMA_VERSION,
            primary=self.PRIMARY,
            components=CANONICAL_COGNITIVE_STATE_COMPONENTS,
        )

    @property
    def bound(self) -> bool:
        return self._authority is not None

    def current(self) -> CognitiveState:
        return self._require_authority().snapshot()

    def bind(self, authority: CognitiveStateAuthority) -> None:
        if self._authority is not None:
            raise RuntimeError("canonical cognitive state authority is already bound")
        required = ("snapshot", "update", "reset")
        if not all(callable(getattr(authority, name, None)) for name in required):
            raise TypeError("cognitive state authority does not satisfy its contract")
        self._authority = authority

    def update(self, changes: CognitiveStateUpdate) -> CognitiveState:
        return self._require_authority().update(changes)

    def reset(self) -> CognitiveState:
        return self._require_authority().reset()

    def _require_authority(self) -> CognitiveStateAuthority:
        if self._authority is None:
            raise RuntimeError(
                "canonical cognitive state facade is not bound to an authority"
            )
        return self._authority

    def _validate(self) -> None:
        keys = [component.key for component in CANONICAL_COGNITIVE_STATE_COMPONENTS]
        if len(keys) != len(set(keys)):
            raise ValueError("canonical cognitive state keys must be unique")

        primaries = [
            component
            for component in CANONICAL_COGNITIVE_STATE_COMPONENTS
            if component.role is CanonicalCognitiveStateRole.PRIMARY
        ]
        if len(primaries) != 1 or primaries[0].key != self.PRIMARY:
            raise ValueError("canonical cognitive state needs one official primary")

        for component in CANONICAL_COGNITIVE_STATE_COMPONENTS:
            if not component.operations:
                raise ValueError(
                    f"cognitive state component {component.key} needs operations"
                )
            if not component.writable:
                mutating = {
                    CanonicalCognitiveStateOperation.UPDATE,
                    CanonicalCognitiveStateOperation.RESET,
                }
                if mutating.intersection(component.operations):
                    raise ValueError(
                        f"read-only cognitive state component {component.key} "
                        "cannot mutate state"
                    )
