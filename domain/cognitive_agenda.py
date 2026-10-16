from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol


class CognitiveAgendaKind(str, Enum):
    COMMITMENT = "commitment"
    CONVERSATION = "conversation"
    PROJECT = "project"
    GOAL = "goal"
    OPPORTUNITY = "opportunity"
    FOLLOW_UP = "follow_up"
    AMBIENT = "ambient"
    PRESENCE = "presence"


class CognitiveAgendaStatus(str, Enum):
    ACTIVE = "active"
    WATCHING = "watching"
    BLOCKED = "blocked"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CognitiveCommitmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    STALLED = "stalled"
    COMPLETED = "completed"


class CognitiveAgendaOperationalStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class CognitiveMetacognitiveStatus(str, Enum):
    UNREVIEWED = "unreviewed"
    SOUND = "sound"
    REFORMULATE = "reformulate"
    DEFERRED = "deferred"


@dataclass(frozen=True)
class CognitiveAgendaSignal:
    key: str
    kind: CognitiveAgendaKind
    title: str
    source: str
    priority: float = 0.5
    urgency: float = 0.0
    relevance: float = 0.5
    status: CognitiveAgendaStatus = CognitiveAgendaStatus.ACTIVE
    observed_at: datetime | None = None
    expires_at: datetime | None = None
    rationale: str = ""
    resume_conditions: tuple[str, ...] = ()
    resolution_conditions: tuple[str, ...] = ()
    expected_benefit: float = 0.5
    cognitive_cost: float = 0.5
    dependencies: tuple[str, ...] = ()
    context_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("agenda signal key must not be empty")
        if not self.title.strip():
            raise ValueError("agenda signal title must not be empty")
        if not self.source.strip():
            raise ValueError("agenda signal source must not be empty")
        for name, value in (
            ("priority", self.priority),
            ("urgency", self.urgency),
            ("relevance", self.relevance),
            ("expected_benefit", self.expected_benefit),
            ("cognitive_cost", self.cognitive_cost),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"agenda signal {name} must be between 0 and 1")


@dataclass(frozen=True)
class CognitiveAgendaItem:
    key: str
    kind: CognitiveAgendaKind
    title: str
    sources: tuple[str, ...]
    score: float
    priority: float
    urgency: float
    relevance: float
    status: CognitiveAgendaStatus
    first_seen_at: datetime
    last_seen_at: datetime
    expires_at: datetime | None
    rationale: str
    resume_conditions: tuple[str, ...] = ()
    last_activated_at: datetime | None = None
    activation_count: int = 0
    resolution_conditions: tuple[str, ...] = ()
    last_transition: str = ""
    expected_benefit: float = 0.5
    cognitive_cost: float = 0.5
    dependencies: tuple[str, ...] = ()
    context_tags: tuple[str, ...] = ()
    commitment_status: CognitiveCommitmentStatus = CognitiveCommitmentStatus.PENDING
    commitment_started_at: datetime | None = None
    progress: float = 0.0
    last_progress_at: datetime | None = None
    execution_note: str = ""
    stall_count: int = 0
    metacognitive_status: CognitiveMetacognitiveStatus = (
        CognitiveMetacognitiveStatus.UNREVIEWED
    )
    progress_quality: float = 1.0
    formulation_clarity: float = 1.0
    review_count: int = 0
    last_reviewed_at: datetime | None = None
    review_note: str = ""
    adaptive_priority_adjustment: float = 0.0
    adaptive_cost_adjustment: float = 0.0
    learning_event_count: int = 0
    last_learned_at: datetime | None = None
    learning_rationale: str = ""

    def __post_init__(self) -> None:
        if self.activation_count < 0:
            raise ValueError("agenda activation count must not be negative")
        if not 0.0 <= self.progress <= 1.0:
            raise ValueError("agenda commitment progress must be between 0 and 1")
        if self.stall_count < 0:
            raise ValueError("agenda stall count must not be negative")
        if not 0.0 <= self.progress_quality <= 1.0:
            raise ValueError("agenda progress quality must be between 0 and 1")
        if not 0.0 <= self.formulation_clarity <= 1.0:
            raise ValueError("agenda formulation clarity must be between 0 and 1")
        if self.review_count < 0:
            raise ValueError("agenda review count must not be negative")
        if not -1.0 <= self.adaptive_priority_adjustment <= 1.0:
            raise ValueError(
                "agenda adaptive priority adjustment must be between -1 and 1"
            )
        if not -1.0 <= self.adaptive_cost_adjustment <= 1.0:
            raise ValueError("agenda adaptive cost adjustment must be between -1 and 1")
        if self.learning_event_count < 0:
            raise ValueError("agenda learning event count must not be negative")

    @property
    def effective_priority(self) -> float:
        return max(0.0, min(1.0, self.priority + self.adaptive_priority_adjustment))

    @property
    def effective_cognitive_cost(self) -> float:
        return max(0.0, min(1.0, self.cognitive_cost + self.adaptive_cost_adjustment))


