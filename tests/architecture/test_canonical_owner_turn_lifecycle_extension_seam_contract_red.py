from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.governed_source_query import GovernedSourceQuery
from app.official_conversation_gateway import OfficialConversationGateway
from core.end_to_end_local_conversation import LocalConversationTurn

ROOT = Path(__file__).resolve().parents[2]
OLD_GATEWAY_HASH = (
    "0f8896575116a7ebaac908486d897e22c2f6adff59a05b3cc2997d028b5e0b11"
)
BRAIN_HASH = (
    "05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750"
)


class Runtime:
    def __init__(self) -> None:
        self.calls = []

    def converse(self, text: str, **kwargs) -> LocalConversationTurn:
        self.calls.append((text, kwargs))
        return LocalConversationTurn(
            owner="Carlos y Cristina",
            session_id="runtime-session",
            sequence=len(self.calls),
            user_text=text,
            response_text="respuesta normal",
            status="completed",
            pipeline_result_id="runtime-pipeline",
            operational_response_id="runtime-response",
            provider_call_performed=False,
            retrieval_performed=False,
            network_access_performed=False,
            rationale=("runtime",),
            response_path="provider",
            degradation_reason="not_applicable",
        )


class NasaAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        return (
            {
                "external_id": "JWST-LIFECYCLE-001",
                "title": "Nueva observación del James Webb",
                "topics": tuple(topic.value for topic in query.topics),
                "verification": "confirmed",
                "information_kind": "release",
            },
        )


def _gateway() -> tuple[OfficialConversationGateway, Runtime]:
    runtime = Runtime()
    gateway = OfficialConversationGateway(runtime)
    gateway.register_governed_source_query_adapter("nasa", NasaAdapter())
    return gateway, runtime


def _applied_text() -> str:
    return "Roby, buscá novedades del James Webb"


def test_red_recognized_applied_request_is_one_canonical_gateway_turn() -> None:
    gateway, runtime = _gateway()

    turn = gateway.submit(_applied_text(), session_id="applied-session")

    assert runtime.calls == []
    assert turn.response_path == "interceptor"
    assert "applied_conversational_intelligence" in turn.rationale
    assert gateway.snapshot.submitted_turns == 1
    assert gateway.snapshot.last_session_id == "applied-session"


def test_red_exact_applied_result_is_exposed_without_second_execution() -> None:
    gateway, _ = _gateway()
    calls = []
    original = gateway.execute_applied_conversational_intelligence

    def execute_once(text: str):
        result = original(text)
        calls.append(result)
        return result

    gateway.execute_applied_conversational_intelligence = execute_once

    gateway.submit(_applied_text(), session_id="applied-session")

    assert len(calls) == 1
    assert gateway.last_applied_owner_turn_result is calls[0]


def test_red_non_applied_turn_clears_exact_result_exposure() -> None:
    gateway, _ = _gateway()

    gateway.submit(_applied_text(), session_id="applied-session")
    assert gateway.last_applied_owner_turn_result is not None

    gateway.submit("Roby, hoy estoy contento.", session_id="normal-session")

    assert gateway.last_applied_owner_turn_result is None


def test_red_explicit_context_preserves_normal_runtime_path() -> None:
    fields = (
        ("explicit_document_ids", ("doc-1",)),
        ("explicit_sources", (object(),)),
        ("explicit_evidence_references", (object(),)),
        ("integrated_visual_context", object()),
    )
    for field, value in fields:
        gateway, runtime = _gateway()
        applied_calls = []
        original = gateway.execute_applied_conversational_intelligence

        def execute_spy(text: str):
            applied_calls.append(text)
            return original(text)

        gateway.execute_applied_conversational_intelligence = execute_spy
        kwargs = {field: value}

        gateway.submit(_applied_text(), session_id="explicit-session", **kwargs)

        assert applied_calls == []
        assert len(runtime.calls) == 1
        assert gateway.last_applied_owner_turn_result is None


def test_red_applied_turn_uses_common_observer_and_cycle_epilogue() -> None:
    gateway, _ = _gateway()
    observed = []

    turn = gateway.submit_observed(
        _applied_text(),
        session_id="applied-session",
        post_turn_observer=lambda item: observed.append(item),
    )

    assert observed == [turn]
    assert gateway.snapshot.submitted_turns == 1
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()
    assert gateway.target_cognitive_cycle_evidence.latest_cycle is not None


def test_red_applied_failure_uses_existing_failure_closure() -> None:
    gateway, runtime = _gateway()

    def fail(_text: str):
        raise RuntimeError("applied failure")

    gateway.execute_applied_conversational_intelligence = fail

    with pytest.raises(RuntimeError, match="applied failure"):
        gateway.submit(_applied_text(), session_id="failed-session")

    assert runtime.calls == []
    assert gateway.snapshot.submitted_turns == 0
    assert gateway.last_applied_owner_turn_result is None
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()


def test_red_additive_composition_delegates_to_gateway_only() -> None:
    path = ROOT / "app/applied_conversational_intelligence_owner_turn_composition.py"
    source = path.read_text(encoding="utf-8")

    assert ".execute_applied_conversational_intelligence(" not in source
    assert "gateway.submit(" in source
    assert "last_applied_owner_turn_result" in source


def test_red_local_turn_schema_remains_unchanged() -> None:
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


def test_red_unified_brain_remains_byte_identical() -> None:
    payload = (ROOT / "app/unified_brain.py").read_bytes()

    import hashlib

    assert hashlib.sha256(payload).hexdigest() == BRAIN_HASH


def test_red_no_parallel_lifecycle_authority_is_introduced() -> None:
    gateway_source = (
        ROOT / "app/official_conversation_gateway.py"
    ).read_text(encoding="utf-8")
    composition_source = (
        ROOT / "app/applied_conversational_intelligence_owner_turn_composition.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(composition_source)

    assert "class OfficialConversationGateway" not in composition_source
    assert "class UnifiedBrain" not in composition_source
    assert "_submitted_turns +=" not in composition_source
    assert "complete_turn(" not in composition_source
    assert ".seal(" not in composition_source
    assert not any(
        isinstance(node, (ast.Import, ast.ImportFrom))
        and any(alias.name in {"threading", "subprocess"} for alias in node.names)
        for node in ast.walk(tree)
    )
    assert "execute_applied_conversational_intelligence" in gateway_source


def test_red_gateway_hash_migration_is_explicit_not_mechanical() -> None:
    migration_doc = (
        ROOT
        / "docs"
        / (
            "ROBY_XI_2_CANONICAL_OWNER_TURN_LIFECYCLE_EXTENSION_SEAM_"
            "MIGRATION_PRE_RED_RECONCILIATION.md"
        )
    ).read_text(encoding="utf-8")
    gateway_payload = (ROOT / "app/official_conversation_gateway.py").read_bytes()

    import hashlib

    assert OLD_GATEWAY_HASH in migration_doc
    assert hashlib.sha256(gateway_payload).hexdigest() != OLD_GATEWAY_HASH
