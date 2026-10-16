from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

from .governed_intellectual_goal_proposal import GovernedIntellectualGoalProposal
from .governed_level2b_productive_entry import (
    GovernedLevel2BProductiveEntryFoundationV1,
)


class _ProductiveRequirementEntry(Protocol):
    def admit(
        self,
        requirement: DiscriminatingEvidenceRequirement,
        *,
        originating_reasoning_id: str,
    ) -> object: ...


@dataclass(frozen=True)
class GovernedAuthorizedIntellectualGoal:
    """Explicitly authorized G3 goal that remains non-executive."""

    goal_id: str
    proposal_id: str
    owner: str
    subject: str
    unknown_element: str
    question: str
    curiosity_report_id: str
    question_id: str
    source_reference: str
    curiosity_source_fingerprint: str
    assembly_source_fingerprint: str
    relevance_recipient: str
    initiative_disposition: str
    authorization_reference: str
    authorized_by: str
    schema_version: str = "intel-g4-governed-authorized-intellectual-goal-v1"
    authorized: bool = True
    read_only: bool = True
    non_executive: bool = True
    planning_invoked: bool = False
    investigation_started: bool = False
    executes_capabilities: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.goal_id.startswith("authorized-intellectual-goal-"):
            raise ValueError("authorized intellectual goal identifier is invalid")
        required = (
            self.proposal_id,
            self.owner,
            self.subject,
            self.unknown_element,
            self.question,
            self.curiosity_report_id,
            self.question_id,
            self.source_reference,
            self.curiosity_source_fingerprint,
            self.assembly_source_fingerprint,
            self.relevance_recipient,
            self.initiative_disposition,
            self.authorization_reference,
            self.authorized_by,
        )
        if any(not value.strip() for value in required):
            raise ValueError("authorized intellectual goal lineage cannot be blank")
        if not self.authorized or not self.read_only or not self.non_executive:
            raise ValueError("authorized intellectual goal must remain non-executive")
        if any(
            (
                self.planning_invoked,
                self.investigation_started,
                self.executes_capabilities,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_knowledge,
                self.starts_background_process,
            )
        ):
            raise ValueError("authorized intellectual goal crossed its governed stop")


class GovernedIntellectualGoalAuthorizationAdmissionV1:
    """Admit explicit authorization without initiating investigation."""

    def admit(
        self,
        proposal: GovernedIntellectualGoalProposal,
        *,
        authorization_reference: str,
        authorized_by: str,
    ) -> GovernedAuthorizedIntellectualGoal:
        reference = authorization_reference.strip()
        authorizer = authorized_by.strip()
        if not reference or not authorizer:
            raise ValueError("intellectual goal authorization is required")
        if not proposal.authorization_required or proposal.authorized:
            raise ValueError("intellectual goal authorization lineage is invalid")
        if not proposal.read_only or not proposal.non_executive:
            raise ValueError(
                "intellectual goal authorization requires governed proposal"
            )

        fingerprint = sha256(
            repr((proposal.proposal_id, reference, authorizer)).encode("utf-8")
        ).hexdigest()
        return GovernedAuthorizedIntellectualGoal(
            goal_id=f"authorized-intellectual-goal-{fingerprint[:24]}",
            proposal_id=proposal.proposal_id,
            owner=proposal.owner,
            subject=proposal.subject,
            unknown_element=proposal.unknown_element,
            question=proposal.question,
            curiosity_report_id=proposal.curiosity_report_id,
            question_id=proposal.question_id,
            source_reference=proposal.source_reference,
            curiosity_source_fingerprint=proposal.curiosity_source_fingerprint,
            assembly_source_fingerprint=proposal.assembly_source_fingerprint,
            relevance_recipient=proposal.relevance_recipient,
            initiative_disposition=proposal.initiative_disposition,
            authorization_reference=reference,
            authorized_by=authorizer,
        )


@dataclass(frozen=True)
class GovernedAuthorizedIntellectualGoalRequirementAdmissionResult:
    """Audit projection of one exact requirement entering existing CAP-11."""

    source_goal: GovernedAuthorizedIntellectualGoal
    source_requirement: DiscriminatingEvidenceRequirement
    productive_entry_result: object
    requirement_id: str
    source_reference: str
    world_snapshot_id: str
    requirement_admission_invocation_count: int = 1
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    invokes_reasoning: bool = False

    def __post_init__(self) -> None:
        if self.requirement_id != self.source_requirement.requirement_id:
            raise ValueError("requirement admission must preserve requirement identity")
        if self.source_reference != self.source_requirement.source_reference:
            raise ValueError("requirement admission must preserve source lineage")
        if self.world_snapshot_id != self.source_requirement.world_snapshot_id:
            raise ValueError("requirement admission must preserve snapshot lineage")
        if self.requirement_admission_invocation_count != 1:
            raise ValueError("requirement admission must occur exactly once")
        if any(
            (
                self.invokes_planning,
                self.invokes_authorization,
                self.invokes_execution,
                self.invokes_reasoning,
            )
        ):
            raise ValueError("requirement admission crossed its governed stop")


class GovernedAuthorizedIntellectualGoalRequirementAdmissionV1:
    """Forward one already-existing requirement into canonical Level2B entry."""

    def __init__(
        self,
        productive_entry: _ProductiveRequirementEntry | None = None,
    ) -> None:
        self._productive_entry = (
            productive_entry or GovernedLevel2BProductiveEntryFoundationV1()
        )

    def admit(
        self,
        goal: GovernedAuthorizedIntellectualGoal,
        requirement: DiscriminatingEvidenceRequirement,
        *,
        originating_reasoning_id: str,
    ) -> GovernedAuthorizedIntellectualGoalRequirementAdmissionResult:
        reasoning_id = originating_reasoning_id.strip()
        if not goal.authorized or not goal.read_only or not goal.non_executive:
            raise ValueError("requirement admission requires authorized goal")
        if requirement.source_reference != goal.source_reference:
            raise ValueError("intellectual goal requirement lineage does not match")
        if not reasoning_id:
            raise ValueError("requirement admission requires reasoning lineage")

        productive_result = self._productive_entry.admit(
            requirement,
            originating_reasoning_id=reasoning_id,
        )
        return GovernedAuthorizedIntellectualGoalRequirementAdmissionResult(
            source_goal=goal,
            source_requirement=requirement,
            productive_entry_result=productive_result,
            requirement_id=requirement.requirement_id,
            source_reference=requirement.source_reference,
            world_snapshot_id=requirement.world_snapshot_id,
        )
