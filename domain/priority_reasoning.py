from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PriorityCandidateKind(StrEnum):
    GOAL = "goal"
    PROJECT = "project"
    TASK = "task"
    NOTIFICATION = "notification"
    SAFETY = "safety"
    CONTEXT = "context"


class PriorityDisposition(StrEnum):
    PRIORITIZE = "prioritize"
    DEFER = "defer"
    BLOCKED = "blocked"
    REQUIRE_REVIEW = "require_review"


class PriorityReason(StrEnum):
    USER_DECLARED = "user_declared"
    URGENCY = "urgency"
    IMPORTANCE = "importance"
    GOAL_ALIGNMENT = "goal_alignment"
    CONTEXT_RELEVANCE = "context_relevance"
    SAFETY_RISK = "safety_risk"
    DEADLINE_PROXIMITY = "deadline_proximity"
    BLOCKED = "blocked"
    CONFLICT = "conflict"
    LOW_SIGNAL = "low_signal"


@dataclass(frozen=True)
class PriorityCandidate:
    candidate_id: str
    kind: PriorityCandidateKind
    title: str
    urgency: float = 0.0
    importance: float = 0.0
    goal_alignment: float = 0.0
    context_relevance: float = 0.0
    deadline_proximity: float = 0.0
    safety_risk: float = 0.0
    user_declared: bool = False
    blocked: bool = False
    conflicting: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must not be blank")
        if not self.title.strip():
            raise ValueError("title must not be blank")
        for name in (
            "urgency",
            "importance",
            "goal_alignment",
            "context_relevance",
            "deadline_proximity",
            "safety_risk",
        ):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class PriorityAssessment:
    candidate_id: str
    disposition: PriorityDisposition
    score: float
    reasons: tuple[PriorityReason, ...]
    action_authorized: bool = False
    runtime_behavior_changed: bool = False
    persistence_performed: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0 and 1")
        if self.action_authorized:
            raise ValueError("priority reasoning cannot authorize action")
        if self.runtime_behavior_changed:
            raise ValueError("priority reasoning cannot change runtime")
        if self.persistence_performed:
            raise ValueError("priority reasoning cannot persist")


@dataclass(frozen=True)
class PriorityReasoningResult:
    assessments: tuple[PriorityAssessment, ...]
    ordered_ids: tuple[str, ...]
    review_ids: tuple[str, ...]
    blocked_ids: tuple[str, ...]


@dataclass(frozen=True)
class PriorityReasoningSnapshot:
    schema_version: str
    canonical_authority: str
    parent_world_authority: str
    existing_policy: str
    context_authority: str
    explainable: bool
    deterministic: bool
    read_only: bool
    action_authorized: bool
    persistence_added: bool
    runtime_behavior_changed: bool


class PriorityReasoning:
    """Deterministic, explainable ranking over admitted world-model candidates."""

    SCHEMA_VERSION = "m367.6"
    CANONICAL_AUTHORITY = "priority_reasoning"
    PARENT_WORLD_AUTHORITY = "internal_world_model"
    EXISTING_POLICY = "core.cognitive_priority.policy:DeterministicPriorityPolicy"
    CONTEXT_AUTHORITY = "context_state_model"

    @property
    def snapshot(self) -> PriorityReasoningSnapshot:
        return PriorityReasoningSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_world_authority=self.PARENT_WORLD_AUTHORITY,
            existing_policy=self.EXISTING_POLICY,
            context_authority=self.CONTEXT_AUTHORITY,
            explainable=True,
            deterministic=True,
            read_only=True,
            action_authorized=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def evaluate(
        self,
        candidates: tuple[PriorityCandidate, ...],
        *,
        limit: int | None = None,
    ) -> PriorityReasoningResult:
        if limit is not None and limit < 1:
            raise ValueError("limit must be positive")

        assessments = tuple(self._assess(candidate) for candidate in candidates)
        selectable = sorted(
            (
                item
                for item in assessments
                if item.disposition is PriorityDisposition.PRIORITIZE
            ),
            key=lambda item: (-item.score, item.candidate_id),
        )
        if limit is not None:
            selectable = selectable[:limit]

        return PriorityReasoningResult(
            assessments=assessments,
            ordered_ids=tuple(item.candidate_id for item in selectable),
            review_ids=tuple(
                item.candidate_id
                for item in assessments
                if item.disposition is PriorityDisposition.REQUIRE_REVIEW
            ),
            blocked_ids=tuple(
                item.candidate_id
                for item in assessments
                if item.disposition is PriorityDisposition.BLOCKED
            ),
        )

    @staticmethod
    def _assess(candidate: PriorityCandidate) -> PriorityAssessment:
        if candidate.conflicting:
            return PriorityAssessment(
                candidate_id=candidate.candidate_id,
                disposition=PriorityDisposition.REQUIRE_REVIEW,
                score=0.0,
                reasons=(PriorityReason.CONFLICT,),
            )
        if candidate.blocked:
            return PriorityAssessment(
                candidate_id=candidate.candidate_id,
                disposition=PriorityDisposition.BLOCKED,
                score=0.0,
                reasons=(PriorityReason.BLOCKED,),
            )

        score = (
            candidate.urgency * 0.24
            + candidate.importance * 0.22
            + candidate.goal_alignment * 0.18
            + candidate.context_relevance * 0.16
            + candidate.deadline_proximity * 0.10
            + candidate.safety_risk * 0.10
        )
        if candidate.user_declared:
            score = min(1.0, score + 0.10)

        reasons: list[PriorityReason] = []
        if candidate.user_declared:
            reasons.append(PriorityReason.USER_DECLARED)
        dimensions = (
            (candidate.urgency, PriorityReason.URGENCY),
            (candidate.importance, PriorityReason.IMPORTANCE),
            (candidate.goal_alignment, PriorityReason.GOAL_ALIGNMENT),
            (candidate.context_relevance, PriorityReason.CONTEXT_RELEVANCE),
            (candidate.safety_risk, PriorityReason.SAFETY_RISK),
            (candidate.deadline_proximity, PriorityReason.DEADLINE_PROXIMITY),
        )
        reasons.extend(reason for value, reason in dimensions if value >= 0.6)

        disposition = PriorityDisposition.PRIORITIZE
        if score < 0.35:
            disposition = PriorityDisposition.DEFER
            reasons.append(PriorityReason.LOW_SIGNAL)

        return PriorityAssessment(
            candidate_id=candidate.candidate_id,
            disposition=disposition,
            score=round(score, 4),
            reasons=tuple(reasons),
        )
