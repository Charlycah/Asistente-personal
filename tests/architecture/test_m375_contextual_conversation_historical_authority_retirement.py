from __future__ import annotations

from pathlib import Path

from app.context_continuity_runtime import OfficialContextContinuityRuntimeGateway
from core.conversation_strategy import ConversationContext
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)

ROOT = Path(__file__).resolve().parents[2]


def test_m375_retirement_preserves_current_continuity() -> None:
    assert not (ROOT / "core/contextual_conversation.py").exists()
    assert not (ROOT / "tests/test_m375_contextual_conversation.py").exists()
    assert not (ROOT / "docs/M375_CONTEXTUAL_CONVERSATION.md").exists()
    assert (
        ROOT
        / "docs/history/legacy-conversation/M375_CONTEXTUAL_CONVERSATION.md"
    ).exists()

    assert OfficialContextContinuityRuntimeGateway is not None
    assert enrich_with_recent_conversation_context is not None
    assert ConversationContext is not None

    runtime_factory = (ROOT / "app/runtime_root_factory.py").read_text(
        encoding="utf-8"
    )
    assert "OfficialContextContinuityRuntimeGateway()" in runtime_factory
    assert 'name="conversation.context_continuity_runtime"' in runtime_factory

    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    current_boundary = rules.split(
        "## M375 Historical Context Authority Retirement Boundary", maxsplit=1
    )[1]
    assert "ConversationContextAuthority" in current_boundary
    assert "retired" in current_boundary
