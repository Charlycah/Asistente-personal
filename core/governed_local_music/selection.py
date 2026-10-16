from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .catalogue import GovernedLocalMusicCatalogueV1
from .models import GovernedMusicEntry


class GovernedMusicSelectionStatus(StrEnum):
    SELECTED = "selected"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class GovernedMusicSelection:
    query: str
    status: GovernedMusicSelectionStatus
    selected: GovernedMusicEntry | None
    candidates: tuple[GovernedMusicEntry, ...]
    rationale: str
    playback_authorized: bool = False


class GovernedLocalMusicSelectionV1:
    """Pure selection authority over the existing read-only music catalogue."""

    def __init__(self, catalogue: GovernedLocalMusicCatalogueV1) -> None:
        self.catalogue = catalogue

    def select(self, query: str) -> GovernedMusicSelection:
        normalized = query.strip()
        if not normalized:
            raise ValueError("music selection query must not be blank")

        result = self.catalogue.search(normalized, max_results=10)
        if not result.matches:
            return GovernedMusicSelection(
                query=normalized,
                status=GovernedMusicSelectionStatus.NOT_FOUND,
                selected=None,
                candidates=(),
                rationale="no_catalogue_match",
            )

        exact = tuple(
            item
            for item in result.matches
            if normalized.casefold()
            in {item.filename.casefold(), item.title_hint.casefold()}
        )
        if len(exact) == 1:
            return self._selected(normalized, exact[0], "unique_exact_match")
        if len(exact) > 1:
            return self._ambiguous(normalized, exact, "multiple_exact_matches")
        if len(result.matches) == 1 and not result.bounded:
            return self._selected(
                normalized,
                result.matches[0],
                "unique_bounded_catalogue_match",
            )
        return self._ambiguous(
            normalized,
            result.matches,
            "multiple_catalogue_matches_require_human_disambiguation",
        )

    @staticmethod
    def _selected(
        query: str,
        entry: GovernedMusicEntry,
        rationale: str,
    ) -> GovernedMusicSelection:
        return GovernedMusicSelection(
            query=query,
            status=GovernedMusicSelectionStatus.SELECTED,
            selected=entry,
            candidates=(entry,),
            rationale=rationale,
        )

    @staticmethod
    def _ambiguous(
        query: str,
        candidates: tuple[GovernedMusicEntry, ...],
        rationale: str,
    ) -> GovernedMusicSelection:
        return GovernedMusicSelection(
            query=query,
            status=GovernedMusicSelectionStatus.AMBIGUOUS,
            selected=None,
            candidates=candidates,
            rationale=rationale,
        )
