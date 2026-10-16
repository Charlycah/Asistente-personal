from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.context_transfer import ContextTransferManifest
from core.device_capabilities import DeviceCapabilityMatch
from core.device_continuity import CompanionSession, DeviceSessionEndpoint


class DeviceArbitrationStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class DeviceArbitrationAction(str, Enum):
    SWITCH = "switch"
    STAY = "stay"
    CONFIRM = "confirm"
    NONE = "none"


@dataclass(frozen=True)
class DeviceArbitrationCandidate:
    endpoint: DeviceSessionEndpoint
    capability_match: DeviceCapabilityMatch
    transfer_manifest: ContextTransferManifest | None = None
    user_preference: float = 0.0

    def __post_init__(self) -> None:
        if not -1.0 <= self.user_preference <= 1.0:
            raise ValueError("device preference must be between minus one and one")
        if self.capability_match.device != self.endpoint.device:
            raise ValueError("capability match must describe candidate device")
        if self.transfer_manifest is not None:
            target = self.transfer_manifest.request.continuity.request.target.device
            if target != self.endpoint.device:
                raise ValueError("transfer manifest must target candidate device")


@dataclass(frozen=True)
class DeviceArbitrationPolicy:
    max_observation_age_seconds: float = 300.0
    minimum_switch_margin: float = 0.15
    require_ready_transfer_for_switch: bool = True
    prefer_current_device: bool = True
    allow_untrusted_devices: bool = False

    def __post_init__(self) -> None:
        if self.max_observation_age_seconds <= 0:
            raise ValueError("maximum observation age must be positive")
        if self.minimum_switch_margin < 0:
            raise ValueError("minimum switch margin must not be negative")


@dataclass(frozen=True)
class DeviceArbitrationRequest:
    owner: str
    session: CompanionSession
    candidates: tuple[DeviceArbitrationCandidate, ...]
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("arbitration owner must not be blank")
        if self.requested_at.tzinfo is None:
            raise ValueError("arbitration request timestamp must be aware")
        ids = tuple(item.endpoint.device.device_id for item in self.candidates)
        if len(ids) != len(set(ids)):
            raise ValueError("arbitration candidate devices must be unique")


@dataclass(frozen=True)
class DeviceArbitrationDecision:
    request: DeviceArbitrationRequest
    status: DeviceArbitrationStatus | str
    action: DeviceArbitrationAction | str
    selected_device_id: str | None
    previous_device_id: str
    candidate_scores: tuple[tuple[str, float], ...]
    eligible_for_activation: bool
    rationale: tuple[str, ...]
    created_at: datetime
    decision_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", DeviceArbitrationStatus(self.status))
        object.__setattr__(self, "action", DeviceArbitrationAction(self.action))
        if self.created_at.tzinfo is None:
            raise ValueError("arbitration decision timestamp must be aware")
        if not self.previous_device_id.strip():
            raise ValueError("previous device id must not be blank")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("arbitration rationale must not be empty")
        if self.eligible_for_activation != (
            self.status is DeviceArbitrationStatus.READY
        ):
            raise ValueError("only ready arbitration may be eligible for activation")
        if self.status is DeviceArbitrationStatus.READY and not self.selected_device_id:
            raise ValueError("ready arbitration requires a selected device")
        ids = tuple(item[0] for item in self.candidate_scores)
        if len(ids) != len(set(ids)):
            raise ValueError("candidate scores must be unique")
        expected = sha256(
            "|".join(
                (
                    self.request.session.session_id,
                    self.status.value,
                    self.action.value,
                    self.selected_device_id or "",
                    self.previous_device_id,
                    ";".join(
                        f"{key}:{value:.6f}" for key, value in self.candidate_scores
                    ),
                    str(self.eligible_for_activation),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("arbitration decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)


@runtime_checkable
class DeviceArbitrationRepository(Protocol):
    def add(self, decision: DeviceArbitrationDecision) -> None: ...
    def get(self, decision_id: str) -> DeviceArbitrationDecision | None: ...
    def list_all(self) -> tuple[DeviceArbitrationDecision, ...]: ...


class InMemoryDeviceArbitrationRepository:
    def __init__(self) -> None:
        self._items: dict[str, DeviceArbitrationDecision] = {}

    def add(self, decision: DeviceArbitrationDecision) -> None:
        if decision.decision_id in self._items:
            raise ValueError("device arbitration decision already exists")
        self._items[decision.decision_id] = decision

    def get(self, decision_id: str) -> DeviceArbitrationDecision | None:
        return self._items.get(decision_id)

    def list_all(self) -> tuple[DeviceArbitrationDecision, ...]:
        return tuple(self._items.values())
