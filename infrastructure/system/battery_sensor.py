from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from pathlib import Path

from core.always_on_personal_runtime import BatterySnapshot


class WindowsSystemBatteryState(ctypes.Structure):
    _fields_ = [
        ("ac_line_status", ctypes.c_ubyte),
        ("battery_flag", ctypes.c_ubyte),
        ("battery_life_percent", ctypes.c_ubyte),
        ("system_status_flag", ctypes.c_ubyte),
        ("battery_life_time", wintypes.DWORD),
        ("battery_full_life_time", wintypes.DWORD),
    ]


class NativeBatterySensor:
    """Reads the host battery without optional third-party dependencies."""

    def read(self) -> BatterySnapshot | None:
        if sys.platform == "win32":
            return self._read_windows()
        if sys.platform.startswith("linux"):
            return self._read_linux()
        return None

    @staticmethod
    def _read_windows() -> BatterySnapshot | None:
        state = WindowsSystemBatteryState()
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        success = kernel32.GetSystemPowerStatus(ctypes.byref(state))
        if not success or state.battery_life_percent == 255:
            return None
        no_battery = bool(state.battery_flag & 128)
        if no_battery:
            return None
        return BatterySnapshot(
            percent=int(state.battery_life_percent),
            charging=state.ac_line_status == 1,
        )

    @staticmethod
    def _read_linux() -> BatterySnapshot | None:
        roots = sorted(Path("/sys/class/power_supply").glob("BAT*"))
        for root in roots:
            try:
                percent = int((root / "capacity").read_text(encoding="utf-8").strip())
                status = (
                    (root / "status").read_text(encoding="utf-8").strip().casefold()
                )
            except (OSError, ValueError):
                continue
            return BatterySnapshot(
                percent=percent,
                charging=status in {"charging", "full"},
            )
        return None
