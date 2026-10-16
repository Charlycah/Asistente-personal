from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from statistics import mean
from typing import Protocol, runtime_checkable

from .feedback import (
    ConversationalFeedbackAssessment,
    ConversationalFeedbackSignalKind,
    ConversationalFeedbackStatus,
)


class ConversationalRhythm(str, Enum):
    BRISK = "brisk"
    STEADY = "steady"
    MEASURED = "measured"
    PAUSED = "paused"
    CLOSING = "closing"


class ConversationalRhythmStatus(str, Enum):
    REGULATED = "regulated"
    REVIEW_REQUIRED = "review_required"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class ConversationalRhythmPolicy:
    brisk_interval_seconds: float = 0.4
    steady_interval_seconds: float = 1.0
    measured_interval_seconds: float = 2.0
    paused_interval_seconds: float = 4.0
    closing_interval_seconds: float = 1.5
    maximum_consecutive_turns: int = 3
    interruption_threshold: int = 2
    long_response_character_threshold: int = 240
    silence_threshold_seconds: float = 20.0

    def __post_init__(self) -> None:
        intervals = (
            self.brisk_interval_seconds,
            self.steady_interval_seconds,
            self.measured_interval_seconds,
            self.paused_interval_seconds,
            self.closing_interval_seconds,
            self.silence_threshold_seconds,
        )
        if any(value < 0 for value in intervals):
            raise ValueError("rhythm intervals cannot be negative")
        if self.maximum_consecutive_turns < 1:
            raise ValueError("maximum consecutive turns must be positive")
        if self.interruption_threshold < 1:
            raise ValueError("interruption threshold must be positive")
        if self.long_response_character_threshold < 1:
            raise ValueError("long response threshold must be positive")


@dataclass(frozen=True)
class ConversationalRhythmRequest:
    feedback: ConversationalFeedbackAssessment
    owner: str
    recent_turn_intervals_seconds: tuple[float, ...] = ()
    consecutive_roby_turns: int = 1
    user_response_characters: int = 0
    interruption_count: int = 0
    silence_seconds: float = 0.0
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("conversational rhythm owner must not be blank")
        if self.owner.casefold() != self.feedback.request.owner.casefold():
            raise ValueError("conversational rhythm owner must match feedback owner")
        if any(value < 0 for value in self.recent_turn_intervals_seconds):
            raise ValueError("recent turn intervals cannot be negative")
        if self.consecutive_roby_turns < 0:
            raise ValueError("consecutive ROBY turns cannot be negative")
        if self.user_response_characters < 0:
            raise ValueError("user response characters cannot be negative")
        if self.interruption_count < 0:
            raise ValueError("interruption count cannot be negative")
        if self.silence_seconds < 0:
            raise ValueError("silence cannot be negative")
        if self.requested_at.tzinfo is None:
            raise ValueError("conversational rhythm request timestamp must be aware")


