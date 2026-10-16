from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from core.end_to_end_local_conversation import (
    EndToEndLocalConversation,
    EndToEndLocalConversationConfig,
    LocalConversationTurnStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.knowledge_source_policy import KnowledgeSourceKind
from core.local_runtime_bootstrap import (
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from core.operational_acceptance_suite import (
    OperationalAcceptanceCheck,
    OperationalAcceptanceReport,
    OperationalAcceptanceStatus,
    OperationalAcceptanceSuite,
)
from core.runtime_composition_root import (
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from core.tool_gateway import ToolCapability, ToolGatewayManager
from core.tool_runtime_integration import ToolRuntimeIntegration, ToolRuntimeStatus
from tests.test_m171_knowledge_retrieval_execution import FakeRetriever
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)
from tests.test_m190_living_conversation_runtime_integration import (
    Source as LivingSource,
)
from tests.test_m190_living_conversation_runtime_integration import integration
from tests.test_m191_reasoning_runtime_integration import (
    Source as ReasoningSource,
)
from tests.test_m191_reasoning_runtime_integration import reasoning_result
from tests.test_m192_planning_runtime_integration import Source as PlanningSource
from tests.test_m192_planning_runtime_integration import plan
from tests.test_m193_reflection_runtime_integration import Source as ReflectionSource
from tests.test_m193_reflection_runtime_integration import reflection
from tests.test_m194_executive_cognitive_runtime import Source as ExecutiveSource
from tests.test_m194_executive_cognitive_runtime import coordination

NOW = datetime(2026, 7, 13, 18, 0, tzinfo=timezone.utc)


def build_runtime(tmp_path, *, provider=None, session_id="acceptance-main"):
    provider = provider or RecordingProvider()
    memory = MemoryRuntimeIntegration(
        MemoryRuntimeConfig(root_path=tmp_path / "memory")
    )
    gateway = ToolGatewayManager()
    gateway.register_capability(
        ToolCapability("echo", "Eco local"),
        lambda payload: {"echo": payload["value"]},
    )
    tools = ToolRuntimeIntegration(gateway)
    dependencies = RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(provider,),
        retrievers={
            KnowledgeSourceKind.INTERNAL: FakeRetriever(content="acceptance evidence")
        },
        memory_runtime=memory,
        living_conversation_source=LivingSource(integration()),
        governed_reasoning_source=ReasoningSource(reasoning_result()),
        executive_planning_source=PlanningSource(plan()),
        adaptive_reflection_source=ReflectionSource(reflection()),
        executive_coordination_source=ExecutiveSource(coordination()),
        tool_runtime=tools,
    )
    bootstrap = LocalRuntimeBootstrap(
        root=RuntimeCompositionRoot(dependencies),
        config=LocalRuntimeBootstrapConfig(
            owner="Carlos",
            session_id=session_id,
            state_path=tmp_path / session_id / "runtime.json",
        ),
    )
    runtime = EndToEndLocalConversation(
        bootstrap=bootstrap,
        config=EndToEndLocalConversationConfig(
            journal_path=tmp_path / session_id / "turns.jsonl",
            trace_path=tmp_path / session_id / "traces.jsonl",
        ),
    )
    return runtime, provider, memory, tools


def test_acceptance_suite_reports_all_checks_as_passed():
    report = OperationalAcceptanceSuite(
        (("one", lambda: True), ("two", lambda: 1 == 1))
    ).run()
    assert report.passed
    assert report.failed_checks == ()


def test_acceptance_suite_contains_exceptions_without_private_details():
    def failure():
        raise RuntimeError("private detail")

    report = OperationalAcceptanceSuite((("contained", failure),)).run()
    assert not report.passed
    assert report.failed_checks[0].detail == "RuntimeError"
    assert "private detail" not in report.failed_checks[0].detail


def test_acceptance_report_requires_unique_checks():
    with pytest.raises(ValueError, match="unique"):
        OperationalAcceptanceReport(
            (
                OperationalAcceptanceCheck("same", True),
                OperationalAcceptanceCheck("Same", True),
            )
        )


def test_check_exposes_normalized_status():
    assert (
        OperationalAcceptanceCheck("ok", True).status
        is OperationalAcceptanceStatus.PASSED
    )
    assert (
        OperationalAcceptanceCheck("bad", False).status
        is OperationalAcceptanceStatus.FAILED
    )


def test_full_runtime_starts_and_composes_all_cognitive_stages(tmp_path):
    runtime, _, _, _ = build_runtime(tmp_path)
    composition = runtime.bootstrap.start(now=NOW)
    prepared = composition.preparation.prepare(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="acceptance-main",
            text="Ayudame a resolver esto",
        )
    )
    prompt = prepared.inference_request.prompt
    assert "Cadencia conversacional" in prompt
    assert "Conclusión gobernada" in prompt
    assert "Plan ejecutivo" in prompt
    assert "Reflexión adaptativa" in prompt
    assert "Coordinación ejecutiva gobernada" in prompt


