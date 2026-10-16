from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .active_identity import ActiveIdentityRequest
from .safe_personal_context import SafePersonalContextService
from .service import BrainQuery


@dataclass(frozen=True)
class ConversationContextItem:
    """Minimal memory projection safe for a future conversation consumer."""

    memory_id: str
    subject: str
    memory_type: str
    text: str
    source: str


@dataclass(frozen=True)
class ConversationContextPackage:
    """Bounded, identity-scoped context prepared but not injected into runtime."""

    identity_status: str
    active_subject: str | None
    allowed_subjects: tuple[str, ...]
    private_context_enabled: bool
    items: tuple[ConversationContextItem, ...]
    omitted_count: int
    character_count: int
    max_items: int
    max_characters: int

    @property
    def is_empty(self) -> bool:
        return not self.items

    def to_dict(self) -> dict[str, object]:
        return {
            "identity": {
                "status": self.identity_status,
                "subject": self.active_subject,
                "allowed_subjects": list(self.allowed_subjects),
                "private_context_enabled": self.private_context_enabled,
            },
            "limits": {
                "max_items": self.max_items,
                "max_characters": self.max_characters,
                "character_count": self.character_count,
                "omitted_count": self.omitted_count,
            },
            "items": [
                {
                    "memory_id": item.memory_id,
                    "subject": item.subject,
                    "memory_type": item.memory_type,
                    "text": item.text,
                    "source": item.source,
                }
                for item in self.items
            ],
        }


class ConversationContextPreparer:
    """Prepare bounded context without changing memories or visible runtime."""

    def __init__(
        self,
        service: SafePersonalContextService,
        *,
        default_max_items: int = 8,
        default_max_characters: int = 1600,
    ) -> None:
        if default_max_items < 1:
            raise ValueError("default_max_items must be positive")
        if default_max_characters < 1:
            raise ValueError("default_max_characters must be positive")
        self.service = service
        self.default_max_items = default_max_items
        self.default_max_characters = default_max_characters

    def prepare(
        self,
        *,
        identity_request: ActiveIdentityRequest,
        query: BrainQuery | None = None,
        max_items: int | None = None,
        max_characters: int | None = None,
        now: datetime | None = None,
    ) -> ConversationContextPackage:
        item_limit = self._positive_limit(
            max_items,
            fallback=self.default_max_items,
            name="max_items",
        )
        character_limit = self._positive_limit(
            max_characters,
            fallback=self.default_max_characters,
            name="max_characters",
        )
        requested = query or BrainQuery()
        expanded_query = BrainQuery(
            text=requested.text,
            memory_type=requested.memory_type,
            subject=requested.subject,
            status=requested.status,
            include_expired=requested.include_expired,
            limit=max(requested.limit, item_limit + 1),
        )
        context = self.service.build(
            identity_request=identity_request,
            query=expanded_query,
            now=now,
        )
        items: list[ConversationContextItem] = []
        character_count = 0
        for memory in context.memories:
            if len(items) >= item_limit:
                break
            text = " ".join(memory.content.split())
            if not text:
                continue
            available = character_limit - character_count
            if available <= 0:
                break
            if len(text) > available:
                if not items:
                    text = text[:available].rstrip()
                else:
                    break
            items.append(
                ConversationContextItem(
                    memory_id=memory.memory_id,
                    subject=memory.subject,
                    memory_type=memory.normalized_type.value,
                    text=text,
                    source=memory.source,
                )
            )
            character_count += len(text)
        omitted_count = max(0, len(context.memories) - len(items))
        return ConversationContextPackage(
            identity_status=context.identity.status.value,
            active_subject=context.identity.subject,
            allowed_subjects=context.allowed_subjects,
            private_context_enabled=context.private_context_enabled,
            items=tuple(items),
            omitted_count=omitted_count,
            character_count=character_count,
            max_items=item_limit,
            max_characters=character_limit,
        )

    @staticmethod
    def _positive_limit(
        value: int | None,
        *,
        fallback: int,
        name: str,
    ) -> int:
        resolved = fallback if value is None else value
        if resolved < 1:
            raise ValueError(f"{name} must be positive")
        return resolved
