from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.ambient_context_foundation.models import (
    AmbientContext,
    AmbientFoundationStatus,
)
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
)


class ContextRepresentationStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"


class GovernedContextSource(StrEnum):
    COGNITIVE_BLACKBOARD = "unified_cognitive_blackboard"
    AMBIENT_CONTEXT = "ambient_context_foundation"


@dataclass(frozen=True)
class GovernedContextItem:
    context_id: str
    source: GovernedContextSource
    domain: str
    key: str
    value: str
    confidence: float
    observed_at: datetime
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class GovernedContextRepresentation:
    representation_id: str
    status: ContextRepresentationStatus
    items: tuple[GovernedContextItem, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m392.6"
    canonical_authority: str = "internal_world_model"
    read_only: bool = True
    persistence_added: bool = False
    context_inference_added: bool = False
    personal_state_inference_added: bool = False
    location_tracking_added: bool = False
    automation_added: bool = False
    modifies_source_data: bool = False
    grants_authority: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "internal_world_model":
            raise ValueError("context representation must preserve world authority")
        if tuple(sorted(self.items, key=_item_sort_key)) != self.items:
            raise ValueError("context items must use canonical ordering")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.context_inference_added,
                self.personal_state_inference_added,
                self.location_tracking_added,
                self.automation_added,
                self.modifies_source_data,
                self.grants_authority,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("context representation violates governed limits")

    def item(self, context_id: str) -> GovernedContextItem | None:
        return next(
            (item for item in self.items if item.context_id == context_id),
            None,
        )


class GovernedContextRepresentationView:
    """Pure projection of explicit governed context evidence."""

    def build(
        self,
        blackboard_entries: tuple[CognitiveBlackboardEntry, ...] = (),
        *,
        ambient_contexts: tuple[AmbientContext, ...] = (),
    ) -> GovernedContextRepresentation:
        blackboard_items = tuple(
            self._from_blackboard(entry)
            for entry in blackboard_entries
            if entry.kind is CognitiveBlackboardEntryKind.CONTEXT
        )
        ambient_items, ambient_risks = self._ambient_items(ambient_contexts)
        items = tuple(sorted((*blackboard_items, *ambient_items), key=_item_sort_key))
        self._validate_unique_ids(items)
        risks = tuple(sorted(ambient_risks))
        evidence_codes = (
            "authority:internal_world_model",
            "source:unified_cognitive_blackboard",
            "source:ambient_context_foundation",
            "context:explicit_evidence_only",
        )
        fingerprint = _fingerprint(items, risks)
        return GovernedContextRepresentation(
            representation_id=f"context-world-{fingerprint[:16]}",
            status=self._status(items, risks),
            items=items,
            evidence_codes=evidence_codes,
            risk_codes=risks,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _from_blackboard(entry: CognitiveBlackboardEntry) -> GovernedContextItem:
        return GovernedContextItem(
            context_id=f"blackboard:{entry.entry_id}",
            source=GovernedContextSource.COGNITIVE_BLACKBOARD,
            domain=entry.domain.value,
            key=entry.key,
            value=entry.value,
            confidence=entry.confidence,
            observed_at=entry.created_at,
            evidence_refs=(entry.entry_id, *entry.source_reference_ids),
        )

    @staticmethod
    def _ambient_items(
        contexts: tuple[AmbientContext, ...],
    ) -> tuple[tuple[GovernedContextItem, ...], tuple[str, ...]]:
        items: list[GovernedContextItem] = []
        risks: list[str] = []
        for context in contexts:
            if context.status is not AmbientFoundationStatus.READY:
                risks.append(f"ambient_context_not_ready:{context.context_id}")
                continue
            observation = context.request.observation
            if observation is None:
                risks.append(
                    f"ambient_context_missing_observation:{context.context_id}"
                )
                continue
            items.append(
                GovernedContextItem(
                    context_id=f"ambient:{context.context_id}",
                    source=GovernedContextSource.AMBIENT_CONTEXT,
                    domain="environment",
                    key="ambient_observation",
                    value=observation.observation_ref,
                    confidence=observation.confidence,
                    observed_at=observation.observed_at,
                    evidence_refs=(context.context_id, observation.observation_ref),
                )
            )
        return tuple(items), tuple(risks)

    @staticmethod
    def _validate_unique_ids(items: tuple[GovernedContextItem, ...]) -> None:
        ids = tuple(item.context_id for item in items)
        if len(ids) != len(set(ids)):
            raise ValueError("context representation ids must be unique")

    @staticmethod
    def _status(
        items: tuple[GovernedContextItem, ...], risks: tuple[str, ...]
    ) -> ContextRepresentationStatus:
        if risks:
            return ContextRepresentationStatus.REVIEW_REQUIRED
        if not items:
            return ContextRepresentationStatus.EMPTY
        return ContextRepresentationStatus.COMPLETE


def _item_sort_key(item: GovernedContextItem) -> tuple[str, str, str]:
    return (item.observed_at.isoformat(), item.source.value, item.context_id)


def _fingerprint(
    items: tuple[GovernedContextItem, ...], risks: tuple[str, ...]
) -> str:
    payload = "|".join(
        (
            *(
                ":".join(
                    (
                        item.context_id,
                        item.source.value,
                        item.domain,
                        item.key,
                        item.value,
                        f"{item.confidence:.3f}",
                        item.observed_at.isoformat(),
                        ",".join(item.evidence_refs),
                    )
                )
                for item in items
            ),
            *risks,
        )
    )
    return sha256(payload.encode("utf-8")).hexdigest()
