from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.personal_organization import (
    PersonalOrganizationAuthority,
    PersonalOrganizationCapability,
)
from core.priority_reasoning import (
    PriorityCandidate,
    PriorityDisposition,
    PriorityReason,
)
from domain.priority_reasoning import PriorityReasoning


class OrganizationRecommendationKind(StrEnum):
    PRIORITIZE = "prioritize"
    DEFER = "defer"
    BLOCKED = "blocked"
    REVIEW = "review"


@dataclass(frozen=True)
class PersonalOrganizationItem:
    item_id: str
    capability: PersonalOrganizationCapability | str
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
    source_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError("organization item id must not be blank")
        PersonalOrganizationCapability(self.capability)
        if not self.title.strip():
            raise ValueError("organization item title must not be blank")
        if self.source_reference is not None and not self.source_reference.strip():
            raise ValueError("organization source reference must not be blank")
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

    @property
    def normalized_capability(self) -> PersonalOrganizationCapability:
        return PersonalOrganizationCapability(self.capability)


@dataclass(frozen=True)
class PersonalOrganizationRecommendation:
    item_id: str
    capability: PersonalOrganizationCapability
    kind: OrganizationRecommendationKind
    score: float
    reason_codes: tuple[str, ...]
    source_reference: str | None = None
    action_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError("recommendation item id must not be blank")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("recommendation score must be between 0 and 1")
        if not self.reason_codes:
            raise ValueError("recommendation requires reason codes")
        if any(not code.strip() for code in self.reason_codes):
            raise ValueError("recommendation reason codes must not be blank")
        if self.action_authorized:
            raise ValueError("organization recommendations cannot authorize action")


@dataclass(frozen=True)
class IntelligentPersonalOrganizationReport:
    report_id: str
    recommendations: tuple[PersonalOrganizationRecommendation, ...]
    ordered_ids: tuple[str, ...]
    review_ids: tuple[str, ...]
    blocked_ids: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m391.5"
    canonical_authority: str = "PersonalOrganizationAuthority"
    priority_authority: str = "priority_reasoning"
    read_only: bool = True
    creates_items: bool = False
    modifies_items: bool = False
    deletes_items: bool = False
    persists_results: bool = False
    schedules_events: bool = False
    fires_reminders: bool = False
    writes_notes: bool = False
    modifies_memory: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    starts_background_process: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("personal-organization-"):
            raise ValueError("personal organization report id is invalid")
        if self.canonical_authority != "PersonalOrganizationAuthority":
            raise ValueError("personal organization authority must remain canonical")
        if self.priority_authority != "priority_reasoning":
            raise ValueError("priority reasoning authority must be reused")
        ids = tuple(item.item_id for item in self.recommendations)
        if len(ids) != len(set(ids)):
            raise ValueError("organization recommendation ids must be unique")
        known = set(ids)
        for collection in (self.ordered_ids, self.review_ids, self.blocked_ids):
            if not set(collection).issubset(known):
                raise ValueError("report references unknown organization items")
        if any(
            (
                not self.read_only,
                self.creates_items,
                self.modifies_items,
                self.deletes_items,
                self.persists_results,
                self.schedules_events,
                self.fires_reminders,
                self.writes_notes,
                self.modifies_memory,
                self.modifies_planning,
                self.executes_actions,
                self.starts_background_process,
                self.grants_authority,
            )
        ):
            raise ValueError("intelligent organization violates governed limits")


class IntelligentPersonalOrganizationView:
    """Pure coordination view subordinate to PersonalOrganizationAuthority."""

    CANONICAL_AUTHORITY = "PersonalOrganizationAuthority"

    def __init__(self) -> None:
        self._organization = PersonalOrganizationAuthority()
        self._priority = PriorityReasoning()

    def organize(
        self,
        items: tuple[PersonalOrganizationItem, ...],
        *,
        limit: int | None = None,
    ) -> IntelligentPersonalOrganizationReport:
        self._validate_unique_items(items)
        bindings = self._organization.snapshot()
        candidates = tuple(self._candidate(item) for item in items)
        priority = self._priority.evaluate(candidates, limit=limit)
        assessments = {item.candidate_id: item for item in priority.assessments}
        ordered_items = tuple(sorted(items, key=lambda item: item.item_id))
        recommendations = tuple(
            self._recommend(item, assessments[item.item_id]) for item in ordered_items
        )
        fingerprint = self._fingerprint(
            bindings.bindings,
            ordered_items,
            recommendations,
            priority.ordered_ids,
            priority.review_ids,
            priority.blocked_ids,
        )
        return IntelligentPersonalOrganizationReport(
            report_id=f"personal-organization-{fingerprint[:16]}",
            recommendations=recommendations,
            ordered_ids=priority.ordered_ids,
            review_ids=priority.review_ids,
            blocked_ids=priority.blocked_ids,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _validate_unique_items(items: tuple[PersonalOrganizationItem, ...]) -> None:
        ids = tuple(item.item_id for item in items)
        if len(ids) != len(set(ids)):
            raise ValueError("organization item ids must be unique")

    @staticmethod
    def _candidate(item: PersonalOrganizationItem) -> PriorityCandidate:
        return PriorityCandidate(
            candidate_id=item.item_id,
            kind=IntelligentPersonalOrganizationView._priority_kind(item),
            title=item.title,
            urgency=item.urgency,
            importance=item.importance,
            goal_alignment=item.goal_alignment,
            context_relevance=item.context_relevance,
            deadline_proximity=item.deadline_proximity,
            safety_risk=item.safety_risk,
            user_declared=item.user_declared,
            blocked=item.blocked,
            conflicting=item.conflicting,
        )

    @staticmethod
    def _priority_kind(item: PersonalOrganizationItem) -> str:
        mapping = {
            PersonalOrganizationCapability.GOALS: "goal",
            PersonalOrganizationCapability.PROJECTS: "project",
            PersonalOrganizationCapability.TASKS: "task",
        }
        return mapping.get(item.normalized_capability, "context")

    @staticmethod
    def _recommend(item, assessment) -> PersonalOrganizationRecommendation:
        disposition_map = {
            PriorityDisposition.PRIORITIZE: OrganizationRecommendationKind.PRIORITIZE,
            PriorityDisposition.DEFER: OrganizationRecommendationKind.DEFER,
            PriorityDisposition.BLOCKED: OrganizationRecommendationKind.BLOCKED,
            PriorityDisposition.REQUIRE_REVIEW: OrganizationRecommendationKind.REVIEW,
        }
        reasons = tuple(reason.value for reason in assessment.reasons)
        if not reasons:
            reasons = (PriorityReason.LOW_SIGNAL.value,)
        return PersonalOrganizationRecommendation(
            item_id=item.item_id,
            capability=item.normalized_capability,
            kind=disposition_map[assessment.disposition],
            score=assessment.score,
            reason_codes=reasons,
            source_reference=item.source_reference,
        )

    @staticmethod
    def _fingerprint(*parts: object) -> str:
        return sha256(repr(parts).encode("utf-8")).hexdigest()
