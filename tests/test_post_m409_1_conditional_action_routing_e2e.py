from datetime import datetime, timezone

from app.executive_conversation_planner import ExecutiveConversationPlanner
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedConversationPreparation,
    GovernedOperationalConversationPipeline,
)
from core.governed_provider_execution_adapter import GovernedProviderExecutionAdapter
from core.llm_provider import LLMRequest
from tests.test_m173_governed_provider_execution_adapter import (
    RecordingProvider,
    local_route,
)


class RecordingPreparation:
    def __init__(self) -> None:
        self.calls: list[GovernedConversationPipelineRequest] = []

    def prepare(self, request: GovernedConversationPipelineRequest):
        self.calls.append(request)
        return GovernedConversationPreparation(
            owner=request.owner,
            session_id=request.session_id,
            text=request.text,
            provider_route=local_route(),
            inference_request=LLMRequest(prompt=request.text),
        )


def test_hypothetical_reasoning_reaches_normal_provider_path():
    registry = OfficialRuntimeCapabilityRegistry()
    registry.set_planner(ExecutiveConversationPlanner(registry))
    preparation = RecordingPreparation()
    provider = RecordingProvider()
    pipeline = GovernedOperationalConversationPipeline(
        preparation_port=preparation,
        provider_executor=GovernedProviderExecutionAdapter((provider,)),
        operational_interceptor=registry,
    )
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="coowners-main",
        text=(
            "Si el cielo estuvo despejado toda la noche, "
            "¿qué hipótesis sobre el origen del agua perdería fuerza?"
        ),
    )

    result = pipeline.process(request, now=datetime.now(timezone.utc))

    assert result.provider_call_performed
    assert result.preparation is not None
    assert result.preparation.inference_request.prompt == request.text
    assert preparation.calls == [request]
    assert len(provider.calls) == 1
