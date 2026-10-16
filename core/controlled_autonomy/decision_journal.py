from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .contracts import DecisionJournal, DecisionJournalEntry


@dataclass(frozen=True)
class JournalSnapshot:
    """Immutable point-in-time view of an append-only decision journal."""

    entries: tuple[DecisionJournalEntry, ...]

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def is_empty(self) -> bool:
        return not self.entries


class InMemoryDecisionJournal:
    """Deterministic append-only journal with auditable lookup operations."""

    def __init__(
        self,
        entries: Iterable[DecisionJournalEntry] = (),
    ) -> None:
        self._entries: list[DecisionJournalEntry] = []
        self._journal_ids: set[str] = set()
        self._decision_ids: set[str] = set()
        self._outcome_ids: set[str] = set()
        for entry in entries:
            self.append(entry)

    def append(self, entry: DecisionJournalEntry) -> None:
        """Append one unique, already validated audit entry."""

        if entry.journal_id in self._journal_ids:
            raise ValueError("journal id is already recorded")
        if entry.decision.decision_id in self._decision_ids:
            raise ValueError("decision id is already recorded")
        if entry.outcome is not None:
            if entry.outcome.outcome_id in self._outcome_ids:
                raise ValueError("outcome id is already recorded")
        self._entries.append(entry)
        self._journal_ids.add(entry.journal_id)
        self._decision_ids.add(entry.decision.decision_id)
        if entry.outcome is not None:
            self._outcome_ids.add(entry.outcome.outcome_id)

    def entries(self) -> tuple[DecisionJournalEntry, ...]:
        """Return an immutable insertion-ordered journal snapshot."""

        return tuple(self._entries)

    def snapshot(self) -> JournalSnapshot:
        return JournalSnapshot(entries=self.entries())

    def by_journal_id(self, journal_id: str) -> DecisionJournalEntry | None:
        _require_text(journal_id, "journal id")
        return _first_matching(
            self._entries,
            lambda entry: entry.journal_id == journal_id,
        )

    def by_decision_id(self, decision_id: str) -> DecisionJournalEntry | None:
        _require_text(decision_id, "decision id")
        return _first_matching(
            self._entries,
            lambda entry: entry.decision.decision_id == decision_id,
        )

    def by_outcome_id(self, outcome_id: str) -> DecisionJournalEntry | None:
        _require_text(outcome_id, "outcome id")
        return _first_matching(
            self._entries,
            lambda entry: (
                entry.outcome is not None
                and entry.outcome.outcome_id == outcome_id
            ),
        )

    def for_situation(self, situation_id: str) -> tuple[DecisionJournalEntry, ...]:
        _require_text(situation_id, "situation id")
        return tuple(
            entry
            for entry in self._entries
            if entry.situation.situation_id == situation_id
        )

    def for_candidate(self, candidate_id: str) -> tuple[DecisionJournalEntry, ...]:
        _require_text(candidate_id, "candidate id")
        return tuple(
            entry
            for entry in self._entries
            if any(
                candidate.candidate_id == candidate_id
                for candidate in entry.candidates
            )
        )

    def completed(self) -> tuple[DecisionJournalEntry, ...]:
        return tuple(entry for entry in self._entries if entry.outcome is not None)

    def pending(self) -> tuple[DecisionJournalEntry, ...]:
        return tuple(entry for entry in self._entries if entry.outcome is None)


def _first_matching(
    entries: list[DecisionJournalEntry],
    predicate: Callable[[DecisionJournalEntry], bool],
) -> DecisionJournalEntry | None:
    for entry in entries:
        if predicate(entry):
            return entry
    return None


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank")


__all__ = [
    "DecisionJournal",
    "InMemoryDecisionJournal",
    "JournalSnapshot",
]
