from __future__ import annotations

from dataclasses import dataclass

from .trace_anomaly_lifecycle import (
    CognitiveTraceAnomalyLifecycleRecord,
    CognitiveTraceAnomalyLifecycleSnapshot,
)


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleComparisonPolicy:
    """Explicit bounds for deterministic local lifecycle comparisons."""

    maximum_changes: int = 50

    def __post_init__(self) -> None:
        if self.maximum_changes < 1:
            raise ValueError("maximum_changes must be positive")


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleChange:
    code: str
    change_type: str
    previous_state: str | None
    current_state: str | None
    priority_delta: int
    occurrence_delta: int
    trend: str

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "change_type": self.change_type,
            "previous_state": self.previous_state,
            "current_state": self.current_state,
            "priority_delta": self.priority_delta,
            "occurrence_delta": self.occurrence_delta,
            "trend": self.trend,
        }


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleComparison:
    schema_version: str
    previous_record_count: int
    current_record_count: int
    matched_code_count: int
    changed_count: int
    returned_count: int
    truncated_count: int
    improving_count: int
    degrading_count: int
    stable_count: int
    changes: tuple[CognitiveTraceAnomalyLifecycleChange, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "previous_record_count": self.previous_record_count,
            "current_record_count": self.current_record_count,
            "matched_code_count": self.matched_code_count,
            "changed_count": self.changed_count,
            "returned_count": self.returned_count,
            "truncated_count": self.truncated_count,
            "improving_count": self.improving_count,
            "degrading_count": self.degrading_count,
            "stable_count": self.stable_count,
            "changes": [change.as_dict() for change in self.changes],
        }


class CognitiveTraceAnomalyLifecycleComparator:
    """Compare redacted lifecycle snapshots without mutating runtime state."""

    SCHEMA_VERSION = "rp22.16"
    _STATE_RANK = {
        "resolved": 0,
        "acknowledged": 1,
        "new": 2,
        "active": 3,
        "reopened": 4,
    }

    def __init__(
        self,
        policy: CognitiveTraceAnomalyLifecycleComparisonPolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveTraceAnomalyLifecycleComparisonPolicy()

    def compare(
        self,
        previous: CognitiveTraceAnomalyLifecycleSnapshot,
        current: CognitiveTraceAnomalyLifecycleSnapshot,
    ) -> CognitiveTraceAnomalyLifecycleComparison:
        previous_by_code = {record.code: record for record in previous.records}
        current_by_code = {record.code: record for record in current.records}
        all_codes = sorted(set(previous_by_code) | set(current_by_code))
        changes = tuple(
            self._change(code, previous_by_code.get(code), current_by_code.get(code))
            for code in all_codes
        )
        changed = tuple(
            change for change in changes if change.change_type != "unchanged"
        )
        ordered = tuple(
            sorted(
                changed,
                key=lambda item: (
                    {"degrading": 0, "improving": 1, "stable": 2}[item.trend],
                    -abs(item.priority_delta),
                    item.code,
                ),
            )
        )
        returned = ordered[: self.policy.maximum_changes]
        return CognitiveTraceAnomalyLifecycleComparison(
            schema_version=self.SCHEMA_VERSION,
            previous_record_count=len(previous.records),
            current_record_count=len(current.records),
            matched_code_count=len(set(previous_by_code) & set(current_by_code)),
            changed_count=len(ordered),
            returned_count=len(returned),
            truncated_count=max(0, len(ordered) - len(returned)),
            improving_count=sum(change.trend == "improving" for change in ordered),
            degrading_count=sum(change.trend == "degrading" for change in ordered),
            stable_count=sum(change.trend == "stable" for change in ordered),
            changes=returned,
        )

    def _change(
        self,
        code: str,
        previous: CognitiveTraceAnomalyLifecycleRecord | None,
        current: CognitiveTraceAnomalyLifecycleRecord | None,
    ) -> CognitiveTraceAnomalyLifecycleChange:
        if previous is None and current is not None:
            return CognitiveTraceAnomalyLifecycleChange(
                code=code,
                change_type="added",
                previous_state=None,
                current_state=current.state,
                priority_delta=current.priority_score,
                occurrence_delta=current.occurrence_count,
                trend="degrading" if current.state != "resolved" else "stable",
            )
        if previous is not None and current is None:
            return CognitiveTraceAnomalyLifecycleChange(
                code=code,
                change_type="removed",
                previous_state=previous.state,
                current_state=None,
                priority_delta=-previous.priority_score,
                occurrence_delta=-previous.occurrence_count,
                trend="improving",
            )
        assert previous is not None and current is not None
        priority_delta = current.priority_score - previous.priority_score
        occurrence_delta = current.occurrence_count - previous.occurrence_count
        state_changed = previous.state != current.state
        change_type = "state_changed" if state_changed else (
            "metrics_changed" if priority_delta or occurrence_delta else "unchanged"
        )
        trend = self._trend(previous, current, priority_delta)
        return CognitiveTraceAnomalyLifecycleChange(
            code=code,
            change_type=change_type,
            previous_state=previous.state,
            current_state=current.state,
            priority_delta=priority_delta,
            occurrence_delta=occurrence_delta,
            trend=trend,
        )

    def _trend(
        self,
        previous: CognitiveTraceAnomalyLifecycleRecord,
        current: CognitiveTraceAnomalyLifecycleRecord,
        priority_delta: int,
    ) -> str:
        previous_rank = self._STATE_RANK[previous.state]
        current_rank = self._STATE_RANK[current.state]
        if current_rank < previous_rank or current.state == "resolved":
            return "improving"
        if current_rank > previous_rank or current.state == "reopened":
            return "degrading"
        if priority_delta > 0:
            return "degrading"
        if priority_delta < 0:
            return "improving"
        return "stable"