def test_complete_operational_turn_reaches_provider_and_persists(tmp_path):
    runtime, provider, _, _ = build_runtime(tmp_path)
    runtime.bootstrap.start(now=NOW)
    turn = runtime.converse("Ayudame a resolver esto", now=NOW)
    assert turn.status is LocalConversationTurnStatus.COMPLETED
    assert len(provider.calls) == 1
    assert len(runtime.history) == 1
    assert len(runtime.traces) == 1


def test_operational_prompt_contains_all_official_cognitive_stages(tmp_path):
    runtime, provider, _, _ = build_runtime(tmp_path)
    runtime.bootstrap.start(now=NOW)
    runtime.converse("Ayudame a resolver esto", now=NOW)
    prompt = provider.calls[0].prompt
    expected = (
        "Cadencia conversacional",
        "Conclusión gobernada",
        "Plan ejecutivo",
        "Reflexión adaptativa",
        "Coordinación ejecutiva gobernada",
    )
    assert all(fragment in prompt for fragment in expected)


def test_explicit_read_only_tool_runs_inside_full_runtime(tmp_path):
    runtime, provider, _, tools = build_runtime(tmp_path)
    runtime.bootstrap.start(now=NOW)
    turn = runtime.converse('/tool echo {"value":"ok"}', now=NOW)
    assert turn.status is LocalConversationTurnStatus.COMPLETED
    assert tools.last_context is not None
    assert tools.last_context.status is ToolRuntimeStatus.EXECUTED
    assert "Resultado gobernado de herramienta local" in provider.calls[0].prompt


def test_turn_trace_preserves_non_mutating_execution_boundary(tmp_path):
    runtime, _, _, _ = build_runtime(tmp_path)
    runtime.bootstrap.start(now=NOW)
    runtime.converse("Ayudame a resolver esto", now=NOW)
    terminal = runtime.traces[0].events[1]
    assert terminal.provider_call_performed
    assert not terminal.platform_mutation_performed


def test_memory_learning_and_recall_survive_runtime_recreation(tmp_path):
    first, _, memory, _ = build_runtime(tmp_path)
    first.bootstrap.start(now=NOW)
    first.converse(
        "En ROBY usamos Ruff para validar milestones",
        now=NOW,
    )
    first.bootstrap.stop(now=NOW + timedelta(seconds=1))

    second, provider, _, _ = build_runtime(tmp_path, session_id="acceptance-main")
    second.bootstrap.start(now=NOW + timedelta(seconds=2))
    second.converse(
        "Recordemos Ruff en milestones",
        now=NOW + timedelta(seconds=3),
    )
    assert memory.private_store("Carlos").count() >= 1
    assert provider.calls


def test_session_sequence_continues_after_restart(tmp_path):
    first, _, _, _ = build_runtime(tmp_path)
    first.bootstrap.start(now=NOW)
    assert first.converse("Primer turno", now=NOW).sequence == 1
    first.bootstrap.stop(now=NOW + timedelta(seconds=1))
    second, _, _, _ = build_runtime(tmp_path)
    second.bootstrap.start(now=NOW + timedelta(seconds=2))
    turn = second.converse(
        "Segundo turno",
        now=NOW + timedelta(seconds=3),
    )
    assert turn.sequence == 2


def test_runtime_state_is_stopped_cleanly(tmp_path):
    runtime, _, _, _ = build_runtime(tmp_path)
    runtime.bootstrap.start(now=NOW)
    state = runtime.bootstrap.stop(now=NOW + timedelta(seconds=1))
    assert state.status.value == "stopped"
    assert not runtime.bootstrap.is_running


def test_provider_failure_is_contained_and_traced(tmp_path):
    provider = RecordingProvider(error=RuntimeError("offline private detail"))
    runtime, _, _, _ = build_runtime(tmp_path, provider=provider)
    runtime.bootstrap.start(now=NOW)
    turn = runtime.converse("Hola", now=NOW)
    assert turn.status is LocalConversationTurnStatus.FAILED
    assert runtime.traces[0].events[1].status.value == "failed"
    assert "private detail" not in str(runtime.traces[0].events[1])


def test_acceptance_observation_does_not_repeat_provider_execution(tmp_path):
    runtime, provider, _, _ = build_runtime(tmp_path)
    runtime.bootstrap.start(now=NOW)
    runtime.converse("Hola", now=NOW)
    _ = runtime.history
    _ = runtime.traces
    _ = runtime.bootstrap.state
    assert len(provider.calls) == 1


def test_acceptance_report_can_summarize_real_runtime(tmp_path):
    runtime, provider, _, _ = build_runtime(tmp_path)
    runtime.bootstrap.start(now=NOW)
    turn = runtime.converse("Hola", now=NOW)
    report = OperationalAcceptanceSuite(
        (
            ("runtime_running", lambda: runtime.bootstrap.is_running),
            ("turn_completed", lambda: turn.status.value == "completed"),
            ("provider_called_once", lambda: len(provider.calls) == 1),
            ("turn_persisted", lambda: len(runtime.history) == 1),
            ("trace_persisted", lambda: len(runtime.traces) == 1),
        )
    ).run()
    assert report.passed
