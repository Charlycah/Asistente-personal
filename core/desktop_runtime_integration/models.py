from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.operational_response_assembly import OperationalResponse
from core.roby_console_application import ROBYConsoleTurn
from core.runtime_readiness_gate import RuntimeReadinessResult


class DesktopRuntimeStatus(str, Enum):
    DELIVERED = "delivered"
    NEEDS_INPUT = "needs_input"
    BLOCKED = "blocked"
    FAILED = "failed"
    WITHHELD = "withheld"


class DesktopRuntimeAction(str, Enum):
    PRESENT_RESPONSE = "present_response"
    REQUEST_INPUT = "request_input"
    REPORT_BLOCKED = "report_blocked"
    REPORT_FAILURE = "report_failure"
    WITHHOLD = "withhold"


@dataclass(frozen=True)
class DesktopRuntimeIntegrationConfig:
    incomplete_response: str = "Necesito que escribas un mensaje para continuar."
    blocked_response: str = "ROBY no esta listo para conversar."
    failure_response: str = "Ocurrió un error al procesar tu mensaje."
    withheld_response: str = "No puedo entregar una respuesta en este momento."
    maximum_input_characters: int = 16_000

    def __post_init__(self) -> None:
        for value in (
            self.incomplete_response,
            self.blocked_response,
            self.failure_response,
            self.withheld_response,
        ):
            if not value.strip():
                raise ValueError("desktop runtime responses must not be blank")
        if self.maximum_input_characters < 1:
            raise ValueError("desktop runtime input limit must be positive")


@dataclass(frozen=True)
class DesktopRuntimeRequest:
    owner: str
    session_id: str
    text: str
    readiness_result: RuntimeReadinessResult

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        text = self.text.strip()
        if not owner:
            raise ValueError("desktop runtime owner must not be blank")
        if not session_id:
            raise ValueError("desktop runtime session id must not be blank")
        if self.readiness_result.request.owner.casefold() != owner.casefold():
            raise ValueError("desktop runtime owner must match readiness owner")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "text", text)


@dataclass(frozen=True)
class DesktopRuntimeResult:
    request: DesktopRuntimeRequest
    status: DesktopRuntimeStatus | str
    action: DesktopRuntimeAction | str
    response_text: str
    console_turn: ROBYConsoleTurn | None
    operational_response: OperationalResponse | None
    provider_call_performed: bool
    network_access_performed: bool
    platform_mutation_performed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result_id: str = ""

    def __post_init__(self) -> None:
        status = DesktopRuntimeStatus(self.status)
        action = DesktopRuntimeAction(self.action)
        response = self.response_text.strip()
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("desktop runtime timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("desktop runtime rationale must not be empty")
        if status is DesktopRuntimeStatus.DELIVERED and not response:
            raise ValueError("delivered desktop result requires response text")
        if self.console_turn is not None and self.operational_response is not None:
            raise ValueError("desktop result cannot contain two response lineages")
        if self.platform_mutation_performed:
            raise ValueError("M176 cannot perform platform mutation")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "response_text", response)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.result_id and self.result_id != expected:
            raise ValueError("desktop runtime result id is inconsistent")
        object.__setattr__(self, "result_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.session_id,
                self.request.text,
                self.request.readiness_result.readiness_id,
                self.status.value,
                self.action.value,
                self.response_text,
                self.console_turn.turn_id if self.console_turn else "",
                self.operational_response.response_id
                if self.operational_response
                else "",
                str(self.provider_call_performed),
                str(self.network_access_performed),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class OperationalDesktopPipeline(Protocol):
    def execute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
    ) -> OperationalResponse: ...


@runtime_checkable
class DesktopRuntimeRepository(Protocol):
    def add(self, result: DesktopRuntimeResult) -> None: ...
    def get(self, result_id: str) -> DesktopRuntimeResult | None: ...
    def list_all(self) -> tuple[DesktopRuntimeResult, ...]: ...


class InMemoryDesktopRuntimeRepository:
    def __init__(self) -> None:
        self._items: dict[str, DesktopRuntimeResult] = {}

    def add(self, result: DesktopRuntimeResult) -> None:
        if result.result_id in self._items:
            raise ValueError("desktop runtime result already exists")
        self._items[result.result_id] = result

    def get(self, result_id: str) -> DesktopRuntimeResult | None:
        return self._items.get(result_id)

    def list_all(self) -> tuple[DesktopRuntimeResult, ...]:
        return tuple(self._items.values())
