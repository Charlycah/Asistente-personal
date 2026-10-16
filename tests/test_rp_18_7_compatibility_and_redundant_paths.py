from __future__ import annotations

from pathlib import Path

from app.runtime_compatibility import (
    CompatibilityDisposition,
    compatibility_record,
    redundant_runtime_paths,
)


def test_desktop_alias_is_classified_as_thin_delegation() -> None:
    record = compatibility_record("desktop_builder_alias")

    assert record.disposition is CompatibilityDisposition.THIN_ALIAS
    assert record.delegates_to == "app.desktop_bootstrap:build_unified_desktop_app"
    assert not record.executable


def test_retired_legacy_core_composition_is_absent() -> None:
    assert all(
        record.key != "legacy_core_application" for record in redundant_runtime_paths()
    )
    try:
        compatibility_record("legacy_core_application")
    except KeyError:
        pass
    else:
        raise AssertionError("retired legacy composition must not remain registered")


def test_redundant_surfaces_are_never_certified_execution_roots() -> None:
    assert redundant_runtime_paths()
    assert all(not record.executable for record in redundant_runtime_paths())


def test_desktop_camera_capture_has_no_direct_adapter_bypass() -> None:
    source = Path("app/desktop_bootstrap.py").read_text(encoding="utf-8")

    assert "camera_registration.interceptor.adapter.capture" not in source
    assert "capability_registry.execute_registration(" in source
    assert 'origin="ambient_proactive_runtime"' in source


def test_official_desktop_uses_original_runtime_with_residents() -> None:
    source = Path("app/desktop_bootstrap.py").read_text(encoding="utf-8")
    builder = source.split("def build_unified_desktop_app", maxsplit=1)[1]

    assert "DesktopPersonalRuntime(" not in builder
    assert "official_runtime.with_residents(" in builder
