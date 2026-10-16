from __future__ import annotations

import os

from application.governed_web_panel import GovernedWebPanelReadModel, SectionReader
from infrastructure.web_panel_http import (
    LocalWebPanelHttpConfig,
    LocalWebPanelHttpService,
)

from .official_runtime_composition import OfficialROBYRuntime
from .web_panel_sources import RuntimeWebPanelSource

DEFAULT_WEB_PANEL_PORT = 8765


class ProductiveWebPanelResident:
    """Lifecycle adapter that reports bind failure to the optional resident registry."""

    def __init__(self, service: LocalWebPanelHttpService) -> None:
        self.service = service

    def start(self) -> None:
        if not self.service.start():
            failure = self.service.last_failure_code or "start_failed"
            raise RuntimeError(f"web panel unavailable: {failure}")

    def stop(self) -> None:
        self.service.stop()


def build_local_web_panel_service(
    runtime: OfficialROBYRuntime,
    *,
    residence_reader: SectionReader | None = None,
    synchronization_reader: SectionReader | None = None,
    resources_reader: SectionReader | None = None,
    port: int | None = None,
) -> ProductiveWebPanelResident:
    """Build the optional local Web Panel without creating runtime authority."""

    system_source = RuntimeWebPanelSource(runtime)
    read_model = GovernedWebPanelReadModel(
        system_reader=system_source.read,
        residence_reader=residence_reader or _no_data,
        synchronization_reader=synchronization_reader or _no_data,
        resources_reader=resources_reader or _no_data,
    )
    service = LocalWebPanelHttpService(
        read_model,
        config=LocalWebPanelHttpConfig(
            host="127.0.0.1",
            port=_web_panel_port_from_environment() if port is None else port,
        ),
    )
    return ProductiveWebPanelResident(service)


def web_panel_enabled_from_environment() -> bool:
    value = os.getenv("ROBY_WEB_PANEL_ENABLED")
    if value is None or not value.strip():
        return False
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _web_panel_port_from_environment() -> int:
    raw = os.getenv("ROBY_WEB_PANEL_PORT", str(DEFAULT_WEB_PANEL_PORT)).strip()
    try:
        port = int(raw)
    except ValueError as exc:
        raise ValueError("ROBY_WEB_PANEL_PORT must be an integer") from exc
    if not 1 <= port <= 65535:
        raise ValueError("ROBY_WEB_PANEL_PORT must be between 1 and 65535")
    return port


def _no_data() -> None:
    return None
