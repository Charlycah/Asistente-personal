from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityRegistryManager,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


class EvidenceAcquisitionPlanningStatus(StrEnum):
    PLANNABLE = "plannable"
    PARTIALLY_PLANNABLE = "partially_plannable"
    AMBIGUOUS = "ambiguous"
    NO_CAPABILITY_AVAILABLE = "no_capability_available"


@dataclass(frozen=True)
class EvidenceCapabilityCandidate:
    evidence_description: str
    capability_name: str
    capability_kind: str
    risk: str
    permission_scope: str
    requires_confirmation: bool
    declared_evidence_output: str
    enabled: bool
    selected_for_execution: bool = False
    authorized_for_execution: bool = False
    executed: bool = False

    def __post_init__(self) -> None:
        for value, label in (
            (self.evidence_description, "evidence description"),
            (self.capability_name, "capability name"),
            (self.declared_evidence_output, "declared evidence output"),
        ):
            if not value.strip():
                raise ValueError(f"candidate {label} must not be blank")
        if any(
            (
                self.selected_for_execution,
                self.authorized_for_execution,
                self.executed,
            )
        ):
            raise ValueError("planning candidates cannot authorize or execute")


@dataclass(frozen=True)
class EvidenceAcquisitionPlanningReport:
    plan_id: str
    status: EvidenceAcquisitionPlanningStatus
    requirement_id: str
    hypothesis_ids: tuple[str, str]
    source_reference: str
    world_snapshot_id: str
    candidates: tuple[EvidenceCapabilityCandidate, ...]
    unmatched_evidence_descriptions: tuple[str, ...]
    ambiguous_evidence_descriptions: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-evidence-acquisition-planning-v1"
    canonical_authority: str = "planning_foundation"
    read_only: bool = True
    consultative: bool = True
    planning_execution_authorized: bool = False
    creates_questions: bool = False
    acquires_evidence: bool = False
    invokes_capabilities: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.plan_id.startswith("evidence-acquisition-plan-"):
            raise ValueError("evidence acquisition plan identifier is invalid")
        if not self.requirement_id.startswith("discrimination-requirement-"):
            raise ValueError("planning requires a discrimination requirement")
        if len(set(self.hypothesis_ids)) != 2:
            raise ValueError("planning requires two distinct hypotheses")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("planning must preserve source lineage")
        if self.canonical_authority != "planning_foundation":
            raise ValueError("evidence acquisition planning must preserve authority")
        if not self.read_only or not self.consultative or any(
            (
                self.planning_execution_authorized,
                self.creates_questions,
                self.acquires_evidence,
                self.invokes_capabilities,
                self.modifies_memory,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("evidence acquisition planning violates governed limits")


class GovernedEvidenceAcquisitionPlanner:
    """Read-only planner over explicit M62 capability evidence declarations."""

    CANONICAL_AUTHORITY = "planning_foundation"

    def __init__(self, registry: CapabilityRegistryManager) -> None:
        self._registry = registry

    def plan(
        self,
        requirement: DiscriminatingEvidenceRequirement,
    ) -> EvidenceAcquisitionPlanningReport:
        if not requirement.read_only or any(
            (
                requirement.creates_acquisition_plan,
                requirement.acquires_evidence,
                requirement.creates_question,
                requirement.modifies_memory,
                requirement.executes_actions,
            )
        ):
            raise ValueError("planning requires a governed read-only requirement")

        candidates: list[EvidenceCapabilityCandidate] = []
        unmatched: list[str] = []
        ambiguous: list[str] = []
        for description in requirement.missing_evidence_descriptions:
            matches = self._matching_capabilities(description)
            if not matches:
                unmatched.append(description)
                continue
            if len(matches) > 1:
                ambiguous.append(description)
            candidates.extend(
                self._candidate(description, descriptor, output)
                for descriptor, output in matches
            )

        status = self._status(
            total=len(requirement.missing_evidence_descriptions),
            matched=len(requirement.missing_evidence_descriptions) - len(unmatched),
            ambiguous=bool(ambiguous),
        )
        fingerprint = sha256(
            repr(
                (
                    requirement.requirement_id,
                    requirement.source_reference,
                    requirement.world_snapshot_id,
                    tuple(
                        (
                            item.evidence_description,
                            item.capability_name,
                            item.declared_evidence_output,
                        )
                        for item in candidates
                    ),
                    tuple(unmatched),
                    tuple(ambiguous),
                )
            ).encode("utf-8")
        ).hexdigest()
        return EvidenceAcquisitionPlanningReport(
            plan_id=f"evidence-acquisition-plan-{fingerprint[:24]}",
            status=status,
            requirement_id=requirement.requirement_id,
            hypothesis_ids=requirement.hypothesis_ids,
            source_reference=requirement.source_reference,
            world_snapshot_id=requirement.world_snapshot_id,
            candidates=tuple(candidates),
            unmatched_evidence_descriptions=tuple(unmatched),
            ambiguous_evidence_descriptions=tuple(ambiguous),
            source_fingerprint=fingerprint,
        )

    def _matching_capabilities(
        self,
        description: str,
    ) -> tuple[tuple[CapabilityDescriptor, str], ...]:
        normalized = self._normalize(description)
        matches: list[tuple[CapabilityDescriptor, str]] = []
        for descriptor in self._registry.capabilities.values():
            if not descriptor.enabled:
                continue
            for output in descriptor.evidence_outputs:
                if self._normalize(output) == normalized:
                    matches.append((descriptor, output))
        return tuple(
            sorted(matches, key=lambda item: (item[0].name, item[1]))
        )

    @staticmethod
    def _candidate(
        description: str,
        descriptor: CapabilityDescriptor,
        output: str,
    ) -> EvidenceCapabilityCandidate:
        return EvidenceCapabilityCandidate(
            evidence_description=description,
            capability_name=descriptor.name,
            capability_kind=descriptor.normalized_kind.value,
            risk=descriptor.normalized_risk.value,
            permission_scope=descriptor.normalized_permission_scope.value,
            requires_confirmation=descriptor.requires_confirmation,
            declared_evidence_output=output,
            enabled=descriptor.enabled,
        )

    @staticmethod
    def _status(
        *,
        total: int,
        matched: int,
        ambiguous: bool,
    ) -> EvidenceAcquisitionPlanningStatus:
        if ambiguous:
            return EvidenceAcquisitionPlanningStatus.AMBIGUOUS
        if matched == 0:
            return EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE
        if matched < total:
            return EvidenceAcquisitionPlanningStatus.PARTIALLY_PLANNABLE
        return EvidenceAcquisitionPlanningStatus.PLANNABLE

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.casefold().split())
