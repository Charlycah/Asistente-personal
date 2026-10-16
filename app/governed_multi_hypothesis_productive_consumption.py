from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
    GovernedMultiHypothesisDiscriminationReport,
    GovernedMultiHypothesisDiscriminator,
)


@dataclass(frozen=True)
class GovernedMultiHypothesisProductiveConsumption:
    """Productive read-only exposure of governed hypothesis discrimination."""

    source_report_id: str
    discrimination_report: GovernedMultiHypothesisDiscriminationReport
    discrimination_requirements: tuple[DiscriminatingEvidenceRequirement, ...]
    source_reference: str
    world_snapshot_id: str
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-multi-hypothesis-productive-consumption-v1"
    )
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_questions: bool = False
    creates_acquisition_plans: bool = False
    acquires_evidence: bool = False
    modifies_memory: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.source_report_id.startswith("hypothesis-deepening-"):
            raise ValueError("productive consumption requires deepening lineage")
        if (
            self.source_reference != self.discrimination_report.source_reference
            or self.world_snapshot_id
            != self.discrimination_report.world_snapshot_id
        ):
            raise ValueError("productive consumption must preserve source lineage")
        if (
            self.discrimination_requirements
            != self.discrimination_report.discrimination_requirements
        ):
            raise ValueError("productive consumption cannot rewrite requirements")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("productive consumption must preserve reasoning authority")
        if not self.read_only or not self.consultative or any(
            (
                self.persists_results,
                self.creates_questions,
                self.creates_acquisition_plans,
                self.acquires_evidence,
                self.modifies_memory,
                self.modifies_planning,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("productive consumption violates governed limits")


class GovernedMultiHypothesisProductiveConsumptionV1:
    """Expose existing discrimination productively without operationalizing it."""

    def __init__(
        self,
        discriminator: GovernedMultiHypothesisDiscriminator | None = None,
    ) -> None:
        self._discriminator = discriminator or GovernedMultiHypothesisDiscriminator()

    def consume(
        self,
        report: GovernedHypothesisDeepeningReport,
    ) -> GovernedMultiHypothesisProductiveConsumption:
        discrimination = self._discriminator.compare(report)
        fingerprint = sha256(
            repr(
                (
                    report.report_id,
                    report.source_reference,
                    report.world_snapshot_id,
                    discrimination.source_fingerprint,
                    tuple(
                        item.requirement_id
                        for item in discrimination.discrimination_requirements
                    ),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedMultiHypothesisProductiveConsumption(
            source_report_id=report.report_id,
            discrimination_report=discrimination,
            discrimination_requirements=(
                discrimination.discrimination_requirements
            ),
            source_reference=report.source_reference,
            world_snapshot_id=report.world_snapshot_id,
            source_fingerprint=fingerprint,
        )
