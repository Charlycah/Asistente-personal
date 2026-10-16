from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.capability_registry import CapabilityRegistryManager
from core.evidence_acquisition_planning import (
    EvidenceAcquisitionPlanningReport,
    EvidenceAcquisitionPlanningStatus,
    EvidenceCapabilityCandidate,
    GovernedEvidenceAcquisitionPlanner,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


@dataclass(frozen=True)
class GovernedEvidenceAcquisitionProductiveConsumption:
    """Read-only productive exposure of one governed evidence-acquisition plan."""

    requirement_id: str
    planning_report: EvidenceAcquisitionPlanningReport
    status: EvidenceAcquisitionPlanningStatus
    candidates: tuple[EvidenceCapabilityCandidate, ...]
    unmatched_evidence_descriptions: tuple[str, ...]
    ambiguous_evidence_descriptions: tuple[str, ...]
    source_reference: str
    world_snapshot_id: str
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-evidence-acquisition-productive-consumption-v1"
    )
    canonical_authority: str = "planning_foundation"
    read_only: bool = True
    consultative: bool = True
    planning_execution_authorized: bool = False
    selects_capability: bool = False
    invokes_capabilities: bool = False
    acquires_evidence: bool = False
    creates_questions: bool = False
    modifies_registry: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.requirement_id != self.planning_report.requirement_id:
            raise ValueError(
                "productive consumption must preserve requirement identity"
            )
        if self.status is not self.planning_report.status:
            raise ValueError("productive consumption must preserve planning status")
        if self.candidates != self.planning_report.candidates:
            raise ValueError("productive consumption cannot rewrite candidates")
        if (
            self.unmatched_evidence_descriptions
            != self.planning_report.unmatched_evidence_descriptions
            or self.ambiguous_evidence_descriptions
            != self.planning_report.ambiguous_evidence_descriptions
        ):
            raise ValueError("productive consumption must preserve planning coverage")
        if (
            self.source_reference != self.planning_report.source_reference
            or self.world_snapshot_id != self.planning_report.world_snapshot_id
        ):
            raise ValueError("productive consumption must preserve source lineage")
        if self.canonical_authority != "planning_foundation":
            raise ValueError("productive consumption must preserve planning authority")
        if not self.read_only or not self.consultative or any(
            (
                self.planning_execution_authorized,
                self.selects_capability,
                self.invokes_capabilities,
                self.acquires_evidence,
                self.creates_questions,
                self.modifies_registry,
                self.modifies_memory,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("productive consumption violates governed limits")
        if any(
            item.selected_for_execution
            or item.authorized_for_execution
            or item.executed
            for item in self.candidates
        ):
            raise ValueError("productive consumption cannot operationalize candidates")


class GovernedEvidenceAcquisitionProductiveConsumptionV1:
    """Compose an existing planning authority into a non-executive product."""

    def __init__(self, registry: CapabilityRegistryManager) -> None:
        self._planner = GovernedEvidenceAcquisitionPlanner(registry)

    def consume(
        self,
        requirement: DiscriminatingEvidenceRequirement,
    ) -> GovernedEvidenceAcquisitionProductiveConsumption:
        planning_report = self._planner.plan(requirement)
        fingerprint = sha256(
            repr(
                (
                    planning_report.plan_id,
                    planning_report.requirement_id,
                    planning_report.status.value,
                    planning_report.source_fingerprint,
                    tuple(
                        (
                            item.evidence_description,
                            item.capability_name,
                            item.declared_evidence_output,
                        )
                        for item in planning_report.candidates
                    ),
                    planning_report.unmatched_evidence_descriptions,
                    planning_report.ambiguous_evidence_descriptions,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedEvidenceAcquisitionProductiveConsumption(
            requirement_id=planning_report.requirement_id,
            planning_report=planning_report,
            status=planning_report.status,
            candidates=planning_report.candidates,
            unmatched_evidence_descriptions=(
                planning_report.unmatched_evidence_descriptions
            ),
            ambiguous_evidence_descriptions=(
                planning_report.ambiguous_evidence_descriptions
            ),
            source_reference=planning_report.source_reference,
            world_snapshot_id=planning_report.world_snapshot_id,
            source_fingerprint=fingerprint,
        )
