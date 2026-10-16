from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class BatterySnapshot:
    percent: int
    charging: bool

    def __post_init__(self) -> None:
        if not 0 <= self.percent <= 100:
            raise ValueError("battery percent must be between zero and one hundred")


@dataclass(frozen=True)
class BatteryAwarenessPolicy:
    low_threshold: int = 15
    recovery_margin: int = 5
    poll_interval: timedelta = timedelta(seconds=30)
    repeat_after: timedelta = timedelta(minutes=30)

    def __post_init__(self) -> None:
        if not 1 <= self.low_threshold <= 99:
            raise ValueError("low battery threshold must be between 1 and 99")
        if not 1 <= self.recovery_margin <= 50:
            raise ValueError("battery recovery margin must be between 1 and 50")
        if self.low_threshold + self.recovery_margin > 100:
            raise ValueError("battery recovery threshold must not exceed 100")
        if self.poll_interval.total_seconds() <= 0:
            raise ValueError("battery poll interval must be positive")
        if self.repeat_after.total_seconds() <= 0:
            raise ValueError("battery repeat interval must be positive")
