from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
from core.long_term_experience_evaluation import LongTermExperienceResult
from core.unified_permission_consent import UnifiedPermissionConsentResult


class UnifiedCompanionIntegrationStatus(str, Enum):
    READY = "ready"
    DEGRADED = "degraded"
    HOLD = "hold"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class UnifiedCompanionIntegrationAction(str, Enum):
    DECLARE_READY = "declare_ready"
    DECLARE_DEGRADED = "declare_degraded"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class UnifiedCompanionIntegrationConfig:
    minimum_confidence: float = 0.6
    allow_mixed_experience: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "integration minimum confidence must be between zero and one"
            )


@dataclass(frozen=True)
class UnifiedCompanionIntegrationRequest:
    owner: str
    experience_result: LongTermExperienceResult
    integration_requested: bool = True
    cycle_label: str = "unified-companion"

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        label = self.cycle_label.strip()
        if not owner:
            raise ValueError("integration owner must not be blank")
        if not label:
            raise ValueError("integration cycle label must not be blank")
        if self.experience_result.request.owner.casefold() != owner.casefold():
            raise ValueError("integration owner must match experience owner")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "cycle_label", label)


@dataclass(frozen=True)
class UnifiedCompanionIntegrationResult:
    request: UnifiedCompanionIntegrationRequest
    status: UnifiedCompanionIntegrationStatus | str
    action: UnifiedCompanionIntegrationAction | str
    selected_experience_result: LongTermExperienceResult | None
    selected_reliability_result: CompanionReliabilityResult | None
    selected_permission_result: UnifiedPermissionConsentResult | None
    selected_continuity: CrossContextContinuityResult | None
    selected_timing_evaluation: (
        LivingConversationConversationTimingEvaluationResult | None
    )
    selected_candidate: LivingConversationConversationCandidateResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    stage_reference_ids: tuple[str, ...]
    confidence: float
    ready: bool
    degraded: bool
    hold: bool
    confirmation_required: bool
    activation_allowed: bool
    conversation_start_allowed: bool
    device_selection_allowed: bool
    channel_selection_allowed: bool
    context_transfer_allowed: bool
    scheduling_allowed: bool
    prompt_generation_allowed: bool
    response_realization_allowed: bool
    provider_call_allowed: bool
    automation_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    integration_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", UnifiedCompanionIntegrationStatus(self.status)
        )
        object.__setattr__(
            self, "action", UnifiedCompanionIntegrationAction(self.action)
        )
        object.__setattr__(self, "stage_reference_ids", tuple(self.stage_reference_ids))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("integration timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("integration confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("integration rationale must not be empty")
        if len(self.stage_reference_ids) != len(set(self.stage_reference_ids)) or any(
            not item.strip() for item in self.stage_reference_ids
        ):
            raise ValueError(
                "integration stage references must be unique and non-blank"
            )
        forbidden = (
            self.activation_allowed,
            self.conversation_start_allowed,
            self.device_selection_allowed,
            self.channel_selection_allowed,
            self.context_transfer_allowed,
            self.scheduling_allowed,
            self.prompt_generation_allowed,
            self.response_realization_allowed,
            self.provider_call_allowed,
            self.automation_allowed,
            self.platform_mutation_allowed,
        )
        if any(forbidden):
            raise ValueError("M161 cannot authorize downstream capabilities")
        expected_flags = (
            self.status is self.status.READY,
            self.status is self.status.DEGRADED,
            self.status is self.status.HOLD,
            self.status in {self.status.HOLD, self.status.BLOCKED},
        )
        if (
            self.ready,
            self.degraded,
            self.hold,
            self.confirmation_required,
        ) != expected_flags:
            raise ValueError("integration flags are inconsistent")
        lineage = (
            self.selected_experience_result,
            self.selected_reliability_result,
            self.selected_permission_result,
            self.selected_continuity,
            self.selected_timing_evaluation,
            self.selected_candidate,
            self.selected_opportunity,
        )
        active = self.status in {
            self.status.READY,
            self.status.DEGRADED,
            self.status.HOLD,
        }
        if active:
            if (
                any(item is None for item in lineage)
                or len(self.stage_reference_ids) != 7
                or self.confidence <= 0
            ):
                raise ValueError("active integration requires full lineage")
            (
                experience,
                reliability,
                permission,
                continuity,
                timing,
                candidate,
                opportunity,
            ) = lineage
            assert (
                experience
                and reliability
                and permission
                and continuity
                and timing
                and candidate
                and opportunity
            )
            if (
                experience.selected_reliability_result is not reliability
                or experience.selected_permission_result is not permission
                or experience.selected_continuity is not continuity
                or experience.selected_timing_evaluation is not timing
                or experience.selected_candidate is not candidate
                or experience.selected_opportunity is not opportunity
            ):
                raise ValueError("integration lineage must come from experience result")
        elif (
            any(item is not None for item in lineage)
            or self.stage_reference_ids
            or self.confidence != 0
        ):
            raise ValueError("inactive integration cannot expose lineage")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.integration_id and self.integration_id != expected:
            raise ValueError("integration id is inconsistent")
        object.__setattr__(self, "integration_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.experience_result.evaluation_id,
                str(self.request.integration_requested),
                self.request.cycle_label,
                self.status.value,
                self.action.value,
                ";".join(self.stage_reference_ids),
                str(self.confidence),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class UnifiedCompanionIntegrationRepository(Protocol):
    def add(self, result: UnifiedCompanionIntegrationResult) -> None: ...
    def get(self, integration_id: str) -> UnifiedCompanionIntegrationResult | None: ...
    def list_all(self) -> tuple[UnifiedCompanionIntegrationResult, ...]: ...


class InMemoryUnifiedCompanionIntegrationRepository:
    def __init__(self) -> None:
        self._items: dict[str, UnifiedCompanionIntegrationResult] = {}

    def add(self, result: UnifiedCompanionIntegrationResult) -> None:
        if result.integration_id in self._items:
            raise ValueError("unified companion integration already exists")
        self._items[result.integration_id] = result

    def get(self, integration_id: str) -> UnifiedCompanionIntegrationResult | None:
        return self._items.get(integration_id)

    def list_all(self) -> tuple[UnifiedCompanionIntegrationResult, ...]:
        return tuple(self._items.values())
