from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CompatibilityDisposition(str, Enum):
    """Certified disposition for one historical ROBY runtime surface."""

    CANONICAL = "canonical"
    THIN_ALIAS = "thin_alias"
    SPECIALIZED_ADAPTER = "specialized_adapter"
    LEGACY_ISOLATED = "legacy_isolated"
    RETIRED = "retired"


@dataclass(frozen=True)
class RuntimeCompatibilityRecord:
    key: str
    target: str
    disposition: CompatibilityDisposition
    delegates_to: str | None
    executable: bool
    notes: str


@dataclass(frozen=True)
class LegacyPackageRecord:
    """Certified status for one historical milestone package."""

    package: str
    frozen: bool
    modern_import_allowed: bool
    compatibility_role: str
    notes: str


RUNTIME_COMPATIBILITY_REGISTRY: tuple[RuntimeCompatibilityRecord, ...] = (
    RuntimeCompatibilityRecord(
        key="official_runtime",
        target="app.official_runtime_composition:OfficialROBYRuntime",
        disposition=CompatibilityDisposition.CANONICAL,
        delegates_to=None,
        executable=True,
        notes="Única autoridad oficial de lifecycle y composición operacional.",
    ),
    RuntimeCompatibilityRecord(
        key="desktop_builder_alias",
        target="app.desktop_bootstrap:build_desktop_app",
        disposition=CompatibilityDisposition.THIN_ALIAS,
        delegates_to="app.desktop_bootstrap:build_unified_desktop_app",
        executable=False,
        notes="Nombre histórico conservado sin composición ni lifecycle propios.",
    ),
    RuntimeCompatibilityRecord(
        key="desktop_personal_runtime",
        target="app.desktop_bootstrap:DesktopPersonalRuntime",
        disposition=CompatibilityDisposition.THIN_ALIAS,
        delegates_to="app.official_runtime_composition:OfficialROBYRuntime",
        executable=False,
        notes=(
            "Fachada de pruebas y consumidores históricos; el escritorio oficial "
            "ya no la construye."
        ),
    ),
    RuntimeCompatibilityRecord(
        key="operational_desktop_adapter",
        target="app.desktop_bootstrap:build_operational_desktop_app",
        disposition=CompatibilityDisposition.SPECIALIZED_ADAPTER,
        delegates_to="app.desktop_operational_adapter:DesktopOperationalAdapter",
        executable=False,
        notes="Adapter especializado de integración M176; no posee lifecycle.",
    ),
    RuntimeCompatibilityRecord(
        key="legacy_hal_runtime",
        target="core.hal:HAL",
        disposition=CompatibilityDisposition.RETIRED,
        delegates_to=None,
        executable=False,
        notes=(
            "Runtime HAL histórico retirado tras la consolidación post-auditoría. "
            "El registro se conserva sólo como trazabilidad; no existe implementación "
            "ni alias ejecutable."
        ),
    ),
    RuntimeCompatibilityRecord(
        key="legacy_roby_runtime",
        target="core.roby:ROBY",
        disposition=CompatibilityDisposition.RETIRED,
        delegates_to=None,
        executable=False,
        notes=(
            "Runtime ROBY histórico retirado tras la reconciliación post-auditoría. "
            "El registro se conserva sólo como trazabilidad; no existe implementación "
            "ni alias ejecutable."
        ),
    ),
)


LEGACY_PACKAGE_REGISTRY: tuple[LegacyPackageRecord, ...] = (
    LegacyPackageRecord(
        package="m3",
        frozen=False,
        modern_import_allowed=False,
        compatibility_role="retired_historical_intent_foundation",
        notes=(
            "Implementación histórica retirada; el registro se conserva sólo "
            "como trazabilidad."
        ),
    ),
    LegacyPackageRecord(
        package="m4",
        frozen=False,
        modern_import_allowed=False,
        compatibility_role="retired_historical_decision_planning",
        notes=(
            "Implementación histórica retirada; el registro se conserva sólo "
            "como trazabilidad."
        ),
    ),
    LegacyPackageRecord(
        package="m5",
        frozen=False,
        modern_import_allowed=False,
        compatibility_role="retired_historical_execution",
        notes=(
            "Implementación histórica retirada; el registro se conserva sólo "
            "como trazabilidad."
        ),
    ),
    LegacyPackageRecord(
        package="m6",
        frozen=True,
        modern_import_allowed=False,
        compatibility_role="response_compatibility_shim",
        notes=(
            "Sólo m6.response.models permanece como shim de identidad hacia "
            "domain.response; el runtime histórico de respuesta fue retirado."
        ),
    ),
    LegacyPackageRecord(
        package="m7",
        frozen=False,
        modern_import_allowed=False,
        compatibility_role="retired_historical_conversation_sessions",
        notes=(
            "Implementación histórica retirada; el registro se conserva sólo "
            "como trazabilidad."
        ),
    ),
)


def compatibility_record(key: str) -> RuntimeCompatibilityRecord:
    normalized = key.strip()
    for record in RUNTIME_COMPATIBILITY_REGISTRY:
        if record.key == normalized:
            return record
    raise KeyError(normalized)


def redundant_runtime_paths() -> tuple[RuntimeCompatibilityRecord, ...]:
    """Return surfaces that remain visible but cannot be official execution roots."""

    return tuple(
        record
        for record in RUNTIME_COMPATIBILITY_REGISTRY
        if record.disposition
        in {
            CompatibilityDisposition.THIN_ALIAS,
            CompatibilityDisposition.LEGACY_ISOLATED,
            CompatibilityDisposition.RETIRED,
        }
    )

def legacy_package_record(package: str) -> LegacyPackageRecord:
    normalized = package.strip()
    for record in LEGACY_PACKAGE_REGISTRY:
        if record.package == normalized:
            return record
    raise KeyError(normalized)

