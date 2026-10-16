from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from typing import Any, Mapping

from core.llm_provider import LLMRequest
from core.tool_gateway import ToolGatewayStatus, ToolResult


class ToolRuntimeStatus(str, Enum):
    NOT_REQUESTED = "not_requested"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True)
class ToolRuntimeConfig:
    enabled: bool = True
    command_prefix: str = "/tool"
    maximum_payload_characters: int = 8_000
    include_output_in_prompt: bool = True
    allow_platform_mutation: bool = False

    def __post_init__(self) -> None:
        prefix = self.command_prefix.strip()
        if not prefix:
            raise ValueError("tool runtime command prefix must not be blank")
        if self.maximum_payload_characters < 2:
            raise ValueError("tool runtime payload limit must be at least two")
        object.__setattr__(self, "command_prefix", prefix)


@dataclass(frozen=True)
class ToolRuntimeInvocation:
    owner: str
    session_id: str
    capability_name: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    source_text: str = ""
    invocation_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        capability = self.capability_name.strip()
        if not owner or not session_id or not capability:
            raise ValueError("tool runtime invocation identity must be complete")
        identity = (
            owner.casefold(),
            session_id,
            capability,
            repr(dict(self.payload)),
        )
        expected = sha256("|".join(identity).encode()).hexdigest()
        if self.invocation_id and self.invocation_id != expected:
            raise ValueError("tool runtime invocation id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "capability_name", capability)
        object.__setattr__(self, "payload", dict(self.payload))
        object.__setattr__(self, "invocation_id", expected)


@dataclass(frozen=True)
class ToolRuntimeContext:
    owner: str
    session_id: str
    status: ToolRuntimeStatus | str
    request: LLMRequest
    invocation: ToolRuntimeInvocation | None = None
    gateway_result: ToolResult | None = None
    rationale: tuple[str, ...] = ("tool_not_requested",)

    def __post_init__(self) -> None:
        status = ToolRuntimeStatus(self.status)
        rationale = tuple(item.strip() for item in self.rationale)
        if not self.owner.strip() or not self.session_id.strip():
            raise ValueError("tool runtime context identity must be complete")
        if not rationale or any(not item for item in rationale):
            raise ValueError("tool runtime rationale must not be empty")
        if status is ToolRuntimeStatus.EXECUTED:
            if self.gateway_result is None or not self.gateway_result.succeeded:
                raise ValueError(
                    "executed tool context requires successful gateway result"
                )
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "rationale", rationale)

    @property
    def succeeded(self) -> bool:
        return self.status is ToolRuntimeStatus.EXECUTED

    @property
    def gateway_status(self) -> ToolGatewayStatus | None:
        if self.gateway_result is None:
            return None
        return self.gateway_result.normalized_status
