from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CognitiveIntent(StrEnum):
    CONVERSATION = "conversation"
    INFORMATION = "information"
    CURRENT_INFORMATION = "current_information"
    ACTION = "action"
    CLARIFICATION = "clarification"


class CognitiveNeed(StrEnum):
    REASONING = "reasoning"
    PLANNING = "planning"
    REFLECTION = "reflection"
    COORDINATION = "coordination"
    DECISION = "decision"


class ContextRequirement(StrEnum):
    NONE = "none"
    CURRENT_TURN = "current_turn"
    CONVERSATION = "conversation"
    PERSONAL_MEMORY = "personal_memory"


class ToolRequirement(StrEnum):
    NONE = "none"
    CURRENT_AFFAIRS = "current_affairs"
    WEATHER = "weather"
    CALENDAR = "calendar"
    MEMORY = "memory"
    CAPABILITY_ROUTER = "capability_router"


class FreshnessRequirement(StrEnum):
    NONE = "none"
    CURRENT = "current"


class EvidenceLevel(StrEnum):
    NONE = "none"
    INTERNAL = "internal"
    SINGLE_SOURCE = "single_source"
    CORROBORATED = "corroborated"


class PlannedResponseDecision(StrEnum):
    RESPOND = "respond"
    ABSTAIN_IF_UNVERIFIED = "abstain_if_unverified"


class ShadowAssessmentStatus(StrEnum):
    SATISFIED = "satisfied"
    PARTIAL = "partial"
    UNSATISFIED = "unsatisfied"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class CognitivePlan:
    intent: CognitiveIntent
    required_context: tuple[ContextRequirement, ...]
    required_tools: tuple[ToolRequirement, ...]
    freshness: FreshnessRequirement
    minimum_evidence: EvidenceLevel
    response_decision: PlannedResponseDecision
    rationale_codes: tuple[str, ...]

    @property
    def needs_current_information(self) -> bool:
        return self.freshness is FreshnessRequirement.CURRENT


@dataclass(frozen=True)
class CognitivePlanOutcomeAssessment:
    """Advisory comparison between a plan and the response actually produced."""

    status: ShadowAssessmentStatus
    freshness_satisfied: bool
    evidence_satisfied: bool
    abstention_consistent: bool
    observed_evidence_count: int
    observed_conflicting_sources: bool
    observed_freshness: str
    observed_verification: str
    observed_abstention: bool
    rationale_codes: tuple[str, ...]
