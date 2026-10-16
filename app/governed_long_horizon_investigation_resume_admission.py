from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_long_horizon_investigation_continuity import (
    GovernedInvestigationResumeCandidate,
    GovernedInvestigationResumeStatus,
    GovernedPassiveInvestigationCheckpoint,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


class GovernedInvestigationResumeAdmissionStatus(StrEnum):
    ADMITTED = "admitted"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"
    LINEAGE_MISMATCH = "lineage_mismatch"
    REQUIREMENT_MISMATCH = "requirement_mismatch"
    SNAPSHOT_MISMATCH = "snapshot_mismatch"
    BUDGET_EXHAUSTED = "budget_exhausted"


@dataclass(frozen=True)
class GovernedInvestigationResumeAdmission:
    admission_id: str
    thread_id: str
    checkpoint_id: str
    resume_id: str
    episode_id: str
    originating_reasoning_id: str
    requirement: DiscriminatingEvidenceRequirement
    requirement_id: str
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationResumeAdmissionStatus
    rationale_codes: tuple[str, ...]
    eligible_for_existing_planning: bool
    source_fingerprint: str
    schema_version: str = "post-m409.1-long-horizon-resume-admission-v1"
    canonical_planning_authority: str = "planning_foundation"
    read_only: bool = True
    planning_execution_authorized: bool = False
    creates_plans: bool = False
    invokes_capabilities: bool = False
    executes_actions: bool = False
    performs_reasoning: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    starts_background_process: bool = False
    grants_authority: bool = False
    creates_episode: bool = False

    def __post_init__(self) -> None:
        if not self.admission_id.startswith("investigation-resume-admission-"):
            raise ValueError("resume admission identifier is invalid")
        if not self.thread_id.startswith("investigation-thread-"):
            raise ValueError("resume admission requires thread lineage")
        if not self.checkpoint_id.startswith("investigation-checkpoint-"):
            raise ValueError("resume admission requires checkpoint lineage")
        if not self.resume_id.startswith("investigation-resume-"):
            raise ValueError("resume admission requires resume lineage")
        if not self.episode_id.startswith("investigation-episode-"):
            raise ValueError("resume admission requires episode lineage")
        if not self.originating_reasoning_id.strip():
            raise ValueError("resume admission requires reasoning lineage")
        if self.requirement_id != self.requirement.requirement_id:
            raise ValueError("resume admission requirement identity is inconsistent")
        if self.source_reference != self.requirement.source_reference:
            raise ValueError("resume admission requirement source is inconsistent")
        if self.world_snapshot_id != self.requirement.world_snapshot_id:
            raise ValueError("resume admission requirement snapshot is inconsistent")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("resume admission requires rationale codes")
        if not self.source_fingerprint.strip():
            raise ValueError("resume admission requires source fingerprint")
        if self.canonical_planning_authority != "planning_foundation":
            raise ValueError("resume admission must preserve planning authority")
        if self.eligible_for_existing_planning != (
            self.status is GovernedInvestigationResumeAdmissionStatus.ADMITTED
        ):
            raise ValueError("planning eligibility must match admission status")
        if not self.read_only or any(
            (
                self.planning_execution_authorized,
                self.creates_plans,
                self.invokes_capabilities,
                self.executes_actions,
                self.performs_reasoning,
                self.persists_results,
                self.modifies_memory,
                self.modifies_world_model,
                self.modifies_planning,
                self.starts_background_process,
                self.grants_authority,
                self.creates_episode,
            )
        ):
            raise ValueError("resume admission violates governed limits")


class GovernedLongHorizonInvestigationResumeAdmissionV1:
    """Explicit requirement re-binding; stops before Planning."""

    def admit(
        self,
        checkpoint: GovernedPassiveInvestigationCheckpoint,
        resume_candidate: GovernedInvestigationResumeCandidate,
        requirement: DiscriminatingEvidenceRequirement,
    ) -> GovernedInvestigationResumeAdmission:
        status, rationale = self._evaluate(
            checkpoint=checkpoint,
            resume_candidate=resume_candidate,
            requirement=requirement,
        )
        fingerprint = sha256(
            repr(
                (
                    checkpoint.checkpoint_id,
                    checkpoint.thread_id,
                    checkpoint.episode_id,
                    checkpoint.originating_reasoning_id,
                    resume_candidate.resume_id,
                    requirement.requirement_id,
                    requirement.hypothesis_ids,
                    requirement.source_reference,
                    requirement.world_snapshot_id,
                    requirement.known_elements,
                    requirement.missing_evidence_descriptions,
                    requirement.evidence_codes,
                    status.value,
                    rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedInvestigationResumeAdmission(
            admission_id=f"investigation-resume-admission-{fingerprint[:24]}",
            thread_id=checkpoint.thread_id,
            checkpoint_id=checkpoint.checkpoint_id,
            resume_id=resume_candidate.resume_id,
            episode_id=checkpoint.episode_id,
            originating_reasoning_id=checkpoint.originating_reasoning_id,
            requirement=requirement,
            requirement_id=requirement.requirement_id,
            source_reference=requirement.source_reference,
            world_snapshot_id=requirement.world_snapshot_id,
            status=status,
            rationale_codes=rationale,
            eligible_for_existing_planning=(
                status is GovernedInvestigationResumeAdmissionStatus.ADMITTED
            ),
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _evaluate(
        *,
        checkpoint: GovernedPassiveInvestigationCheckpoint,
        resume_candidate: GovernedInvestigationResumeCandidate,
        requirement: DiscriminatingEvidenceRequirement,
    ) -> tuple[
        GovernedInvestigationResumeAdmissionStatus,
        tuple[str, ...],
    ]:
        if resume_candidate.checkpoint_id != checkpoint.checkpoint_id:
            return (
                GovernedInvestigationResumeAdmissionStatus.LINEAGE_MISMATCH,
                (
                    "investigation_resume_admission:checkpoint_lineage_mismatch",
                    "investigation_resume_admission:fail_closed",
                ),
            )
        if resume_candidate.thread_id != checkpoint.thread_id:
            return (
                GovernedInvestigationResumeAdmissionStatus.LINEAGE_MISMATCH,
                (
                    "investigation_resume_admission:thread_lineage_mismatch",
                    "investigation_resume_admission:fail_closed",
                ),
            )
        if (
            resume_candidate.status
            is GovernedInvestigationResumeStatus.SNAPSHOT_REVIEW_REQUIRED
        ):
            return (
                GovernedInvestigationResumeAdmissionStatus.REVIEW_REQUIRED,
                (
                    "investigation_resume_admission:snapshot_review_required",
                    "investigation_resume_admission:not_admitted",
                ),
            )
        if (
            resume_candidate.status
            is GovernedInvestigationResumeStatus.BUDGET_REVIEW_REQUIRED
            or checkpoint.consumed_acquisitions >= checkpoint.max_acquisitions
        ):
            return (
                GovernedInvestigationResumeAdmissionStatus.BUDGET_EXHAUSTED,
                (
                    "investigation_resume_admission:historical_budget_exhausted",
                    "investigation_resume_admission:not_admitted",
                ),
            )
        if (
            resume_candidate.status
            is not GovernedInvestigationResumeStatus.RESUME_CANDIDATE
        ):
            return (
                GovernedInvestigationResumeAdmissionStatus.NOT_ELIGIBLE,
                (
                    "investigation_resume_admission:resume_candidate_not_eligible",
                    "investigation_resume_admission:not_admitted",
                ),
            )
        if not checkpoint.requirement_ids:
            return (
                GovernedInvestigationResumeAdmissionStatus.REQUIREMENT_MISMATCH,
                (
                    "investigation_resume_admission:no_requirement_lineage",
                    "investigation_resume_admission:fail_closed",
                ),
            )
        if requirement.requirement_id != checkpoint.requirement_ids[-1]:
            return (
                GovernedInvestigationResumeAdmissionStatus.REQUIREMENT_MISMATCH,
                (
                    "investigation_resume_admission:current_requirement_mismatch",
                    "investigation_resume_admission:fail_closed",
                ),
            )
        if requirement.source_reference != checkpoint.source_reference:
            return (
                GovernedInvestigationResumeAdmissionStatus.LINEAGE_MISMATCH,
                (
                    "investigation_resume_admission:source_lineage_mismatch",
                    "investigation_resume_admission:fail_closed",
                ),
            )
        previous_snapshot = checkpoint.world_snapshot_ids[-1]
        if (
            resume_candidate.previous_world_snapshot_id != previous_snapshot
            or resume_candidate.current_world_snapshot_id != previous_snapshot
            or requirement.world_snapshot_id != previous_snapshot
        ):
            return (
                GovernedInvestigationResumeAdmissionStatus.SNAPSHOT_MISMATCH,
                (
                    "investigation_resume_admission:same_snapshot_required",
                    "investigation_resume_admission:fail_closed",
                ),
            )
        if not requirement.read_only or any(
            (
                requirement.creates_acquisition_plan,
                requirement.acquires_evidence,
                requirement.creates_question,
                requirement.modifies_memory,
                requirement.executes_actions,
            )
        ):
            return (
                GovernedInvestigationResumeAdmissionStatus.NOT_ELIGIBLE,
                (
                    "investigation_resume_admission:requirement_governance_invalid",
                    "investigation_resume_admission:fail_closed",
                ),
            )
        return (
            GovernedInvestigationResumeAdmissionStatus.ADMITTED,
            (
                "investigation_resume_admission:exact_requirement_rebound",
                "investigation_resume_admission:same_snapshot_lineage_preserved",
                "investigation_resume_admission:eligible_for_existing_planning",
                "investigation_resume_admission:no_planning_performed",
            ),
        )
