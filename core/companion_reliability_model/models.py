from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

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


class CompanionReliabilityStatus(str, Enum):
    RELIABLE = "reliable"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class CompanionReliabilityAction(str, Enum):
    DECLARE_RELIABLE = "declare_reliable"
    DECLARE_DEGRADED = "declare_degraded"
    DECLARE_UNAVAILABLE = "declare_unavailable"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


class ReliabilityComponent(str, Enum):
    CONTEXT_SOURCE = "context_source"
    CONTEXT_TARGET = "context_target"
    CONVERSATION_PIPELINE = "conversation_pipeline"
    PERMISSION_SERVICE = "permission_service"
    DEVICE_RUNTIME = "device_runtime"
    NETWORK_PATH = "network_path"


@dataclass(frozen=True)
class ReliabilityObservation:
    observation_id: str
    owner: str
    component: ReliabilityComponent | str
    context_ids: tuple[str, ...]
    observed_at: datetime
    availability: float
    health: float
    error_rate: float = 0.0
    latency_ms: int | None = None
    stale: bool = False

    def __post_init__(self) -> None:
        for name in ("observation_id", "owner"):
            value = getattr(self, name).strip()
            if not value:
                raise ValueError(f"reliability {name} must not be blank")
            object.__setattr__(self, name, value)
        object.__setattr__(self, "component", ReliabilityComponent(self.component))
        contexts = tuple(item.strip() for item in self.context_ids)
        if any(not item for item in contexts) or len(set(contexts)) != len(contexts):
            raise ValueError("reliability context ids must be unique and non-blank")
        object.__setattr__(self, "context_ids", contexts)
        if self.observed_at.tzinfo is None:
            raise ValueError("reliability observation timestamp must be timezone-aware")
        if any(
            not 0 <= value <= 1
            for value in (self.availability, self.health, self.error_rate)
        ):
            raise ValueError("reliability scores must be between zero and one")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("reliability latency cannot be negative")


@dataclass(frozen=True)
class CompanionReliabilityConfig:
    maximum_permission_results: int = 64
    maximum_observations: int = 128
    maximum_result_age: timedelta = timedelta(hours=2)
    maximum_observation_age: timedelta = timedelta(minutes=15)
    minimum_source_confidence: float = 0.7
    reliable_threshold: float = 0.85
    degraded_threshold: float = 0.55
    maximum_error_rate: float = 0.2
    maximum_latency_ms: int = 5000
    require_context_coverage: bool = True

    def __post_init__(self) -> None:
        if (
            min(
                self.maximum_permission_results,
                self.maximum_observations,
                self.maximum_latency_ms,
            )
            <= 0
        ):
            raise ValueError("reliability limits must be positive")
        if min(self.maximum_result_age, self.maximum_observation_age) <= timedelta(0):
            raise ValueError("reliability ages must be positive")
        values = (
            self.minimum_source_confidence,
            self.reliable_threshold,
            self.degraded_threshold,
            self.maximum_error_rate,
        )
        if any(not 0 <= value <= 1 for value in values):
            raise ValueError("reliability thresholds must be between zero and one")
        if self.degraded_threshold > self.reliable_threshold:
            raise ValueError("reliability thresholds must be ordered")


