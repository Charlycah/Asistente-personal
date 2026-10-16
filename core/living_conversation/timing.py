from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .foundation import (
    ConversationOpportunity,
    ConversationOpportunityKind,
    LivingConversationContext,
)


class ConversationActivityState(str, Enum):
    AVAILABLE = "available"
    IDLE = "idle"
    FOCUSED = "focused"
    BUSY = "busy"
    SLEEPING = "sleeping"
    UNKNOWN = "unknown"


class TimingRecommendation(str, Enum):
    INTERVENE_NOW = "intervene_now"
    DEFER = "defer"
    WAIT_FOR_PRIVATE_CONTEXT = "wait_for_private_context"
    REVIEW_REQUIRED = "review_required"
    CANCEL = "cancel"


@dataclass(frozen=True)
class ConversationTimingContext:
    conversation: LivingConversationContext
    activity: ConversationActivityState | str = ConversationActivityState.UNKNOWN
    cognitive_load: float = 0.5
    local_hour: int = 12
    spontaneous_interventions_today: int = 0
    last_spontaneous_intervention_at: datetime | None = None
    quiet_until: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "activity", ConversationActivityState(self.activity))
        if not 0.0 <= self.cognitive_load <= 1.0:
            raise ValueError(
                "conversation timing cognitive load must be between 0 and 1"
            )
        if not 0 <= self.local_hour <= 23:
            raise ValueError("conversation timing local hour must be between 0 and 23")
        if self.spontaneous_interventions_today < 0:
            raise ValueError("spontaneous intervention count cannot be negative")
        for timestamp in (
            self.last_spontaneous_intervention_at,
            self.quiet_until,
        ):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError(
                    "conversation timing timestamps must be timezone-aware"
                )


