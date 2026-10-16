from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable


class CapabilityAvailability(str, Enum):
    AVAILABLE = "available"
    DISABLED = "disabled"
    MISSING_DEPENDENCY = "missing_dependency"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    capability_id: str
    description: str
    risk: str
    reversible: bool
    authorization_required: bool
    dependencies: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.capability_id.strip() or not self.description.strip():
            raise ValueError("capability identity and description must not be blank")
        if self.risk not in {"none", "low", "medium", "high"}:
            raise ValueError("capability risk is invalid")
        if self.capability_id in self.dependencies:
            raise ValueError("capability cannot depend on itself")
        if any(not item.strip() for item in self.dependencies + self.tags):
            raise ValueError("capability dependencies and tags must not be blank")


@dataclass(frozen=True, slots=True)
class CapabilityAssessment:
    capability_id: str
    availability: CapabilityAvailability
    risk: str | None
    reversible: bool | None
    authorization_required: bool
    missing_dependencies: tuple[str, ...]
    reasons: tuple[str, ...]

    @property
    def available(self) -> bool:
        return self.availability is CapabilityAvailability.AVAILABLE


@dataclass(frozen=True, slots=True)
class CapabilityModelSnapshot:
    capabilities: tuple[CapabilityDefinition, ...]

    @property
    def enabled_count(self) -> int:
        return sum(item.enabled for item in self.capabilities)

    def get(self, capability_id: str) -> CapabilityDefinition | None:
        return next(
            (item for item in self.capabilities if item.capability_id == capability_id),
            None,
        )


@runtime_checkable
class CapabilityModel(Protocol):
    def register(self, capability: CapabilityDefinition) -> None: ...

    def snapshot(self) -> CapabilityModelSnapshot: ...

    def assess(self, capability_id: str) -> CapabilityAssessment: ...


class JsonCapabilityModel:
    """Persistent descriptive model; it never authorizes or executes capabilities."""

    def __init__(
        self,
        path: Path | str,
        *,
        defaults: tuple[CapabilityDefinition, ...] = (),
    ) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._capabilities = self._load()
        if not self._capabilities and defaults:
            self._capabilities = {item.capability_id: item for item in defaults}
            self._persist(self._capabilities)

    def register(self, capability: CapabilityDefinition) -> None:
        with self._lock:
            if capability.capability_id in self._capabilities:
                raise ValueError(
                    f"duplicate capability id: {capability.capability_id}"
                )
            updated = dict(self._capabilities)
            updated[capability.capability_id] = capability
            _validate_dependencies(updated)
            self._persist(updated)
            self._capabilities = updated

    def snapshot(self) -> CapabilityModelSnapshot:
        with self._lock:
            values = tuple(
                sorted(
                    self._capabilities.values(),
                    key=lambda item: item.capability_id,
                )
            )
        return CapabilityModelSnapshot(values)

    def assess(self, capability_id: str) -> CapabilityAssessment:
        with self._lock:
            capability = self._capabilities.get(capability_id)
            if capability is None:
                return CapabilityAssessment(
                    capability_id=capability_id,
                    availability=CapabilityAvailability.UNKNOWN,
                    risk=None,
                    reversible=None,
                    authorization_required=False,
                    missing_dependencies=(),
                    reasons=("capability_not_registered",),
                )
            missing = tuple(
                dependency
                for dependency in capability.dependencies
                if dependency not in self._capabilities
                or not self._capabilities[dependency].enabled
            )
            if not capability.enabled:
                availability = CapabilityAvailability.DISABLED
                reasons = ("capability_disabled",)
            elif missing:
                availability = CapabilityAvailability.MISSING_DEPENDENCY
                reasons = tuple(
                    f"dependency_unavailable:{dependency}"
                    for dependency in missing
                )
            else:
                availability = CapabilityAvailability.AVAILABLE
                reasons = ("capability_registered_and_dependencies_available",)
            return CapabilityAssessment(
                capability_id=capability.capability_id,
                availability=availability,
                risk=capability.risk,
                reversible=capability.reversible,
                authorization_required=capability.authorization_required,
                missing_dependencies=missing,
                reasons=reasons,
            )

    def _persist(self, capabilities: dict[str, CapabilityDefinition]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "capabilities": [
                _to_payload(item) for item in capabilities.values()
            ],
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def _load(self) -> dict[str, CapabilityDefinition]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != 1:
                raise ValueError("unsupported schema")
            items = [_from_payload(item) for item in payload["capabilities"]]
            result = {item.capability_id: item for item in items}
            if len(result) != len(items):
                raise ValueError("duplicate ids")
            _validate_dependencies(result, allow_missing=True)
            return result
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid capability model file: {self.path}") from error


def default_capabilities() -> tuple[CapabilityDefinition, ...]:
    return (
        CapabilityDefinition(
            capability_id="diagnose_audio_runtime",
            description="Read local audio diagnostics without changing runtime state.",
            risk="low",
            reversible=True,
            authorization_required=False,
            tags=("audio", "diagnostic", "read_only"),
        ),
        CapabilityDefinition(
            capability_id="verify_component_health",
            description="Read and report registered component health.",
            risk="low",
            reversible=True,
            authorization_required=False,
            tags=("health", "diagnostic", "read_only"),
        ),
    )


def _validate_dependencies(
    capabilities: dict[str, CapabilityDefinition],
    *,
    allow_missing: bool = False,
) -> None:
    if allow_missing:
        return
    for capability in capabilities.values():
        missing = set(capability.dependencies) - capabilities.keys()
        if missing:
            raise ValueError(
                f"unknown capability dependencies: {sorted(missing)}"
            )


def _to_payload(capability: CapabilityDefinition) -> dict[str, object]:
    return {
        "capability_id": capability.capability_id,
        "description": capability.description,
        "risk": capability.risk,
        "reversible": capability.reversible,
        "authorization_required": capability.authorization_required,
        "dependencies": list(capability.dependencies),
        "tags": list(capability.tags),
        "enabled": capability.enabled,
    }


def _from_payload(payload: dict[str, object]) -> CapabilityDefinition:
    return CapabilityDefinition(
        capability_id=str(payload["capability_id"]),
        description=str(payload["description"]),
        risk=str(payload["risk"]),
        reversible=bool(payload["reversible"]),
        authorization_required=bool(payload["authorization_required"]),
        dependencies=tuple(str(item) for item in payload["dependencies"]),
        tags=tuple(str(item) for item in payload["tags"]),
        enabled=bool(payload["enabled"]),
    )
