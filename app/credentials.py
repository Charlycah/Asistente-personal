from __future__ import annotations

import json
import os
from pathlib import Path

from infrastructure.config.secrets_loader import (
    SecretsLoader,
    credential_search_roots,
    resolve_default_credentials_path,
)

DEFAULT_CREDENTIALS_PATH = Path(".roby/credentials.json")
ROBY_CREDENTIAL_ALIASES = (
    DEFAULT_CREDENTIALS_PATH,
    Path(".roby/credencial.json"),
)
LEGACY_CREDENTIAL_PATHS = (
    Path(".hal/credentials.json"),
    Path(".hal/credencial.json"),
)
KNOWN_CREDENTIALS = (
    "OPENWEATHER_API_KEY",
    "WEATHERAPI_KEY",
    "GEMINI_API_KEY",
    "MISTRAL_API_KEY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "GOOGLE_CLIENT_SECRET_FILE",
    "GOOGLE_TOKEN_FILE",
    "GMAIL_ADDRESS",
    "GMAIL_APP_PASSWORD",
    "CAMERA_INDEX",
)


def resolve_credentials_path(path: Path = DEFAULT_CREDENTIALS_PATH) -> Path:
    """Return the first existing supported credential file.

    Relative default paths are resolved from stable ROBY roots, so launching
    from a shortcut or a parent directory does not disconnect credentials.
    """
    path = path.expanduser()
    if path != DEFAULT_CREDENTIALS_PATH:
        return path
    return resolve_default_credentials_path()


def activate_credentials(
    path: Path = DEFAULT_CREDENTIALS_PATH,
    *,
    override_existing: bool = False,
) -> tuple[str, ...]:
    """Expose local credentials to runtime adapters for this process only.

    Existing ``.roby/credencial.json`` and previous ``.hal`` credential files
    are accepted and migrated to the canonical plural ROBY path.
    """
    path = path.expanduser()
    if path == DEFAULT_CREDENTIALS_PATH:
        path = credential_search_roots()[0] / path
    source_path = resolve_credentials_path(DEFAULT_CREDENTIALS_PATH)
    loader = SecretsLoader(str(source_path))
    activated: list[str] = []
    for name in KNOWN_CREDENTIALS:
        value = loader.get(name)
        if not value or value.startswith("PEGAR_AQUI_"):
            continue
        if override_existing or not os.environ.get(name, "").strip():
            os.environ[name] = value
            activated.append(name)
    if source_path != path and activated:
        _migrate_credentials(loader, path)
    return tuple(activated)


def _migrate_credentials(loader: SecretsLoader, target: Path) -> None:
    values = {
        name: value
        for name in KNOWN_CREDENTIALS
        if (value := loader.get(name)) and not value.startswith("PEGAR_AQUI_")
    }
    if not values:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"credentials": values}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
