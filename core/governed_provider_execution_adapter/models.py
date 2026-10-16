from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.governed_provider_routing import GovernedProviderRoute
from core.llm_provider import LLMRequest, LLMResponse, ProviderPayloadObservation


class LocalProviderExecutionStatus(str, Enum):
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class LocalProviderExecutionAction(str, Enum):
    EXECUTE_LOCAL_PROVIDER = "execute_local_provider"
    EXECUTE_REMOTE_PROVIDER = "execute_remote_provider"
    REJECT_RESPONSE = "reject_response"
    REPORT_FAILURE = "report_failure"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LocalProviderExecutionConfig:
    allow_local_execution: bool = True
    allow_remote_execution: bool = False
    maximum_prompt_characters: int = 32_000
    maximum_response_characters: int = 64_000
    require_route_model_match: bool = True

    def __post_init__(self) -> None:
        if self.maximum_prompt_characters < 1:
            raise ValueError("maximum prompt characters must be positive")
        if self.maximum_response_characters < 1:
            raise ValueError("maximum response characters must be positive")


@dataclass(frozen=True)
class LocalProviderExecutionRequest:
    owner: str
    route: GovernedProviderRoute
    inference_request: LLMRequest
    execution_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("local provider execution owner must not be blank")
        if owner.casefold() != self.route.request.owner.casefold():
            raise ValueError("local provider execution owner must match route owner")
        if not self.inference_request.prompt.strip():
            raise ValueError("local provider execution prompt must not be blank")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class LocalProviderExecutionResult:
    request: LocalProviderExecutionRequest
    status: LocalProviderExecutionStatus | str
    action: LocalProviderExecutionAction | str
    response: LLMResponse | None
    selected_provider_name: str
    selected_model_name: str
    provider_call_performed: bool
    inference_performed: bool
    network_access_allowed: bool
    remote_fallback_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    provider_payload_observation: ProviderPayloadObservation | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_id: str = ""

    def __post_init__(self) -> None:
        status = LocalProviderExecutionStatus(self.status)
        action = LocalProviderExecutionAction(self.action)
        provider_name = self.selected_provider_name.strip()
        model_name = self.selected_model_name.strip()
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError(
                "local provider execution timestamp must be timezone-aware"
            )
        if not rationale or any(not item for item in rationale):
            raise ValueError("local provider execution rationale must not be empty")
        completed = status is LocalProviderExecutionStatus.COMPLETED
        attempted = status in {
            LocalProviderExecutionStatus.COMPLETED,
            LocalProviderExecutionStatus.REJECTED,
            LocalProviderExecutionStatus.FAILED,
        }
        route_kind = self.request.route.route_kind
        is_remote = route_kind is not None and route_kind.value == "remote"
        if self.platform_mutation_allowed or self.remote_fallback_allowed:
            raise ValueError(
                "provider execution cannot mutate the platform or chain fallback"
            )
        if self.network_access_allowed != (attempted and is_remote):
            raise ValueError("provider execution network flag is inconsistent")
        if (
            self.provider_call_performed != attempted
            or self.inference_performed != attempted
        ):
            raise ValueError("local provider execution attempt flags are inconsistent")
        if completed and self.response is None:
            raise ValueError("completed local execution requires a response")
        if completed and not self.response.accepted:
            raise ValueError("completed local execution requires an accepted response")
        if not completed and self.response is not None and self.response.accepted:
            raise ValueError(
                "non-completed local execution cannot expose an accepted response"
            )
        if attempted and not provider_name:
            raise ValueError("attempted local execution requires a provider name")
        if completed and not model_name:
            raise ValueError("completed local execution requires a model name")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "selected_provider_name", provider_name)
        object.__setattr__(self, "selected_model_name", model_name)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.execution_id and self.execution_id != expected:
            raise ValueError("local provider execution id is inconsistent")
        object.__setattr__(self, "execution_id", expected)

    def _identity_payload(self) -> str:
        response = self.response
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.route.route_id,
                self.request.inference_request.prompt,
                self.status.value,
                self.action.value,
                self.selected_provider_name.casefold(),
                self.selected_model_name.casefold(),
                response.text if response else "",
                str(response.accepted) if response else "",
                response.error or "" if response else "",
                str(self.provider_call_performed),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class LocalProviderExecutionRepository(Protocol):
    def add(self, result: LocalProviderExecutionResult) -> None: ...
    def get(self, execution_id: str) -> LocalProviderExecutionResult | None: ...
    def list_all(self) -> tuple[LocalProviderExecutionResult, ...]: ...


class InMemoryLocalProviderExecutionRepository:
    def __init__(self) -> None:
        self._items: dict[str, LocalProviderExecutionResult] = {}

    def add(self, result: LocalProviderExecutionResult) -> None:
        if result.execution_id in self._items:
            raise ValueError("local provider execution already exists")
        self._items[result.execution_id] = result

    def get(self, execution_id: str) -> LocalProviderExecutionResult | None:
        return self._items.get(execution_id)

    def list_all(self) -> tuple[LocalProviderExecutionResult, ...]:
        return tuple(self._items.values())
