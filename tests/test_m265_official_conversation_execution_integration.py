from datetime import datetime, timezone

from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 16, 12, 0, tzinfo=timezone.utc)


def build_root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root()


def test_entry_runtime_exposes_public_classification_contract(monkeypatch, tmp_path):
    root = build_root(monkeypatch, tmp_path)
    runtime = next(
        item.interceptor
        for item in root.dependencies.official_capability_registry.registrations
        if item.descriptor.name == "conversation.entry_runtime"
    )
    snapshot = runtime.evaluate_text("Hola ROBY")
    assert snapshot.kind == "greeting"
    assert snapshot.action == "route_to_greeting"
    assert runtime.snapshot is snapshot


def test_composed_pipeline_executes_m264_for_normal_turn(monkeypatch, tmp_path):
    root = build_root(monkeypatch, tmp_path)
    composition = root.compose()
    runtime = root.dependencies.end_to_end_conversation_runtime
    before = runtime.snapshot.turns
    composition.conversation_pipeline.process(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="m265",
            text="Hola ROBY",
        ),
        now=NOW,
    )
    assert runtime.snapshot.turns == before + 1
    assert composition.conversation_pipeline.last_result.rationale[-1] == (
        "official_conversation_execution_evaluated"
    )


def test_pipeline_reuses_exact_registered_m264_instance(monkeypatch, tmp_path):
    root = build_root(monkeypatch, tmp_path)
    composition = root.compose()
    runtime = root.dependencies.end_to_end_conversation_runtime
    reliability = root.dependencies.conversation_reliability_observability_runtime
    assert composition.conversation_pipeline.conversation_execution is reliability
    assert reliability.conversation_runtime is runtime
    registration = next(
        item
        for item in root.dependencies.official_capability_registry.registrations
        if item.descriptor.name == "conversation.end_to_end_runtime"
    )
    assert registration.interceptor is runtime


def test_context_enrichment_reaches_intelligence_and_cognition(monkeypatch, tmp_path):
    root = build_root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m265-context",
        text="Como evaluas esto?",
        recent_context=(
            ConversationalContextTurn(
                user_text="Estamos auditando ROBY",
                assistant_text="Seguimos con integración operacional",
            ),
        ),
    )
    captured = {}
    original_intelligence = runtime.intelligence_runtime.evaluate_text
    original_cognition = runtime.cognition_runtime.evaluate_text

    def capture_intelligence(**kwargs):
        captured["intelligence"] = kwargs["text"]
        return original_intelligence(**kwargs)

    def capture_cognition(**kwargs):
        captured["cognition"] = kwargs["text"]
        return original_cognition(**kwargs)

    monkeypatch.setattr(
        runtime.intelligence_runtime, "evaluate_text", capture_intelligence
    )
    monkeypatch.setattr(runtime.cognition_runtime, "evaluate_text", capture_cognition)
    result = runtime.evaluate_turn(request, now=NOW)
    assert result.context_applied
    assert captured["intelligence"] != request.text
    assert captured["cognition"] == captured["intelligence"]
    assert "Estamos auditando ROBY" in captured["intelligence"]


def test_real_question_performs_one_governed_reasoning_evaluation(
    monkeypatch, tmp_path
):
    root = build_root(monkeypatch, tmp_path)
    composition = root.compose()
    reasoning = root.dependencies.governed_reasoning_runtime
    before = reasoning.snapshot.evaluations
    composition.conversation_pipeline.process(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="m265-reasoning",
            text="Como evaluas la evidencia?",
        ),
        now=NOW,
    )
    assert reasoning.snapshot.evaluations == before + 1
