from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Protocol


class ResidentComponent(Protocol):
    def start(self) -> object: ...

    def stop(self) -> object: ...


class ResidentCriticality(str, Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"


class ResidentState(str, Enum):
    REGISTERED = "registered"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class ResidentHealth(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ResidentRegistration:
    component_id: str
    component: ResidentComponent
    criticality: ResidentCriticality = ResidentCriticality.OPTIONAL
    startup_order: int = 100
    description: str = ""
    state: ResidentState = ResidentState.REGISTERED
    health: ResidentHealth = ResidentHealth.UNKNOWN
    last_error: str | None = None

    @property
    def required(self) -> bool:
        return self.criticality is ResidentCriticality.REQUIRED


class ResidentComponentRegistry:
    """Single source of truth for resident runtime components."""

    def __init__(self, registrations: Iterable[ResidentRegistration] = ()) -> None:
        self._registrations: dict[str, ResidentRegistration] = {}
        for registration in registrations:
            self.register(registration)

    def register(self, registration: ResidentRegistration) -> None:
        component_id = registration.component_id.strip()
        if not component_id:
            raise ValueError("component_id no puede estar vacío")
        if component_id in self._registrations:
            raise ValueError(f"componente residente duplicado: {component_id}")
        self._registrations[component_id] = replace(
            registration,
            component_id=component_id,
        )

    def registration_for(self, component_id: str) -> ResidentRegistration | None:
        return self._registrations.get(component_id)

    def ordered(self) -> tuple[ResidentRegistration, ...]:
        return tuple(
            sorted(
                self._registrations.values(),
                key=lambda item: (item.startup_order, item.component_id),
            )
        )

    def components(self) -> tuple[ResidentComponent, ...]:
        return tuple(item.component for item in self.ordered())

    def update_state(
        self,
        component_id: str,
        *,
        state: ResidentState,
        health: ResidentHealth | None = None,
        error: BaseException | str | None = None,
    ) -> ResidentRegistration:
        current = self._require(component_id)
        updated = replace(
            current,
            state=state,
            health=current.health if health is None else health,
            last_error=None if error is None else str(error),
        )
        self._registrations[component_id] = updated
        return updated

    def reset_runtime_state(self) -> None:
        for component_id, current in tuple(self._registrations.items()):
            self._registrations[component_id] = replace(
                current,
                state=ResidentState.REGISTERED,
                health=ResidentHealth.UNKNOWN,
                last_error=None,
            )

    def snapshot(self) -> tuple[ResidentRegistration, ...]:
        return self.ordered()

    def __len__(self) -> int:
        return len(self._registrations)

    def _require(self, component_id: str) -> ResidentRegistration:
        registration = self.registration_for(component_id)
        if registration is None:
            raise KeyError(f"componente residente desconocido: {component_id}")
        return registration


def registration_from_component(
    component: ResidentComponent,
    *,
    component_id: str | None = None,
    criticality: ResidentCriticality = ResidentCriticality.OPTIONAL,
    startup_order: int = 100,
    description: str = "",
) -> ResidentRegistration:
    resolved_id = component_id or _default_component_id(component)
    return ResidentRegistration(
        component_id=resolved_id,
        component=component,
        criticality=criticality,
        startup_order=startup_order,
        description=description,
    )


def _default_component_id(component: object) -> str:
    name = type(component).__name__
    return _camel_to_snake(name)


def _camel_to_snake(value: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(value):
        if char.isupper() and index and not value[index - 1].isupper():
            chars.append("_")
        chars.append(char.casefold())
    return "".join(chars)
