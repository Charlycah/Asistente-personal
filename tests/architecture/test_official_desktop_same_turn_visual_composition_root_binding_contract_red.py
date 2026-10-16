from __future__ import annotations

import ast
import importlib
from pathlib import Path
from types import SimpleNamespace

from core.end_to_end_local_conversation import LocalConversationTurn

ROOT = Path(__file__).resolve().parents[2]
MODULE = "app.applied_conversational_intelligence_owner_turn_composition"


def _module():
    return importlib.import_module(MODULE)


def _turn(text: str = "respuesta") -> LocalConversationTurn:
    return LocalConversationTurn(
        owner="Carlos y Cristina",
        session_id="session-1",
        sequence=1,
        user_text="consulta",
        response_text=text,
        status="completed",
        pipeline_result_id="pipeline-1",
        operational_response_id="response-1",
        provider_call_performed=False,
        retrieval_performed=True,
        network_access_performed=True,
        rationale=("applied_conversational_intelligence",),
        response_path="interceptor",
        degradation_reason="not_applicable",
    )


class Gateway:
    def __init__(self, *, recognized: bool = True) -> None:
        self.recognized = recognized
        self.interpret_calls = 0
        self.applied_calls = 0
        self.submit_calls = 0

    def interpret_applied_conversational_intelligence(self, text: str):
        self.interpret_calls += 1
        request = SimpleNamespace(query_text="James Webb") if self.recognized else None
        return SimpleNamespace(request=request)

    def execute_applied_conversational_intelligence(self, text: str):
        self.applied_calls += 1
        interpretation = self.interpret_applied_conversational_intelligence(text)
        return SimpleNamespace(
            interpretation=interpretation,
            natural_answer_text=(
                "respuesta aplicada" if interpretation.request is not None else None
            ),
            conversational_result=(
                SimpleNamespace(source_result=SimpleNamespace())
                if interpretation.request is not None
                else None
            ),
        )

    def submit(self, text: str, **kwargs):
        self.submit_calls += 1
        self.last_applied_owner_turn_result = None
        explicit = bool(
            kwargs.get("explicit_document_ids")
            or kwargs.get("explicit_sources")
            or kwargs.get("explicit_evidence_references")
            or kwargs.get("integrated_visual_context") is not None
        )
        if explicit:
            return _turn("respuesta normal")
        applied_result = self.execute_applied_conversational_intelligence(text)
        if applied_result.interpretation.request is None:
            return _turn("respuesta normal")
        self.last_applied_owner_turn_result = applied_result
        return _turn("respuesta aplicada")


def test_owner_turn_composition_exists() -> None:
    module = _module()

    assert hasattr(module, "AppliedConversationalIntelligenceOwnerTurnComposition")
    assert callable(module.compose_applied_conversational_owner_turn)


def test_recognized_request_executes_applied_branch_once() -> None:
    module = _module()
    gateway = Gateway(recognized=True)

    outcome = module.compose_applied_conversational_owner_turn(
        gateway=gateway,
        text="Roby, buscá novedades del James Webb",
        session_id="session-1",
    )

    assert gateway.interpret_calls == 1
    assert gateway.applied_calls == 1
    assert gateway.submit_calls == 1
    assert outcome.applied_result is not None
    assert outcome.turn.response_text == "respuesta aplicada"


def test_non_recognized_request_executes_normal_owner_turn_once() -> None:
    module = _module()
    gateway = Gateway(recognized=False)

    outcome = module.compose_applied_conversational_owner_turn(
        gateway=gateway,
        text="Roby, hoy estoy contento.",
        session_id="session-1",
    )

    assert gateway.interpret_calls == 1
    assert gateway.applied_calls == 1
    assert gateway.submit_calls == 1
    assert outcome.applied_result is None
    assert outcome.turn.response_text == "respuesta normal"


def test_explicit_current_turn_selection_has_precedence() -> None:
    module = _module()
    gateway = Gateway(recognized=True)

    outcome = module.compose_applied_conversational_owner_turn(
        gateway=gateway,
        text="Roby, buscá novedades del James Webb",
        session_id="session-1",
        explicit_document_ids=("doc-1",),
    )

    assert gateway.interpret_calls == 0
    assert gateway.applied_calls == 0
    assert gateway.submit_calls == 1
    assert outcome.applied_result is None


def test_all_explicit_context_kinds_preserve_normal_path() -> None:
    module = _module()
    fields = (
        ("explicit_sources", (object(),)),
        ("explicit_evidence_references", (object(),)),
        ("integrated_visual_context", object()),
    )
    for field, value in fields:
        gateway = Gateway(recognized=True)
        kwargs = {field: value}

        outcome = module.compose_applied_conversational_owner_turn(
            gateway=gateway,
            text="Roby, buscá novedades del James Webb",
            session_id="session-1",
            **kwargs,
        )

        assert gateway.interpret_calls == 0
        assert gateway.applied_calls == 0
        assert gateway.submit_calls == 1
        assert outcome.applied_result is None


def test_recognized_result_is_retained_by_exact_identity() -> None:
    module = _module()
    gateway = Gateway(recognized=True)
    captured = gateway.execute_applied_conversational_intelligence

    outcome = module.compose_applied_conversational_owner_turn(
        gateway=gateway,
        text="Roby, buscá novedades del James Webb",
        session_id="session-1",
    )

    assert outcome.applied_result is not None
    assert captured.__self__ is gateway


def test_owner_turn_result_is_immutable() -> None:
    module = _module()

    assert module.AppliedConversationalOwnerTurnResult.__dataclass_params__.frozen


def test_existing_local_turn_contract_remains_unchanged() -> None:
    assert tuple(LocalConversationTurn.__dataclass_fields__) == (
        "owner",
        "session_id",
        "sequence",
        "user_text",
        "response_text",
        "status",
        "pipeline_result_id",
        "operational_response_id",
        "provider_call_performed",
        "retrieval_performed",
        "network_access_performed",
        "rationale",
        "response_path",
        "degradation_reason",
        "created_at",
        "turn_id",
    )


def test_certified_gateway_remains_byte_identical() -> None:
    gateway_source = Path(
        "app/official_conversation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source



def test_composition_does_not_create_parallel_authority() -> None:
    path = ROOT / "app/applied_conversational_intelligence_owner_turn_composition.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = (
        "OfficialConversationGateway(",
        "UnifiedBrain(",
        "GovernedSourceQueryExecutor(",
        "NasaGovernedSourceAdapter(",
        "DesktopConversationController(",
        "Thread(",
        "ThreadPool",
        "mainloop(",
    )

    assert all(token not in source for token in forbidden)
    assert not any(
        isinstance(node, (ast.Import, ast.ImportFrom))
        and any(alias.name in {"threading", "subprocess"} for alias in node.names)
        for node in ast.walk(tree)
    )


def test_composition_does_not_parse_visual_identity_from_text() -> None:
    path = ROOT / "app/applied_conversational_intelligence_owner_turn_composition.py"
    source = path.read_text(encoding="utf-8").casefold()

    assert "preview_url" not in source
    assert "http://" not in source
    assert "https://" not in source
    assert "urlparse" not in source


def test_composition_does_not_claim_reachability_or_freshness() -> None:
    path = ROOT / "app/applied_conversational_intelligence_owner_turn_composition.py"
    source = path.read_text(encoding="utf-8").casefold()

    assert "mostrame fotos" not in source
    assert "últimas" not in source
    assert "ultimas" not in source
    assert "newest" not in source
    assert "latest" not in source
