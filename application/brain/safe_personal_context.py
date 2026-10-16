from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from core.personal_identity_and_session_profiles.models import IdentityScope
from core.personal_identity_and_session_profiles.store import IdentityProfileStore
from domain.brain import BrainMemory

from .active_identity import (
    ActiveIdentityRequest,
    ActiveIdentityResolution,
    ActiveIdentityResolver,
    ActiveIdentityStatus,
)
from .service import BrainQuery, BrainService


@dataclass(frozen=True)
class SafePersonalContext:
    """Identity-scoped, read-only context prepared for a future consumer."""

    identity: ActiveIdentityResolution
    memories: tuple[BrainMemory, ...]
    allowed_subjects: tuple[str, ...]
    private_context_enabled: bool


class SafePersonalContextService:
    """Build context without exposing another person's private memories."""

    def __init__(
        self,
        *,
        brain_service: BrainService,
        identity_resolver: ActiveIdentityResolver,
        identity_profile_store: IdentityProfileStore,
    ) -> None:
        self.brain_service = brain_service
        self.identity_resolver = identity_resolver
        self.identity_profile_store = identity_profile_store

    def build(
        self,
        *,
        identity_request: ActiveIdentityRequest,
        query: BrainQuery | None = None,
        now: datetime | None = None,
    ) -> SafePersonalContext:
        resolution = self.identity_resolver.resolve(identity_request)
        allowed_subjects = self._allowed_subjects(resolution)
        requested = query or BrainQuery()
        memories = self._recall_allowed(
            requested,
            allowed_subjects=allowed_subjects,
            now=now,
        )
        return SafePersonalContext(
            identity=resolution,
            memories=memories,
            allowed_subjects=allowed_subjects,
            private_context_enabled=resolution.may_use_private_preferences,
        )

    def _recall_allowed(
        self,
        query: BrainQuery,
        *,
        allowed_subjects: tuple[str, ...],
        now: datetime | None,
    ) -> tuple[BrainMemory, ...]:
        if not allowed_subjects:
            return ()
        requested_subject = query.subject.strip() if query.subject else None
        subjects = allowed_subjects
        if requested_subject is not None:
            subjects = tuple(
                subject
                for subject in allowed_subjects
                if subject.casefold() == requested_subject.casefold()
            )
        found: dict[str, BrainMemory] = {}
        for subject in subjects:
            scoped_query = replace(query, subject=subject)
            for memory in self.brain_service.recall(scoped_query, now=now):
                found.setdefault(memory.memory_id, memory)
        ordered = sorted(
            found.values(),
            key=lambda item: (item.importance, item.updated_at),
            reverse=True,
        )
        return tuple(ordered[: query.limit])

    def _allowed_subjects(
        self,
        resolution: ActiveIdentityResolution,
    ) -> tuple[str, ...]:
        shared = tuple(
            profile.owner
            for profile in self.identity_profile_store.list_profiles()
            if profile.scope is IdentityScope.SHARED
        )
        if resolution.status is ActiveIdentityStatus.RESOLVED:
            assert resolution.subject is not None
            return tuple(dict.fromkeys((resolution.subject, *shared)))
        if resolution.status is ActiveIdentityStatus.SHARED:
            if resolution.subject is None:
                return tuple(dict.fromkeys(shared))
            return tuple(dict.fromkeys((resolution.subject, *shared)))
        return tuple(dict.fromkeys(shared))
