from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.capability_registry import PermissionScope
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


class UnifiedPermissionConsentStatus(str, Enum):
    SATISFIED = "satisfied"
    SATISFIED_PARTIAL = "satisfied_partial"
    CONSENT_REQUIRED = "consent_required"
    DENIED = "denied"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class UnifiedPermissionConsentAction(str, Enum):
    DECLARE_SATISFIED = "declare_satisfied"
    DECLARE_PARTIAL = "declare_partial"
    REQUEST_EXPLICIT_CONSENT = "request_explicit_consent"
    DECLARE_DENIAL = "declare_denial"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class PermissionRequirement:
    capability_name: str
    scope: PermissionScope | str
    context_ids: tuple[str, ...] = ()
    explicit_consent_required: bool = True

    def __post_init__(self) -> None:
        name = self.capability_name.strip()
        if not name:
            raise ValueError("permission requirement capability must not be blank")
        object.__setattr__(self, "capability_name", name)
        object.__setattr__(self, "scope", PermissionScope(self.scope))
        contexts = tuple(item.strip() for item in self.context_ids)
        if any(not item for item in contexts):
            raise ValueError("permission requirement context id must not be blank")
        if len(set(contexts)) != len(contexts):
            raise ValueError("permission requirement context ids must be unique")
        object.__setattr__(self, "context_ids", contexts)

    @property
    def key(self) -> tuple[str, PermissionScope]:
        return (self.capability_name.casefold(), PermissionScope(self.scope))


@dataclass(frozen=True)
class UnifiedConsentGrant:
    grant_id: str
    owner: str
    capability_name: str
    scope: PermissionScope | str
    context_ids: tuple[str, ...]
    granted_at: datetime
    expires_at: datetime | None = None
    denied: bool = False
    revoked: bool = False

    def __post_init__(self) -> None:
        for name in ("grant_id", "owner", "capability_name"):
            value = getattr(self, name).strip()
            if not value:
                raise ValueError(f"unified consent {name} must not be blank")
            object.__setattr__(self, name, value)
        object.__setattr__(self, "scope", PermissionScope(self.scope))
        contexts = tuple(item.strip() for item in self.context_ids)
        if not contexts or any(not item for item in contexts):
            raise ValueError("unified consent contexts must not be empty")
        if len(set(contexts)) != len(contexts):
            raise ValueError("unified consent contexts must be unique")
        object.__setattr__(self, "context_ids", contexts)
        if self.granted_at.tzinfo is None or (
            self.expires_at is not None and self.expires_at.tzinfo is None
        ):
            raise ValueError("unified consent timestamps must be timezone-aware")
        if self.expires_at is not None and self.expires_at < self.granted_at:
            raise ValueError("unified consent expiry cannot precede grant")
        if self.denied and self.revoked:
            raise ValueError("unified consent cannot be denied and revoked")

    @property
    def key(self) -> tuple[str, PermissionScope]:
        return (self.capability_name.casefold(), PermissionScope(self.scope))


@dataclass(frozen=True)
class UnifiedPermissionConsentConfig:
    maximum_continuity_results: int = 64
    maximum_requirements: int = 64
    maximum_grants: int = 128
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_continuity: bool = True
    require_all_contexts_covered: bool = True

    def __post_init__(self) -> None:
        if (
            min(
                self.maximum_continuity_results,
                self.maximum_requirements,
                self.maximum_grants,
            )
            <= 0
        ):
            raise ValueError("unified permission limits must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("unified permission result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "unified permission confidence must be between zero and one"
            )


