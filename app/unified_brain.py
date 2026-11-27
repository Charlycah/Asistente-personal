from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.cognitive_maturity import UnifiedCoordinationEvidenceAdapter
from core.end_to_end_local_conversation import LocalConversationTurn
from core.governed_operational_conversation_pipeline import (
    ConversationDegradationReason,
    ConversationResponsePath,
)

from .cognitive_analysis_authority import (
    CognitiveAnalysisAuthority,
    CognitiveAnalysisResult,
    CognitiveAnalysisStatus,
)
from .official_conversation_gateway import (
    ConversationOrigin,
    OfficialConversationGateway,
)


@dataclass(frozen=True)
class UnifiedBrainSnapshot:
    processed_messages: int
    last_origin: ConversationOrigin | None
    last_session_id: str | None


@dataclass(frozen=True)
class UnifiedBrainDiagnosticSnapshot:
    conversation: UnifiedBrainSnapshot
    reflection: TurnReflectionSnapshot
    fully_observed: bool
    observation_gap: int


@dataclass(frozen=True)
class TurnReflection:
    status: str
    origin: ConversationOrigin
    session_id: str
    response_path: str
    degradation_reason: str
    provider_call_performed: bool
    retrieval_performed: bool
    network_access_performed: bool


@dataclass(frozen=True)
class DegradationReasonBalance:
    pipeline_disabled: int
    input_limit_exceeded: int
    turn_failed_safely: int
    provider_response_unavailable: int
    unknown: int


@dataclass(frozen=True)
class RecoveryBalance:
    provider_recoveries: int
    interceptor_recoveries: int


@dataclass(frozen=True)
class TurnReflectionSnapshot:
    observed_turns: int
    provider_responses: int
    interceptor_responses: int
    degraded_responses: int
    consecutive_degraded_responses: int
    degradation_reasons: DegradationReasonBalance
    recoveries: RecoveryBalance
    last_reflection: TurnReflection | None


class PostTurnReflectionObserver:
    """Observes safe turn metadata without changing or persisting the turn."""

    def __init__(self) -> None:
        self._observed_turns = 0
        self._provider_responses = 0
        self._interceptor_responses = 0
        self._degraded_responses = 0
        self._consecutive_degraded_responses = 0
        self._degradation_reasons = {
            reason: 0
            for reason in ConversationDegradationReason
            if reason is not ConversationDegradationReason.NOT_APPLICABLE
        }
        self._provider_recoveries = 0
        self._interceptor_recoveries = 0
        self._last_reflection: TurnReflection | None = None

    @property
    def snapshot(self) -> TurnReflectionSnapshot:
        return TurnReflectionSnapshot(
            observed_turns=self._observed_turns,
            provider_responses=self._provider_responses,
            interceptor_responses=self._interceptor_responses,
            degraded_responses=self._degraded_responses,
            consecutive_degraded_responses=self._consecutive_degraded_responses,
            degradation_reasons=DegradationReasonBalance(
                pipeline_disabled=self._degradation_reasons[
                    ConversationDegradationReason.PIPELINE_DISABLED
                ],
                input_limit_exceeded=self._degradation_reasons[
                    ConversationDegradationReason.INPUT_LIMIT_EXCEEDED
                ],
                turn_failed_safely=self._degradation_reasons[
                    ConversationDegradationReason.TURN_FAILED_SAFELY
                ],
                provider_response_unavailable=self._degradation_reasons[
                    ConversationDegradationReason.PROVIDER_RESPONSE_UNAVAILABLE
                ],
                unknown=self._degradation_reasons[
                    ConversationDegradationReason.UNKNOWN
                ],
            ),
            recoveries=RecoveryBalance(
                provider_recoveries=self._provider_recoveries,
                interceptor_recoveries=self._interceptor_recoveries,
            ),
            last_reflection=self._last_reflection,
        )

    def observe(
        self,
        turn: LocalConversationTurn,
        *,
        origin: ConversationOrigin,
        session_id: str | None,
    ) -> TurnReflection:
        status = getattr(turn.status, "value", str(turn.status))
        response_path = getattr(
            turn,
            "response_path",
            ConversationResponsePath.DEGRADED,
        )
        response_path = getattr(response_path, "value", str(response_path))
        default_degradation_reason = (
            ConversationDegradationReason.UNKNOWN
            if response_path == ConversationResponsePath.DEGRADED.value
            else ConversationDegradationReason.NOT_APPLICABLE
        )
        degradation_reason = getattr(
            turn,
            "degradation_reason",
            default_degradation_reason,
        )
        degradation_reason = getattr(
            degradation_reason,
            "value",
            str(degradation_reason),
        )
        reflection = TurnReflection(
            status=status,
            origin=origin,
            session_id=session_id or turn.session_id,
            response_path=response_path,
            degradation_reason=degradation_reason,
            provider_call_performed=getattr(
                turn,
                "provider_call_performed",
                False,
            ),
            retrieval_performed=getattr(turn, "retrieval_performed", False),
            network_access_performed=getattr(
                turn,
                "network_access_performed",
                False,
            ),
        )
        self._observed_turns += 1
        if response_path == ConversationResponsePath.PROVIDER.value:
            self._provider_responses += 1
        elif response_path == ConversationResponsePath.INTERCEPTOR.value:
            self._interceptor_responses += 1
        else:
            self._degraded_responses += 1
        if response_path == ConversationResponsePath.DEGRADED.value:
            self._consecutive_degraded_responses += 1
            try:
                counted_reason = ConversationDegradationReason(degradation_reason)
            except ValueError:
                counted_reason = ConversationDegradationReason.UNKNOWN
            if counted_reason is ConversationDegradationReason.NOT_APPLICABLE:
                counted_reason = ConversationDegradationReason.UNKNOWN
            self._degradation_reasons[counted_reason] += 1
        else:
            if self._consecutive_degraded_responses:
                if response_path == ConversationResponsePath.PROVIDER.value:
                    self._provider_recoveries += 1
                elif response_path == ConversationResponsePath.INTERCEPTOR.value:
                    self._interceptor_recoveries += 1
            self._consecutive_degraded_responses = 0
        self._last_reflection = reflection
        return reflection


