from datetime import datetime, timezone

from app.conversation_reliability_observability import (
    OfficialConversationReliabilityObservabilityGateway,
)
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 16, 12, 0, tzinfo=timezone.utc)


def test_m269_is_registered_and_composed_as_official_execution():
    root = build_runtime_root()
    composition = root.compose()
    runtime = root.dependencies.conversation_reliability_observability_runtime

    assert isinstance(runtime, OfficialConversationReliabilityObservabilityGateway)
    assert composition.conversation_pipeline.conversation_execution is runtime
    registry = root.dependencies.official_capability_registry
    registration = registry.registration_for(
        "conversation.reliability_observability_runtime"
    )
    assert registration is not None
    assert registration.interceptor is runtime


def test_m269_correlates_and_completes_real_pipeline_turn():
    root = build_runtime_root()
    composition = root.compose()
    runtime = root.dependencies.conversation_reliability_observability_runtime

    result = composition.conversation_pipeline.process(
        GovernedConversationPipelineRequest(
            owner="Carlos", session_id="m269-session", text="Hola ROBY"
        ),
        now=NOW,
    )
    traces = runtime.traces_for("Carlos", "m269-session")

    assert len(traces) == 1
    trace = traces[0]
    assert trace.status == result.status.value
    assert (
        trace.conversation_id and trace.turn_id and trace.request_id and trace.trace_id
    )
    assert {span.name for span in trace.spans} >= {
        "entry",
        "context",
        "intelligence",
        "provider",
        "retrieval",
        "response_assembly",
    }


def test_m269_contains_conversation_runtime_failure_and_records_degradation():
    class BrokenRuntime:
        def evaluate_turn(self, request, *, now):
            raise RuntimeError("boom")

    runtime = OfficialConversationReliabilityObservabilityGateway(BrokenRuntime())
    request = GovernedConversationPipelineRequest(
        owner="Carlos", session_id="safe", text="Hola"
    )

    assert runtime.evaluate_turn(request, now=NOW) is None
    assert runtime.health.degraded == 1
    assert runtime.health.availability == "available"


def test_m269_isolates_traces_by_owner_and_session():
    root = build_runtime_root()
    composition = root.compose()
    runtime = root.dependencies.conversation_reliability_observability_runtime

    for owner, session in (("Carlos", "one"), ("Ana", "two")):
        composition.conversation_pipeline.process(
            GovernedConversationPipelineRequest(
                owner=owner, session_id=session, text="Hola ROBY"
            ),
            now=NOW,
        )

    assert len(runtime.traces_for("Carlos", "one")) == 1
    assert len(runtime.traces_for("Ana", "two")) == 1
    assert runtime.traces_for("Carlos", "two") == ()


def test_m269_status_and_audit_are_read_only():
    root = build_runtime_root()
    runtime = root.dependencies.conversation_reliability_observability_runtime
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m269",
        text="estado de confiabilidad conversacional",
    )

    response = runtime.intercept(request, now=NOW)

    assert response is not None
    assert "Evaluaciones" in response.response_text
    assert runtime.health.evaluations == 0
