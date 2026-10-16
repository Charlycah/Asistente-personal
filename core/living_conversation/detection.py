from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Iterable, Protocol, runtime_checkable

from .foundation import (
    ConversationOpportunity,
    ConversationOpportunityKind,
    LivingConversationContext,
)


class ConversationSignalKind(str, Enum):
    USER_TURN = "user_turn"
    UNFINISHED_TOPIC = "unfinished_topic"
    MEMORY_CONNECTION = "memory_connection"
    REFLECTION_READY = "reflection_ready"
    NEW_KNOWLEDGE = "new_knowledge"
    ROUTINE_TRANSITION = "routine_transition"
    SHARED_INTEREST = "shared_interest"
    CONTEXT_CHANGE = "context_change"
    EXTERNAL_EVENT = "external_event"


class ConversationSignalSensitivity(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class ConversationSignal:
    kind: ConversationSignalKind | str
    summary: str
    source_id: str
    relevance: float
    novelty: float
    confidence: float
    occurred_at: datetime
    topic: str | None = None
    content_hint: str | None = None
    sensitivity: ConversationSignalSensitivity | str = (
        ConversationSignalSensitivity.PERSONAL
    )
    requires_review: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", ConversationSignalKind(self.kind))
        object.__setattr__(
            self, "sensitivity", ConversationSignalSensitivity(self.sensitivity)
        )
        if not self.summary.strip():
            raise ValueError("conversation signal summary must not be blank")
        if not self.source_id.strip():
            raise ValueError("conversation signal source id must not be blank")
        for name, value in (
            ("relevance", self.relevance),
            ("novelty", self.novelty),
            ("confidence", self.confidence),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"conversation signal {name} must be between 0 and 1")
        if self.occurred_at.tzinfo is None:
            raise ValueError("conversation signal timestamp must be timezone-aware")
        if self.topic is not None and not self.topic.strip():
            raise ValueError("conversation signal topic must not be blank")
        if self.content_hint is not None and not self.content_hint.strip():
            raise ValueError("conversation signal content hint must not be blank")

    @property
    def fingerprint(self) -> str:
        return sha256(
            "|".join(
                (
                    self.kind.value,
                    self.source_id,
                    self.topic or "",
                    self.summary,
                    self.occurred_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()


@dataclass(frozen=True)
class OpportunityDetectionPolicy:
    minimum_relevance: float = 0.45
    minimum_confidence: float = 0.55
    minimum_novelty: float = 0.25
    maximum_signal_age_seconds: int = 7 * 24 * 60 * 60
    maximum_opportunities: int = 8

    def __post_init__(self) -> None:
        for name, value in (
            ("minimum_relevance", self.minimum_relevance),
            ("minimum_confidence", self.minimum_confidence),
            ("minimum_novelty", self.minimum_novelty),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"detection policy {name} must be between 0 and 1")
        if self.maximum_signal_age_seconds <= 0:
            raise ValueError("maximum signal age must be positive")
        if self.maximum_opportunities <= 0:
            raise ValueError("maximum opportunities must be positive")


@dataclass(frozen=True)
class OpportunityDetectionRecord:
    context: LivingConversationContext
    accepted_signal_ids: tuple[str, ...]
    rejected_signal_reasons: tuple[tuple[str, str], ...]
    opportunities: tuple[ConversationOpportunity, ...]
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    detection_id: str = ""

    def __post_init__(self) -> None:
        if self.detected_at.tzinfo is None:
            raise ValueError("opportunity detection timestamp must be timezone-aware")
        if len(set(self.accepted_signal_ids)) != len(self.accepted_signal_ids):
            raise ValueError("accepted signal ids must be unique")
        rejected_ids = tuple(item[0] for item in self.rejected_signal_reasons)
        if len(set(rejected_ids)) != len(rejected_ids):
            raise ValueError("rejected signal ids must be unique")
        if set(self.accepted_signal_ids).intersection(rejected_ids):
            raise ValueError("a signal cannot be both accepted and rejected")
        expected = sha256(
            "|".join(
                (
                    self.context.owner,
                    self.detected_at.isoformat(),
                    ";".join(self.accepted_signal_ids),
                    ";".join(
                        f"{key}:{value}" for key, value in self.rejected_signal_reasons
                    ),
                    ";".join(
                        f"{item.kind.value}:{item.score:.6f}:{item.reason}"
                        for item in self.opportunities
                    ),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.detection_id and self.detection_id != expected:
            raise ValueError("opportunity detection id is inconsistent")
        object.__setattr__(self, "detection_id", expected)


@runtime_checkable
class OpportunityDetectionRepository(Protocol):
    def add(self, record: OpportunityDetectionRecord) -> None: ...

    def get(self, detection_id: str) -> OpportunityDetectionRecord | None: ...

    def list_all(self) -> tuple[OpportunityDetectionRecord, ...]: ...


class InMemoryOpportunityDetectionRepository:
    def __init__(self) -> None:
        self._records: dict[str, OpportunityDetectionRecord] = {}

    def add(self, record: OpportunityDetectionRecord) -> None:
        if record.detection_id in self._records:
            raise ValueError("opportunity detection record already exists")
        self._records[record.detection_id] = record

    def get(self, detection_id: str) -> OpportunityDetectionRecord | None:
        return self._records.get(detection_id)

    def list_all(self) -> tuple[OpportunityDetectionRecord, ...]:
        return tuple(self._records.values())


class ConversationalOpportunityDetector:
    """Deterministically converts governed signals into M93 opportunities.

    It does not decide whether ROBY should intervene, generate language, invoke a
    tool, mutate memory, or schedule future conversation.
    """

    _KIND_MAP = {
        ConversationSignalKind.USER_TURN: ConversationOpportunityKind.RESPOND,
        ConversationSignalKind.UNFINISHED_TOPIC: ConversationOpportunityKind.RESUME,
        ConversationSignalKind.MEMORY_CONNECTION: ConversationOpportunityKind.REFLECT,
        ConversationSignalKind.REFLECTION_READY: ConversationOpportunityKind.REFLECT,
        ConversationSignalKind.NEW_KNOWLEDGE: ConversationOpportunityKind.SHARE,
        ConversationSignalKind.ROUTINE_TRANSITION: ConversationOpportunityKind.ASK,
        ConversationSignalKind.SHARED_INTEREST: ConversationOpportunityKind.SHARE,
        ConversationSignalKind.CONTEXT_CHANGE: ConversationOpportunityKind.ASK,
        ConversationSignalKind.EXTERNAL_EVENT: ConversationOpportunityKind.SHARE,
    }

    def __init__(
        self,
        *,
        repository: OpportunityDetectionRepository | None = None,
        policy: OpportunityDetectionPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryOpportunityDetectionRepository()
        self.policy = policy or OpportunityDetectionPolicy()

    @property
    def last_detection(self) -> OpportunityDetectionRecord | None:
        records = self.repository.list_all()
        return records[-1] if records else None

    def detect(
        self,
        context: LivingConversationContext,
        signals: Iterable[ConversationSignal],
        *,
        now: datetime | None = None,
    ) -> OpportunityDetectionRecord:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("opportunity detection timestamp must be timezone-aware")

        unique: dict[str, ConversationSignal] = {}
        rejected: dict[str, str] = {}
        for signal in signals:
            if signal.source_id in unique:
                rejected[f"{signal.source_id}#duplicate"] = "duplicate_source_id"
                continue
            unique[signal.source_id] = signal

        accepted: list[ConversationSignal] = []
        for signal in unique.values():
            reason = self._rejection_reason(context, signal, timestamp)
            if reason is None:
                accepted.append(signal)
            else:
                rejected[signal.source_id] = reason

        accepted.sort(key=self._signal_rank, reverse=True)
        opportunities = tuple(
            self._to_opportunity(signal)
            for signal in accepted[: self.policy.maximum_opportunities]
        )
        for signal in accepted[self.policy.maximum_opportunities :]:
            rejected[signal.source_id] = "opportunity_capacity_reached"

        accepted_ids = tuple(
            signal.source_id for signal in accepted[: self.policy.maximum_opportunities]
        )
        record = OpportunityDetectionRecord(
            context=context,
            accepted_signal_ids=accepted_ids,
            rejected_signal_reasons=tuple(sorted(rejected.items())),
            opportunities=opportunities,
            detected_at=timestamp,
        )
        self.repository.add(record)
        return record

    def _rejection_reason(
        self,
        context: LivingConversationContext,
        signal: ConversationSignal,
        now: datetime,
    ) -> str | None:
        age = (now - signal.occurred_at).total_seconds()
        if age < 0:
            return "signal_is_from_the_future"
        if age > self.policy.maximum_signal_age_seconds:
            return "signal_is_stale"
        if signal.relevance < self.policy.minimum_relevance:
            return "relevance_below_detection_minimum"
        if signal.confidence < self.policy.minimum_confidence:
            return "confidence_below_detection_minimum"
        if signal.novelty < self.policy.minimum_novelty:
            return "novelty_below_detection_minimum"
        if (
            context.guests_present
            and signal.sensitivity is not ConversationSignalSensitivity.PUBLIC
        ):
            return "guest_context_blocks_non_public_signal"
        if (
            context.sensitive_context
            and signal.sensitivity is ConversationSignalSensitivity.SENSITIVE
        ):
            return "sensitive_signal_requires_separate_review"
        return None

    @staticmethod
    def _signal_rank(
        signal: ConversationSignal,
    ) -> tuple[float, float, float, float, str]:
        explicit_turn = 1.0 if signal.kind is ConversationSignalKind.USER_TURN else 0.0
        return (
            explicit_turn,
            signal.relevance,
            signal.novelty,
            signal.confidence,
            signal.source_id,
        )

    def _to_opportunity(self, signal: ConversationSignal) -> ConversationOpportunity:
        value = round(signal.relevance * 0.60 + signal.novelty * 0.40, 6)
        return ConversationOpportunity(
            kind=self._KIND_MAP[signal.kind],
            reason=f"detected_from_{signal.kind.value}: {signal.summary}",
            value_score=value,
            relevance_score=signal.relevance,
            confidence=signal.confidence,
            content_hint=signal.content_hint,
            source_reference_ids=(signal.source_id,),
            requires_review=(
                signal.requires_review
                or signal.sensitivity is ConversationSignalSensitivity.SENSITIVE
            ),
        )

    @staticmethod
    def system_prompt_lines() -> tuple[str, ...]:
        return (
            "Conversational Opportunity Detection M94:",
            "- Detectar una oportunidad no autoriza una intervención.",
            "- Toda oportunidad conserva procedencia, confianza y sensibilidad.",
            "- Invitados y privacidad limitan qué señales pueden convertirse "
            "en candidatos.",
            "- M94 no genera lenguaje, no decide timing y no ejecuta acciones.",
        )
