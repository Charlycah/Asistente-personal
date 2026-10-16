from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.productive_temporary_rule_intake import (
    ProductiveTemporaryRuleIntakeStatus,
)
from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 8, 17, 23, 30, tzinfo=timezone.utc)
SESSION = "rf-e-reachability-session"
OTHER = "rf-e-reachability-other"
RULE_TEXT = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
CASE_TEXT = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no existe alternativa."
)
INSUFFICIENT_CASE = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no sabemos si existe otra fuente."
)
NEGATIVE_CASE = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder, pero existe otra fuente independiente."
)
CROSS_DOMAIN_CASE = (
    "La aplicación depende exclusivamente del servicio Q para procesar pagos. "
    "El servicio Q está indisponible y no hay alternativa."
)


def _root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root()


def _request(text: str, *, session: str = SESSION, recent_context=()):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session,
        text=text,
        recent_context=recent_context,
    )


def _teach(runtime, *, session: str = SESSION):
    return runtime.evaluate_turn(_request(RULE_TEXT, session=session), now=NOW)


def test_supported_teaching_reaches_intake_without_rerouting(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime

    result = _teach(runtime)

    assert result.entry_action == "route_to_context"
    assert result.productive_intake_observed is True
    assert result.productive_intake_status == "spec_stored"
    assert runtime.snapshot.productive_intake_status == "spec_stored"
    reasoning = root.dependencies.governed_reasoning_runtime
    intake = reasoning.productive_temporary_rule_intake
    assert intake.pending_count(SESSION) == 1


def test_positive_case_reaches_admission_without_rerouting(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime

    _teach(runtime)
    result = runtime.evaluate_turn(
        _request(CASE_TEXT),
        now=NOW + timedelta(minutes=1),
    )

    assert result.entry_action == "route_to_dialogue"
    assert result.productive_intake_status == "rule_admitted"
    intake_result = reasoning.productive_temporary_rule_intake.last_result
    assert intake_result is not None
    assert intake_result.status is ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED
    assert len(reasoning.orchestrator.inference_engine.registry.list()) == 1


def test_cross_domain_case_reaches_same_productive_admission(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime

    _teach(runtime)
    result = runtime.evaluate_turn(
        _request(CROSS_DOMAIN_CASE),
        now=NOW + timedelta(minutes=1),
    )

    assert result.productive_intake_status == "rule_admitted"
    assert len(reasoning.orchestrator.inference_engine.registry.list()) == 1


def test_insufficient_case_reaches_intake_but_never_admits(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime

    _teach(runtime)
    result = runtime.evaluate_turn(
        _request(INSUFFICIENT_CASE),
        now=NOW + timedelta(minutes=1),
    )

    assert result.productive_intake_status in {
        "case_insufficient",
        "case_unsupported",
    }
    assert reasoning.productive_temporary_rule_intake.pending_count(SESSION) == 1
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_negative_case_reaches_intake_but_never_admits(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime

    _teach(runtime)
    result = runtime.evaluate_turn(
        _request(NEGATIVE_CASE),
        now=NOW + timedelta(minutes=1),
    )

    assert result.productive_intake_status == "case_unsupported"
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_other_session_cannot_consume_pending_teaching(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime

    _teach(runtime)
    result = runtime.evaluate_turn(
        _request(CASE_TEXT, session=OTHER),
        now=NOW + timedelta(minutes=1),
    )

    assert result.productive_intake_status == "no_change"
    intake = reasoning.productive_temporary_rule_intake
    assert intake.pending_count(SESSION) == 1
    assert intake.pending_count(OTHER) == 0
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_ordinary_comment_is_observed_as_no_change(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime

    result = runtime.evaluate_turn(
        _request("La estación sigue funcionando normalmente."),
        now=NOW,
    )

    assert result.productive_intake_observed is True
    assert result.productive_intake_status == "no_change"


def test_reasoning_route_observes_productive_intake_exactly_once(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime
    calls: list[str] = []
    original = reasoning.observe_productive_temporary_rule_intake

    def capture(**kwargs):
        calls.append(kwargs["text"])
        return original(**kwargs)

    monkeypatch.setattr(reasoning, "observe_productive_temporary_rule_intake", capture)
    result = runtime.evaluate_turn(
        _request("Como evaluas esta evidencia?"),
        now=NOW,
    )

    assert result.entry_action == "route_to_reasoning"
    assert calls == ["Como evaluas esta evidencia?"]


def test_productive_intake_observes_raw_turn_not_enriched_prompt(monkeypatch, tmp_path):
    root = _root(monkeypatch, tmp_path)
    runtime = root.dependencies.end_to_end_conversation_runtime
    reasoning = root.dependencies.governed_reasoning_runtime
    seen: list[str] = []
    original = reasoning.observe_productive_temporary_rule_intake

    def capture(**kwargs):
        seen.append(kwargs["text"])
        return original(**kwargs)

    monkeypatch.setattr(reasoning, "observe_productive_temporary_rule_intake", capture)
    context = (
        ConversationalContextTurn(
            user_text="Texto anterior que no debe entrar al intake.",
            assistant_text="Respuesta anterior irrelevante para el intake.",
        ),
    )
    runtime.evaluate_turn(
        _request(RULE_TEXT, recent_context=context),
        now=NOW,
    )

    assert seen == [RULE_TEXT]
