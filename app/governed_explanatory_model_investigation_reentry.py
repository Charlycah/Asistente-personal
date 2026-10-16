from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_explanatory_model_productive_consumption import (
    GovernedExplanatoryModelProductiveConsumption,
)
from app.governed_level2b_productive_entry import (
    GovernedLevel2BProductiveEntryFoundationV1,
    GovernedLevel2BProductiveEntryResult,
    GovernedLevel2BProductiveEntryStatus,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


class GovernedExplanatoryModelInvestigationReentryStatus(StrEnum):
    ADMITTED = "admitted"
    NO_DISCRIMINATING_INQUIRY = "no_discriminating_inquiry"
    AMBIGUOUS_INQUIRY = "ambiguous_inquiry"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedExplanatoryModelInvestigationReentry:
    reentry_id: str
    status: GovernedExplanatoryModelInvestigationReentryStatus
    explanatory_model_id: str
    originating_reasoning_id: str
    requirement: DiscriminatingEvidenceRequirement | None
    investigation_entry: GovernedLevel2BProductiveEntryResult | None
    source_reference: str
    world_snapshot_id: str
    source_fingerprint: str
    canonical_reasoning_authority: str = "governed_reasoning"
    canonical_episode_authority: str = "multistep_investigation_episode_boundary"
    read_only: bool = True
    planning_execution_authorized: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    invokes_capabilities: bool = False
    acquires_evidence: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    creates_learning: bool = False
    starts_background_process: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.reentry_id.startswith("explanatory-investigation-reentry-"):
            raise ValueError("investigation re-entry identifier is invalid")
        if (
            not self.explanatory_model_id.strip()
            or not self.originating_reasoning_id.strip()
        ):
            raise ValueError("investigation re-entry requires exact reasoning lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("investigation re-entry requires source lineage")
        if self.status is GovernedExplanatoryModelInvestigationReentryStatus.ADMITTED:
            if self.requirement is None or self.investigation_entry is None:
                raise ValueError("admitted re-entry requires inquiry and episode entry")
            if (
                self.investigation_entry.status
                is not GovernedLevel2BProductiveEntryStatus.ADMITTED
            ):
                raise ValueError(
                    "admitted re-entry requires governed episode admission"
                )
            if (
                self.investigation_entry.requirement_id
                != self.requirement.requirement_id
            ):
                raise ValueError(
                    "investigation re-entry must preserve requirement identity"
                )
        elif self.investigation_entry is not None:
            raise ValueError("non-admitted re-entry cannot expose an episode entry")
        if self.requirement is not None:
            if self.requirement.source_reference != self.source_reference:
                raise ValueError(
                    "investigation re-entry must preserve source reference"
                )
            if self.requirement.world_snapshot_id != self.world_snapshot_id:
                raise ValueError("investigation re-entry must preserve world snapshot")
        if self.canonical_reasoning_authority != "governed_reasoning":
            raise ValueError("investigation re-entry must preserve reasoning authority")
        if (
            self.canonical_episode_authority
            != "multistep_investigation_episode_boundary"
        ):
            raise ValueError("investigation re-entry must preserve episode authority")
        if not self.read_only or any(
            (
                self.planning_execution_authorized,
                self.invokes_planning,
                self.invokes_authorization,
                self.invokes_execution,
                self.invokes_capabilities,
                self.acquires_evidence,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.creates_learning,
                self.starts_background_process,
                self.grants_authority,
            )
        ):
            raise ValueError("investigation re-entry violates governed limits")


class GovernedExplanatoryModelInvestigationReentryV1:
    """Route one exact discriminating requirement into the existing episode gate."""

    def __init__(
        self,
        entry: GovernedLevel2BProductiveEntryFoundationV1 | None = None,
    ) -> None:
        self._entry = entry or GovernedLevel2BProductiveEntryFoundationV1()

    def consume(
        self,
        explanatory: GovernedExplanatoryModelProductiveConsumption,
        *,
        originating_reasoning_id: str,
    ) -> GovernedExplanatoryModelInvestigationReentry:
        requirements = explanatory.discrimination.discrimination_requirements
        source_reference = explanatory.discrimination.source_reference
        world_snapshot_id = explanatory.discrimination.world_snapshot_id
        if not requirements:
            return self._result(
                explanatory,
                originating_reasoning_id,
                GovernedExplanatoryModelInvestigationReentryStatus.
                NO_DISCRIMINATING_INQUIRY,
                None,
                None,
                source_reference,
                world_snapshot_id,
            )
        if len(requirements) != 1:
            return self._result(
                explanatory,
                originating_reasoning_id,
                GovernedExplanatoryModelInvestigationReentryStatus.AMBIGUOUS_INQUIRY,
                None,
                None,
                source_reference,
                world_snapshot_id,
            )
        requirement = requirements[0]
        entry = self._entry.admit(
            requirement,
            originating_reasoning_id=originating_reasoning_id,
        )
        status = (
            GovernedExplanatoryModelInvestigationReentryStatus.ADMITTED
            if entry.status is GovernedLevel2BProductiveEntryStatus.ADMITTED
            else GovernedExplanatoryModelInvestigationReentryStatus.REVIEW_REQUIRED
        )
        return self._result(
            explanatory,
            originating_reasoning_id,
            status,
            requirement,
            (
                entry
                if status is GovernedExplanatoryModelInvestigationReentryStatus.ADMITTED
                else None
            ),
            source_reference,
            world_snapshot_id,
        )

    @staticmethod
    def _result(
        explanatory: GovernedExplanatoryModelProductiveConsumption,
        originating_reasoning_id: str,
        status: GovernedExplanatoryModelInvestigationReentryStatus,
        requirement: DiscriminatingEvidenceRequirement | None,
        entry: GovernedLevel2BProductiveEntryResult | None,
        source_reference: str,
        world_snapshot_id: str,
    ) -> GovernedExplanatoryModelInvestigationReentry:
        fingerprint = sha256(
            repr(
                (
                    explanatory.model.model_id,
                    originating_reasoning_id,
                    status.value,
                    None if requirement is None else requirement.requirement_id,
                    source_reference,
                    world_snapshot_id,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedExplanatoryModelInvestigationReentry(
            reentry_id=f"explanatory-investigation-reentry-{fingerprint[:24]}",
            status=status,
            explanatory_model_id=explanatory.model.model_id,
            originating_reasoning_id=originating_reasoning_id,
            requirement=requirement,
            investigation_entry=entry,
            source_reference=source_reference,
            world_snapshot_id=world_snapshot_id,
            source_fingerprint=fingerprint,
        )
