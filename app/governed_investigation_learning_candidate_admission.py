from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Protocol

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import GovernedReasoningReentryStatus
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryStatus,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureResult,
    GovernedInvestigationReasoningClosureStatus,
)
from app.learning_foundation import LearningFoundation
from core.learning_foundation import LearningCandidate, LearningObservation


class _LearningCandidateBoundary(Protocol):
    def structure_candidate(
        self,
        *,
        subject: str,
        proposed_value: str,
        observations: tuple[LearningObservation, ...],
        confidence: float,
    ) -> LearningCandidate: ...


class GovernedInvestigationLearningCandidateAdmissionStatus(StrEnum):
    ADMITTED = "admitted"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationLearningCandidateAdmissionResult:
    source_closure: GovernedInvestigationReasoningClosureResult
    status: GovernedInvestigationLearningCandidateAdmissionStatus
    source_evidence: GovernedAcquiredEvidenceEnvelope | None
    learning_observation: LearningObservation | None
    learning_candidate: LearningCandidate | None
    rationale_codes: tuple[str, ...]
    schema_version: str = "intel-g5-investigation-learning-candidate-admission-v1"
    canonical_learning_authority: str = "learning_foundation"
    read_only: bool = True
    uses_existing_m369: bool = True
    establishes_truth: bool = False
    accepts_learning: bool = False
    persists_results: bool = False
    writes_memory: bool = False
    writes_knowledge: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("learning admission requires rationale codes")
        if self.canonical_learning_authority != "learning_foundation":
            raise ValueError("learning admission must preserve M369 authority")
        if not self.read_only or not self.uses_existing_m369:
            raise ValueError("learning admission must remain read-only M369 reuse")
        if any(
            (
                self.establishes_truth,
                self.accepts_learning,
                self.persists_results,
                self.writes_memory,
                self.writes_knowledge,
                self.starts_background_process,
            )
        ):
            raise ValueError("learning admission crossed its governed stop")

        admitted = (
            self.status
            is GovernedInvestigationLearningCandidateAdmissionStatus.ADMITTED
        )
        if admitted:
            if self.source_evidence is None:
                raise ValueError("admitted learning requires source evidence")
            if self.learning_observation is None or self.learning_candidate is None:
                raise ValueError("admitted learning requires canonical M369 artifacts")
            if self.learning_observation.source != "governed_investigation_evidence":
                raise ValueError("learning observation provenance is invalid")
            if (
                self.learning_observation.source_reference
                != self.source_evidence.execution_id
            ):
                raise ValueError("learning observation must preserve execution lineage")
            return

        if self.learning_candidate is not None:
            raise ValueError("closed learning admission cannot expose a candidate")


