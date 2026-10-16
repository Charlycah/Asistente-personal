from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .selection import GovernedMusicSelection, GovernedMusicSelectionStatus


class GovernedMusicPlaybackAuthorizationStatus(StrEnum):
    AUTHORIZED = "authorized"
    DENIED = "denied"


@dataclass(frozen=True)
class GovernedMusicPlaybackAuthorization:
    status: GovernedMusicPlaybackAuthorizationStatus
    entry_id: str | None
    source_reference: str | None
    rationale: str

    @property
    def authorized(self) -> bool:
        return self.status is GovernedMusicPlaybackAuthorizationStatus.AUTHORIZED


class GovernedLocalMusicPlaybackAuthorizationV1:
    """Authorize playback only from explicit human intent plus one valid selection."""

    def authorize(
        self,
        selection: GovernedMusicSelection,
        *,
        explicit_human_request: bool,
    ) -> GovernedMusicPlaybackAuthorization:
        if not explicit_human_request:
            return self._denied("explicit_human_playback_request_required")
        if (
            selection.status is not GovernedMusicSelectionStatus.SELECTED
            or selection.selected is None
        ):
            return self._denied("playback_requires_unique_governed_selection")
        return GovernedMusicPlaybackAuthorization(
            status=GovernedMusicPlaybackAuthorizationStatus.AUTHORIZED,
            entry_id=selection.selected.entry_id,
            source_reference=selection.selected.source_reference,
            rationale="explicit_human_request_plus_unique_governed_selection",
        )

    @staticmethod
    def _denied(rationale: str) -> GovernedMusicPlaybackAuthorization:
        return GovernedMusicPlaybackAuthorization(
            status=GovernedMusicPlaybackAuthorizationStatus.DENIED,
            entry_id=None,
            source_reference=None,
            rationale=rationale,
        )
