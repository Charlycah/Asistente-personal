from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LocalProviderRuntimeState(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MISCONFIGURED = "misconfigured"


@dataclass(frozen=True)
class LocalProviderRuntimeSettings:
    provider_name: str = "local-openai"
    endpoint: str = "http://127.0.0.1:11434/v1"
    model: str = ""
    timeout_seconds: float = 120.0
    health_timeout_seconds: float = 3.0
    api_key: str = ""
    system_prompt: str = "Sos ROBY, un compañero cognitivo personal y familiar."
    max_tokens: int | None = None
    temperature: float | None = None

    def __post_init__(self) -> None:
        provider_name = self.provider_name.strip()
        endpoint = self.endpoint.strip().rstrip("/")
        model = self.model.strip()
        if not provider_name:
            raise ValueError("local provider name must not be blank")
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError("local provider endpoint must use http or https")
        if self.timeout_seconds <= 0 or self.health_timeout_seconds <= 0:
            raise ValueError("local provider timeouts must be positive")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise ValueError("local provider max tokens must be positive")
        if self.temperature is not None and not 0 <= self.temperature <= 2:
            raise ValueError("local provider temperature must be between zero and two")
        object.__setattr__(self, "provider_name", provider_name)
        object.__setattr__(self, "endpoint", endpoint)
        object.__setattr__(self, "model", model)


@dataclass(frozen=True)
class LocalProviderRuntimeHealth:
    state: LocalProviderRuntimeState
    provider_name: str
    endpoint: str
    configured_model: str
    available_models: tuple[str, ...] = ()
    latency_ms: int | None = None
    error_code: str | None = None

    @property
    def available(self) -> bool:
        return self.state is LocalProviderRuntimeState.AVAILABLE
