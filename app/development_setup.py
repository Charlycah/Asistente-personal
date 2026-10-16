from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.roby_config import DEFAULT_CONFIG, save_roby_config


@dataclass(frozen=True)
class SetupOptions:
    project_root: Path = Path(".")
    config_path: Path = Path(".roby/config.json")
    non_interactive: bool = False
    runtime_factory: str = ""
    provider_endpoint: str = "http://127.0.0.1:11434/v1"
    provider_model: str = ""
    owners: tuple[str, str] = ("Carlos", "Cristina")


@dataclass(frozen=True)
class SetupResult:
    config_path: Path
    created_directories: tuple[Path, ...]
    detected_models: tuple[str, ...]
    pending_fields: tuple[str, ...]


REQUIRED_DIRECTORIES = (
    ".roby",
    ".roby/backups",
    ".roby/cache",
    ".roby/exports",
    ".roby/identity",
    ".roby/logs",
    ".roby/memory",
    ".roby/tmp",
)


def detect_ollama_models(
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> tuple[str, ...]:
    if shutil.which("ollama") is None:
        return ()
    try:
        completed = runner(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ()
    if completed.returncode:
        return ()
    return tuple(
        dict.fromkeys(
            line.split()[0]
            for line in completed.stdout.splitlines()[1:]
            if line.split()
        )
    )


def create_runtime_directories(project_root: Path) -> tuple[Path, ...]:
    created: list[Path] = []
    for relative in REQUIRED_DIRECTORIES:
        path = project_root / relative
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)
    return tuple(created)


def setup_environment(options: SetupOptions) -> SetupResult:
    root = options.project_root.resolve()
    config_path = _resolve(root, options.config_path)
    models = detect_ollama_models()
    model = options.provider_model.strip() or (models[0] if len(models) == 1 else "")

    data = _copy_default_config()
    data["household"]["owners"] = [
        owner.strip() for owner in options.owners if owner.strip()
    ]
    data["runtime"]["factory"] = options.runtime_factory.strip()
    data["providers"]["local"]["endpoint"] = options.provider_endpoint.strip()
    data["providers"]["local"]["model"] = model
    pending = tuple(
        field
        for field, value in (
            ("runtime.factory", data["runtime"]["factory"]),
            ("providers.local.model", data["providers"]["local"]["model"]),
        )
        if not value
    )
    save_roby_config(data, config_path)
    return SetupResult(
        config_path=config_path,
        created_directories=create_runtime_directories(root),
        detected_models=models,
        pending_fields=pending,
    )


def render_setup_result(result: SetupResult) -> tuple[str, ...]:
    lines = [
        "Roby Setup Assistant",
        f"[OK] configuración local: {result.config_path}",
        f"[OK] carpetas preparadas: {len(result.created_directories)}",
    ]
    lines.append(
        "[OK] modelos Ollama: " + ", ".join(result.detected_models)
        if result.detected_models
        else "[WARN] no se detectaron modelos de Ollama"
    )
    lines.extend(f"[PENDIENTE] {field}" for field in result.pending_fields)
    lines.append("Siguiente paso: ejecutá python main.py --doctor")
    return tuple(lines)


def _copy_default_config() -> dict:
    import copy

    return copy.deepcopy(DEFAULT_CONFIG)


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path
