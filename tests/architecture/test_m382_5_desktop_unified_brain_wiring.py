from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.official_conversation_gateway import ConversationOrigin
from app.runtime_ui_adapter import LocalConversationUIAdapter
from app.unified_brain import UnifiedBrain

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Turn:
    response_text: str = "respuesta sin cambios"
    status: str = "completed"
    session_id: str = "runtime-session"
    provider_call_performed: bool = False
    retrieval_performed: bool = False
    network_access_performed: bool = False


class ConversationRuntimeStub:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def converse(self, text: str) -> Turn:
        self.messages.append(text)
        return Turn()


def test_desktop_adapter_uses_one_brain_over_the_same_official_gateway() -> None:
    adapter = LocalConversationUIAdapter(ConversationRuntimeStub())

    assert isinstance(adapter._brain, UnifiedBrain)
    assert adapter._brain.conversation is adapter.runtime


def test_desktop_brain_wiring_preserves_response_origin_and_session() -> None:
    conversation = ConversationRuntimeStub()
    adapter = LocalConversationUIAdapter(conversation)

    response = adapter.submit_text("  mensaje familiar  ", session_id="familia")
    snapshot = adapter.runtime.snapshot

    assert conversation.messages == ["mensaje familiar"]
    assert response.text == "respuesta sin cambios"
    assert response.status == "completed"
    assert response.session_id == "familia"
    assert snapshot.submitted_turns == 1
    assert snapshot.last_origin is ConversationOrigin.DESKTOP_TEXT
    assert snapshot.last_session_id == "familia"


def test_retired_console_is_physically_outside_desktop_brain_wiring() -> None:
    console_path = PROJECT_ROOT / "app" / "local_conversation_entrypoint.py"
    main_source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    assert not console_path.exists()
    assert "UnifiedBrain" not in main_source


def test_desktop_wiring_adds_no_memory_decision_or_capability_authority() -> None:
    source = (PROJECT_ROOT / "app" / "runtime_ui_adapter.py").read_text(
        encoding="utf-8"
    )
    forbidden_authorities = (
        "OfficialMemoryGateway",
        "CanonicalMemoryFacade",
        "CanonicalDecisionFacade",
        "OfficialRuntimeCapabilityRegistry",
        "RuntimeCompositionRoot",
    )

    assert all(name not in source for name in forbidden_authorities)
