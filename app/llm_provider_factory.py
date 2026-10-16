from __future__ import annotations

import os
from dataclasses import dataclass

from core.llm_model_providers import GeminiProvider, MistralProvider
from core.llm_provider import LLMProvider
from core.provider_health_evaluation import ProviderKind


@dataclass(frozen=True)
class RuntimeProviderRegistration:
    provider: LLMProvider
    kind: ProviderKind
    endpoint: str
    model: str


def build_remote_providers_from_environment() -> tuple[
    RuntimeProviderRegistration, ...
]:
    registrations: list[RuntimeProviderRegistration] = []

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key and _enabled("ROBY_GEMINI_ENABLED", True):
        endpoint = _text_env(
            "ROBY_GEMINI_ENDPOINT",
            "https://generativelanguage.googleapis.com/v1beta",
        )
        model = os.getenv("ROBY_GEMINI_MODEL", "gemini-2.5-flash").strip()
        registrations.append(
            RuntimeProviderRegistration(
                provider=GeminiProvider(
                    api_key=gemini_key,
                    endpoint=endpoint,
                    default_model=model,
                    timeout=_float_env("ROBY_GEMINI_TIMEOUT_SECONDS", 60.0),
                ),
                kind=ProviderKind.REMOTE,
                endpoint=endpoint,
                model=model,
            )
        )

    mistral_key = os.getenv("MISTRAL_API_KEY", "").strip()
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if (mistral_key or openrouter_key) and _enabled("ROBY_MISTRAL_ENABLED", True):
        direct = bool(mistral_key)
        endpoint = _text_env(
            "ROBY_MISTRAL_ENDPOINT",
            (
                "https://api.mistral.ai/v1/chat/completions"
                if direct
                else "https://openrouter.ai/api/v1/chat/completions"
            ),
        )
        default_model = (
            "mistral-small-latest"
            if direct
            else "mistralai/mistral-small-3.2-24b-instruct"
        )
        model = os.getenv("ROBY_MISTRAL_MODEL", default_model).strip()
        registrations.append(
            RuntimeProviderRegistration(
                provider=MistralProvider(
                    api_key=mistral_key or openrouter_key,
                    endpoint=endpoint,
                    default_model=model,
                    timeout=_float_env("ROBY_MISTRAL_TIMEOUT_SECONDS", 60.0),
                ),
                kind=ProviderKind.REMOTE,
                endpoint=endpoint,
                model=model,
            )
        )

    return tuple(registrations)


def provider_mode_from_environment() -> str:
    value = os.getenv("ROBY_LLM_PROVIDER", "auto").strip().casefold()
    aliases = {
        "": "auto",
        "auto": "auto",
        "local": "local",
        "ollama": "local",
        "gemini": "gemini",
        "mistral": "mistral",
    }
    if value not in aliases:
        raise ValueError("ROBY_LLM_PROVIDER must be auto, local, gemini or mistral")
    return aliases[value]


def preferred_remote_order(mode: str) -> tuple[str, ...]:
    if mode == "mistral":
        return ("mistral", "gemini")
    return ("gemini", "mistral")


def _enabled(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().casefold()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    try:
        return default if not raw else float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc


def _text_env(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value or default