@dataclass(frozen=True)
class UnifiedPermissionConsentRequest:
    owner: str
    continuity_results: tuple[CrossContextContinuityResult, ...]
    requirements: tuple[PermissionRequirement, ...]
    grants: tuple[UnifiedConsentGrant, ...]
    evaluation_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("unified permission owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "continuity_results", tuple(self.continuity_results))
        object.__setattr__(self, "requirements", tuple(self.requirements))
        object.__setattr__(self, "grants", tuple(self.grants))


@dataclass(frozen=True)
class UnifiedPermissionConsentResult:
    request: UnifiedPermissionConsentRequest
    status: UnifiedPermissionConsentStatus | str
    action: UnifiedPermissionConsentAction | str
    selected_continuity: CrossContextContinuityResult | None
    selected_timing_evaluation: (
        LivingConversationConversationTimingEvaluationResult | None
    )
    selected_candidate: LivingConversationConversationCandidateResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    satisfied_requirements: tuple[PermissionRequirement, ...]
    missing_requirements: tuple[PermissionRequirement, ...]
    denied_requirements: tuple[PermissionRequirement, ...]
    matched_grant_ids: tuple[str, ...]
    confidence: float
    consent_satisfied: bool
    partial_consent: bool
    explicit_consent_required: bool
    consent_denied: bool
    confirmation_required: bool
    permission_grant_allowed: bool
    consent_prompt_allowed: bool
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
    evaluation_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", UnifiedPermissionConsentStatus(self.status))
        object.__setattr__(self, "action", UnifiedPermissionConsentAction(self.action))
        for name in (
            "satisfied_requirements",
            "missing_requirements",
            "denied_requirements",
            "matched_grant_ids",
            "rationale",
        ):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "unified permission result timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "unified permission confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("unified permission rationale must not be empty")
        if any(
            (
                self.permission_grant_allowed,
                self.consent_prompt_allowed,
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
        ):
            raise ValueError("M158 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.SATISFIED,
            self.status.SATISFIED_PARTIAL,
            self.status.CONSENT_REQUIRED,
            self.status.DENIED,
        }
        lineage = (
            self.selected_continuity,
            self.selected_timing_evaluation,
            self.selected_candidate,
            self.selected_opportunity,
        )
        if active:
            if any(item is None for item in lineage) or self.confidence <= 0:
                raise ValueError(
                    "active unified permission result requires full lineage"
                )
            continuity, timing, candidate, opportunity = lineage
            assert continuity and timing and candidate and opportunity
            if (
                continuity.selected_timing_evaluation is not timing
                or continuity.selected_candidate is not candidate
                or continuity.selected_opportunity is not opportunity
            ):
                raise ValueError(
                    "unified permission lineage must come from continuity result"
                )
        elif any(item is not None for item in lineage) or self.confidence != 0:
            raise ValueError("inactive unified permission result cannot expose lineage")
        if self.consent_satisfied != (
            self.status in {self.status.SATISFIED, self.status.SATISFIED_PARTIAL}
        ):
            raise ValueError("unified permission satisfied flag is inconsistent")
        if self.partial_consent != (self.status is self.status.SATISFIED_PARTIAL):
            raise ValueError("unified permission partial flag is inconsistent")
        if self.explicit_consent_required != (
            self.status is self.status.CONSENT_REQUIRED
        ):
            raise ValueError("unified permission consent-required flag is inconsistent")
        if self.consent_denied != (self.status is self.status.DENIED):
            raise ValueError("unified permission denial flag is inconsistent")
        if self.confirmation_required != (
            self.status in {self.status.CONSENT_REQUIRED, self.status.REVIEW_REQUIRED}
        ):
            raise ValueError("unified permission confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.evaluation_id and self.evaluation_id != expected:
            raise ValueError("unified permission evaluation id is inconsistent")
        object.__setattr__(self, "evaluation_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                ";".join(x.continuity_id for x in self.request.continuity_results),
                ";".join(
                    f"{x.capability_name.casefold()}:{PermissionScope(x.scope).value}"
                    for x in self.request.requirements
                ),
                ";".join(x.grant_id for x in self.request.grants),
                str(self.request.evaluation_requested),
                self.status.value,
                self.action.value,
                self.selected_continuity.continuity_id
                if self.selected_continuity
                else "none",
                ";".join(self.matched_grant_ids),
                str(self.confidence),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class UnifiedPermissionConsentRepository(Protocol):
    def add(self, result: UnifiedPermissionConsentResult) -> None: ...
    def get(self, evaluation_id: str) -> UnifiedPermissionConsentResult | None: ...
    def list_all(self) -> tuple[UnifiedPermissionConsentResult, ...]: ...


class InMemoryUnifiedPermissionConsentRepository:
    def __init__(self) -> None:
        self._items: dict[str, UnifiedPermissionConsentResult] = {}

    def add(self, result: UnifiedPermissionConsentResult) -> None:
        if result.evaluation_id in self._items:
            raise ValueError("unified permission result already exists")
        self._items[result.evaluation_id] = result

    def get(self, evaluation_id: str) -> UnifiedPermissionConsentResult | None:
        return self._items.get(evaluation_id)

    def list_all(self) -> tuple[UnifiedPermissionConsentResult, ...]:
        return tuple(self._items.values())
