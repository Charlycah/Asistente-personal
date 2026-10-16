from __future__ import annotations

import importlib
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    passed: bool
    detail: str
    required: bool = True


def run_doctor() -> tuple[DoctorCheck, ...]:
    from app.roby_config import DEFAULT_CONFIG_PATH, load_roby_config

    try:
        result = load_roby_config(DEFAULT_CONFIG_PATH)
        config_ok = True
        config_detail = str(result.path)
    except (OSError, ValueError) as exc:
        config_ok = False
        config_detail = str(exc)

    factory_path = os.getenv("ROBY_RUNTIME_ROOT_FACTORY", "").strip()
    model = os.getenv("ROBY_LOCAL_PROVIDER_MODEL", "").strip()
    endpoint = os.getenv(
        "ROBY_LOCAL_PROVIDER_ENDPOINT", "http://127.0.0.1:11434/v1"
    ).strip()
    try:
        from core.cognitive_planning import CognitiveKernelDiagnostic

        kernel_diagnostic = CognitiveKernelDiagnostic().run()
        kernel_ok = kernel_diagnostic.passed
        kernel_detail = (
            f"{kernel_diagnostic.schema_version}; "
            f"checks={len(kernel_diagnostic.check_codes)}"
        )
        if kernel_diagnostic.failure_codes:
            kernel_detail += "; failures=" + ",".join(
                kernel_diagnostic.failure_codes
            )
    except Exception as exc:
        kernel_ok = False
        kernel_detail = f"diagnóstico no disponible: {exc.__class__.__name__}"

    checks = [
        DoctorCheck(
            "python",
            sys.version_info >= (3, 11),
            f"{platform.python_version()} (se requiere 3.11 o superior)",
        ),
        DoctorCheck("configuration", config_ok, config_detail),
        DoctorCheck(
            "runtime_factory",
            _factory_exists(factory_path),
            factory_path or "fábrica oficial no configurada",
        ),
        DoctorCheck(
            "cognitive_kernel",
            kernel_ok,
            kernel_detail,
        ),
        DoctorCheck(
            "provider_endpoint",
            endpoint.startswith(("http://", "https://")),
            endpoint or "endpoint vacío",
        ),
        DoctorCheck(
            "provider_model",
            bool(model),
            model or "falta providers.local.model en .roby/config.json",
        ),
        DoctorCheck(
            "state_directory",
            _parent_is_writable(
                Path(
                    ".roby/identity/profiles/carlos-cristina/sessions/coowners-main/runtime_state.json"
                )
            ),
            ".roby/identity/profiles/carlos-cristina/sessions/coowners-main/runtime_state.json",
        ),
    ]
    return tuple(checks)


def render_doctor(checks: tuple[DoctorCheck, ...]) -> tuple[str, ...]:
    lines = ["Roby Development Doctor"]
    for check in checks:
        marker = "OK" if check.passed else ("WARN" if not check.required else "FAIL")
        lines.append(f"[{marker}] {check.name}: {check.detail}")
    required_ok = all(check.passed for check in checks if check.required)
    lines.append(
        "Resultado: listo" if required_ok else "Resultado: configuración requerida"
    )
    return tuple(lines)


def onboarding_message(error: Exception) -> tuple[str, ...]:
    return (
        "Roby no pudo iniciar.",
        f"Motivo: {error}",
        "",
        "Comprobaciones:",
        "1. Revisá .roby/config.json.",
        "2. Confirmá que Ollama esté iniciado.",
        "3. Confirmá que providers.local.model esté instalado.",
        "4. Ejecutá: python main.py --doctor",
        "",
        "Guía completa: docs/guides/ROBY_FIRST_STEPS.md",
    )


def _factory_exists(path: str) -> bool:
    if not path or ":" not in path:
        return False
    module_name, function_name = path.split(":", 1)
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return False
    return callable(getattr(module, function_name, None))


def _parent_is_writable(path: Path) -> bool:
    parent = path.expanduser().resolve().parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        probe = parent / ".roby_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError:
        return False
    return True
