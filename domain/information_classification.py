from __future__ import annotations

from enum import Enum


class InformationClassification(Enum):
    """Canonical sensitivity vocabulary without access or routing authority."""

    UNCLASSIFIED = "unclassified"
    PUBLIC = "public"
    PERSONAL = "personal"
    PRIVATE = "private"
    SENSITIVE = "sensitive"
