from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .foundation import ConversationOpportunityKind
from .realization import (
    ConversationalAct,
    ConversationalRealization,
    ConversationalRealizationStatus,
)


class ConversationalPresenceStance(str, Enum):
    RESPONSIVE = "responsive"
    ATTENTIVE = "attentive"
    COMPANIONABLE = "companionable"
    REFLECTIVE = "reflective"
    RESTRAINED = "restrained"


class ConversationalTurnRelation(str, Enum):
    DIRECT_REPLY = "direct_reply"
    FOLLOW_UP = "follow_up"
    CONTINUATION = "continuation"
    SPONTANEOUS_ENTRY = "spontaneous_entry"


class ConversationalPresenceStatus(str, Enum):
    READY = "ready"
    ABSTAINED = "abstained"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class ConversationalPresencePolicy:
    maximum_intensity: float = 0.85
    spontaneous_intensity_cap: float = 0.58
    continuation_intensity_floor: float = 0.42
    allow_open_follow_up: bool = True
    require_sources_for_spontaneous_presence: bool = True

    def __post_init__(self) -> None:
        values = (
            self.maximum_intensity,
            self.spontaneous_intensity_cap,
            self.continuation_intensity_floor,
        )
        if any(not 0.0 <= value <= 1.0 for value in values):
            raise ValueError(
                "conversational presence intensity must be between 0 and 1"
            )
        if self.spontaneous_intensity_cap > self.maximum_intensity:
            raise ValueError(
                "spontaneous intensity cap cannot exceed maximum intensity"
            )
        if self.continuation_intensity_floor > self.maximum_intensity:
            raise ValueError(
                "continuation intensity floor cannot exceed maximum intensity"
            )


@dataclass(frozen=True)
class ConversationalPresenceRequest:
    realization: ConversationalRealization
    owner: str
    prior_exchange_count: int = 0
    user_initiated: bool = False
    continuity_thread_id: str | None = None
    permit_follow_up: bool = True
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("conversational presence owner must not be blank")
        governed_owner = (
            self.realization.request.contribution.request.governance.context.owner
        )
        if self.owner.casefold() != governed_owner.casefold():
            raise ValueError("conversational presence owner must match governed owner")
        if self.prior_exchange_count < 0:
            raise ValueError("prior exchange count cannot be negative")
        if (
            self.continuity_thread_id is not None
            and not self.continuity_thread_id.strip()
        ):
            raise ValueError("continuity thread id must not be blank")
        if self.requested_at.tzinfo is None:
            raise ValueError("conversational presence request timestamp must be aware")