@dataclass(frozen=True)
class CognitiveAgendaPlanEntry:
    item: CognitiveAgendaItem
    utility: float
    dependency_ready: bool
    context_affinity: float
    rationale: str


@dataclass(frozen=True)
class CognitiveAgendaOperationalHealth:
    status: CognitiveAgendaOperationalStatus
    invariant_violations: tuple[str, ...] = ()
    repository_failures: tuple[str, ...] = ()
    source_failures: tuple[str, ...] = ()

    @property
    def healthy(self) -> bool:
        return self.status is CognitiveAgendaOperationalStatus.HEALTHY


@dataclass(frozen=True)
class CognitiveAgendaSnapshot:
    generated_at: datetime
    items: tuple[CognitiveAgendaItem, ...]
    primary_focus: CognitiveAgendaItem | None
    source_failures: tuple[str, ...] = ()
    activated_focus: CognitiveAgendaItem | None = None
    activation_rationale: str = ""
    activation_evaluated: bool = False
    deliberative_queue: tuple[CognitiveAgendaPlanEntry, ...] = ()
    planning_rationale: str = ""
    active_commitment: CognitiveAgendaItem | None = None
    execution_rationale: str = ""
    metacognitive_review: CognitiveAgendaItem | None = None
    metacognitive_rationale: str = ""
    adaptive_learning: CognitiveAgendaItem | None = None
    adaptive_learning_rationale: str = ""
    operational_health: CognitiveAgendaOperationalHealth | None = None

    @property
    def effective_focus(self) -> CognitiveAgendaItem | None:
        if self.activation_evaluated:
            return self.activated_focus
        return self.activated_focus or self.primary_focus


@dataclass(frozen=True)
class CognitiveAgendaPolicy:
    capacity: int = 12
    continuity_window: timedelta = timedelta(minutes=20)
    priority_weight: float = 0.45
    urgency_weight: float = 0.35
    relevance_weight: float = 0.20
    continuity_bonus: float = 0.05
    watching_activation_urgency: float = 0.75
    repetition_window: timedelta = timedelta(minutes=10)
    repetition_penalty: float = 0.18
    aging_window: timedelta = timedelta(hours=2)
    aging_bonus: float = 0.12
    benefit_weight: float = 0.22
    cost_weight: float = 0.16
    context_affinity_bonus: float = 0.08
    commitment_stall_window: timedelta = timedelta(hours=6)
    stalled_utility_penalty: float = 0.20
    reformulation_utility_penalty: float = 0.30
    formulation_clarity_threshold: float = 0.40
    progress_quality_threshold: float = 0.30
    adaptive_learning_rate: float = 0.05
    adaptive_adjustment_limit: float = 0.25

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("agenda capacity must be positive")
        if self.continuity_window.total_seconds() < 0:
            raise ValueError("agenda continuity window must not be negative")
        if not 0.0 <= self.watching_activation_urgency <= 1.0:
            raise ValueError("watching activation urgency must be between 0 and 1")
        if self.repetition_window.total_seconds() < 0:
            raise ValueError("agenda repetition window must not be negative")
        if self.aging_window.total_seconds() <= 0:
            raise ValueError("agenda aging window must be positive")
        if self.commitment_stall_window.total_seconds() <= 0:
            raise ValueError("commitment stall window must be positive")
        if (
            min(
                self.priority_weight,
                self.urgency_weight,
                self.relevance_weight,
                self.continuity_bonus,
                self.repetition_penalty,
                self.aging_bonus,
                self.benefit_weight,
                self.cost_weight,
                self.context_affinity_bonus,
                self.stalled_utility_penalty,
                self.reformulation_utility_penalty,
            )
            < 0
        ):
            raise ValueError("agenda policy weights must not be negative")
        if not 0.0 <= self.formulation_clarity_threshold <= 1.0:
            raise ValueError("formulation clarity threshold must be between 0 and 1")
        if not 0.0 <= self.progress_quality_threshold <= 1.0:
            raise ValueError("progress quality threshold must be between 0 and 1")
        if not 0.0 < self.adaptive_learning_rate <= 1.0:
            raise ValueError("adaptive learning rate must be between 0 and 1")
        if not 0.0 <= self.adaptive_adjustment_limit <= 1.0:
            raise ValueError("adaptive adjustment limit must be between 0 and 1")


class CognitiveAgendaRepository(Protocol):
    def load_open(self) -> tuple[CognitiveAgendaItem, ...]: ...

    def save(self, items: tuple[CognitiveAgendaItem, ...]) -> None: ...

    def set_status(self, key: str, status: CognitiveAgendaStatus) -> bool: ...

    def status_for(self, key: str) -> CognitiveAgendaStatus | None: ...


class CognitiveAgendaSource(Protocol):
    name: str
    absence_status: CognitiveAgendaStatus | None

    def collect(self, *, now: datetime) -> Sequence[CognitiveAgendaSignal]: ...
