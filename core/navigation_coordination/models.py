from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.route_intent_modeling import RouteIntent


class NavigationCoordinationStatus(str, Enum):
    READY_FOR_ROUTING = "ready_for_routing"
    AWAITING_INPUT = "awaiting_input"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class NavigationCoordinationAction(str, Enum):
    PREPARE_ROUTE_REQUEST = "prepare_route_request"
    CLARIFY = "clarify"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class NavigationCoordinationPolicy:
    require_explicit_user_authorization: bool = True
    require_routing_provider: bool = True
    require_navigation_surface: bool = False
    allow_background_preparation: bool = True


@dataclass(frozen=True)
class NavigationCoordinationRequest:
    owner: str
    route_intent: RouteIntent
    explicit_user_authorization: bool = False
    routing_provider_available: bool = False
    navigation_surface_available: bool = False
    background_preparation_requested: bool = False
    coordination_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("navigation coordination owner must not be blank")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class NavigationCoordinationDecision:
    request: NavigationCoordinationRequest
    status: NavigationCoordinationStatus | str
    action: NavigationCoordinationAction | str
    routing_request_allowed: bool
    provider_required: bool
    surface_required: bool
    user_authorization_required: bool
    background_preparation_allowed: bool
    navigation_start_allowed: bool
    live_guidance_allowed: bool
    route_intent_id: str | None
    rationale: tuple[str, ...]
    created_at: datetime
    decision_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", NavigationCoordinationStatus(self.status))
        object.__setattr__(self, "action", NavigationCoordinationAction(self.action))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("navigation coordination timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("navigation coordination rationale must not be empty")
        if self.navigation_start_allowed or self.live_guidance_allowed:
            raise ValueError("M126 cannot authorize navigation execution")
        if self.status is NavigationCoordinationStatus.READY_FOR_ROUTING:
            if not self.routing_request_allowed or self.route_intent_id is None:
                raise ValueError("ready coordination requires a routable intent")
            if self.user_authorization_required or self.provider_required:
                raise ValueError(
                    "ready coordination cannot retain blocking requirements"
                )
        elif self.routing_request_allowed or self.route_intent_id is not None:
            raise ValueError(
                "inactive coordination cannot expose routing authorization"
            )
        expected = sha256(
            "|".join(
                (
                    self.request.owner.casefold(),
                    self.request.route_intent.intent_id,
                    str(self.request.explicit_user_authorization),
                    str(self.request.routing_provider_available),
                    str(self.request.navigation_surface_available),
                    str(self.request.background_preparation_requested),
                    str(self.request.coordination_requested),
                    self.status.value,
                    self.action.value,
                    str(self.routing_request_allowed),
                    str(self.provider_required),
                    str(self.surface_required),
                    str(self.user_authorization_required),
                    str(self.background_preparation_allowed),
                    str(self.navigation_start_allowed),
                    str(self.live_guidance_allowed),
                    self.route_intent_id or "none",
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("navigation coordination decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)


@runtime_checkable
class NavigationCoordinationRepository(Protocol):
    def add(self, decision: NavigationCoordinationDecision) -> None: ...
    def get(self, decision_id: str) -> NavigationCoordinationDecision | None: ...
    def list_all(self) -> tuple[NavigationCoordinationDecision, ...]: ...


class InMemoryNavigationCoordinationRepository:
    def __init__(self) -> None:
        self._items: dict[str, NavigationCoordinationDecision] = {}

    def add(self, decision: NavigationCoordinationDecision) -> None:
        if decision.decision_id in self._items:
            raise ValueError("navigation coordination decision already exists")
        self._items[decision.decision_id] = decision

    def get(self, decision_id: str) -> NavigationCoordinationDecision | None:
        return self._items.get(decision_id)

    def list_all(self) -> tuple[NavigationCoordinationDecision, ...]:
        return tuple(self._items.values())
