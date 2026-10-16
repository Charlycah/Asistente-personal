from __future__ import annotations

from pathlib import Path

from app.runtime_compatibility import (
    LEGACY_PACKAGE_REGISTRY,
    CompatibilityDisposition,
    compatibility_record,
    legacy_package_record,
)
from domain.response import ResponseStatus, UserResponse

ROOT = Path(__file__).resolve().parents[2]
MODERN_ROOTS = (
    "app",
    "application",
    "domain",
    "infrastructure",
    "handlers",
    "engines",
    "interfaces",
)
RETIRED_PACKAGES = ("m3", "m4", "m5", "m7")
LEGACY_PREFIXES = tuple(f"m{index}." for index in range(3, 8))


def _imports_legacy(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    return any(
        f"from {prefix}" in source or f"import {prefix}" in source
        for prefix in LEGACY_PREFIXES
    )


def test_m395_4_historical_hal_and_roby_runtimes_are_retired() -> None:
    hal = compatibility_record("legacy_hal_runtime")
    assert hal.target == "core.hal:HAL"
    assert hal.disposition is CompatibilityDisposition.RETIRED
    assert hal.executable is False
    assert hal.delegates_to is None
    assert not (ROOT / "core" / "hal.py").exists()

    roby = compatibility_record("legacy_roby_runtime")
    assert roby.target == "core.roby:ROBY"
    assert roby.disposition is CompatibilityDisposition.RETIRED
    assert roby.executable is False
    assert roby.delegates_to is None
    assert not (ROOT / "core" / "roby.py").exists()


def test_m395_4_legacy_package_registry_records_retirement_and_m6_shim() -> None:
    assert tuple(record.package for record in LEGACY_PACKAGE_REGISTRY) == (
        "m3",
        "m4",
        "m5",
        "m6",
        "m7",
    )

    expected_roles = {
        "m3": "retired_historical_intent_foundation",
        "m4": "retired_historical_decision_planning",
        "m5": "retired_historical_execution",
        "m6": "response_compatibility_shim",
        "m7": "retired_historical_conversation_sessions",
    }
    for package, role in expected_roles.items():
        record = legacy_package_record(package)
        assert record.compatibility_role == role
        assert record.modern_import_allowed is False
        assert record.frozen is (package == "m6")


def test_m395_4_retired_packages_are_absent_and_only_m6_shim_remains() -> None:
    for package in RETIRED_PACKAGES:
        assert not (ROOT / package).exists()

    assert (ROOT / "m6" / "response" / "models.py").exists()
    assert (ROOT / "m6" / "response" / "__init__.py").exists()
    assert not (ROOT / "m6" / "response" / "response_layer.py").exists()
    assert not (ROOT / "m6" / "response" / "renderers.py").exists()


def test_m395_4_modern_layers_do_not_import_m3_to_m7() -> None:
    offenders: list[str] = []
    for root_name in MODERN_ROOTS:
        for path in (ROOT / root_name).rglob("*.py"):
            if _imports_legacy(path):
                offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []


def test_m395_4_core_does_not_import_m3_to_m7() -> None:
    importers = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "core").rglob("*.py")
        if _imports_legacy(path)
    }
    assert importers == set()


def test_m395_4_m6_response_shim_preserves_neutral_type_identity() -> None:
    from m6.response.models import ResponseStatus as LegacyResponseStatus
    from m6.response.models import UserResponse as LegacyUserResponse

    assert LegacyResponseStatus is ResponseStatus
    assert LegacyUserResponse is UserResponse
