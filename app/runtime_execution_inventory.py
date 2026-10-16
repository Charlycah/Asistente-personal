from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.runtime_bootstrap_contract import (
    OFFICIAL_COMPOSITION_ROOT,
    OFFICIAL_RUNTIME_FACTORY,
)


class ExecutionRootRole(str, Enum):
    """Architectural role assigned to a ROBY execution or composition root."""

    CANONICAL_PROCESS_ENTRYPOINT = "canonical_process_entrypoint"
    CANONICAL_UI_ENTRYPOINT = "canonical_ui_entrypoint"
    CANONICAL_RUNTIME_FACTORY = "canonical_runtime_factory"
    CANONICAL_COMPOSITION_ROOT = "canonical_composition_root"
    CANONICAL_LIFECYCLE_AUTHORITY = "canonical_lifecycle_authority"
    RUNTIME_BOOTSTRAP = "runtime_bootstrap"
    LIFECYCLE_ADAPTER = "lifecycle_adapter"
    CONVERSATION_ADAPTER = "conversation_adapter"
    COMPATIBILITY_ALIAS = "compatibility_alias"
    LEGACY_COMPOSITION_ROOT = "legacy_composition_root"
    PROVISIONING_BOOTSTRAP = "provisioning_bootstrap"
    OPERATIONAL_ADAPTER = "operational_adapter"
    MAINTENANCE_TOOL = "maintenance_tool"


class ExecutionRootDisposition(str, Enum):
    """Decision for the root during RP.18.2 consolidation."""

    KEEP_CANONICAL = "keep_canonical"
    KEEP_SPECIALIZED = "keep_specialized"
    DELEGATE_LATER = "delegate_later"
    REVIEW_FOR_RETIREMENT = "review_for_retirement"


@dataclass(frozen=True)
class ExecutionRootRecord:
    key: str
    target: str
    role: ExecutionRootRole
    disposition: ExecutionRootDisposition
    starts_process: bool
    owns_lifecycle: bool
    notes: str


