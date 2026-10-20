"""S4-D7-C.2 RED: canonical operation boundary and historical compatibility.

Contract only. Do not change production code to make this file GREEN yet.
"""

from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 10, 17, tzinfo=timezone.utc)
SOURCE = Path("app/governed_local_library_runtime_wiring.py")


def _intercept_method() -> ast.FunctionDef:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == (
            "GovernedLocalLibraryConversationInterceptionPort"
        ):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "intercept":
                    return child
    raise AssertionError("Missing canonical interceptor")


def test_s4_c2_interceptor_does_not_reach_catalogue_or_selector_internals():
    """Cataloguing and selection remain behind the conversation boundary."""
    method = _intercept_method()
    private_access = []
    for node in ast.walk(method):
        if not isinstance(node, ast.Attribute):
            continue
        if not isinstance(node.value, ast.Attribute):
            continue
        parent = node.value
        if not isinstance(parent.value, ast.Name):
            continue
        if parent.value.id != "self" or parent.attr != "conversation":
            continue
        if node.attr in {"library", "_selector", "max_results"}:
            private_access.append(node.attr)
    assert not private_access, (
        "Interceptor bypasses canonical conversation operation boundary: "
        f"{private_access}"
    )


class _KnowledgeRuntime:
    def assess(self, text: str):
        return SimpleNamespace(
            need=SimpleNamespace(local_documents_available=True)
        )


class _HistoricalConversationPort:
    """Public historical surface; deliberately no library or _selector."""

    def __init__(self):
        self.knowledge_runtime = _KnowledgeRuntime()
        self.calls = []

    def handle_user_request(self, **kwargs):
        self.calls.append(("retrieve", kwargs))
        return SimpleNamespace(
            status=SimpleNamespace(value="no_match"),
            query=kwargs["search_query"],
            bounded=True,
        )

    def handle_admitted_request(self, **kwargs):
        self.calls.append(("follow_up", kwargs))
        raise AssertionError("No follow-up expected")


def test_s4_c2_location_accepts_historical_conversation_surface():
    """An existing public conversation double must not cause AttributeError.

    The future GREEN must route LOCALIZAR through the canonical public
    operation, not silently fall back to content retrieval.
    """
    conversation = _HistoricalConversationPort()
    request = GovernedConversationPipelineRequest(
        owner="owner", session_id="s4-c2", text="Buscá en la biblioteca atlas"
    )
    response = GovernedLocalLibraryConversationInterceptionPort(
        conversation
    ).intercept(request, now=NOW)
    assert response is not None
    assert all(operation != "retrieve" for operation, _ in conversation.calls), (
        "LOCALIZAR must not call content-retrieval handle_user_request"
    )
