from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import ConversationOrigin
from app.unified_brain import UnifiedBrain

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


class Turn:
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False


class ConversationGatewayStub:
    def __init__(self, result=None, error: Exception | None = None) -> None:
        self.result = result or Turn()
        self.error = error
        self.calls: list[dict[str, object]] = []

    def submit(self, text: str, **kwargs):
        self.calls.append({"text": text, **kwargs})
        if self.error is not None:
            raise self.error
        return self.result


def test_unified_brain_delegates_one_message_without_transforming_it() -> None:
    expected = Turn()
    gateway = ConversationGatewayStub(result=expected)
    brain = UnifiedBrain(gateway)

    result = brain.process(
        "  mensaje personal sin modificar  ",
        origin=ConversationOrigin.DESKTOP_TEXT,
        session_id="familia",
        now=NOW,
    )

    assert result is expected
    assert gateway.calls == [
        {
            "text": "  mensaje personal sin modificar  ",
            "origin": ConversationOrigin.DESKTOP_TEXT,
            "session_id": "familia",
            "now": NOW,
        }
    ]


def test_unified_brain_preserves_the_official_gateway_identity() -> None:
    gateway = ConversationGatewayStub()

    assert UnifiedBrain(gateway).conversation is gateway


def test_unified_brain_does_not_hide_gateway_failures() -> None:
    expected = RuntimeError("official gateway failed")
    brain = UnifiedBrain(ConversationGatewayStub(error=expected))

    with pytest.raises(RuntimeError) as captured:
        brain.process("mensaje")

    assert captured.value is expected


def test_unified_brain_owns_no_parallel_authority_or_production_wiring() -> None:
    source = (PROJECT_ROOT / "app" / "unified_brain.py").read_text(encoding="utf-8")
    main_source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
    desktop_source = (PROJECT_ROOT / "app" / "desktop_bootstrap.py").read_text(
        encoding="utf-8"
    )

    forbidden_authorities = (
        "OfficialMemoryGateway",
        "CanonicalMemoryFacade",
        "CanonicalDecisionFacade",
        "OfficialRuntimeCapabilityRegistry",
        "RuntimeCompositionRoot",
        "activate_credentials",
    )

    assert all(name not in source for name in forbidden_authorities)
    assert "UnifiedBrain" not in main_source
    assert "UnifiedBrain" not in desktop_source
