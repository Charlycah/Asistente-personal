from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .presence import (
    ConversationalPresence,
    ConversationalPresenceStatus,
)


class ConversationalFeedbackSignalKind(str, Enum):
    ACCEPTANCE = "acceptance"
    CORRECTION = "correction"
    CONFUSION = "confusion"
    REJECTION = "rejection"
    DEEPENING = "deepening"
    DISENGAGEMENT = "disengagement"
    NO_SIGNAL = "no_signal"


class ConversationalFeedbackOrigin(str, Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    SYSTEM = "system"


class ConversationalFeedbackStatus(str, Enum):
    ASSESSED = "assessed"
    INSUFFICIENT = "insufficient"
    REVIEW_REQUIRED = "review_required"
    NOT_APPLICABLE = "not_applicable"


class ConversationalAdjustment(str, Enum):
    MAINTAIN = "maintain"
    CLARIFY = "clarify"
    CORRECT = "correct"
    DEEPEN = "deepen"
    REDUCE_INTENSITY = "reduce_intensity"
    CLOSE_FOLLOW_UP = "close_follow_up"
    SEEK_CONFIRMATION = "seek_confirmation"
    NONE = "none"


@dataclass(frozen=True)
class ConversationalFeedbackPolicy:
    minimum_confidence: float = 0.55
    review_threshold: float = 0.45
    implicit_confidence_cap: float = 0.72
    disengagement_intensity_delta: float = -0.20
    confusion_intensity_delta: float = -0.10
    deepening_intensity_delta: float = 0.08

    def __post_init__(self) -> None:
        for value in (
            self.minimum_confidence,
            self.review_threshold,
            self.implicit_confidence_cap,
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError("feedback confidence values must be between 0 and 1")
        for value in (
            self.disengagement_intensity_delta,
            self.confusion_intensity_delta,
            self.deepening_intensity_delta,
        ):
            if not -1.0 <= value <= 1.0:
                raise ValueError("feedback intensity deltas must be between -1 and 1")
        if self.review_threshold > self.minimum_confidence:
            raise ValueError("review threshold cannot exceed minimum confidence")
        if self.implicit_confidence_cap < self.minimum_confidence:
            raise ValueError(
                "implicit confidence cap cannot be below minimum confidence"
            )


@dataclass(frozen=True)
class ConversationalFeedbackSignal:
    kind: ConversationalFeedbackSignalKind | str
    origin: ConversationalFeedbackOrigin | str
    confidence: float
    evidence: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", ConversationalFeedbackSignalKind(self.kind))
        object.__setattr__(self, "origin", ConversationalFeedbackOrigin(self.origin))
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("feedback signal confidence must be between 0 and 1")
        if (
            self.kind is not ConversationalFeedbackSignalKind.NO_SIGNAL
            and not self.evidence.strip()
        ):
            raise ValueError("feedback signal evidence must not be blank")
        if (
            self.kind is ConversationalFeedbackSignalKind.NO_SIGNAL
            and self.evidence.strip()
        ):
            raise ValueError("no-signal feedback cannot carry evidence")


@dataclass(frozen=True)
class ConversationalFeedbackRequest:
    presence: ConversationalPresence
    owner: str
    signals: tuple[ConversationalFeedbackSignal, ...]
    observation_window_seconds: int = 0
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("conversational feedback owner must not be blank")
        if self.owner.casefold() != self.presence.request.owner.casefold():
            raise ValueError("conversational feedback owner must match presence owner")
        if not self.signals:
            raise ValueError("conversational feedback requires at least one signal")
        if self.observation_window_seconds < 0:
            raise ValueError("observation window cannot be negative")
        if self.requested_at.tzinfo is None:
            raise ValueError("conversational feedback request timestamp must be aware")
        no_signal_count = sum(
            signal.kind is ConversationalFeedbackSignalKind.NO_SIGNAL
            for signal in self.signals
        )
        if no_signal_count and len(self.signals) > 1:
            raise ValueError("no-signal feedback must be the only signal")


@dataclass(frozen=True)
class ConversationalFeedbackAssessment:
    request: ConversationalFeedbackRequest
    status: ConversationalFeedbackStatus | str
    dominant_signal: ConversationalFeedbackSignalKind | str
    confidence: float
    adjustments: tuple[ConversationalAdjustment | str, ...]
    recommended_intensity: float
    keep_follow_up_open: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ConversationalFeedbackStatus(self.status))
        object.__setattr__(
            self,
            "dominant_signal",
            ConversationalFeedbackSignalKind(self.dominant_signal),
        )
        normalized = tuple(ConversationalAdjustment(item) for item in self.adjustments)
        object.__setattr__(self, "adjustments", normalized)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("feedback assessment confidence must be between 0 and 1")
        if not 0.0 <= self.recommended_intensity <= 1.0:
            raise ValueError("recommended intensity must be between 0 and 1")
        if not self.adjustments:
            raise ValueError("feedback assessment requires adjustments")
        if len(set(self.adjustments)) != len(self.adjustments):
            raise ValueError("feedback adjustments must be unique")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("feedback rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("feedback assessment timestamp must be aware")
        if self.status in {
            ConversationalFeedbackStatus.NOT_APPLICABLE,
            ConversationalFeedbackStatus.INSUFFICIENT,
        } and self.adjustments != (ConversationalAdjustment.NONE,):
            raise ValueError("non-actionable feedback must use the none adjustment")

        expected = sha256(
            "|".join(
                (
                    self.request.presence.presence_id,
                    self.request.owner.casefold(),
                    self.status.value,
                    self.dominant_signal.value,
                    f"{self.confidence:.6f}",
                    ";".join(item.value for item in self.adjustments),
                    f"{self.recommended_intensity:.6f}",
                    str(self.keep_follow_up_open),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("feedback assessment id is inconsistent")
        object.__setattr__(self, "assessment_id", expected)


@runtime_checkable
class ConversationalFeedbackRepository(Protocol):
    def add(self, assessment: ConversationalFeedbackAssessment) -> None: ...

    def get(self, assessment_id: str) -> ConversationalFeedbackAssessment | None: ...

    def list_all(self) -> tuple[ConversationalFeedbackAssessment, ...]: ...


class InMemoryConversationalFeedbackRepository:
    def __init__(self) -> None:
        self._items: dict[str, ConversationalFeedbackAssessment] = {}

    def add(self, assessment: ConversationalFeedbackAssessment) -> None:
        if assessment.assessment_id in self._items:
            raise ValueError("conversational feedback assessment already exists")
        self._items[assessment.assessment_id] = assessment

    def get(self, assessment_id: str) -> ConversationalFeedbackAssessment | None:
        return self._items.get(assessment_id)

    def list_all(self) -> tuple[ConversationalFeedbackAssessment, ...]:
        return tuple(self._items.values())


class ConversationalFeedbackLoop:
    """Assesses post-presence signals without learning or mutating upstream state."""

    def __init__(
        self,
        *,
        repository: ConversationalFeedbackRepository | None = None,
        policy: ConversationalFeedbackPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryConversationalFeedbackRepository()
        self.policy = policy or ConversationalFeedbackPolicy()

    @property
    def last_assessment(self) -> ConversationalFeedbackAssessment | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def assess(
        self,
        request: ConversationalFeedbackRequest,
        *,
        now: datetime | None = None,
    ) -> ConversationalFeedbackAssessment:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversational feedback timestamp must be aware")

        status, dominant, confidence, rationale = self._classify(request)
        adjustments = self._adjustments(status, dominant)
        intensity = self._recommended_intensity(request, status, dominant)
        keep_open = self._keep_follow_up_open(request, status, dominant)
        assessment = ConversationalFeedbackAssessment(
            request=request,
            status=status,
            dominant_signal=dominant,
            confidence=confidence,
            adjustments=adjustments,
            recommended_intensity=intensity,
            keep_follow_up_open=keep_open,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(assessment)
        return assessment

    def _classify(self, request: ConversationalFeedbackRequest):
        if request.presence.status is not ConversationalPresenceStatus.READY:
            return (
                ConversationalFeedbackStatus.NOT_APPLICABLE,
                ConversationalFeedbackSignalKind.NO_SIGNAL,
                1.0,
                ("presence_is_not_ready",),
            )
        signal = max(request.signals, key=self._effective_confidence)
        confidence = self._effective_confidence(signal)
        if signal.kind is ConversationalFeedbackSignalKind.NO_SIGNAL:
            return (
                ConversationalFeedbackStatus.INSUFFICIENT,
                signal.kind,
                confidence,
                ("no_observable_feedback",),
            )
        if confidence < self.policy.review_threshold:
            return (
                ConversationalFeedbackStatus.INSUFFICIENT,
                signal.kind,
                confidence,
                ("feedback_confidence_too_low",),
            )
        if confidence < self.policy.minimum_confidence:
            return (
                ConversationalFeedbackStatus.REVIEW_REQUIRED,
                signal.kind,
                confidence,
                ("feedback_requires_review",),
            )
        return (
            ConversationalFeedbackStatus.ASSESSED,
            signal.kind,
            confidence,
            ("feedback_assessed",),
        )

    def _effective_confidence(self, signal: ConversationalFeedbackSignal) -> float:
        confidence = signal.confidence
        if signal.origin is ConversationalFeedbackOrigin.IMPLICIT:
            confidence = min(confidence, self.policy.implicit_confidence_cap)
        return round(confidence, 2)

    def _adjustments(self, status, signal):
        if status in {
            ConversationalFeedbackStatus.NOT_APPLICABLE,
            ConversationalFeedbackStatus.INSUFFICIENT,
        }:
            return (ConversationalAdjustment.NONE,)
        mapping = {
            ConversationalFeedbackSignalKind.ACCEPTANCE: (
                ConversationalAdjustment.MAINTAIN,
            ),
            ConversationalFeedbackSignalKind.CORRECTION: (
                ConversationalAdjustment.CORRECT,
                ConversationalAdjustment.SEEK_CONFIRMATION,
            ),
            ConversationalFeedbackSignalKind.CONFUSION: (
                ConversationalAdjustment.CLARIFY,
                ConversationalAdjustment.REDUCE_INTENSITY,
            ),
            ConversationalFeedbackSignalKind.REJECTION: (
                ConversationalAdjustment.CLOSE_FOLLOW_UP,
                ConversationalAdjustment.REDUCE_INTENSITY,
            ),
            ConversationalFeedbackSignalKind.DEEPENING: (
                ConversationalAdjustment.DEEPEN,
            ),
            ConversationalFeedbackSignalKind.DISENGAGEMENT: (
                ConversationalAdjustment.CLOSE_FOLLOW_UP,
                ConversationalAdjustment.REDUCE_INTENSITY,
            ),
            ConversationalFeedbackSignalKind.NO_SIGNAL: (
                ConversationalAdjustment.NONE,
            ),
        }
        return mapping[signal]

    def _recommended_intensity(self, request, status, signal) -> float:
        base = request.presence.intensity
        if status in {
            ConversationalFeedbackStatus.NOT_APPLICABLE,
            ConversationalFeedbackStatus.INSUFFICIENT,
        }:
            return base
        delta = {
            ConversationalFeedbackSignalKind.CONFUSION: (
                self.policy.confusion_intensity_delta
            ),
            ConversationalFeedbackSignalKind.REJECTION: (
                self.policy.disengagement_intensity_delta
            ),
            ConversationalFeedbackSignalKind.DISENGAGEMENT: (
                self.policy.disengagement_intensity_delta
            ),
            ConversationalFeedbackSignalKind.DEEPENING: (
                self.policy.deepening_intensity_delta
            ),
        }.get(signal, 0.0)
        return round(min(1.0, max(0.0, base + delta)), 2)

    def _keep_follow_up_open(self, request, status, signal) -> bool:
        if status is ConversationalFeedbackStatus.NOT_APPLICABLE:
            return False
        if signal in {
            ConversationalFeedbackSignalKind.REJECTION,
            ConversationalFeedbackSignalKind.DISENGAGEMENT,
        }:
            return False
        if signal is ConversationalFeedbackSignalKind.DEEPENING:
            return True
        return request.presence.keep_follow_up_open
