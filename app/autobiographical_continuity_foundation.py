from __future__ import annotations

from app.contextual_memory_retrieval_foundation import (
    ContextualMemoryRetrievalFoundation,
)
from core.autobiographical_continuity_foundation import (
    AutobiographicalContinuityResult,
    AutobiographicalContinuitySnapshot,
    AutobiographicalDisposition,
    AutobiographicalEntry,
    AutobiographicalMemoryCandidate,
    AutobiographicalMemoryKind,
)


class AutobiographicalContinuityFoundation:
    """Read-only chronological continuity over governed personal memories."""

    SCHEMA_VERSION = "m366.8"
    IDENTITY_AUTHORITY = (
        "core.personal_identity_and_session_profiles:PersonalIdentityProfile"
    )
    RELATIONSHIP_AUTHORITY = "core.relationship_memory:RelationshipMemoryManager"

    def __init__(
        self,
        *,
        retrieval: ContextualMemoryRetrievalFoundation | None = None,
    ) -> None:
        self._retrieval = retrieval or ContextualMemoryRetrievalFoundation()

    @property
    def snapshot(self) -> AutobiographicalContinuitySnapshot:
        retrieval = self._retrieval.snapshot
        return AutobiographicalContinuitySnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=retrieval.canonical_authority,
            identity_authority=self.IDENTITY_AUTHORITY,
            relationship_authority=self.RELATIONSHIP_AUTHORITY,
            retrieval_authority=retrieval.specialized_retrieval,
            supported_kinds=tuple(AutobiographicalMemoryKind),
            read_only=True,
            fabrication_forbidden=True,
            consciousness_claimed=False,
            persistence_added=False,
            automatic_narrative_injection_added=False,
            runtime_behavior_changed=False,
        )

    def compose(
        self,
        subject_id: str,
        candidates: tuple[AutobiographicalMemoryCandidate, ...],
    ) -> AutobiographicalContinuityResult:
        normalized_subject = subject_id.strip()
        if not normalized_subject:
            raise ValueError("subject id must not be blank")
        entries = tuple(self._assess(candidate) for candidate in candidates)
        included = tuple(
            sorted(
                (
                    item
                    for item in entries
                    if item.disposition is AutobiographicalDisposition.INCLUDE
                ),
                key=lambda item: (item.sequence, item.occurred_at, item.memory_id),
            )
        )
        review_ids = tuple(
            item.memory_id
            for item in entries
            if item.disposition is AutobiographicalDisposition.REQUIRE_REVIEW
        )
        return AutobiographicalContinuityResult(
            subject_id=normalized_subject,
            entries=entries,
            included_ids=tuple(item.memory_id for item in included),
            review_ids=review_ids,
        )

    @staticmethod
    def _assess(candidate: AutobiographicalMemoryCandidate) -> AutobiographicalEntry:
        if candidate.archived:
            disposition = AutobiographicalDisposition.EXCLUDE_ARCHIVED
        elif candidate.superseded:
            disposition = AutobiographicalDisposition.EXCLUDE_SUPERSEDED
        elif candidate.disputed:
            disposition = AutobiographicalDisposition.REQUIRE_REVIEW
        else:
            disposition = AutobiographicalDisposition.INCLUDE
        return AutobiographicalEntry(
            memory_id=candidate.memory_id,
            kind=candidate.kind,
            summary=candidate.summary,
            occurred_at=candidate.occurred_at,
            sequence=candidate.sequence,
            disposition=disposition,
            confidence=candidate.confidence,
            user_confirmed=candidate.user_confirmed,
        )
