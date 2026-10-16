from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable

from .first_capability import CapabilityRunResult, CapabilityRunStatus


@dataclass(frozen=True, slots=True)
class ExperiencePattern:
    """Aggregated experience for one situation/action pair."""

    situation_kind: str
    action: str
    occurrences: int
    succeeded: int
    degraded: int
    failed: int
    unknown: int
    last_observed_at: datetime
    last_summary: str

    def __post_init__(self) -> None:
        if not self.situation_kind.strip():
            raise ValueError("experience situation kind must not be blank")
        if not self.action.strip():
            raise ValueError("experience action must not be blank")
        counters = (
            self.occurrences,
            self.succeeded,
            self.degraded,
            self.failed,
            self.unknown,
        )
        if min(counters) < 0:
            raise ValueError("experience counters must not be negative")
        if sum(counters[1:]) != self.occurrences:
            raise ValueError("experience outcome counters must match occurrences")
        if self.last_observed_at.tzinfo is None:
            raise ValueError("experience timestamp must be timezone-aware")
        if not self.last_summary.strip():
            raise ValueError("experience summary must not be blank")


@dataclass(frozen=True, slots=True)
class ExperienceMemorySnapshot:
    patterns: tuple[ExperiencePattern, ...]

    @property
    def total_occurrences(self) -> int:
        return sum(pattern.occurrences for pattern in self.patterns)


@runtime_checkable
class ExperienceMemory(Protocol):
    def remember(self, result: CapabilityRunResult) -> ExperiencePattern | None: ...

    def snapshot(self) -> ExperienceMemorySnapshot: ...


class JsonExperienceMemory:
    """Durable aggregate memory derived from executed autonomy outcomes."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._patterns = self._load()

    def remember(self, result: CapabilityRunResult) -> ExperiencePattern | None:
        if result.status is not CapabilityRunStatus.EXECUTED:
            return None
        candidate = result.candidate
        outcome = result.outcome
        situation = result.orchestration.assessment.situation
        if candidate is None or outcome is None or situation is None:
            raise ValueError("executed result requires experience inputs")
        key = (situation.kind, candidate.action)
        with self._lock:
            previous = self._patterns.get(key)
            counts = {
                "succeeded": previous.succeeded if previous else 0,
                "degraded": previous.degraded if previous else 0,
                "failed": previous.failed if previous else 0,
                "unknown": previous.unknown if previous else 0,
            }
            bucket = _outcome_bucket(outcome.status.value)
            counts[bucket] += 1
            pattern = ExperiencePattern(
                situation_kind=situation.kind,
                action=candidate.action,
                occurrences=(previous.occurrences + 1 if previous else 1),
                succeeded=counts["succeeded"],
                degraded=counts["degraded"],
                failed=counts["failed"],
                unknown=counts["unknown"],
                last_observed_at=outcome.observed_at,
                last_summary=outcome.summary,
            )
            updated = dict(self._patterns)
            updated[key] = pattern
            self._persist(updated)
            self._patterns = updated
            return pattern

    def snapshot(self) -> ExperienceMemorySnapshot:
        with self._lock:
            patterns = tuple(
                sorted(
                    self._patterns.values(),
                    key=lambda item: (item.situation_kind, item.action),
                )
            )
            return ExperienceMemorySnapshot(patterns=patterns)

    def _persist(
        self,
        patterns: dict[tuple[str, str], ExperiencePattern],
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "patterns": [_pattern_to_payload(item) for item in patterns.values()],
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                payload,
                stream,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def _load(self) -> dict[tuple[str, str], ExperiencePattern]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload["schema_version"] != 1:
                raise ValueError("unsupported experience memory schema version")
            patterns = tuple(
                _pattern_from_payload(item) for item in payload["patterns"]
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid experience memory file") from exc
        keyed = {(item.situation_kind, item.action): item for item in patterns}
        if len(keyed) != len(patterns):
            raise ValueError("experience memory contains duplicate patterns")
        return keyed


def _outcome_bucket(status: str) -> str:
    if status == "succeeded":
        return "succeeded"
    if status == "degraded":
        return "degraded"
    if status == "failed":
        return "failed"
    return "unknown"


def _pattern_to_payload(pattern: ExperiencePattern) -> dict[str, object]:
    return {
        "situation_kind": pattern.situation_kind,
        "action": pattern.action,
        "occurrences": pattern.occurrences,
        "succeeded": pattern.succeeded,
        "degraded": pattern.degraded,
        "failed": pattern.failed,
        "unknown": pattern.unknown,
        "last_observed_at": pattern.last_observed_at.isoformat(),
        "last_summary": pattern.last_summary,
    }


def _pattern_from_payload(payload: dict[str, object]) -> ExperiencePattern:
    return ExperiencePattern(
        situation_kind=str(payload["situation_kind"]),
        action=str(payload["action"]),
        occurrences=int(payload["occurrences"]),
        succeeded=int(payload["succeeded"]),
        degraded=int(payload["degraded"]),
        failed=int(payload["failed"]),
        unknown=int(payload["unknown"]),
        last_observed_at=datetime.fromisoformat(str(payload["last_observed_at"])),
        last_summary=str(payload["last_summary"]),
    )


__all__ = [
    "ExperienceMemory",
    "ExperienceMemorySnapshot",
    "ExperiencePattern",
    "JsonExperienceMemory",
]
