from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_android_legacy_executable_island_is_physically_absent() -> None:
    retired = (
        "app/android_bridge.py",
        "core/android_bridge",
        "core/android_device_state.py",
        "core/android_notifications.py",
        "core/android_clipboard.py",
        "core/android_files.py",
        "core/android_sensors.py",
        "core/android_location.py",
        "core/current_location",
    )
    assert all(not (ROOT / relative).exists() for relative in retired)


def test_neutral_m364_device_gateway_has_no_android_extension() -> None:
    source = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")
    assert "core.android" not in source
    assert "observe_android_" not in source
    assert "latest_android_" not in source


def test_official_laptop_device_runtime_is_preserved() -> None:
    source = (ROOT / "app/device_runtime.py").read_text(encoding="utf-8")
    assert "class OfficialDeviceRuntimeGateway" in source


def test_runtime_root_does_not_depend_on_retired_android_surface() -> None:
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert "app.android_bridge" not in source
    assert "core.android" not in source
    assert "OfficialDeviceGateway" not in source