@dataclass(frozen=True)
class CompanionReliabilityRequest:
    owner: str
    permission_results: tuple[UnifiedPermissionConsentResult, ...]
    observations: tuple[ReliabilityObservation, ...]
    evaluation_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("reliability owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "permission_results", tuple(self.permission_results))
        object.__setattr__(self, "observations", tuple(self.observations))


@dataclass(frozen=True)
class CompanionReliabilityResult:
    request: CompanionReliabilityRequest
    status: CompanionReliabilityStatus | str
    action: CompanionReliabilityAction | str
    selected_permission_result: UnifiedPermissionConsentResult | None
    selected_continuity: CrossContextContinuityResult | None
    selected_timing_evaluation: (
        LivingConversationConversationTimingEvaluationResult | None
    )
    selected_candidate: LivingConversationConversationCandidateResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    matched_observation_ids: tuple[str, ...]
    reliability_score: float
    confidence: float
    reliable: bool
    degraded: bool
    unavailable: bool
    confirmation_required: bool
    conversation_start_allowed: bool
    conversational_activation_allowed: bool
    device_handoff_allowed: bool
    context_transfer_allowed: bool
    channel_selection_allowed: bool
    scheduling_allowed: bool
    prompt_generation_allowed: bool
    response_realization_allowed: bool
    provider_call_allowed: bool
    automation_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reliability_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", CompanionReliabilityStatus(self.status))
        object.__setattr__(self, "action", CompanionReliabilityAction(self.action))
        object.__setattr__(
            self, "matched_observation_ids", tuple(self.matched_observation_ids)
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("reliability result timestamp must be timezone-aware")
        if any(
            not 0 <= value <= 1 for value in (self.reliability_score, self.confidence)
        ):
            raise ValueError("reliability result scores must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("reliability rationale must not be empty")
        forbidden = (
            self.conversation_start_allowed,
            self.conversational_activation_allowed,
            self.device_handoff_allowed,
            self.context_transfer_allowed,
            self.channel_selection_allowed,
            self.scheduling_allowed,
            self.prompt_generation_allowed,
            self.response_realization_allowed,
            self.provider_call_allowed,
            self.automation_allowed,
            self.platform_mutation_allowed,
        )
        if any(forbidden):
            raise ValueError("M159 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.RELIABLE,
            self.status.DEGRADED,
            self.status.UNAVAILABLE,
        }
        lineage = (
            self.selected_permission_result,
            self.selected_continuity,
            self.selected_timing_evaluation,
            self.selected_candidate,
            self.selected_opportunity,
        )
        if active:
            if any(item is None for item in lineage) or self.confidence <= 0:
                raise ValueError("active reliability result requires full lineage")
            permission, continuity, timing, candidate, opportunity = lineage
            assert permission and continuity and timing and candidate and opportunity
            if (
                permission.selected_continuity is not continuity
                or permission.selected_timing_evaluation is not timing
                or permission.selected_candidate is not candidate
                or permission.selected_opportunity is not opportunity
            ):
                raise ValueError("reliability lineage must come from permission result")
        elif (
            any(item is not None for item in lineage)
            or self.confidence != 0
            or self.reliability_score != 0
        ):
            raise ValueError("inactive reliability result cannot expose lineage")
        if self.reliable != (self.status is self.status.RELIABLE):
            raise ValueError("reliable flag is inconsistent")
        if self.degraded != (self.status is self.status.DEGRADED):
            raise ValueError("degraded flag is inconsistent")
        if self.unavailable != (self.status is self.status.UNAVAILABLE):
            raise ValueError("unavailable flag is inconsistent")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("reliability confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.reliability_id and self.reliability_id != expected:
            raise ValueError("reliability id is inconsistent")
        object.__setattr__(self, "reliability_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                ";".join(x.evaluation_id for x in self.request.permission_results),
                ";".join(x.observation_id for x in self.request.observations),
                str(self.request.evaluation_requested),
                self.status.value,
                self.action.value,
                self.selected_permission_result.evaluation_id
                if self.selected_permission_result
                else "none",
                ";".join(self.matched_observation_ids),
                str(self.reliability_score),
                str(self.confidence),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class CompanionReliabilityRepository(Protocol):
    def add(self, result: CompanionReliabilityResult) -> None: ...
    def get(self, reliability_id: str) -> CompanionReliabilityResult | None: ...
    def list_all(self) -> tuple[CompanionReliabilityResult, ...]: ...


class InMemoryCompanionReliabilityRepository:
    def __init__(self) -> None:
        self._items: dict[str, CompanionReliabilityResult] = {}

    def add(self, result: CompanionReliabilityResult) -> None:
        if result.reliability_id in self._items:
            raise ValueError("companion reliability result already exists")
        self._items[result.reliability_id] = result

    def get(self, reliability_id: str) -> CompanionReliabilityResult | None:
        return self._items.get(reliability_id)

    def list_all(self) -> tuple[CompanionReliabilityResult, ...]:
        return tuple(self._items.values())
