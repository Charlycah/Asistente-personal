from __future__ import annotations

from datetime import datetime, timezone

from core.governed_provider_execution_adapter import (
    GovernedProviderExecutionAdapter,
    LocalProviderExecutionRequest,
)
from core.knowledge_retrieval_execution import (
    KnowledgeRetrievalExecutionGateway,
    KnowledgeRetrievalExecutionRequest,
)
from core.operational_response_assembly import (
    OperationalResponse,
    OperationalResponseAction,
    OperationalResponseAssembler,
    OperationalResponseAssemblyRequest,
    OperationalResponseStatus,
)

from .models import (
    ConversationDegradationReason,
    ConversationResponsePath,
    GovernedConversationPipelineConfig,
    GovernedConversationPipelineRepository,
    GovernedConversationPipelineRequest,
    GovernedConversationPipelineResult,
    GovernedConversationPipelineStatus,
    GovernedConversationPreparationPort,
    GovernedOperationalInterceptionPort,
    InMemoryGovernedConversationPipelineRepository,
    OfficialConversationExecutionPort,
    ResponseOriginMetadata,
)


class GovernedOperationalConversationPipeline:
    """Runs one prepared operational turn through existing governed boundaries."""

    def __init__(
        self,
        *,
        preparation_port: GovernedConversationPreparationPort,
        provider_executor: GovernedProviderExecutionAdapter,
        response_assembler: OperationalResponseAssembler | None = None,
        retrieval_executor: KnowledgeRetrievalExecutionGateway | None = None,
        config: GovernedConversationPipelineConfig | None = None,
        repository: GovernedConversationPipelineRepository | None = None,
        operational_interceptor: GovernedOperationalInterceptionPort | None = None,
        conversation_execution: OfficialConversationExecutionPort | None = None,
        experience_layer: object | None = None,
    ) -> None:
        self.preparation_port = preparation_port
        self.provider_executor = provider_executor
        self.retrieval_executor = retrieval_executor
        self.response_assembler = response_assembler or OperationalResponseAssembler()
        self.config = config or GovernedConversationPipelineConfig()
        self.repository = repository or InMemoryGovernedConversationPipelineRepository()
        self.operational_interceptor = operational_interceptor
        self.conversation_execution = conversation_execution
        self.experience_layer = experience_layer

    @property
    def last_result(self) -> GovernedConversationPipelineResult | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def execute(self, *, owner: str, session_id: str, text: str):
        request = GovernedConversationPipelineRequest(
            owner=owner,
            session_id=session_id,
            text=text,
        )
        return self.process(request).operational_response

    def process(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime | None = None,
    ) -> GovernedConversationPipelineResult:
        created_at = now or datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            raise ValueError("conversation pipeline timestamp must be timezone-aware")
        if not self.config.execution_enabled:
            return self._inactive(request, created_at, "conversation_pipeline_disabled")
        if len(request.text) > self.config.maximum_input_characters:
            return self._inactive(
                request, created_at, "conversation_pipeline_input_limit_exceeded"
            )
        if self.operational_interceptor is not None:
            interception = self.operational_interceptor.intercept(
                request, now=created_at
            )
            if interception is not None:
                return self._intercepted(request, created_at, interception)
        try:
            execution_evaluated = False
            if self.conversation_execution is not None:
                self.conversation_execution.evaluate_turn(request, now=created_at)
                execution_evaluated = True
            prepare_at = getattr(self.preparation_port, "prepare_at", None)
            preparation = (
                prepare_at(request, now=created_at)
                if callable(prepare_at)
                else self.preparation_port.prepare(request)
            )
            self._validate_preparation(request, preparation)
            provider_execution = self.provider_executor.execute(
                LocalProviderExecutionRequest(
                    owner=request.owner,
                    route=preparation.provider_route,
                    inference_request=preparation.inference_request,
                ),
                now=created_at,
            )
            retrieval_execution = None
            if preparation.retrieval_plan is not None and self.config.execute_retrieval:
                if self.retrieval_executor is None:
                    raise RuntimeError("retrieval plan requires an execution gateway")
                retrieval_execution = self.retrieval_executor.execute(
                    KnowledgeRetrievalExecutionRequest(
                        owner=request.owner,
                        plan=preparation.retrieval_plan,
                    ),
                    now=created_at,
                )
            response = self.response_assembler.assemble(
                OperationalResponseAssemblyRequest(
                    owner=request.owner,
                    provider_execution=provider_execution,
                    retrieval_execution=retrieval_execution,
                ),
                now=created_at,
            )
            if self.experience_layer is not None:
                response = self.experience_layer.present_operational_response(
                    response,
                    request=request,
                )
            status = self._status_from_response(response.status)
            rationale = (
                "governed_operational_turn_completed",
                *(
                    ("official_conversation_execution_evaluated",)
                    if execution_evaluated
                    else ()
                ),
            )
        except Exception as exc:
            # ROBY_TEMP_PIPELINE_DIAGNOSTIC
            try:
                import traceback as _diag_traceback
                from pathlib import Path as _DiagPath

                _diag_root = _DiagPath(__file__).resolve().parents[2]
                _diag_log = _diag_root / ".roby/diagnostico_pipeline_documentos.log"

                _diag_lines = [
                    "",
                    "[" + datetime.now(timezone.utc).isoformat() + "]",
                    "origin=governed_operational_conversation_pipeline",
                    "exception_type=" + type(exc).__name__,
                ]

                for _diag_frame in _diag_traceback.extract_tb(exc.__traceback__):
                    _diag_lines.append(
                        f"{_diag_frame.filename}:{_diag_frame.lineno}"
                        f" in {_diag_frame.name}"
                    )

                _diag_log.parent.mkdir(parents=True, exist_ok=True)

                with _diag_log.open("a", encoding="utf-8") as _diag_stream:
                    _diag_stream.write("\n".join(_diag_lines) + "\n")

            except Exception:
                pass
            # END_ROBY_TEMP_PIPELINE_DIAGNOSTIC
            record_failure = getattr(
                self.conversation_execution,
                "record_failure",
                None,
            )
            if callable(record_failure):
                try:
                    record_failure(request, exc)
                except Exception:
                    pass  # Diagnostics must not defeat safe failure containment.
            preparation = None
            provider_execution = None
            retrieval_execution = None
            response = self.response_assembler.assemble(
                OperationalResponseAssemblyRequest(
                    owner=request.owner,
                    provider_execution=None,
                    retrieval_execution=None,
                ),
                now=created_at,
            )
            status = GovernedConversationPipelineStatus.FAILED
            rationale = ("governed_operational_turn_failed_safely",)
        result = GovernedConversationPipelineResult(
            request=request,
            status=status,
            preparation=preparation,
            provider_execution=provider_execution,
            retrieval_execution=retrieval_execution,
            operational_response=response,
            provider_call_performed=response.provider_call_performed,
            retrieval_performed=response.retrieval_performed,
            network_access_performed=response.network_access_performed,
            platform_mutation_performed=False,
            rationale=rationale,
            created_at=created_at,
            response_origin=ResponseOriginMetadata.general_knowledge(),
            response_path=(
                ConversationResponsePath.PROVIDER
                if response.provider_call_performed
                else ConversationResponsePath.DEGRADED
            ),
            degradation_reason=(
                ConversationDegradationReason.NOT_APPLICABLE
                if response.provider_call_performed
                else (
                    ConversationDegradationReason.TURN_FAILED_SAFELY
                    if status is GovernedConversationPipelineStatus.FAILED
                    else ConversationDegradationReason.PROVIDER_RESPONSE_UNAVAILABLE
                )
            ),
        )
        completion = getattr(self.conversation_execution, "complete_turn", None)
        if completion is not None:
            completion(result, now=created_at)
        self.repository.add(result)
        return result

    def _intercepted(self, request, created_at, interception):
        assembly_request = OperationalResponseAssemblyRequest(
            owner=request.owner,
            external_network_access_performed=interception.network_access_performed,
        )
        response = OperationalResponse(
            request=assembly_request,
            status=OperationalResponseStatus.COMPLETED,
            action=OperationalResponseAction.DELIVER_RESPONSE,
            response_text=interception.response_text,
            evidence=(),
            limitations=(),
            provider_execution_id="",
            retrieval_execution_id="",
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=interception.network_access_performed,
            platform_mutation_performed=False,
            rationale=(interception.rationale,),
            created_at=created_at,
        )
        result = GovernedConversationPipelineResult(
            request=request,
            status=GovernedConversationPipelineStatus.COMPLETED,
            preparation=None,
            provider_execution=None,
            retrieval_execution=None,
            operational_response=response,
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=interception.network_access_performed,
            platform_mutation_performed=False,
            rationale=(interception.rationale,),
            created_at=created_at,
            response_origin=interception.origin,
            response_path=ConversationResponsePath.INTERCEPTOR,
            degradation_reason=ConversationDegradationReason.NOT_APPLICABLE,
        )
        self.repository.add(result)
        return result

    def _inactive(self, request, created_at, reason):
        response = self.response_assembler.assemble(
            OperationalResponseAssemblyRequest(owner=request.owner),
            now=created_at,
        )
        result = GovernedConversationPipelineResult(
            request=request,
            status=GovernedConversationPipelineStatus.WITHHELD,
            preparation=None,
            provider_execution=None,
            retrieval_execution=None,
            operational_response=response,
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            platform_mutation_performed=False,
            rationale=(reason,),
            created_at=created_at,
            response_origin=ResponseOriginMetadata(
                origin="inference",
                confidence="withheld",
                freshness="not_applicable",
                verifiable=False,
                abstained=True,
            ),
            response_path=ConversationResponsePath.DEGRADED,
            degradation_reason=(
                ConversationDegradationReason.PIPELINE_DISABLED
                if reason == "conversation_pipeline_disabled"
                else ConversationDegradationReason.INPUT_LIMIT_EXCEEDED
            ),
        )
        self.repository.add(result)
        return result

    @staticmethod
    def _validate_preparation(request, preparation):
        if request.owner.casefold() != preparation.owner.casefold():
            raise ValueError("prepared owner must match pipeline request")
        if request.session_id != preparation.session_id:
            raise ValueError("prepared session must match pipeline request")
        if request.text != preparation.text:
            raise ValueError("prepared text must match pipeline request")

    @staticmethod
    def _status_from_response(status):
        if status is OperationalResponseStatus.COMPLETED:
            return GovernedConversationPipelineStatus.COMPLETED
        if status is OperationalResponseStatus.PARTIAL:
            return GovernedConversationPipelineStatus.PARTIAL
        if status is OperationalResponseStatus.FAILED:
            return GovernedConversationPipelineStatus.FAILED
        return GovernedConversationPipelineStatus.WITHHELD
