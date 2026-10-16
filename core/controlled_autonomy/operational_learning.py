from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .experience_memory import ExperienceMemorySnapshot, ExperiencePattern


class OperationalLearningDisposition(str, Enum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FAVOR = "favor"
    NEUTRAL = "neutral"
    CAUTION = "caution"


@dataclass(frozen=True, slots=True)
class OperationalLearning:
    learning_id: str
    situation_kind: str
    action: str
    observed_at: datetime
    occurrences: int
    success_rate: float
    failure_rate: float
    adjustment: float
    disposition: OperationalLearningDisposition
    evidence: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        if not self.learning_id.strip():
            raise ValueError("operational learning id must not be blank")
        if not self.situation_kind.strip() or not self.action.strip():
            raise ValueError("operational learning subject must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("operational learning timestamp must be timezone-aware")
        if self.occurrences < 0:
            raise ValueError("operational learning occurrences must not be negative")
        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError("operational learning success rate is invalid")
        if not 0.0 <= self.failure_rate <= 1.0:
            raise ValueError("operational learning failure rate is invalid")
        if not -0.2 <= self.adjustment <= 0.2:
            raise ValueError("operational learning adjustment exceeds safe bounds")
        if not self.evidence or not self.summary.strip():
            raise ValueError("operational learning evidence must not be blank")


@dataclass(frozen=True, slots=True)
class OperationalLearningSnapshot:
    learnings: tuple[OperationalLearning, ...]

    @property
    def actionable_count(self) -> int:
        return sum(
            item.disposition
            is not OperationalLearningDisposition.INSUFFICIENT_EVIDENCE
            for item in self.learnings
        )


@runtime_checkable
class OperationalLearner(Protocol):
    def learn(
        self,
        *,
        experience: ExperienceMemorySnapshot,
        situation_kind: str,
        action: str,
        observed_at: datetime,
    ) -> OperationalLearning: ...


class DeterministicOperationalLearner:
    """Derives bounded recommendations from audited aggregate outcomes."""

    minimum_occurrences = 3
    maximum_adjustment = 0.2

    def learn(
        self,
        *,
        experience: ExperienceMemorySnapshot,
        situation_kind: str,
        action: str,
        observed_at: datetime,
    ) -> OperationalLearning:
        if observed_at.tzinfo is None:
            raise ValueError("operational learning timestamp must be timezone-aware")
        if not situation_kind.strip() or not action.strip():
            raise ValueError("operational learning subject must not be blank")
        pattern = _find_pattern(experience, situation_kind, action)
        if pattern is None:
            return self._insufficient(situation_kind, action, observed_at, None)
        if pattern.occurrences < self.minimum_occurrences:
            return self._insufficient(situation_kind, action, observed_at, pattern)
        success_rate = pattern.succeeded / pattern.occurrences
        failure_rate = pattern.failed / pattern.occurrences
        raw_adjustment = (success_rate - failure_rate) * self.maximum_adjustment
        adjustment = max(
            -self.maximum_adjustment,
            min(self.maximum_adjustment, round(raw_adjustment, 4)),
        )
        if adjustment >= 0.05:
            disposition = OperationalLearningDisposition.FAVOR
        elif adjustment <= -0.05:
            disposition = OperationalLearningDisposition.CAUTION
        else:
            disposition = OperationalLearningDisposition.NEUTRAL
        evidence = _pattern_evidence(pattern)
        summary = (
            f"Bounded operational recommendation for {action}: "
            f"{disposition.value}; policy and authorization remain unchanged."
        )
        return OperationalLearning(
            learning_id=uuid4().hex,
            situation_kind=situation_kind,
            action=action,
            observed_at=observed_at,
            occurrences=pattern.occurrences,
            success_rate=success_rate,
            failure_rate=failure_rate,
            adjustment=adjustment,
            disposition=disposition,
            evidence=evidence,
            summary=summary,
        )

    def _insufficient(
        self,
        situation_kind: str,
        action: str,
        observed_at: datetime,
        pattern: ExperiencePattern | None,
    ) -> OperationalLearning:
        occurrences = pattern.occurrences if pattern is not None else 0
        evidence = (
            f"occurrences={occurrences}",
            f"minimum_required={self.minimum_occurrences}",
        )
        return OperationalLearning(
            learning_id=uuid4().hex,
            situation_kind=situation_kind,
            action=action,
            observed_at=observed_at,
            occurrences=occurrences,
            success_rate=(
                pattern.succeeded / occurrences if occurrences else 0.0
            ),
            failure_rate=(pattern.failed / occurrences if occurrences else 0.0),
            adjustment=0.0,
            disposition=OperationalLearningDisposition.INSUFFICIENT_EVIDENCE,
            evidence=evidence,
            summary="Insufficient audited evidence; no operational adjustment.",
        )


@runtime_checkable
class OperationalLearningStore(Protocol):
    def append(self, learning: OperationalLearning) -> None: ...

    def snapshot(self) -> OperationalLearningSnapshot: ...


class JsonOperationalLearningStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._learnings = self._load()

    def append(self, learning: OperationalLearning) -> None:
        with self._lock:
            if learning.learning_id in self._learnings:
                raise ValueError(
                    f"duplicate operational learning id: {learning.learning_id}"
                )
            updated = dict(self._learnings)
            updated[learning.learning_id] = learning
            self._persist(updated)
            self._learnings = updated

    def snapshot(self) -> OperationalLearningSnapshot:
        with self._lock:
            values = tuple(
                sorted(
                    self._learnings.values(),
                    key=lambda item: (item.observed_at, item.learning_id),
                )
            )
        return OperationalLearningSnapshot(values)

    def _persist(self, learnings: dict[str, OperationalLearning]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "learnings": [_to_payload(item) for item in learnings.values()],
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def _load(self) -> dict[str, OperationalLearning]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != 1:
                raise ValueError("unsupported schema")
            items = [_from_payload(item) for item in payload["learnings"]]
            result = {item.learning_id: item for item in items}
            if len(result) != len(items):
                raise ValueError("duplicate ids")
            return result
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(
                f"invalid operational learning file: {self.path}"
            ) from error


def _find_pattern(
    experience: ExperienceMemorySnapshot,
    situation_kind: str,
    action: str,
) -> ExperiencePattern | None:
    return next(
        (
            item
            for item in experience.patterns
            if item.situation_kind == situation_kind and item.action == action
        ),
        None,
    )


def _pattern_evidence(pattern: ExperiencePattern) -> tuple[str, ...]:
    return (
        f"occurrences={pattern.occurrences}",
        f"succeeded={pattern.succeeded}",
        f"degraded={pattern.degraded}",
        f"failed={pattern.failed}",
        f"unknown={pattern.unknown}",
        f"last_summary={pattern.last_summary}",
    )


def _to_payload(learning: OperationalLearning) -> dict[str, object]:
    return {
        "learning_id": learning.learning_id,
        "situation_kind": learning.situation_kind,
        "action": learning.action,
        "observed_at": learning.observed_at.isoformat(),
        "occurrences": learning.occurrences,
        "success_rate": learning.success_rate,
        "failure_rate": learning.failure_rate,
        "adjustment": learning.adjustment,
        "disposition": learning.disposition.value,
        "evidence": list(learning.evidence),
        "summary": learning.summary,
    }


def _from_payload(payload: dict[str, object]) -> OperationalLearning:
    return OperationalLearning(
        learning_id=str(payload["learning_id"]),
        situation_kind=str(payload["situation_kind"]),
        action=str(payload["action"]),
        observed_at=datetime.fromisoformat(str(payload["observed_at"])),
        occurrences=int(payload["occurrences"]),
        success_rate=float(payload["success_rate"]),
        failure_rate=float(payload["failure_rate"]),
        adjustment=float(payload["adjustment"]),
        disposition=OperationalLearningDisposition(str(payload["disposition"])),
        evidence=tuple(str(item) for item in payload["evidence"]),
        summary=str(payload["summary"]),
    )


__all__ = [
    "DeterministicOperationalLearner",
    "JsonOperationalLearningStore",
    "OperationalLearner",
    "OperationalLearning",
    "OperationalLearningDisposition",
    "OperationalLearningSnapshot",
    "OperationalLearningStore",
]
