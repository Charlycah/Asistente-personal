from __future__ import annotations

import os

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from core.local_provider_runtime_adapter import (
    LocalProviderRuntimeAdapter,
    LocalProviderRuntimeSettings,
)


def build_local_provider_from_environment() -> LocalProviderRuntimeAdapter:
    return LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name=os.getenv("ROBY_LOCAL_PROVIDER_NAME", "local-openai"),
            endpoint=os.getenv(
                "ROBY_LOCAL_PROVIDER_ENDPOINT", "http://127.0.0.1:11434/v1"
            ),
            model=os.getenv("ROBY_LOCAL_PROVIDER_MODEL", ""),
            timeout_seconds=_float_env("ROBY_LOCAL_PROVIDER_TIMEOUT_SECONDS", 120.0),
            health_timeout_seconds=_float_env(
                "ROBY_LOCAL_PROVIDER_HEALTH_TIMEOUT_SECONDS", 3.0
            ),
            api_key=os.getenv("ROBY_LOCAL_PROVIDER_API_KEY", ""),
            system_prompt=os.getenv(
                "ROBY_LOCAL_PROVIDER_SYSTEM_PROMPT",
                DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt,
            ),
            max_tokens=_optional_int_env("ROBY_LOCAL_PROVIDER_MAX_TOKENS"),
            temperature=_optional_float_env("ROBY_LOCAL_PROVIDER_TEMPERATURE"),
        )
    )


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    try:
        return default if not raw else float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc


def _optional_float_env(name: str) -> float | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc


def _optional_int_env(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
