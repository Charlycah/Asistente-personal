from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RETIRED_PATHS = (
    "app/driving_runtime.py",
    "core/mobile_companion",
    "core/mobile_runtime",
    "core/mobile_presence",
    "core/notification_intelligence",
    "core/background_continuity",
    "core/mobile_context",
    "core/hands_free",
    "core/driving_companion",
    "core/driving_context",
    "core/driving_interaction_policy",
    "core/driving_conversation_adaptation",
    "core/driving_safety_coordination",
    "core/mobile_extension",
)


def test_mobile_driving_legacy_executable_lineage_is_physically_absent() -> None:
    assert all(not (ROOT / relative).exists() for relative in RETIRED_PATHS)


def test_official_runtime_root_no_longer_wires_driving_runtime() -> None:
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert "OfficialDrivingRuntimeGateway" not in source
    assert 'name="driving.runtime"' not in source
    assert "driving_runtime=" not in source


def test_end_to_end_runtime_no_longer_retains_driving_dependency() -> None:
    source = (ROOT / "app/end_to_end_conversation_runtime.py").read_text(
        encoding="utf-8"
    )
    assert "driving_runtime" not in source
    assert "integrated_runtimes=7" in source


def test_neutral_device_runtime_is_preserved() -> None:
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert (ROOT / "app/device_runtime.py").is_file()
    assert (ROOT / "core/device_capabilities").is_dir()
    assert (ROOT / "core/device_continuity").is_dir()
    assert "OfficialDeviceRuntimeGateway" in source
    assert 'name="device.runtime"' in source
