from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.companion_reliability_model import CompanionReliabilityResult
from core.cross_context_continuity import CrossContextContinuityResult
from core.living_conversation_conversation_candidate import (
    LivingConversationConversationCandidateResult,
)
from core.living_conversation_conversation_timing_evaluation import (
    LivingConversationConversationTimingEvaluationResult,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)
from core.unified_permission_consent import UnifiedPermissionConsentResult


class LongTermExperienceStatus(str, Enum):
    POSITIVE = "positive"
    MIXED = "mixed"
    NEGATIVE = "negative"
    INSUFFICIENT = "insufficient"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LongTermExperienceAction(str, Enum):
    DECLARE_POSITIVE = "declare_positive"
    DECLARE_MIXED = "declare_mixed"
    DECLARE_NEGATIVE = "declare_negative"
    DECLARE_INSUFFICIENT = "declare_insufficient"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


class ExperienceOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    NEUTRAL = "neutral"
    FAILURE = "failure"
    ABANDONED = "abandoned"


@dataclass(frozen=True)
class ExperienceObservation:
    observation_id: str
    owner: str
    reliability_id: str
    occurred_at: datetime
    outcome: ExperienceOutcome | str
    satisfaction: float
    continuity_quality: float
    consent_alignment: float
    reliability_quality: float
    context_ids: tuple[str, ...] = ()
    explicit_user_feedback: bool = False
    excluded: bool = False

    def __post_init__(self) -> None:
        for name in ("observation_id", "owner", "reliability_id"):
            value = getattr(self, name).strip()
            if not value:
                raise ValueError(f"experience {name} must not be blank")
            object.__setattr__(self, name, value)
        object.__setattr__(self, "outcome", ExperienceOutcome(self.outcome))
        if self.occurred_at.tzinfo is None:
            raise ValueError("experience observation timestamp must be timezone-aware")
        scores = (
            self.satisfaction,
            self.continuity_quality,
            self.consent_alignment,
            self.reliability_quality,
        )
        if any(not 0 <= value <= 1 for value in scores):
            raise ValueError("experience scores must be between zero and one")
        contexts = tuple(item.strip() for item in self.context_ids)
        if any(not item for item in contexts) or len(set(contexts)) != len(contexts):
            raise ValueError("experience context ids must be unique and non-blank")
        object.__setattr__(self, "context_ids", contexts)

    @property
    def experience_score(self) -> float:
        outcome_factor = {
            ExperienceOutcome.SUCCESS: 1.0,
            ExperienceOutcome.PARTIAL_SUCCESS: 0.7,
            ExperienceOutcome.NEUTRAL: 0.5,
            ExperienceOutcome.FAILURE: 0.2,
            ExperienceOutcome.ABANDONED: 0.0,
        }[self.outcome]
        return round(
            (
                self.satisfaction
                + self.continuity_quality
                + self.consent_alignment
                + self.reliability_quality
                + outcome_factor
            )
            / 5,
            6,
        )


@dataclass(frozen=True)
class LongTermExperienceConfig:
    maximum_reliability_results: int = 256
    maximum_observations: int = 512
    evaluation_horizon: timedelta = timedelta(days=90)
    minimum_observations: int = 3
    minimum_observation_span: timedelta = timedelta(days=1)
    minimum_source_confidence: float = 0.6
    positive_threshold: float = 0.8
    negative_threshold: float = 0.45
    maximum_negative_ratio_for_positive: float = 0.2
    require_explicit_feedback: bool = False

    def __post_init__(self) -> None:
        if (
            min(
                self.maximum_reliability_results,
                self.maximum_observations,
                self.minimum_observations,
            )
            <= 0
        ):
            raise ValueError("experience limits must be positive")
        if min(self.evaluation_horizon, self.minimum_observation_span) <= timedelta(0):
            raise ValueError("experience durations must be positive")
        values = (
            self.minimum_source_confidence,
            self.positive_threshold,
            self.negative_threshold,
            self.maximum_negative_ratio_for_positive,
        )
        if any(not 0 <= value <= 1 for value in values):
            raise ValueError("experience thresholds must be between zero and one")
        if self.negative_threshold > self.positive_threshold:
            raise ValueError("experience thresholds must be ordered")