class UnifiedBrain:
    """Transparent adapter over ROBY's official conversation boundary.

    This first prototype owns no memory, decisions, capabilities, persistence,
    permissions, or lifecycle. It only preserves one future integration seam
    while delegating every message to the already-certified gateway.
    """

    def __init__(
        self,
        conversation: OfficialConversationGateway,
        reflection_observer: PostTurnReflectionObserver | None = None,
        cognitive_analysis: CognitiveAnalysisAuthority | None = None,
    ) -> None:
        self._conversation = conversation
        self._reflection_observer = reflection_observer or PostTurnReflectionObserver()
        self._coordination_evidence = UnifiedCoordinationEvidenceAdapter()
        self._cognitive_analysis = cognitive_analysis or CognitiveAnalysisAuthority()
        self._last_cognitive_analysis: CognitiveAnalysisResult | None = None

    @property
    def conversation(self) -> OfficialConversationGateway:
        return self._conversation

    @property
    def snapshot(self) -> UnifiedBrainSnapshot:
        conversation = self._conversation.snapshot
        return UnifiedBrainSnapshot(
            processed_messages=conversation.submitted_turns,
            last_origin=conversation.last_origin,
            last_session_id=conversation.last_session_id,
        )

    @property
    def reflection_snapshot(self) -> TurnReflectionSnapshot:
        return self._reflection_observer.snapshot

    @property
    def diagnostics(self) -> UnifiedBrainDiagnosticSnapshot:
        conversation = self.snapshot
        reflection = self.reflection_snapshot
        observation_gap = conversation.processed_messages - reflection.observed_turns
        return UnifiedBrainDiagnosticSnapshot(
            conversation=conversation,
            reflection=reflection,
            fully_observed=observation_gap == 0,
            observation_gap=observation_gap,
        )

    @property
    def cognitive_analysis(self) -> CognitiveAnalysisResult | None:
        return self._last_cognitive_analysis

    def process(
        self,
        message: str,
        *,
        origin: ConversationOrigin = ConversationOrigin.INTERNAL,
        session_id: str | None = None,
        now: datetime | None = None,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
        _causal_result_receiver=None,
    ) -> LocalConversationTurn:
        def observe_turn(turn: LocalConversationTurn) -> TurnReflection:
            return self._reflection_observer.observe(
                turn,
                origin=origin,
                session_id=session_id,
            )

        causal_kwargs = (
            {"_causal_result_receiver": _causal_result_receiver}
            if _causal_result_receiver is not None
            else {}
        )
        with self._coordination_evidence.activate():
            submit_observed = getattr(self._conversation, "submit_observed", None)
            has_explicit_selection = bool(
                explicit_document_ids
                or explicit_sources
                or explicit_evidence_references
                or integrated_visual_context is not None
            )
            if callable(submit_observed):
                if has_explicit_selection:
                    turn = submit_observed(
                        message,
                        post_turn_observer=observe_turn,
                        origin=origin,
                        session_id=session_id,
                        now=now,
                        explicit_document_ids=explicit_document_ids,
                        explicit_sources=explicit_sources,
                        explicit_evidence_references=explicit_evidence_references,
                        integrated_visual_context=integrated_visual_context,
                        **causal_kwargs,
                    )
                else:
                    turn = submit_observed(
                        message,
                        post_turn_observer=observe_turn,
                        origin=origin,
                        session_id=session_id,
                        now=now,
                        **causal_kwargs,
                    )
            else:
                if has_explicit_selection:
                    turn = self._conversation.submit(
                        message,
                        origin=origin,
                        session_id=session_id,
                        now=now,
                        explicit_document_ids=explicit_document_ids,
                        explicit_sources=explicit_sources,
                        explicit_evidence_references=explicit_evidence_references,
                        integrated_visual_context=integrated_visual_context,
                        **causal_kwargs,
                    )
                else:
                    turn = self._conversation.submit(
                        message,
                        origin=origin,
                        session_id=session_id,
                        now=now,
                        **causal_kwargs,
                    )
                observe_turn(turn)
        self._analyze_completed_turn()
        return turn

    def _analyze_completed_turn(self) -> None:
        try:
            dossier = self._conversation.cognitive_turn_dossiers.latest_dossier
            if dossier is None:
                raise RuntimeError("sealed cognitive dossier unavailable")
            report = self._cognitive_analysis.analyze(dossier)
        except Exception:
            self._last_cognitive_analysis = CognitiveAnalysisResult(
                status=CognitiveAnalysisStatus.DEGRADED,
                report=None,
                failure_code="analysis:internal_failure",
            )
            return
        self._last_cognitive_analysis = CognitiveAnalysisResult(
            status=CognitiveAnalysisStatus.COMPLETED,
            report=report,
        )