class GovernedInvestigationLearningCandidateAdmissionV1:
    """Admit terminal governed investigation evidence into existing M369.1."""

    def __init__(
        self,
        learning_foundation: _LearningCandidateBoundary | None = None,
    ) -> None:
        self._learning_foundation = learning_foundation or LearningFoundation()

    def admit(
        self,
        closure: GovernedInvestigationReasoningClosureResult,
        *,
        subject: str,
        proposed_value: str,
        confidence: float,
    ) -> GovernedInvestigationLearningCandidateAdmissionResult:
        normalized_subject = subject.strip()
        normalized_value = proposed_value.strip()
        if not normalized_subject or not normalized_value:
            return self._closed_result(
                closure,
                GovernedInvestigationLearningCandidateAdmissionStatus.NOT_ELIGIBLE,
                ("intel_g5:explicit_learning_semantics_required",),
            )
        if not 0.0 <= confidence <= 1.0:
            return self._closed_result(
                closure,
                GovernedInvestigationLearningCandidateAdmissionStatus.NOT_ELIGIBLE,
                ("intel_g5:valid_learning_confidence_required",),
            )

        lineage_error = self._terminal_lineage_error(closure)
        if lineage_error is not None:
            return self._closed_result(
                closure,
                GovernedInvestigationLearningCandidateAdmissionStatus.NOT_ELIGIBLE,
                (lineage_error,),
            )

        evidence = closure.execution_reentry.evidence_envelope
        if evidence is None:
            return self._closed_result(
                closure,
                GovernedInvestigationLearningCandidateAdmissionStatus.NOT_ELIGIBLE,
                ("intel_g5:terminal_acquired_evidence_required",),
            )

        observation = self._observation(evidence, confidence=confidence)
        try:
            candidate = self._learning_foundation.structure_candidate(
                subject=normalized_subject,
                proposed_value=normalized_value,
                observations=(observation,),
                confidence=confidence,
            )
        except (TypeError, ValueError):
            return GovernedInvestigationLearningCandidateAdmissionResult(
                source_closure=closure,
                status=(
                    GovernedInvestigationLearningCandidateAdmissionStatus
                    .REVIEW_REQUIRED
                ),
                source_evidence=evidence,
                learning_observation=observation,
                learning_candidate=None,
                rationale_codes=("intel_g5:canonical_m369_structure_requires_review",),
            )

        return GovernedInvestigationLearningCandidateAdmissionResult(
            source_closure=closure,
            status=GovernedInvestigationLearningCandidateAdmissionStatus.ADMITTED,
            source_evidence=evidence,
            learning_observation=observation,
            learning_candidate=candidate,
            rationale_codes=(
                "intel_g5:terminal_investigation_evidence_admitted",
                "intel_g5:existing_m369_learning_foundation_reused",
                "intel_g5:review_required_stop_preserved",
            ),
        )

    @staticmethod
    def _terminal_lineage_error(
        closure: GovernedInvestigationReasoningClosureResult,
    ) -> str | None:
        execution = closure.execution_reentry
        evidence = execution.evidence_envelope
        reentry = closure.reasoning_reentry
        state = closure.resulting_episode_state

        if closure.status is not GovernedInvestigationReasoningClosureStatus.CLOSED:
            return "intel_g5:terminal_closed_investigation_required"
        if not closure.episode_closed:
            return "intel_g5:closed_episode_marker_required"
        if state.status is not GovernedInvestigationEpisodeStatus.CLOSED:
            return "intel_g5:terminal_episode_state_required"
        if (
            closure.stopping_reason
            is not GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
            or closure.remaining_acquisitions != 0
        ):
            return "intel_g5:terminal_budget_closure_required"
        if (
            execution.status
            is not GovernedInvestigationExecutionReentryStatus.ACQUIRED
            or evidence is None
            or evidence.status is not GovernedLevel2ExecutionStatus.ACQUIRED
        ):
            return "intel_g5:acquired_evidence_required"
        if (
            reentry is None
            or reentry.status is not GovernedReasoningReentryStatus.REEVALUATED
        ):
            return "intel_g5:successful_reasoning_reentry_required"
        if closure.reasoning_reentry_invocation_count != 1:
            return "intel_g5:single_reasoning_reentry_required"
        if closure.episode_record_invocation_count != 1:
            return "intel_g5:single_episode_record_required"

        exact_lineage = all(
            (
                closure.episode_id == execution.episode_id == state.episode_id,
                closure.execution_id == execution.execution_id == evidence.execution_id,
                closure.authorization_id
                == execution.authorization_id
                == evidence.authorization_id
                == reentry.authorization_id,
                closure.requirement_id
                == execution.requirement_id
                == evidence.requirement_id
                == reentry.requirement_id,
                closure.plan_id
                == execution.plan_id
                == evidence.plan_id
                == reentry.plan_id,
                closure.reasoning_reentry_id == reentry.reentry_id,
                closure.source_reference
                == execution.source_reference
                == evidence.source_reference
                == reentry.source_reference,
                closure.world_snapshot_id
                == execution.world_snapshot_id
                == evidence.world_snapshot_id
                == reentry.world_snapshot_id,
                reentry.execution_id == evidence.execution_id,
            )
        )
        if not exact_lineage:
            return "intel_g5:exact_investigation_lineage_required"
        return None

    @staticmethod
    def _observation(
        evidence: GovernedAcquiredEvidenceEnvelope,
        *,
        confidence: float,
    ) -> LearningObservation:
        description = (evidence.evidence_description or "governed evidence").strip()
        statement = f"{description}: {evidence.observed_value!r}"
        fingerprint = sha256(
            repr(
                (
                    evidence.execution_id,
                    evidence.source_fingerprint,
                    statement,
                    confidence,
                )
            ).encode("utf-8")
        ).hexdigest()
        return LearningObservation(
            observation_id=f"investigation-learning-observation-{fingerprint[:16]}",
            statement=statement,
            source="governed_investigation_evidence",
            source_reference=evidence.execution_id,
            confidence=confidence,
        )

    @staticmethod
    def _closed_result(
        closure: GovernedInvestigationReasoningClosureResult,
        status: GovernedInvestigationLearningCandidateAdmissionStatus,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationLearningCandidateAdmissionResult:
        return GovernedInvestigationLearningCandidateAdmissionResult(
            source_closure=closure,
            status=status,
            source_evidence=closure.execution_reentry.evidence_envelope,
            learning_observation=None,
            learning_candidate=None,
            rationale_codes=rationale_codes,
        )
