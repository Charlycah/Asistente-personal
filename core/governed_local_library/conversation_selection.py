from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .handoff import GovernedLibrarySelection
from .models import GovernedLibraryEntry, GovernedLibrarySearchResult


class GovernedLibrarySelectionDisposition(str, Enum):
    NO_MATCH = "no_match"
    SELECTED = "selected"
    NEEDS_DISAMBIGUATION = "needs_disambiguation"


@dataclass(frozen=True)
class GovernedLibraryConversationalSelectionResult:
    disposition: GovernedLibrarySelectionDisposition
    selection: GovernedLibrarySelection | None
    candidates: tuple[GovernedLibraryEntry, ...]
    bounded: bool


class GovernedLibraryConversationalSelectionV1:
    """Turn one bounded catalogue search into an explicit 0/1/N disposition."""

    def decide_explicit(
        self, *, query: str, entry: GovernedLibraryEntry
    ) -> GovernedLibraryConversationalSelectionResult:
        """Select one canonically resolved path without a catalogue claim."""
        return GovernedLibraryConversationalSelectionResult(
            disposition=GovernedLibrarySelectionDisposition.SELECTED,
            selection=GovernedLibrarySelection(
                query=query,
                entry_id=entry.entry_id,
                source_reference=entry.source_reference,
                explicit_entry_fingerprint=entry.fingerprint,
            ),
            candidates=(),
            bounded=False,
        )

    def decide(
        self,
        search: GovernedLibrarySearchResult,
    ) -> GovernedLibraryConversationalSelectionResult:
        matches = tuple(search.matches)
        if not matches:
            return GovernedLibraryConversationalSelectionResult(
                disposition=GovernedLibrarySelectionDisposition.NO_MATCH,
                selection=None,
                candidates=(),
                bounded=search.bounded,
            )
        if len(matches) == 1:
            entry = matches[0]
            return GovernedLibraryConversationalSelectionResult(
                disposition=GovernedLibrarySelectionDisposition.SELECTED,
                selection=GovernedLibrarySelection(
                    query=search.query,
                    entry_id=entry.entry_id,
                    source_reference=entry.source_reference,
                    catalogue_fingerprint=search.catalogue_fingerprint,
                ),
                candidates=(),
                bounded=search.bounded,
            )
        return GovernedLibraryConversationalSelectionResult(
            disposition=GovernedLibrarySelectionDisposition.NEEDS_DISAMBIGUATION,
            selection=None,
            candidates=matches,
            bounded=search.bounded,
        )
