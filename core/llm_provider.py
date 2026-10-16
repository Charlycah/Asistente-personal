from dataclasses import dataclass, field
from typing import Literal, Protocol

ConversationRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ConversationMessage:
    """Mensaje conversacional neutral, independiente del proveedor."""

    role: ConversationRole
    content: str

    def __post_init__(self) -> None:
        normalized = self.content.strip()
        if not normalized:
            raise ValueError("conversation message content must not be blank")
        object.__setattr__(self, "content", normalized)


@dataclass(frozen=True)
class LLMRequest:
    """Solicitud neutral para un proveedor de modelos."""

    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    messages: tuple[ConversationMessage, ...] = ()


@dataclass(frozen=True)
class LLMResponse:
    """Respuesta normalizada de un proveedor de modelos."""

    text: str
    provider: str
    model: str | None = None
    accepted: bool = True
    error: str | None = None


@dataclass(frozen=True)
class ProviderPayloadObservation:
    """Snapshot no sensible del payload efectivo entregado al proveedor."""

    endpoint_path: str
    message_roles: tuple[str, ...]
    effective_system_prompt_characters: int = 0
    request_system_prompt_included: bool = False

    @property
    def system_message_count(self) -> int:
        return self.message_roles.count("system")


class LLMProvider(Protocol):
    """Contrato mínimo para desacoplar ROBY del motor de modelos."""

    name: str

    def generate(self, request: LLMRequest) -> LLMResponse: ...
