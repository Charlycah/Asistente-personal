from __future__ import annotations

from dataclasses import dataclass

from .trace_anomaly_consolidation import CognitiveTraceAnomalyConsolidationSnapshot


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecyclePolicy:
    """Explicit bounds for deterministic local anomaly lifecycle tracking."""

    maximum_records: int = 50
    maximum_transitions: int = 200
    resolve_absent: bool = True

    def __post_init__(self) -> None:
        if self.maximum_records < 1:
            raise ValueError("maximum_records must be positive")
        if self.maximum_transitions < 1:
            raise ValueError("maximum_transitions must be positive")


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleTransition:
    sequence: int
    code: str
    previous_state: str | None
    current_state: str
    reason_code: str

    def as_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "code": self.code,
            "previous_state": self.previous_state,
            "current_state": self.current_state,
            "reason_code": self.reason_code,
        }


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleRecord:
    code: str
    state: str
    occurrence_count: int
    reopen_count: int
    transition_count: int
    priority_score: int
    classification: str

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "state": self.state,
            "occurrence_count": self.occurrence_count,
            "reopen_count": self.reopen_count,
            "transition_count": self.transition_count,
            "priority_score": self.priority_score,
            "classification": self.classification,
        }


@dataclass(frozen=True)
class CognitiveTraceAnomalyLifecycleSnapshot:
    schema_version: str
    record_count: int
    transition_count: int
    records: tuple[CognitiveTraceAnomalyLifecycleRecord, ...]
    transitions: tuple[CognitiveTraceAnomalyLifecycleTransition, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "record_count": self.record_count,
            "transition_count": self.transition_count,
            "records": [record.as_dict() for record in self.records],
            "transitions": [transition.as_dict() for transition in self.transitions],
        }


class CognitiveTraceAnomalyLifecycle:
    """Track redacted anomaly states locally without executive action."""

    SCHEMA_VERSION = "rp22.14"
    STATES = frozenset({"new", "active", "acknowledged", "resolved", "reopened"})

    def __init__(
        self,
        policy: CognitiveTraceAnomalyLifecyclePolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveTraceAnomalyLifecyclePolicy()
        self._records: dict[str, CognitiveTraceAnomalyLifecycleRecord] = {}
        self._transitions: list[CognitiveTraceAnomalyLifecycleTransition] = []
        self._sequence = 0

    @property
    def snapshot(self) -> CognitiveTraceAnomalyLifecycleSnapshot:
        records = tuple(sorted(self._records.values(), key=lambda item: item.code))
        return CognitiveTraceAnomalyLifecycleSnapshot(
            schema_version=self.SCHEMA_VERSION,
            record_count=len(records),
            transition_count=len(self._transitions),
            records=records,
            transitions=tuple(self._transitions),
        )

    def ingest(
        self,
        consolidation: CognitiveTraceAnomalyConsolidationSnapshot,
    ) -> CognitiveTraceAnomalyLifecycleSnapshot:
        observed = {record.code: record for record in consolidation.records}
        for code in sorted(observed):
            source = observed[code]
            current = self._records.get(code)
            if current is None:
                self._set(code, "new", "first_observation", source)
            elif current.state == "resolved":
                self._set(code, "reopened", "observed_after_resolution", source)
            elif current.state in {"new", "reopened"}:
                self._set(code, "active", "observation_repeated", source)
            else:
                self._refresh(current, source)

        if self.policy.resolve_absent:
            for code in sorted(set(self._records) - set(observed)):
                current = self._records[code]
                if current.state != "resolved":
                    self._transition(current, "resolved", "absent_from_snapshot")

        self._enforce_record_bound()
        return self.snapshot

    def acknowledge(self, code: str) -> CognitiveTraceAnomalyLifecycleSnapshot:
        current = self._require(code)
        if current.state not in {"new", "active", "reopened"}:
            raise ValueError("anomaly cannot be acknowledged from current state")
        self._transition(current, "acknowledged", "explicit_acknowledgement")
        return self.snapshot

    def resolve(self, code: str) -> CognitiveTraceAnomalyLifecycleSnapshot:
        current = self._require(code)
        if current.state == "resolved":
            return self.snapshot
        self._transition(current, "resolved", "explicit_resolution")
        return self.snapshot

    def clear(self) -> None:
        self._records.clear()
        self._transitions.clear()
        self._sequence = 0

    def _set(self, code: str, state: str, reason: str, source: object) -> None:
        priority_score = int(getattr(source, "priority_score"))
        classification = str(getattr(source, "classification"))
        current = self._records.get(code)
        occurrence_count = 1 if current is None else current.occurrence_count + 1
        reopen_count = 0 if current is None else current.reopen_count
        if state == "reopened":
            reopen_count += 1
        transition_count = 1 if current is None else current.transition_count + 1
        previous_state = None if current is None else current.state
        self._records[code] = CognitiveTraceAnomalyLifecycleRecord(
            code=code,
            state=state,
            occurrence_count=occurrence_count,
            reopen_count=reopen_count,
            transition_count=transition_count,
            priority_score=priority_score,
            classification=classification,
        )
        self._append_transition(code, previous_state, state, reason)

    def _refresh(
        self,
        current: CognitiveTraceAnomalyLifecycleRecord,
        source: object,
    ) -> None:
        self._records[current.code] = CognitiveTraceAnomalyLifecycleRecord(
            code=current.code,
            state=current.state,
            occurrence_count=current.occurrence_count + 1,
            reopen_count=current.reopen_count,
            transition_count=current.transition_count,
            priority_score=max(
                current.priority_score,
                int(getattr(source, "priority_score")),
            ),
            classification=str(getattr(source, "classification")),
        )

    def _transition(
        self,
        current: CognitiveTraceAnomalyLifecycleRecord,
        state: str,
        reason: str,
    ) -> None:
        self._records[current.code] = CognitiveTraceAnomalyLifecycleRecord(
            code=current.code,
            state=state,
            occurrence_count=current.occurrence_count,
            reopen_count=current.reopen_count,
            transition_count=current.transition_count + 1,
            priority_score=current.priority_score,
            classification=current.classification,
        )
        self._append_transition(current.code, current.state, state, reason)

    def _append_transition(
        self,
        code: str,
        previous_state: str | None,
        current_state: str,
        reason_code: str,
    ) -> None:
        self._sequence += 1
        self._transitions.append(
            CognitiveTraceAnomalyLifecycleTransition(
                sequence=self._sequence,
                code=code,
                previous_state=previous_state,
                current_state=current_state,
                reason_code=reason_code,
            )
        )
        if len(self._transitions) > self.policy.maximum_transitions:
            self._transitions = self._transitions[-self.policy.maximum_transitions :]

    def _require(self, code: str) -> CognitiveTraceAnomalyLifecycleRecord:
        try:
            return self._records[code]
        except KeyError as exc:
            raise KeyError("unknown anomaly code") from exc

    def _enforce_record_bound(self) -> None:
        overflow = len(self._records) - self.policy.maximum_records
        if overflow <= 0:
            return
        ordered = sorted(
            self._records.values(),
            key=lambda item: (item.state != "resolved", item.priority_score, item.code),
        )
        for record in ordered[:overflow]:
            del self._records[record.code]
