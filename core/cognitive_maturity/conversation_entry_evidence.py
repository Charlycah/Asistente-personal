from __future__ import annotations

from dataclasses import dataclass

from .cycle_contract import (
    CanonicalCognitiveCycle,
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
)
from .cycle_observer import CanonicalCognitiveCycleObserver


@dataclass(frozen=True)
class ConversationEntryEvidenceSnapshot:
    cycles: tuple[CanonicalCognitiveCycle, ...]
    active_cycle_ids: tuple[str, ...]
    accepted_turns: int
    retained_cycles: int
    read_only: bool = True
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if self.accepted_turns < 0 or self.retained_cycles < 0:
            raise ValueError("conversation entry evidence counts are invalid")
        if self.retained_cycles != len(self.cycles):
            raise ValueError("conversation entry retained count is inconsistent")
        if len(self.active_cycle_ids) != len(set(self.active_cycle_ids)):
            raise ValueError("conversation entry active cycles must be unique")
        cycle_ids = {cycle.cycle_id for cycle in self.cycles}
        if any(cycle_id not in cycle_ids for cycle_id in self.active_cycle_ids):
            raise ValueError("conversation entry active cycle is not retained")
        if not self.read_only or self.grants_authority:
            raise ValueError("conversation entry evidence must remain advisory")

    @property
    def latest_cycle(self) -> CanonicalCognitiveCycle | None:
        if not self.cycles:
            return None
        return self.cycles[-1]


class ConversationEntryEvidenceAdapter:
    """Translate official gateway acceptance into one canonical node fact."""

    EVIDENCE_CODE = "gateway:accepted"
    NODE_ID = "conversation_ingress"

    def __init__(self, *, max_cycles: int = 100) -> None:
        if max_cycles < 1:
            raise ValueError("conversation entry evidence capacity must be positive")
        self._max_cycles = max_cycles
        self._accepted_turns = 0
        self._active: dict[str, CanonicalCognitiveCycleObserver] = {}
        self._completed: list[CanonicalCognitiveCycle] = []

    def begin(self, cycle_id: str) -> CanonicalCognitiveCycle:
        observer = CanonicalCognitiveCycleObserver(cycle_id)
        normalized_id = observer.cycle_id
        retained_ids = {cycle.cycle_id for cycle in self._completed}
        if normalized_id in self._active or normalized_id in retained_ids:
            raise ValueError("conversation entry cycle already exists")
        observer.observe(
            CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=(self.EVIDENCE_CODE,),
            )
        )
        self._active[normalized_id] = observer
        self._accepted_turns += 1
        return observer.cycle

    def seal(self, cycle_id: str) -> CanonicalCognitiveCycle:
        normalized_id = cycle_id.strip().casefold()
        try:
            observer = self._active.pop(normalized_id)
        except KeyError as exc:
            raise KeyError(cycle_id) from exc
        cycle = observer.seal()
        self._completed.append(cycle)
        if len(self._completed) > self._max_cycles:
            del self._completed[: len(self._completed) - self._max_cycles]
        return cycle

    def observe(
        self,
        cycle_id: str,
        record: CognitiveCycleNodeRecord,
    ) -> CanonicalCognitiveCycle:
        normalized_id = cycle_id.strip().casefold()
        try:
            observer = self._active[normalized_id]
        except KeyError as exc:
            raise KeyError(cycle_id) from exc
        return observer.observe(record)

    @property
    def snapshot(self) -> ConversationEntryEvidenceSnapshot:
        active = tuple(observer.cycle for observer in self._active.values())
        cycles = tuple(self._completed) + active
        return ConversationEntryEvidenceSnapshot(
            cycles=cycles,
            active_cycle_ids=tuple(self._active),
            accepted_turns=self._accepted_turns,
            retained_cycles=len(cycles),
        )
