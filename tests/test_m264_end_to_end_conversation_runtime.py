from datetime import datetime, timezone

from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 23, 30, tzinfo=timezone.utc)


def request(text: str, recent_context=()):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m264",
        text=text,
        recent_context=recent_context,
    )


def runtime_from_root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    return root, root.dependencies.end_to_end_conversation_runtime


def test_final_runtime_reuses_all_certified_runtime_instances(monkeypatch, tmp_path):
    root, runtime = runtime_from_root(monkeypatch, tmp_path)
    deps = root.dependencies
    assert runtime.entry_runtime is next(
        item.interceptor
        for item in deps.official_capability_registry.registrations
        if item.descriptor.name == "conversation.entry_runtime"
    )
    assert runtime.context_runtime is deps.context_continuity_runtime
    assert runtime.device_runtime is deps.device_runtime
    assert runtime.retrieval_runtime is deps.external_retrieval_runtime
    assert runtime.reasoning_runtime is deps.governed_reasoning_runtime
    assert runtime.cognition_runtime is deps.adaptive_cognition_runtime
    assert runtime.intelligence_runtime is deps.conversation_intelligence_runtime


def test_turn_runs_entry_continuity_and_intelligence(monkeypatch, tmp_path):
    _, runtime = runtime_from_root(monkeypatch, tmp_path)
    result = runtime.evaluate_turn(request("Hola ROBY"), now=NOW)
    assert result.entry_kind == "greeting"
    assert result.entry_action == "route_to_greeting"
    assert result.intelligence_state
    assert runtime.snapshot.turns == 1
    assert runtime.snapshot.integrated_runtimes == 7


def test_question_routes_through_reasoning_and_cognition(monkeypatch, tmp_path):
    _, runtime = runtime_from_root(monkeypatch, tmp_path)
    result = runtime.evaluate_turn(request("Como evaluas la evidencia?"), now=NOW)
    assert result.entry_action == "route_to_reasoning"
    assert result.reasoning_status is not None
    assert result.cognition_status is not None


def test_audit_is_explicit_and_non_executive(monkeypatch, tmp_path):
    _, runtime = runtime_from_root(monkeypatch, tmp_path)
    result = runtime.intercept(
        request("Auditá runtime conversacional end to end"), now=NOW
    )
    assert result is not None
    assert "Runtimes" not in result.response_text
    assert "no ejecutados por la auditoría" in result.response_text


def test_m264_is_registered_last_with_same_instance(monkeypatch, tmp_path):
    root, runtime = runtime_from_root(monkeypatch, tmp_path)
    registry = root.dependencies.official_capability_registry
    registration = registry.registration_for("conversation.end_to_end_runtime")
    assert registration is not None
    assert registration.interceptor is runtime
    assert registry.capability_names[-5:] == (
        "conversation.end_to_end_runtime",
        "conversation.reliability_observability_runtime",
        "retrieval.unified_execution_runtime",
        "capability.governed_routing_runtime",
        "vision.stored_images.read_analyze",
    )
