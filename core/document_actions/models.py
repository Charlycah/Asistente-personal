from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.document_extraction import StructuredDocument
from core.document_intelligence import DocumentIntelligence


class DocumentActionType(str, Enum):
    CREATE_REMINDER = "create_reminder"
    SAVE_SUMMARY = "save_summary"
    OPEN_SOURCE = "open_source"


@dataclass(frozen=True)
class DocumentActionProposal:
    action_type: DocumentActionType
    title: str
    payload: dict[str, str]
    requires_confirmation: bool = True

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("document action title is required")
        if not self.payload:
            raise ValueError("document action payload is required")
        if not self.requires_confirmation:
            raise ValueError("document actions must require confirmation")


@dataclass(frozen=True)
class DocumentActionRequest:
    document: StructuredDocument
    intelligence: DocumentIntelligence
    action_type: DocumentActionType
    explicit_user_consent: bool = False
    user_confirmed: bool = False
    source_url: str | None = None


@dataclass(frozen=True)
class DocumentActionResult:
    action_type: DocumentActionType
    status: str
    capability_name: str
    output: dict[str, object]

    def __post_init__(self) -> None:
        if self.status not in {"prepared", "executed"}:
            raise ValueError("document action status must be prepared or executed")
        if not self.capability_name.strip():
            raise ValueError("document action capability is required")
