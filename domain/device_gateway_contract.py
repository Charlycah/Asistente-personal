from __future__ import annotations

from typing import Protocol


class RegisteredDeviceLookup(Protocol):
    """Neutral lookup contract required by governed device activation policies."""

    def get(self, device_id: str) -> object | None:
        """Return a registered device representation, or None when unknown."""
