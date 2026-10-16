from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RETIRED_PATHS = (
    "core/residence_domain",
    "core/connectivity_domain",
    "core/physical_transport",
    "core/governed_synchronization",
    "core/resident_runtime_service",
    "core/residential_node",
    "core/residential_perception",
    "core/residential_remote_presence",
    "application/residential_perception",
    "application/residential_remote_presence",
    "app/resident_runtime_entrypoint.py",
    "app/residential_connectivity_composition.py",
    "app/residential_connectivity_wiring.py",
    "app/residential_node_bootstrap.py",
    "app/residential_node_lifecycle.py",
    "app/residential_node_process_entrypoint.py",
    "infrastructure/residential_deployment_dependencies.py",
)

PRESERVED_PATHS = (
    "app/resident_component_registry.py",
    "app/official_runtime_composition.py",
    "app/desktop_bootstrap.py",
    "app/web_panel_runtime.py",
    "application/governed_web_panel.py",
    "infrastructure/web_panel_http.py",
    "domain/information_classification.py",
    "app/device_runtime.py",
    "app/device_gateway.py",
    "app/presence_runtime.py",
    "core/device_capabilities",
    "core/device_continuity",
    "core/external_resource_registry.py",
)


def test_residential_legacy_executable_lineage_is_physically_absent() -> None:
    assert all(not (ROOT / relative).exists() for relative in RETIRED_PATHS)


def test_neutral_laptop_runtime_boundaries_are_preserved() -> None:
    assert all((ROOT / relative).exists() for relative in PRESERVED_PATHS)


def test_official_runtime_root_has_no_residential_remote_presence_wiring() -> None:
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    forbidden = (
        "ResidentialRemotePresence",
        "residential.remote_presence",
        "ROBY_RESIDENTIAL_REMOTE_PRESENCE_ENABLED",
        "residential_remote_presence_execution",
        "residential_remote_presence_presentation",
    )
    assert all(token not in source for token in forbidden)


def test_web_panel_sources_keep_only_neutral_runtime_and_resource_projections() -> None:
    source = (ROOT / "app/web_panel_sources.py").read_text(encoding="utf-8")
    assert "class RuntimeWebPanelSource" in source
    assert "class ExternalResourcesWebPanelSource" in source
    assert "ResidentialNodeWebPanelSource" not in source
    assert "SynchronizationWebPanelSource" not in source
