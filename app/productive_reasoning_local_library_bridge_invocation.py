from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)
from core.governed_reasoning.hypothesis_deepening import GovernedHypothesisDeepener
from core.llm_provider import LLMRequest

from .cognitive_evidence_local_library_bridge import (
    GovernedCognitiveEvidenceLibraryRequest,
    GovernedCognitiveEvidenceLibraryResult,
)
from .governed_cap11_one_step_continuation import (
    GovernedCAP11OneStepContinuationCoordinatorV1,
    GovernedCAP11OneStepContinuationResult,
)
from .governed_explanatory_model_investigation_reentry import (
    GovernedExplanatoryModelInvestigationReentryStatus,
)
from .governed_local_evidence_reasoning_reentry import (
    GovernedLocalEvidenceReasoningReentryRequest,
    GovernedLocalEvidenceReasoningReentryResult,
    GovernedLocalEvidenceReasoningReentryV1,
)
from .governed_local_library_runtime_wiring import (
    GovernedLocalLibraryRuntimeProvisionStatus,
    GovernedLocalLibraryRuntimeWiring,
)
from .governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeTransition,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from .governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway


class GovernedProductiveReasoningLibraryInvocationStatus(str, Enum):
    INVOKED = "invoked"
    LIBRARY_UNAVAILABLE = "library_unavailable"
    NO_REASONING_EPISODE = "no_reasoning_episode"
    NO_INVESTIGATION_REENTRY = "no_investigation_reentry"
    NOT_ADMITTED = "not_admitted"
    LINEAGE_MISMATCH = "lineage_mismatch"


@dataclass(frozen=True)
class GovernedProductiveReasoningLibraryInvocationResult:
    status: GovernedProductiveReasoningLibraryInvocationStatus
    turn_id: str
    reasoning_id: str | None = None
    requirement_id: str | None = None
    bridge_result: GovernedCognitiveEvidenceLibraryResult | None = None
    episode_transition: GovernedInvestigationEpisodeTransition | None = None
    local_reasoning_reentry: GovernedLocalEvidenceReasoningReentryResult | None = None
    requirement_admission: object | None = None
    cap11_continuation: GovernedCAP11OneStepContinuationResult | None = None


