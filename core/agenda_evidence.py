from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgendaEventEvidence:
    """Minimal provider-neutral evidence admitted into Personal Organization."""

    agenda_id: str
    title: str
    source_reference: str

    def __post_init__(self) -> None:
        if not self.agenda_id.strip():
            raise ValueError("agenda evidence id must not be blank")
        if not self.title.strip():
            raise ValueError("agenda evidence title must not be blank")
        if not self.source_reference.strip():
            raise ValueError("agenda evidence source reference must not be blank")
