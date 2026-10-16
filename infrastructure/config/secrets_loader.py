from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_CREDENTIAL_FILENAMES = (
    (".roby", "credentials.json"),
    (".roby", "credencial.json"),
    (".hal", "credentials.json"),
    (".hal", "credencial.json"),
)


def credential_search_roots() -> tuple[Path, ...]:
    """Return stable roots used to locate ROBY's private credential store.

    ``ROBY_HOME`` has explicit priority. Without it, credentials are searched
    relative to the current working directory, the installed project root and
    the executable directory. This keeps desktop shortcuts and launches from a
    parent directory from breaking credential discovery.
    """
    configured = os.getenv("ROBY_HOME", "").strip()
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())
    else:
        candidates.extend(
            (
                Path.cwd(),
                Path(__file__).resolve().parents[2],
                Path(sys.executable).resolve().parent,
            )
        )

    roots: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        marker = os.path.normcase(str(resolved))
        if marker not in seen:
            roots.append(resolved)
            seen.add(marker)
    return tuple(roots)


def resolve_default_credentials_path() -> Path:
    """Return the first supported credential file or the canonical target."""
    roots = credential_search_roots()
    for root in roots:
        for directory, filename in _CREDENTIAL_FILENAMES:
            candidate = root / directory / filename
            if candidate.is_file():
                return candidate
    return roots[0] / ".roby" / "credentials.json"


class SecretsLoader:
    """Load credentials from the private local JSON store.

    Values are read from the first supported ROBY or legacy HAL credential
    file. Process environment variables remain an explicit compatibility
    override for tests and managed deployments.
    """

    def __init__(self, credentials_path: str | None = None):
        self.credentials_path = (
            resolve_default_credentials_path()
            if credentials_path is None
            else Path(credentials_path).expanduser()
        )
        self._values = self._load_credentials()

    def get(self, key: str, default: str | None = None) -> str | None:
        environment_value = os.getenv(key)
        if environment_value is not None and environment_value.strip():
            return environment_value
        value = self._values.get(key)
        if value is None or str(value).strip() == "":
            return default
        return str(value)

    def require(self, key: str) -> str:
        value = self.get(key)
        if not value:
            raise RuntimeError(f"Falta la credencial {key} en {self.credentials_path}.")
        return value

    def _load_credentials(self) -> dict[str, Any]:
        if not self.credentials_path.exists():
            return {}
        content = self.credentials_path.read_text(encoding="utf-8")
        try:
            raw = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Credenciales inválidas en {self.credentials_path}: "
                f"línea {exc.lineno}, columna {exc.colno}"
            ) from exc
        if not isinstance(raw, dict):
            raise ValueError(
                f"Las credenciales en {self.credentials_path} deben ser un objeto JSON."
            )
        values: dict[str, Any] = {}
        for section in raw.values():
            if isinstance(section, dict):
                for key, value in section.items():
                    if isinstance(key, str) and key.isupper():
                        values[key] = value
        for key, value in raw.items():
            if isinstance(key, str) and key.isupper():
                values[key] = value
        return values