OFFICIAL_PROCESS_ENTRYPOINT = "main:main"
EXECUTION_ROOT_INVENTORY: tuple[ExecutionRootRecord, ...] = (
    ExecutionRootRecord(
        key="roby_process_entrypoint",
        target=OFFICIAL_PROCESS_ENTRYPOINT,
        role=ExecutionRootRole.CANONICAL_PROCESS_ENTRYPOINT,
        disposition=ExecutionRootDisposition.KEEP_CANONICAL,
        starts_process=True,
        owns_lifecycle=False,
        notes="Único punto de entrada de proceso para ROBY Desktop.",
    ),
    ExecutionRootRecord(
        key="desktop_runtime",
        target="app.desktop_bootstrap:build_unified_desktop_app",
        role=ExecutionRootRole.CANONICAL_UI_ENTRYPOINT,
        disposition=ExecutionRootDisposition.KEEP_CANONICAL,
        starts_process=False,
        owns_lifecycle=True,
        notes="Compone la interfaz de escritorio y sus residentes domésticos.",
    ),
    ExecutionRootRecord(
        key="desktop_compatibility_alias",
        target="app.desktop_bootstrap:build_desktop_app",
        role=ExecutionRootRole.COMPATIBILITY_ALIAS,
        disposition=ExecutionRootDisposition.KEEP_SPECIALIZED,
        starts_process=False,
        owns_lifecycle=False,
        notes="Alias compatible que delega al constructor unificado de escritorio.",
    ),
    ExecutionRootRecord(
        key="local_conversation",
        target=(
            "app.local_conversation_factory:"
            "build_local_conversation_from_environment"
        ),
        role=ExecutionRootRole.CONVERSATION_ADAPTER,
        disposition=ExecutionRootDisposition.KEEP_SPECIALIZED,
        starts_process=False,
        owns_lifecycle=False,
        notes="Adapta el runtime local a la conversación extremo a extremo.",
    ),
    ExecutionRootRecord(
        key="local_runtime_bootstrap_factory",
        target="app.local_runtime_entrypoint:build_local_runtime_from_environment",
        role=ExecutionRootRole.RUNTIME_BOOTSTRAP,
        disposition=ExecutionRootDisposition.KEEP_CANONICAL,
        starts_process=False,
        owns_lifecycle=False,
        notes="Carga la fábrica oficial y crea un solo LocalRuntimeBootstrap.",
    ),
    ExecutionRootRecord(
        key="official_runtime_factory",
        target=OFFICIAL_RUNTIME_FACTORY,
        role=ExecutionRootRole.CANONICAL_RUNTIME_FACTORY,
        disposition=ExecutionRootDisposition.KEEP_CANONICAL,
        starts_process=False,
        owns_lifecycle=False,
        notes="Construye las dependencias del grafo operativo oficial.",
    ),
    ExecutionRootRecord(
        key="runtime_composition_root",
        target=OFFICIAL_COMPOSITION_ROOT,
        role=ExecutionRootRole.CANONICAL_COMPOSITION_ROOT,
        disposition=ExecutionRootDisposition.KEEP_CANONICAL,
        starts_process=False,
        owns_lifecycle=False,
        notes="Autoridad idempotente de composición del runtime operacional.",
    ),
    ExecutionRootRecord(
        key="official_roby_runtime",
        target="app.official_runtime_composition:OfficialROBYRuntime",
        role=ExecutionRootRole.CANONICAL_LIFECYCLE_AUTHORITY,
        disposition=ExecutionRootDisposition.KEEP_CANONICAL,
        starts_process=False,
        owns_lifecycle=True,
        notes="Única autoridad de arranque y apagado del runtime oficial.",
    ),
    ExecutionRootRecord(
        key="long_lived_lifecycle",
        target=(
            "app.long_lived_runtime_entrypoint:"
            "build_long_lived_lifecycle_from_environment"
        ),
        role=ExecutionRootRole.LIFECYCLE_ADAPTER,
        disposition=ExecutionRootDisposition.KEEP_SPECIALIZED,
        starts_process=False,
        owns_lifecycle=True,
        notes="Supervisa lease, heartbeat y cierre del bootstrap local.",
    ),
    ExecutionRootRecord(
        key="desktop_operational_adapter",
        target="app.desktop_bootstrap:build_operational_desktop_app",
        role=ExecutionRootRole.OPERATIONAL_ADAPTER,
        disposition=ExecutionRootDisposition.KEEP_SPECIALIZED,
        starts_process=False,
        owns_lifecycle=False,
        notes="Frontera de escritorio usada por integraciones operativas gobernadas.",
    ),
    ExecutionRootRecord(
        key="household_provisioning",
        target="app.household_always_on_bootstrap:bootstrap_household",
        role=ExecutionRootRole.PROVISIONING_BOOTSTRAP,
        disposition=ExecutionRootDisposition.KEEP_SPECIALIZED,
        starts_process=False,
        owns_lifecycle=False,
        notes="Inicializa datos domésticos; no es un runtime de proceso.",
    ),
    ExecutionRootRecord(
        key="artifact_cleaner",
        target="scripts.clean_project_artifacts:main",
        role=ExecutionRootRole.MAINTENANCE_TOOL,
        disposition=ExecutionRootDisposition.KEEP_SPECIALIZED,
        starts_process=True,
        owns_lifecycle=False,
        notes="Herramienta de mantenimiento; no inicia ROBY.",
    ),
)


def execution_root_by_key(key: str) -> ExecutionRootRecord:
    normalized = key.strip()
    for record in EXECUTION_ROOT_INVENTORY:
        if record.key == normalized:
            return record
    raise KeyError(normalized)


def canonical_execution_chain() -> tuple[str, ...]:
    """Return the certified construction chain without importing runtime code."""

    return (
        OFFICIAL_PROCESS_ENTRYPOINT,
        "app.local_conversation_factory:build_local_conversation_from_environment",
        "app.local_runtime_entrypoint:build_local_runtime_from_environment",
        OFFICIAL_RUNTIME_FACTORY,
        OFFICIAL_COMPOSITION_ROOT,
        "app.official_runtime_composition:OfficialROBYRuntime",
    )
