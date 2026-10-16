from dataclasses import dataclass, field

from core.llm_provider import LLMRequest, LLMResponse
from core.provider_router import ProviderRouter


@dataclass(frozen=True)
class LLMServiceDefaults:
    system_prompt: str | None = None
    model: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    metadata: dict[str, str] = field(default_factory=dict)


class LLMService:
    """
    Fachada mínima para que ROBY consulte modelos sin conocer proveedores.

    Construye solicitudes LLM normalizadas y delega la resolución del proveedor
    en ProviderRouter. No conoce adaptadores concretos, UI, voz, memoria,
    herramientas ni caché.
    """

    def __init__(
        self,
        router: ProviderRouter,
        *,
        defaults: LLMServiceDefaults | None = None,
    ) -> None:
        self.router = router
        self.defaults = defaults or LLMServiceDefaults()

    def generate(
        self,
        prompt: str,
        *,
        provider: str | None = None,
        system_prompt: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        metadata: dict[str, str] | None = None,
    ) -> LLMResponse:
        normalized_prompt = prompt.strip()

        if not normalized_prompt:
            return LLMResponse(
                text="Necesito un prompt para consultar el modelo.",
                provider=provider or self.router.snapshot.default_provider or "none",
                accepted=False,
                error="empty_prompt",
            )

        try:
            selected_provider = self.router.resolve(provider)
        except KeyError:
            return LLMResponse(
                text=f"Proveedor LLM no registrado: {provider}",
                provider=provider or "none",
                accepted=False,
                error="unknown_provider",
            )
        except LookupError:
            return LLMResponse(
                text="No hay proveedor LLM configurado.",
                provider="none",
                accepted=False,
                error="missing_provider",
            )

        request = LLMRequest(
            prompt=normalized_prompt,
            system_prompt=(
                system_prompt
                if system_prompt is not None
                else self.defaults.system_prompt
            ),
            model=model if model is not None else self.defaults.model,
            max_tokens=(
                max_tokens if max_tokens is not None else self.defaults.max_tokens
            ),
            temperature=(
                temperature if temperature is not None else self.defaults.temperature
            ),
            metadata={**self.defaults.metadata, **(metadata or {})},
        )

        try:
            return selected_provider.generate(request)
        except Exception:
            return LLMResponse(
                text="Ocurrió un error al consultar el servicio LLM.",
                provider=selected_provider.name,
                model=request.model,
                accepted=False,
                error="provider_error",
            )
