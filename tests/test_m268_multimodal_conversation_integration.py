from datetime import datetime, timezone

from app.multimodal_conversation_integration import MultimodalConversationRequest
from app.runtime_root_factory import build_runtime_root

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


def _runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root().dependencies.multimodal_conversation_runtime


def test_text_and_presence_are_coordinated_without_hardware(monkeypatch, tmp_path):
    runtime = _runtime(monkeypatch, tmp_path)
    result = runtime.evaluate(
        MultimodalConversationRequest(
            owner="Carlos",
            session_id="session-1",
            text="Hola ROBY",
            modalities=("text", "presence"),
        ),
        now=NOW,
    )
    assert result.active_modalities == ("text", "presence")
    assert result.presence_observed is True
    assert result.hardware_access_performed is False


def test_sensitive_modalities_are_withheld_without_consent(monkeypatch, tmp_path):
    runtime = _runtime(monkeypatch, tmp_path)
    result = runtime.evaluate(
        MultimodalConversationRequest(
            owner="Carlos",
            session_id="session-1",
            text="Usá voz y móvil",
            modalities=("voice", "mobile", "ambient"),
        ),
        now=NOW,
    )
    assert result.status == "withheld"
    assert result.active_modalities == ()
    assert result.withheld_modalities == ("voice", "mobile", "ambient")


def test_explicit_consent_enables_declared_modalities_only(monkeypatch, tmp_path):
    runtime = _runtime(monkeypatch, tmp_path)
    result = runtime.evaluate(
        MultimodalConversationRequest(
            owner="Carlos",
            session_id="session-1",
            text="Sesión multimodal",
            modalities=("text", "voice", "mobile", "device"),
            explicit_consent=("voice", "mobile", "device"),
        ),
        now=NOW,
    )
    assert result.active_modalities == ("text", "voice", "mobile", "device")
    assert result.mobile_mode_declared is True
    assert result.automation_performed is False


def test_runtime_reuses_official_component_instances(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    runtime = root.dependencies.multimodal_conversation_runtime
    registration = root.dependencies.official_capability_registry.registration_for(
        "conversation.multimodal_integration"
    )
    assert registration is not None
    assert registration.interceptor is runtime
    assert runtime.device_runtime is root.dependencies.device_runtime


def test_runtime_status_is_explicit_and_observable(monkeypatch, tmp_path):
    runtime = _runtime(monkeypatch, tmp_path)
    runtime.evaluate(
        MultimodalConversationRequest(
            owner="Carlos",
            session_id="session-1",
            text="Hola",
            modalities=("text",),
        ),
        now=NOW,
    )
    assert runtime.snapshot.evaluations == 1
    assert runtime.snapshot.last_status == "ready"