@dataclass(frozen=True)
class LongTermExperienceRequest:
    owner: str
    reliability_results: tuple[CompanionReliabilityResult, ...]
    observations: tuple[ExperienceObservation, ...]
    evaluation_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("experience owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "reliability_results", tuple(self.reliability_results))
        object.__setattr__(self, "observations", tuple(self.observations))


@dataclass(frozen=True)
class LongTermExperienceResult:
    request: LongTermExperienceRequest
    status: LongTermExperienceStatus | str
    action: LongTermExperienceAction | str
    selected_reliability_result: CompanionReliabilityResult | None
    selected_permission_result: UnifiedPermissionConsentResult | None
    selected_continuity: CrossContextContinuityResult | None
    selected_timing_evaluation: (
        LivingConversationConversationTimingEvaluationResult | None
    )
    selected_candidate: LivingConversationConversationCandidateResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    matched_observation_ids: tuple[str, ...]
    matched_reliability_ids: tuple[str, ...]
    experience_score: float
    negative_ratio: float
    observation_count: int
    observation_span: timedelta
    confidence: float
    positive: bool
    mixed: bool
    negative: bool
    insufficient: bool
    confirmation_required: bool
    memory_write_allowed: bool
    learning_allowed: bool
    personality_change_allowed: bool
    policy_change_allowed: bool
    knowledge_evolution_allowed: bool
    conversation_start_allowed: bool
    scheduling_allowed: bool
    prompt_generation_allowed: bool
    response_realization_allowed: bool
    provider_call_allowed: bool
    automation_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluation_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", LongTermExperienceStatus(self.status))
        object.__setattr__(self, "action", LongTermExperienceAction(self.action))
        object.__setattr__(
            self, "matched_observation_ids", tuple(self.matched_observation_ids)
        )
        object.__setattr__(
            self, "matched_reliability_ids", tuple(self.matched_reliability_ids)
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("experience result timestamp must be timezone-aware")
        if self.observation_span < timedelta(0):
            raise ValueError("experience observation span cannot be negative")
        if any(
            not 0 <= value <= 1
            for value in (self.experience_score, self.negative_ratio, self.confidence)
        ):
            raise ValueError("experience result scores must be between zero and one")
        if self.observation_count != len(self.matched_observation_ids):
            raise ValueError("experience observation count is inconsistent")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("experience rationale must not be empty")
        forbidden = (
            self.memory_write_allowed,
            self.learning_allowed,
            self.personality_change_allowed,
            self.policy_change_allowed,
            self.knowledge_evolution_allowed,
            self.conversation_start_allowed,
            self.scheduling_allowed,
            self.prompt_generation_allowed,
            self.response_realization_allowed,
            self.provider_call_allowed,
            self.automation_allowed,
            self.platform_mutation_allowed,
        )
        if any(forbidden):
            raise ValueError("M160 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.POSITIVE,
            self.status.MIXED,
            self.status.NEGATIVE,
        }
        lineage = (
            self.selected_reliability_result,
            self.selected_permission_result,
            self.selected_continuity,
            self.selected_timing_evaluation,
            self.selected_candidate,
            self.selected_opportunity,
        )
        if active:
            if any(item is None for item in lineage) or self.confidence <= 0:
                raise ValueError("active experience result requires full lineage")
            reliability, permission, continuity, timing, candidate, opportunity = (
                lineage
            )
            assert (
                reliability
                and permission
                and continuity
                and timing
                and candidate
                and opportunity
            )
            if (
                reliability.selected_permission_result is not permission
                or reliability.selected_continuity is not continuity
                or reliability.selected_timing_evaluation is not timing
                or reliability.selected_candidate is not candidate
                or reliability.selected_opportunity is not opportunity
            ):
                raise ValueError("experience lineage must come from reliability result")
        elif any(item is not None for item in lineage):
            raise ValueError("inactive experience result cannot expose lineage")
        expected_flags = (
            self.status is self.status.POSITIVE,
            self.status is self.status.MIXED,
            self.status is self.status.NEGATIVE,
            self.status is self.status.INSUFFICIENT,
            self.status is self.status.REVIEW_REQUIRED,
        )
        actual_flags = (
            self.positive,
            self.mixed,
            self.negative,
            self.insufficient,
            self.confirmation_required,
        )
        if actual_flags != expected_flags:
            raise ValueError("experience flags are inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.evaluation_id and self.evaluation_id != expected:
            raise ValueError("experience evaluation id is inconsistent")
        object.__setattr__(self, "evaluation_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                ";".join(
                    item.reliability_id for item in self.request.reliability_results
                ),
                ";".join(item.observation_id for item in self.request.observations),
                str(self.request.evaluation_requested),
                self.status.value,
                self.action.value,
                self.selected_reliability_result.reliability_id
                if self.selected_reliability_result
                else "none",
                ";".join(self.matched_observation_ids),
                ";".join(self.matched_reliability_ids),
                str(self.experience_score),
                str(self.negative_ratio),
                str(self.observation_count),
                str(self.observation_span.total_seconds()),
                str(self.confidence),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LongTermExperienceRepository(Protocol):
    def add(self, result: LongTermExperienceResult) -> None: ...
    def get(self, evaluation_id: str) -> LongTermExperienceResult | None: ...
    def list_all(self) -> tuple[LongTermExperienceResult, ...]: ...


class InMemoryLongTermExperienceRepository:
    def __init__(self) -> None:
        self._items: dict[str, LongTermExperienceResult] = {}

    def add(self, result: LongTermExperienceResult) -> None:
        if result.evaluation_id in self._items:
            raise ValueError("long-term experience result already exists")
        self._items[result.evaluation_id] = result

    def get(self, evaluation_id: str) -> LongTermExperienceResult | None:
        return self._items.get(evaluation_id)

    def list_all(self) -> tuple[LongTermExperienceResult, ...]:
        return tuple(self._items.values())