@dataclass(frozen=True)
class ConversationalPresence:
    request: ConversationalPresenceRequest
    status: ConversationalPresenceStatus | str
    stance: ConversationalPresenceStance | str
    turn_relation: ConversationalTurnRelation | str
    intensity: float
    acknowledge_prior_turn: bool
    keep_follow_up_open: bool
    continuity_thread_id: str | None
    source_reference_ids: tuple[str, ...]
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    presence_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ConversationalPresenceStatus(self.status))
        object.__setattr__(self, "stance", ConversationalPresenceStance(self.stance))
        object.__setattr__(
            self, "turn_relation", ConversationalTurnRelation(self.turn_relation)
        )
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError(
                "conversational presence intensity must be between 0 and 1"
            )
        if self.created_at.tzinfo is None:
            raise ValueError("conversational presence timestamp must be aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("conversational presence rationale must not be empty")
        if len(set(self.source_reference_ids)) != len(self.source_reference_ids):
            raise ValueError("conversational presence sources must be unique")
        if any(not item.strip() for item in self.source_reference_ids):
            raise ValueError("conversational presence sources must not be blank")
        if (
            self.continuity_thread_id is not None
            and not self.continuity_thread_id.strip()
        ):
            raise ValueError("conversational presence continuity id must not be blank")
        if self.status is not ConversationalPresenceStatus.READY:
            if self.acknowledge_prior_turn or self.keep_follow_up_open:
                raise ValueError("non-ready presence cannot expose engagement signals")
            if self.intensity != 0.0:
                raise ValueError("non-ready presence intensity must be zero")

        expected = sha256(
            "|".join(
                (
                    self.request.realization.realization_id,
                    self.request.owner.casefold(),
                    str(self.request.prior_exchange_count),
                    str(self.request.user_initiated),
                    self.status.value,
                    self.stance.value,
                    self.turn_relation.value,
                    f"{self.intensity:.6f}",
                    str(self.acknowledge_prior_turn),
                    str(self.keep_follow_up_open),
                    self.continuity_thread_id or "",
                    ";".join(self.source_reference_ids),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.presence_id and self.presence_id != expected:
            raise ValueError("conversational presence id is inconsistent")
        object.__setattr__(self, "presence_id", expected)

    @property
    def text(self) -> str | None:
        if self.status is not ConversationalPresenceStatus.READY:
            return None
        return self.request.realization.text


@runtime_checkable
class ConversationalPresenceRepository(Protocol):
    def add(self, presence: ConversationalPresence) -> None: ...

    def get(self, presence_id: str) -> ConversationalPresence | None: ...

    def list_all(self) -> tuple[ConversationalPresence, ...]: ...


class InMemoryConversationalPresenceRepository:
    def __init__(self) -> None:
        self._items: dict[str, ConversationalPresence] = {}

    def add(self, presence: ConversationalPresence) -> None:
        if presence.presence_id in self._items:
            raise ValueError("conversational presence already exists")
        self._items[presence.presence_id] = presence

    def get(self, presence_id: str) -> ConversationalPresence | None:
        return self._items.get(presence_id)

    def list_all(self) -> tuple[ConversationalPresence, ...]:
        return tuple(self._items.values())


class ConversationalPresenceEngine:
    """Adds conversational posture to M99 without delivering or rewriting it."""

    def __init__(
        self,
        *,
        repository: ConversationalPresenceRepository | None = None,
        policy: ConversationalPresencePolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryConversationalPresenceRepository()
        self.policy = policy or ConversationalPresencePolicy()

    @property
    def last_presence(self) -> ConversationalPresence | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def compose(
        self,
        request: ConversationalPresenceRequest,
        *,
        now: datetime | None = None,
    ) -> ConversationalPresence:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversational presence timestamp must be aware")

        status, rationale = self._status(request)
        relation = self._turn_relation(request)
        stance = self._stance(request, relation)
        intensity = 0.0
        acknowledge = False
        follow_up = False

        if status is ConversationalPresenceStatus.READY:
            intensity = self._intensity(request, relation)
            acknowledge = request.user_initiated and request.prior_exchange_count > 0
            follow_up = (
                self.policy.allow_open_follow_up
                and request.permit_follow_up
                and request.realization.act
                in {
                    ConversationalAct.QUESTION,
                    ConversationalAct.CONNECTION,
                    ConversationalAct.CONTINUATION,
                }
            )

        presence = ConversationalPresence(
            request=request,
            status=status,
            stance=stance,
            turn_relation=relation,
            intensity=intensity,
            acknowledge_prior_turn=acknowledge,
            keep_follow_up_open=follow_up,
            continuity_thread_id=request.continuity_thread_id,
            source_reference_ids=request.realization.source_reference_ids,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(presence)
        return presence

    def _status(
        self, request: ConversationalPresenceRequest
    ) -> tuple[ConversationalPresenceStatus, tuple[str, ...]]:
        realization = request.realization
        if realization.status is ConversationalRealizationStatus.REVIEW_REQUIRED:
            return ConversationalPresenceStatus.REVIEW_REQUIRED, (
                "realization_requires_review",
            )
        if realization.status is not ConversationalRealizationStatus.READY:
            return ConversationalPresenceStatus.ABSTAINED, ("realization_is_not_ready",)
        if realization.text is None:
            return ConversationalPresenceStatus.ABSTAINED, ("realization_has_no_text",)
        if (
            not request.user_initiated
            and self.policy.require_sources_for_spontaneous_presence
            and not realization.source_reference_ids
        ):
            return ConversationalPresenceStatus.ABSTAINED, (
                "spontaneous_presence_requires_sources",
            )
        return ConversationalPresenceStatus.READY, ("presence_composed",)

    def _turn_relation(
        self, request: ConversationalPresenceRequest
    ) -> ConversationalTurnRelation:
        kind = (
            request.realization.request.contribution.request.governance.opportunity.kind
        )
        if kind is ConversationOpportunityKind.RESUME or request.continuity_thread_id:
            return ConversationalTurnRelation.CONTINUATION
        if request.user_initiated and request.prior_exchange_count == 0:
            return ConversationalTurnRelation.DIRECT_REPLY
        if request.user_initiated:
            return ConversationalTurnRelation.FOLLOW_UP
        return ConversationalTurnRelation.SPONTANEOUS_ENTRY

    def _stance(
        self,
        request: ConversationalPresenceRequest,
        relation: ConversationalTurnRelation,
    ) -> ConversationalPresenceStance:
        if request.realization.status is not ConversationalRealizationStatus.READY:
            return ConversationalPresenceStance.RESTRAINED
        if relation is ConversationalTurnRelation.DIRECT_REPLY:
            return ConversationalPresenceStance.RESPONSIVE
        if relation is ConversationalTurnRelation.FOLLOW_UP:
            return ConversationalPresenceStance.ATTENTIVE
        if relation is ConversationalTurnRelation.CONTINUATION:
            return ConversationalPresenceStance.COMPANIONABLE
        if request.realization.act in {
            ConversationalAct.OBSERVATION,
            ConversationalAct.CONNECTION,
        }:
            return ConversationalPresenceStance.REFLECTIVE
        return ConversationalPresenceStance.RESTRAINED

    def _intensity(
        self,
        request: ConversationalPresenceRequest,
        relation: ConversationalTurnRelation,
    ) -> float:
        base = {
            ConversationalTurnRelation.DIRECT_REPLY: 0.72,
            ConversationalTurnRelation.FOLLOW_UP: 0.68,
            ConversationalTurnRelation.CONTINUATION: 0.62,
            ConversationalTurnRelation.SPONTANEOUS_ENTRY: 0.50,
        }[relation]
        if request.realization.act is ConversationalAct.QUESTION:
            base += 0.05
        if request.realization.act is ConversationalAct.OBSERVATION:
            base -= 0.04
        if relation is ConversationalTurnRelation.CONTINUATION:
            base = max(base, self.policy.continuation_intensity_floor)
        if relation is ConversationalTurnRelation.SPONTANEOUS_ENTRY:
            base = min(base, self.policy.spontaneous_intensity_cap)
        return round(min(base, self.policy.maximum_intensity), 2)
