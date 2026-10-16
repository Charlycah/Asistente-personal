from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class OperationalAcceptanceStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True)
class OperationalAcceptanceCheck:
    name: str
    passed: bool
    detail: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip()
        detail = self.detail.strip()
        if not name:
            raise ValueError("operational acceptance check name must not be blank")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "detail", detail)

    @property
    def status(self) -> OperationalAcceptanceStatus:
        return (
            OperationalAcceptanceStatus.PASSED
            if self.passed
            else OperationalAcceptanceStatus.FAILED
        )


@dataclass(frozen=True)
class OperationalAcceptanceReport:
    checks: tuple[OperationalAcceptanceCheck, ...]

    def __post_init__(self) -> None:
        names = tuple(item.name.casefold() for item in self.checks)
        if not self.checks:
            raise ValueError("operational acceptance report requires checks")
        if len(set(names)) != len(names):
            raise ValueError("operational acceptance check names must be unique")

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.checks)

    @property
    def failed_checks(self) -> tuple[OperationalAcceptanceCheck, ...]:
        return tuple(item for item in self.checks if not item.passed)


class OperationalAcceptanceSuite:
    """Runs deterministic acceptance checks without adding runtime authority."""

    def __init__(
        self,
        checks: tuple[tuple[str, Callable[[], bool]], ...],
    ) -> None:
        self._checks = tuple(checks)

    def run(self) -> OperationalAcceptanceReport:
        results = []
        for name, check in self._checks:
            try:
                passed = bool(check())
                detail = ""
            except Exception as exc:
                passed = False
                detail = type(exc).__name__
            results.append(OperationalAcceptanceCheck(name, passed, detail))
        return OperationalAcceptanceReport(tuple(results))