@dataclass(frozen=True)
class ConversationalRhythmDecision:
    request: ConversationalRhythmRequest
    status: ConversationalRhythmStatus | str
    rhythm: ConversationalRhythm | str
    interval_seconds: float
    maximum_consecutive_turns: int
    allow_follow_up_prompt: bool
    preserve_user_floor: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ConversationalRhythmStatus(self.status))
        object.__setattr__(self, "rhythm", ConversationalRhythm(self.rhythm))
        if self.interval_seconds < 0:
            raise ValueError("rhythm interval cannot be negative")
        if self.maximum_consecutive_turns < 1:
            raise ValueError("maximum consecutive turns must be positive")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("rhythm rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("rhythm decision timestamp must be aware")
        if self.status is ConversationalRhythmStatus.NOT_APPLICABLE:
            if self.allow_follow_up_prompt:
                raise ValueError("non-applicable rhythm cannot allow follow-up prompts")
        expected = sha256(
            "|".join(
                (
                    self.request.feedback.assessment_id,
                    self.request.owner.casefold(),
                    self.status.value,
                    self.rhythm.value,
                    f"{self.interval_seconds:.6f}",
                    str(self.maximum_consecutive_turns),
                    str(self.allow_follow_up_prompt),
                    str(self.preserve_user_floor),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("rhythm decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)


@runtime_checkable
class ConversationalRhythmRepository(Protocol):
    def add(self, decision: ConversationalRhythmDecision) -> None: ...
    def get(self, decision_id: str) -> ConversationalRhythmDecision | None: ...
    def list_all(self) -> tuple[ConversationalRhythmDecision, ...]: ...


class InMemoryConversationalRhythmRepository:
    def __init__(self) -> None:
        self._items: dict[str, ConversationalRhythmDecision] = {}

    def add(self, decision: ConversationalRhythmDecision) -> None:
        if decision.decision_id in self._items:
            raise ValueError("conversational rhythm decision already exists")
        self._items[decision.decision_id] = decision

    def get(self, decision_id: str) -> ConversationalRhythmDecision | None:
        return self._items.get(decision_id)

    def list_all(self) -> tuple[ConversationalRhythmDecision, ...]:
        return tuple(self._items.values())


class ConversationalRhythmRegulator:
    """Regulates cadence after M101 without scheduling or delivering content."""

    def __init__(
        self,
        *,
        repository: ConversationalRhythmRepository | None = None,
        policy: ConversationalRhythmPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryConversationalRhythmRepository()
        self.policy = policy or ConversationalRhythmPolicy()

    @property
    def last_decision(self) -> ConversationalRhythmDecision | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def regulate(
        self, request: ConversationalRhythmRequest, *, now: datetime | None = None
    ) -> ConversationalRhythmDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversational rhythm timestamp must be aware")
        status, rhythm, rationale = self._classify(request)
        interval = self._interval(rhythm, request)
        maximum = self._maximum_turns(request, rhythm)
        allow_prompt = self._allow_prompt(request, status, rhythm, maximum)
        preserve_floor = rhythm in {
            ConversationalRhythm.MEASURED,
            ConversationalRhythm.PAUSED,
            ConversationalRhythm.CLOSING,
        }
        decision = ConversationalRhythmDecision(
            request=request,
            status=status,
            rhythm=rhythm,
            interval_seconds=interval,
            maximum_consecutive_turns=maximum,
            allow_follow_up_prompt=allow_prompt,
            preserve_user_floor=preserve_floor,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(decision)
        return decision

    def _classify(self, request: ConversationalRhythmRequest):
        feedback = request.feedback
        if feedback.status in {
            ConversationalFeedbackStatus.NOT_APPLICABLE,
            ConversationalFeedbackStatus.INSUFFICIENT,
        }:
            return (
                ConversationalRhythmStatus.NOT_APPLICABLE,
                ConversationalRhythm.PAUSED,
                ("feedback_is_not_actionable",),
            )
        if feedback.status is ConversationalFeedbackStatus.REVIEW_REQUIRED:
            return (
                ConversationalRhythmStatus.REVIEW_REQUIRED,
                ConversationalRhythm.MEASURED,
                ("feedback_requires_review",),
            )
        signal = feedback.dominant_signal
        if signal in {
            ConversationalFeedbackSignalKind.REJECTION,
            ConversationalFeedbackSignalKind.DISENGAGEMENT,
        }:
            return (
                ConversationalRhythmStatus.REGULATED,
                ConversationalRhythm.CLOSING,
                ("feedback_requests_conversational_closure",),
            )
        if signal in {
            ConversationalFeedbackSignalKind.CONFUSION,
            ConversationalFeedbackSignalKind.CORRECTION,
        }:
            return (
                ConversationalRhythmStatus.REGULATED,
                ConversationalRhythm.MEASURED,
                ("feedback_requires_space_and_precision",),
            )
        if request.interruption_count >= self.policy.interruption_threshold:
            return (
                ConversationalRhythmStatus.REGULATED,
                ConversationalRhythm.PAUSED,
                ("repeated_interruptions_require_space",),
            )
        if request.silence_seconds >= self.policy.silence_threshold_seconds:
            return (
                ConversationalRhythmStatus.REGULATED,
                ConversationalRhythm.PAUSED,
                ("extended_silence_requires_space",),
            )
        if (
            request.user_response_characters
            >= self.policy.long_response_character_threshold
        ):
            return (
                ConversationalRhythmStatus.REGULATED,
                ConversationalRhythm.MEASURED,
                ("long_user_response_requires_room",),
            )
        if signal is ConversationalFeedbackSignalKind.DEEPENING:
            return (
                ConversationalRhythmStatus.REGULATED,
                ConversationalRhythm.BRISK,
                ("deepening_supports_fluid_exchange",),
            )
        return (
            ConversationalRhythmStatus.REGULATED,
            ConversationalRhythm.STEADY,
            ("stable_exchange_uses_steady_rhythm",),
        )

    def _interval(
        self, rhythm: ConversationalRhythm, request: ConversationalRhythmRequest
    ) -> float:
        base = {
            ConversationalRhythm.BRISK: self.policy.brisk_interval_seconds,
            ConversationalRhythm.STEADY: self.policy.steady_interval_seconds,
            ConversationalRhythm.MEASURED: self.policy.measured_interval_seconds,
            ConversationalRhythm.PAUSED: self.policy.paused_interval_seconds,
            ConversationalRhythm.CLOSING: self.policy.closing_interval_seconds,
        }[rhythm]
        if request.recent_turn_intervals_seconds:
            observed = mean(request.recent_turn_intervals_seconds)
            if rhythm in {ConversationalRhythm.BRISK, ConversationalRhythm.STEADY}:
                base = max(base, min(observed, self.policy.measured_interval_seconds))
        return round(base, 2)

    def _maximum_turns(
        self, request: ConversationalRhythmRequest, rhythm: ConversationalRhythm
    ) -> int:
        if rhythm in {ConversationalRhythm.PAUSED, ConversationalRhythm.CLOSING}:
            return 1
        if rhythm is ConversationalRhythm.MEASURED:
            return min(2, self.policy.maximum_consecutive_turns)
        return self.policy.maximum_consecutive_turns

    def _allow_prompt(self, request, status, rhythm, maximum) -> bool:
        if status is ConversationalRhythmStatus.NOT_APPLICABLE:
            return False
        if rhythm in {ConversationalRhythm.PAUSED, ConversationalRhythm.CLOSING}:
            return False
        if request.consecutive_roby_turns >= maximum:
            return False
        return request.feedback.keep_follow_up_open
