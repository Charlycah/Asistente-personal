from dataclasses import dataclass

from core.llm_provider import LLMProvider


@dataclass(frozen=True)
class ProviderRouterSnapshot:
    default_provider: str | None
    providers: tuple[str, ...]


class ProviderRouter:
    """
    Router mínimo de proveedores LLM para Phase 2.

    Mantiene el registro de proveedores concretos y resuelve el proveedor por
    defecto o el solicitado explícitamente. No conoce UI, memoria, voz, caché ni
    clientes externos.
    """

    def __init__(self, providers: list[LLMProvider] | None = None) -> None:
        self._providers: dict[str, LLMProvider] = {}
        self._default_provider: str | None = None

        for provider in providers or []:
            self.register(provider)

    @property
    def snapshot(self) -> ProviderRouterSnapshot:
        return ProviderRouterSnapshot(
            default_provider=self._default_provider,
            providers=tuple(self._providers.keys()),
        )

    def register(self, provider: LLMProvider) -> None:
        provider_name = provider.name.strip()

        if not provider_name:
            raise ValueError("El proveedor LLM necesita un nombre.")

        self._providers[provider_name] = provider

        if self._default_provider is None:
            self._default_provider = provider_name

    def set_default(self, provider_name: str) -> None:
        normalized_name = provider_name.strip()

        if normalized_name not in self._providers:
            raise KeyError(f"Proveedor LLM no registrado: {normalized_name}")

        self._default_provider = normalized_name

    def resolve(self, provider_name: str | None = None) -> LLMProvider:
        selected_provider_name = (provider_name or self._default_provider or "").strip()

        if not selected_provider_name:
            raise LookupError("No hay proveedor LLM configurado.")

        provider = self._providers.get(selected_provider_name)

        if provider is None:
            raise KeyError(f"Proveedor LLM no registrado: {selected_provider_name}")

        return provider