@dataclass(frozen=True)
class ConversationTimingPolicy:
    maximum_cognitive_load: float = 0.72
    maximum_spontaneous_interventions_per_day: int = 4
    minimum_spontaneous_interval_seconds: int = 45 * 60
    default_deferral_seconds: int = 30 * 60
    quiet_hours_start: int = 22
    quiet_hours_end: int = 8
    opportunity_lifetime_seconds: int = 24 * 60 * 60

    def __post_init__(self) -> None:
        if not 0.0 <= self.maximum_cognitive_load <= 1.0:
            raise ValueError("maximum cognitive load must be between 0 and 1")
        if self.maximum_spontaneous_interventions_per_day <= 0:
            raise ValueError("daily spontaneous intervention limit must be positive")
        for name, value in (
            ("minimum spontaneous interval", self.minimum_spontaneous_interval_seconds),
            ("default deferral", self.default_deferral_seconds),
            ("opportunity lifetime", self.opportunity_lifetime_seconds),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if not 0 <= self.quiet_hours_start <= 23:
            raise ValueError("quiet hours start must be between 0 and 23")
        if not 0 <= self.quiet_hours_end <= 23:
            raise ValueError("quiet hours end must be between 0 and 23")
        if self.quiet_hours_start == self.quiet_hours_end:
            raise ValueError("quiet hours cannot cover the entire day")


@dataclass(frozen=True)
class ConversationTimingDecision:
    context: ConversationTimingContext
    opportunity: ConversationOpportunity
    recommendation: TimingRecommendation | str
    rationale: tuple[str, ...]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    earliest_at: datetime | None = None
    expires_at: datetime | None = None
    timing_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "recommendation", TimingRecommendation(self.recommendation)
        )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("conversation timing rationale must not be empty")
        for timestamp in (self.evaluated_at, self.earliest_at, self.expires_at):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError(
                    "conversation timing decision timestamps must be aware"
                )
        if self.earliest_at is not None and self.earliest_at < self.evaluated_at:
            raise ValueError("earliest conversation time cannot be in the past")
        if self.expires_at is not None and self.expires_at <= self.evaluated_at:
            raise ValueError("conversation timing expiry must be after evaluation")
        if (
            self.earliest_at is not None
            and self.expires_at is not None
            and self.earliest_at >= self.expires_at
        ):
            raise ValueError("earliest conversation time must precede expiry")
        expected = sha256(
            "|".join(
                (
                    self.context.conversation.owner,
                    self.opportunity.kind.value,
                    f"{self.opportunity.score:.6f}",
                    self.recommendation.value,
                    ";".join(self.rationale),
                    self.evaluated_at.isoformat(),
                    self.earliest_at.isoformat() if self.earliest_at else "",
                    self.expires_at.isoformat() if self.expires_at else "",
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.timing_id and self.timing_id != expected:
            raise ValueError("conversation timing id is inconsistent")
        object.__setattr__(self, "timing_id", expected)


@runtime_checkable
class ConversationTimingRepository(Protocol):
    def add(self, decision: ConversationTimingDecision) -> None: ...

    def get(self, timing_id: str) -> ConversationTimingDecision | None: ...

    def list_all(self) -> tuple[ConversationTimingDecision, ...]: ...


class InMemoryConversationTimingRepository:
    def __init__(self) -> None:
        self._decisions: dict[str, ConversationTimingDecision] = {}

    def add(self, decision: ConversationTimingDecision) -> None:
        if decision.timing_id in self._decisions:
            raise ValueError("conversation timing decision already exists")
        self._decisions[decision.timing_id] = decision

    def get(self, timing_id: str) -> ConversationTimingDecision | None:
        return self._decisions.get(timing_id)

    def list_all(self) -> tuple[ConversationTimingDecision, ...]:
        return tuple(self._decisions.values())


class ConversationTimingEngine:
    """Produces a governed timing recommendation without scheduling or speaking."""

    _BLOCKING_ACTIVITY = {
        ConversationActivityState.FOCUSED,
        ConversationActivityState.BUSY,
        ConversationActivityState.SLEEPING,
    }

    def __init__(
        self,
        *,
        repository: ConversationTimingRepository | None = None,
        policy: ConversationTimingPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryConversationTimingRepository()
        self.policy = policy or ConversationTimingPolicy()

    @property
    def last_decision(self) -> ConversationTimingDecision | None:
        decisions = self.repository.list_all()
        return decisions[-1] if decisions else None

    def evaluate(
        self,
        context: ConversationTimingContext,
        opportunity: ConversationOpportunity,
        *,
        now: datetime | None = None,
    ) -> ConversationTimingDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversation timing evaluation timestamp must be aware")

        recommendation, rationale, earliest = self._recommend(
            context, opportunity, timestamp
        )
        expires = timestamp + timedelta(
            seconds=self.policy.opportunity_lifetime_seconds
        )
        if earliest is not None and earliest >= expires:
            recommendation = TimingRecommendation.CANCEL
            rationale = ("recommended_window_exceeds_opportunity_lifetime",)
            earliest = None

        decision = ConversationTimingDecision(
            context=context,
            opportunity=opportunity,
            recommendation=recommendation,
            rationale=rationale,
            evaluated_at=timestamp,
            earliest_at=earliest,
            expires_at=expires,
        )
        self.repository.add(decision)
        return decision

    def _recommend(
        self,
        context: ConversationTimingContext,
        opportunity: ConversationOpportunity,
        now: datetime,
    ) -> tuple[TimingRecommendation, tuple[str, ...], datetime | None]:
        conversation = context.conversation
        explicit_response = (
            conversation.explicit_user_turn
            or opportunity.kind is ConversationOpportunityKind.RESPOND
        )

        if opportunity.requires_review:
            return (
                TimingRecommendation.REVIEW_REQUIRED,
                ("opportunity_requires_review_before_timing",),
                None,
            )
        if conversation.sensitive_context:
            return (
                TimingRecommendation.WAIT_FOR_PRIVATE_CONTEXT,
                ("sensitive_context_requires_private_window",),
                now + timedelta(seconds=self.policy.default_deferral_seconds),
            )
        if conversation.guests_present and not explicit_response:
            return (
                TimingRecommendation.WAIT_FOR_PRIVATE_CONTEXT,
                ("guest_context_blocks_spontaneous_intervention",),
                now + timedelta(seconds=self.policy.default_deferral_seconds),
            )
        if conversation.do_not_disturb:
            earliest = context.quiet_until or now + timedelta(
                seconds=self.policy.default_deferral_seconds
            )
            return TimingRecommendation.DEFER, ("do_not_disturb_is_active",), earliest
        if not conversation.user_present:
            return (
                TimingRecommendation.DEFER,
                ("user_is_not_present",),
                now + timedelta(seconds=self.policy.default_deferral_seconds),
            )
        if explicit_response:
            return (
                TimingRecommendation.INTERVENE_NOW,
                ("explicit_user_turn_has_temporal_priority",),
                now,
            )
        if context.activity in self._BLOCKING_ACTIVITY:
            return (
                TimingRecommendation.DEFER,
                (f"activity_state_{context.activity.value}_blocks_interruption",),
                now + timedelta(seconds=self.policy.default_deferral_seconds),
            )
        if context.cognitive_load > self.policy.maximum_cognitive_load:
            return (
                TimingRecommendation.DEFER,
                ("cognitive_load_exceeds_interruption_threshold",),
                now + timedelta(seconds=self.policy.default_deferral_seconds),
            )
        if self._is_quiet_hour(context.local_hour):
            return (
                TimingRecommendation.DEFER,
                ("local_time_is_within_quiet_hours",),
                (now + self._until_quiet_hours_end(context.local_hour)),
            )
        if (
            context.spontaneous_interventions_today
            >= self.policy.maximum_spontaneous_interventions_per_day
        ):
            return (
                TimingRecommendation.CANCEL,
                ("daily_spontaneous_intervention_budget_exhausted",),
                None,
            )
        cooldown_end = self._cooldown_end(context)
        if cooldown_end is not None and cooldown_end > now:
            return (
                TimingRecommendation.DEFER,
                ("minimum_spontaneous_intervention_interval_not_elapsed",),
                cooldown_end,
            )
        return (
            TimingRecommendation.INTERVENE_NOW,
            ("natural_conversation_window_is_open",),
            now,
        )

    def _is_quiet_hour(self, hour: int) -> bool:
        start = self.policy.quiet_hours_start
        end = self.policy.quiet_hours_end
        if start < end:
            return start <= hour < end
        return hour >= start or hour < end

    def _until_quiet_hours_end(self, local_hour: int) -> timedelta:
        end = self.policy.quiet_hours_end
        hours = (end - local_hour) % 24
        if hours == 0:
            hours = 24
        return timedelta(hours=hours)

    def _cooldown_end(self, context: ConversationTimingContext) -> datetime | None:
        if context.last_spontaneous_intervention_at is None:
            return None
        return context.last_spontaneous_intervention_at + timedelta(
            seconds=self.policy.minimum_spontaneous_interval_seconds
        )

    @staticmethod
    def system_prompt_lines() -> tuple[str, ...]:
        return (
            "Conversation Timing Engine M95:",
            "- Una oportunidad válida no implica que deba aprovecharse ahora.",
            "- Priorizar presencia, privacidad, foco y presupuesto de interrupción.",
            "- Responder a un turno explícito tiene prioridad temporal.",
            "- M95 recomienda ventanas; no agenda, no habla y no genera contenido.",
        )
