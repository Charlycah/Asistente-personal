from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.living_conversation.integration import (
    LivingConversationIntegrationStatus,
    LivingConversationNextMove,
)
from core.living_conversation_runtime_integration import (
    LivingConversationRuntimeContributor,
    LivingConversationRuntimeProjection,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import (
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)
from tests.test_m178_runtime_composition_root import (
    request as pipeline_request,
)

NOW = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


@dataclass
class Source:
    integration: object | None
    calls: int = 0

    def resolve(self, **kwargs):
        self.calls += 1
        return self.integration


def integration(
    *,
    status=LivingConversationIntegrationStatus.READY,
    eligible=None,
    preserve=False,
    prompt="Profundizar con una pregunta breve.",
    owner="Carlos",
):
    is_ready = status is LivingConversationIntegrationStatus.READY
    if eligible is None:
        eligible = is_ready
    if status in {
        LivingConversationIntegrationStatus.PAUSED,
        LivingConversationIntegrationStatus.NOT_APPLICABLE,
    }:
        prompt = None
    return LivingConversationRuntimeProjection(
        owner=owner,
        status=status,
        eligible_for_activation=eligible,
        preserve_user_floor=preserve,
        rhythm="steady",
        selected_prompt=prompt,
        next_move=LivingConversationNextMove.EXPLORE,
        integration_id="integration-1",
        stage_reference_ids=("presence-1", "timing-1"),
        source_kind="test_fixture",
    )


def request():
    return LLMRequest(prompt="Hola", metadata={"original": "yes"})


def contributor(source):
    return LivingConversationRuntimeContributor(source)


def test_ready_integration_contributes_governed_context():
    result = contributor(Source(integration())).contribute(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.APPLIED
    assert "Cadencia conversacional: steady." in result.prompt_lines
    assert "Próximo movimiento conversacional: explore." in result.prompt_lines
    assert result.reference_ids[0] == "integration-1"


def test_preserve_user_floor_adds_non_invasive_instruction():
    result = contributor(Source(integration(preserve=True))).contribute(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert any("Preservar el turno" in line for line in result.prompt_lines)


@pytest.mark.parametrize(
    "status",
    (
        LivingConversationIntegrationStatus.PAUSED,
        LivingConversationIntegrationStatus.NOT_APPLICABLE,
    ),
)
def test_inactive_integration_is_skipped(status):
    result = contributor(Source(integration(status=status))).contribute(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == ("living_conversation_is_inactive",)


def test_review_required_is_skipped():
    result = contributor(
        Source(integration(status=LivingConversationIntegrationStatus.REVIEW_REQUIRED))
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == ("living_conversation_requires_review",)


def test_missing_context_is_skipped_without_reference():
    result = contributor(Source(None)).contribute(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.reference_ids == ()


def test_activation_must_be_explicitly_eligible():
    result = contributor(Source(integration(eligible=False))).contribute(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert result.status is CognitiveRuntimeStageStatus.SKIPPED
    assert result.rationale == ("living_conversation_activation_not_eligible",)


def test_owner_mismatch_is_contained_by_cognitive_orchestrator():
    runtime = CognitiveRuntimeOrchestrator(
        (contributor(Source(integration(owner="Other"))),)
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert result.contributions[0].status is CognitiveRuntimeStageStatus.FAILED


def test_orchestrator_includes_living_conversation_in_prompt():
    runtime = CognitiveRuntimeOrchestrator((contributor(Source(integration())),))
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Hola",
        request=request(),
        now=NOW,
    )
    assert "[Contexto cognitivo gobernado]" in result.request.prompt
    assert "Profundizar con una pregunta breve." in result.request.prompt
    assert result.request.metadata["cognitive_stages"] == "living_conversation"


def test_composition_root_builds_official_living_conversation_contributor():
    source = Source(integration())
    dependencies = RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
        living_conversation_source=source,
    )
    composition = RuntimeCompositionRoot(dependencies).compose()
    prepared = composition.preparation.prepare(pipeline_request())
    assert source.calls == 1
    assert "Cadencia conversacional" in prepared.inference_request.prompt


def test_composition_rejects_non_official_cognitive_runtime_combination():
    dependencies = RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
        cognitive_runtime=SimpleNamespace(enrich=lambda **kwargs: None),
        living_conversation_source=Source(integration()),
    )
    with pytest.raises(TypeError, match="official"):
        RuntimeCompositionRoot(dependencies).compose()