class GovernedProductiveReasoningLibraryBridgeContributorV1:
    """Connect one admitted same-turn reasoning requirement to CAP-17."""

    name = "local_library_evidence"

    _NOT_ADMITTED_REENTRY_STATUSES = (
        GovernedExplanatoryModelInvestigationReentryStatus.NO_DISCRIMINATING_INQUIRY,
        GovernedExplanatoryModelInvestigationReentryStatus.AMBIGUOUS_INQUIRY,
        GovernedExplanatoryModelInvestigationReentryStatus.REVIEW_REQUIRED,
    )

    def __init__(
        self,
        *,
        reasoning_runtime: OfficialGovernedReasoningRuntimeGateway,
        library_runtime: GovernedLocalLibraryRuntimeWiring,
        reasoning_reentry: GovernedLocalEvidenceReasoningReentryV1,
        episode_boundary: GovernedMultiStepInvestigationEpisodeBoundaryV1 | None = None,
    ) -> None:
        self.reasoning_runtime = reasoning_runtime
        self.library_runtime = library_runtime
        self.reasoning_reentry = reasoning_reentry
        self.episode_boundary = (
            episode_boundary or GovernedMultiStepInvestigationEpisodeBoundaryV1()
        )
        self._cap11_continuation_coordinator: (
            GovernedCAP11OneStepContinuationCoordinatorV1 | None
        ) = None
        self.last_result: GovernedProductiveReasoningLibraryInvocationResult | None = (
            None
        )

    def bind_cap11_one_step_continuation(
        self,
        coordinator: GovernedCAP11OneStepContinuationCoordinatorV1,
    ) -> None:
        """Bind the CAP-11 continuation coordinator."""
        self._cap11_continuation_coordinator = coordinator

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del request
        result = self.consume(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        if (
            result.status
            is not GovernedProductiveReasoningLibraryInvocationStatus.INVOKED
        ):
            return CognitiveRuntimeContribution(
                stage=self.name,
                status=CognitiveRuntimeStageStatus.SKIPPED,
                reference_ids=self._references(result),
                rationale=(f"local_library_evidence:{result.status.value}",),
            )

        bridge = result.bridge_result
        if bridge is None:
            raise RuntimeError("invoked local library evidence requires bridge result")
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "La necesidad de evidencia local del razonamiento fue procesada "
                "por la ruta gobernada de Biblioteca.",
            ),
            reference_ids=self._references(result),
            rationale=(f"local_library_evidence:{bridge.status.value}",),
        )

    def consume(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ) -> GovernedProductiveReasoningLibraryInvocationResult:
        if now.tzinfo is None:
            raise ValueError(
                "productive library invocation time must be timezone-aware"
            )
        pipeline_request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        identity = build_governed_conversation_turn_identity(pipeline_request, now)
        episode = self.reasoning_runtime.productive_episode(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if episode is None:
            return self._record(
                GovernedProductiveReasoningLibraryInvocationStatus.NO_REASONING_EPISODE,
                identity.turn_id,
            )

        reentry = self.reasoning_runtime.productive_explanatory_investigation_reentry(
            owner=owner,
            session_id=session_id,
            turn_id=identity.turn_id,
        )
        if reentry is None:
            return self._record(
                (
                    GovernedProductiveReasoningLibraryInvocationStatus.NO_INVESTIGATION_REENTRY
                ),
                identity.turn_id,
                reasoning_id=episode.result.result_id,
            )
        if reentry.status in self._NOT_ADMITTED_REENTRY_STATUSES:
            return self._record(
                GovernedProductiveReasoningLibraryInvocationStatus.NOT_ADMITTED,
                identity.turn_id,
                reasoning_id=episode.result.result_id,
            )
        if (
            reentry.status
            is not GovernedExplanatoryModelInvestigationReentryStatus.ADMITTED
            or reentry.requirement is None
        ):
            return self._record(
                GovernedProductiveReasoningLibraryInvocationStatus.NOT_ADMITTED,
                identity.turn_id,
                reasoning_id=episode.result.result_id,
            )

        requirement = reentry.requirement
        if reentry.originating_reasoning_id != episode.result.result_id:
            return self._record(
                GovernedProductiveReasoningLibraryInvocationStatus.LINEAGE_MISMATCH,
                identity.turn_id,
                reasoning_id=episode.result.result_id,
                requirement_id=requirement.requirement_id,
            )

        provisioned = (
            self.library_runtime.status
            is GovernedLocalLibraryRuntimeProvisionStatus.PROVISIONED
        )
        cognitive_bridge = self.library_runtime.cognitive_bridge
        if not provisioned or cognitive_bridge is None:
            return self._record(
                GovernedProductiveReasoningLibraryInvocationStatus.LIBRARY_UNAVAILABLE,
                identity.turn_id,
                reasoning_id=episode.result.result_id,
                requirement_id=requirement.requirement_id,
            )

        bridge_result = cognitive_bridge.handle(
            GovernedCognitiveEvidenceLibraryRequest(
                owner=owner,
                requirement=requirement,
                internal_confidence=episode.result.decision.confidence_score,
                library_available=provisioned,
            ),
            now=now,
        )
        investigation_entry = reentry.investigation_entry
        if investigation_entry is None or investigation_entry.episode_id is None:
            return self._record(
                GovernedProductiveReasoningLibraryInvocationStatus.NOT_ADMITTED,
                identity.turn_id,
                reasoning_id=episode.result.result_id,
                requirement_id=requirement.requirement_id,
                bridge_result=bridge_result,
            )
        local_reasoning_reentry = self.reasoning_reentry.reenter(
            GovernedLocalEvidenceReasoningReentryRequest(
                owner=owner,
                turn_id=identity.turn_id,
                originating_reasoning_id=episode.result.result_id,
                requirement=requirement,
                episode_id=investigation_entry.episode_id,
                bridge_result=bridge_result,
            ),
            now=now,
        )
        if investigation_entry.episode_state is None:
            return self._record(
                GovernedProductiveReasoningLibraryInvocationStatus.NOT_ADMITTED,
                identity.turn_id,
                reasoning_id=episode.result.result_id,
                requirement_id=requirement.requirement_id,
                bridge_result=bridge_result,
            )
        episode_transition = self.episode_boundary.record_local_evidence_reentry(
            investigation_entry.episode_state,
            local_reasoning_reentry,
        )
        requirement_admission = None
        cap11_continuation = None
        epistemic = self.reasoning_runtime.productive_epistemic_episode(
            owner=owner, session_id=session_id, turn_id=identity.turn_id
        )
        previous_report = None if epistemic is None else epistemic.deepening
        if (
            previous_report is not None
            and requirement.source_report_id == previous_report.report_id
            and local_reasoning_reentry.evidence_id
        ):
            revised_report = (
                GovernedHypothesisDeepener().reassess_with_governed_evidence(
                    previous_report,
                    source_report_id=requirement.source_report_id,
                    evidence_id=local_reasoning_reentry.evidence_id,
                    hypothesis_ids=requirement.hypothesis_ids,
                )
            )
            from .governed_long_horizon_investigation_reassessment_requirement_admission import (  # noqa: E501
                GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1,
            )

            requirement_admission = (
                GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
                .consume_local_reentry(
                    episode_transition,
                    local_reasoning_reentry,
                    revised_report,
                )
            )
            if (
                requirement_admission.eligible_for_existing_planning
                and self._cap11_continuation_coordinator is not None
            ):
                cap11_continuation = self._cap11_continuation_coordinator.consume(
                    requirement_admission,
                    now=now,
                )
        return self._record(
            GovernedProductiveReasoningLibraryInvocationStatus.INVOKED,
            identity.turn_id,
            reasoning_id=episode.result.result_id,
            requirement_id=requirement.requirement_id,
            bridge_result=bridge_result,
            episode_transition=episode_transition,
            local_reasoning_reentry=local_reasoning_reentry,
            requirement_admission=requirement_admission,
            cap11_continuation=cap11_continuation,
        )

    @staticmethod
    def _references(
        result: GovernedProductiveReasoningLibraryInvocationResult,
    ) -> tuple[str, ...]:
        references = (
            result.reasoning_id,
            result.requirement_id,
            (
                None
                if result.bridge_result is None
                else result.bridge_result.source_decision.decision_id
            ),
        )
        return tuple(item for item in references if item)

    def _record(
        self,
        status: GovernedProductiveReasoningLibraryInvocationStatus,
        turn_id: str,
        *,
        reasoning_id: str | None = None,
        requirement_id: str | None = None,
        bridge_result: GovernedCognitiveEvidenceLibraryResult | None = None,
        episode_transition: GovernedInvestigationEpisodeTransition | None = None,
        local_reasoning_reentry: GovernedLocalEvidenceReasoningReentryResult
        | None = None,
        requirement_admission: object | None = None,
        cap11_continuation: GovernedCAP11OneStepContinuationResult | None = None,
    ) -> GovernedProductiveReasoningLibraryInvocationResult:
        result = GovernedProductiveReasoningLibraryInvocationResult(
            status=status,
            turn_id=turn_id,
            reasoning_id=reasoning_id,
            requirement_id=requirement_id,
            bridge_result=bridge_result,
            episode_transition=episode_transition,
            local_reasoning_reentry=local_reasoning_reentry,
            requirement_admission=requirement_admission,
            cap11_continuation=cap11_continuation,
        )
        self.last_result = result
        return result
