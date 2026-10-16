from __future__ import annotations

import ast
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import CognitiveCycleNodeState

ROOT = Path(__file__).resolve().parents[2]


class Turn:
    response_text = "respuesta normal"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False
    response_path = "pipeline"
    degradation_reason = "not_applicable"


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def converse(self, text: str, **kwargs) -> Turn:
        self.calls.append((text, kwargs))
        return Turn()


def test_explicit_deliberation_is_productively_intercepted_without_runtime() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit("¿A o B?", session_id="main")

    assert runtime.calls == []
    assert turn.response_path == "interceptor"
    assert turn.status == "completed"
    assert turn.provider_call_performed is False
    assert turn.retrieval_performed is False
    assert turn.network_access_performed is False
    assert turn.pipeline_result_id.startswith("decision-advisory-")
    assert turn.operational_response_id.startswith("decision-advisory-response-")
    assert "requiere más revisión" in turn.response_text
    assert "decisión sigue siendo tuya" in turn.response_text
    assert "explicit_human_decision_deliberation" in turn.rationale
    assert "governed_decision_advisory" in turn.rationale
    assert "human_decision_preserved" in turn.rationale


def test_identification_keeps_precedence_over_deliberation_interceptor() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)

    class ProducerMustNotRun:
        def analyze(self, text: str):
            raise AssertionError(
                f"deliberation producer ran for identification: {text}"
            )

    gateway._explicit_deliberation_producer = ProducerMustNotRun()
    turn = gateway.submit("Confirmo que soy Carlos", session_id="main")

    assert turn.pipeline_result_id.startswith("identity-")
    assert runtime.calls == []


def test_non_explicit_ambiguous_and_insufficient_forms_keep_runtime_path() -> None:
    for text in ("mensaje normal", "¿A o el otro?", "¿Qué me conviene?"):
        runtime = RuntimeStub()
        gateway = OfficialConversationGateway(runtime)
        turn = gateway.submit(text, session_id="main")
        assert len(runtime.calls) == 1
        assert runtime.calls[0][0] == text
        assert turn.response_text == "respuesta normal"


def test_external_evidence_forces_safe_v1_runtime_fallback() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    external = (object(),)

    turn = gateway.submit("¿A o B?", session_id="main", external_evidence=external)

    assert len(runtime.calls) == 1
    assert runtime.calls[0][1]["external_evidence"] == external
    assert turn.response_text == "respuesta normal"


def test_now_is_preserved_for_runtime_fallback_but_not_needed_for_interceptor() -> None:
    from datetime import datetime, timezone

    now = datetime(2026, 8, 12, 21, 0, tzinfo=timezone.utc)
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)

    advisory = gateway.submit("¿A o B?", session_id="main", now=now)
    assert advisory.created_at == now
    assert runtime.calls == []

    gateway.submit("mensaje normal", session_id="main", now=now)
    assert runtime.calls[-1][1]["now"] == now


def test_gateway_epilogue_and_cycle_sealing_are_preserved_for_interceptor() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())

    gateway.submit("¿A o B?", session_id="decision-session")

    assert gateway.snapshot.submitted_turns == 1
    assert gateway.snapshot.last_session_id == "decision-session"
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.node("conversation_ingress").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert cycle.node("perception_and_evidence").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )


def test_post_turn_observer_still_runs_on_advisory_interceptor() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    observed = []

    turn = gateway.submit_observed(
        "¿A o B?",
        session_id="main",
        post_turn_observer=lambda item: observed.append(item),
    )

    assert observed == [turn]


def test_gateway_calls_canonical_advisory_once_and_never_runs_runtime() -> None:
    runtime = RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    original = gateway._canonical_decision

    class DecisionSpy:
        def __init__(self) -> None:
            self.calls = 0

        def advise(self, options, **kwargs):
            self.calls += 1
            return original.advise(options, **kwargs)

    spy = DecisionSpy()
    gateway._canonical_decision = spy

    gateway.submit("¿A o B?", session_id="main")

    assert spy.calls == 1
    assert runtime.calls == []


def test_gateway_source_preserves_one_official_boundary_and_no_new_binding() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    assert "CanonicalDecisionFacade().bind" not in source
    assert "UnifiedCognitiveCoordinator(" not in source
    assert "DecisionDeliberationRuntime" not in source
    assert "_runtime.converse" in source
    constructors = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert constructors == [52]


def test_frozen_producer_adapter_and_m391_6_are_not_modified_by_wiring_delta() -> None:
    gateway_source = (ROOT / "app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "ExplicitHumanDecisionDeliberationEvidenceProducer" in gateway_source
    assert "ExplicitDeliberationDecisionOptionAdapter" in gateway_source
    assert "organization=None" in gateway_source
    assert "scenarios=None" in gateway_source
    assert "causal=None" in gateway_source
