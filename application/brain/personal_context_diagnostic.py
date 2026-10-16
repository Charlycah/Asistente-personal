from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .active_identity import ActiveIdentityRequest
from .safe_personal_context import SafePersonalContextService
from .service import BrainQuery


@dataclass(frozen=True)
class PersonalContextDiagnosticEntry:
    memory_id: str
    source: str
    subject: str
    memory_type: str
    content: str
    read_only: bool


@dataclass(frozen=True)
class PersonalContextDiagnosticReport:
    identity_status: str
    identity_source: str
    profile_id: str | None
    display_name: str | None
    subject: str | None
    participants: tuple[str, ...]
    confidence: float
    reason: str
    allowed_subjects: tuple[str, ...]
    private_context_enabled: bool
    query: BrainQuery
    entries: tuple[PersonalContextDiagnosticEntry, ...]

    @property
    def total_count(self) -> int:
        return len(self.entries)

    def _query_memory_type(self) -> str | None:
        value = self.query.memory_type
        if value is None:
            return None
        return getattr(value, "value", str(value))

    def to_dict(self) -> dict[str, object]:
        return {
            "identity": {
                "status": self.identity_status,
                "source": self.identity_source,
                "profile_id": self.profile_id,
                "display_name": self.display_name,
                "subject": self.subject,
                "participants": list(self.participants),
                "confidence": self.confidence,
                "reason": self.reason,
            },
            "access": {
                "allowed_subjects": list(self.allowed_subjects),
                "private_context_enabled": self.private_context_enabled,
            },
            "query": {
                "text": self.query.text,
                "memory_type": self._query_memory_type(),
                "subject": self.query.subject,
                "include_expired": self.query.include_expired,
                "limit": self.query.limit,
            },
            "summary": {"total": self.total_count},
            "entries": [
                {
                    "memory_id": entry.memory_id,
                    "source": entry.source,
                    "subject": entry.subject,
                    "memory_type": entry.memory_type,
                    "content": entry.content,
                    "read_only": entry.read_only,
                }
                for entry in self.entries
            ],
        }


class PersonalContextDiagnostic:
    """Inspect identity-scoped context without changing runtime state."""

    def __init__(self, service: SafePersonalContextService) -> None:
        self.service = service

    def inspect(
        self,
        *,
        identity_request: ActiveIdentityRequest,
        query: BrainQuery | None = None,
        now: datetime | None = None,
    ) -> PersonalContextDiagnosticReport:
        requested = query or BrainQuery()
        context = self.service.build(
            identity_request=identity_request,
            query=requested,
            now=now,
        )
        identity = context.identity
        entries = tuple(
            PersonalContextDiagnosticEntry(
                memory_id=memory.memory_id,
                source=memory.source,
                subject=memory.subject,
                memory_type=memory.normalized_type.value,
                content=memory.content,
                read_only=bool(memory.metadata.get("read_only", False)),
            )
            for memory in context.memories
        )
        return PersonalContextDiagnosticReport(
            identity_status=identity.status.value,
            identity_source=identity.source.value,
            profile_id=identity.profile_id,
            display_name=identity.display_name,
            subject=identity.subject,
            participants=identity.participants,
            confidence=identity.confidence,
            reason=identity.reason,
            allowed_subjects=context.allowed_subjects,
            private_context_enabled=context.private_context_enabled,
            query=requested,
            entries=entries,
        )
