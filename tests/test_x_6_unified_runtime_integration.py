from datetime import datetime, timezone
from types import SimpleNamespace

from app.unified_runtime_integration import (
    CameraConversationInterceptionPort,
    MailReaderConversationInterceptionPort,
    UnifiedRuntimeIntegrationGateway,
    VoiceRuntimeConversationInterceptionPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


def request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="household-main",
        text=text,
    )


def test_mail_adapter_is_exposed_as_read_only_conversation_capability():
    class Adapter:
        def read_mail(self, payload):
            assert payload["action"] == "summary"
            assert payload["unread_only"] is True
            return {"natural_summary": "Tenes dos correos nuevos."}

    port = MailReaderConversationInterceptionPort(Adapter())
    result = port.intercept(request("que correos nuevos tengo"), now=NOW)
    assert result.response_text == "Tenes dos correos nuevos."


def test_camera_adapter_is_connected_behind_governed_registry():
    class Adapter:
        def capture(self, payload):
            assert payload == {}
            return {"natural_summary": "Capture una imagen autorizada."}

    port = CameraConversationInterceptionPort(Adapter())
    result = port.intercept(request("captura una imagen"), now=NOW)
    assert "autorizada" in result.response_text


def test_voice_input_and_output_boundaries_are_reused():
    spoken = []
    transcriber = SimpleNamespace(transcribe=lambda: "consulta por voz")
    reader = SimpleNamespace(read=lambda response: spoken.append(response.text))
    port = VoiceRuntimeConversationInterceptionPort(
        transcriber=transcriber,
        response_reader=reader,
        response_factory=lambda text: SimpleNamespace(text=text),
    )
    heard = port.intercept(request("escuchar"), now=NOW)
    read = port.intercept(request("leer en voz alta: hola"), now=NOW)
    assert heard.response_text == "consulta por voz"
    assert read is not None
    assert spoken == ["hola"]


def test_integration_gateway_reports_connected_runtime_surface():
    gateway = UnifiedRuntimeIntegrationGateway(
        ("mail.read", "camera.capture", "voice.input", "voice.output")
    )
    result = gateway.intercept(request("estado de integracion"), now=NOW)
    assert "mail.read" in result.response_text
    snapshot = gateway.snapshot()
    assert snapshot.evaluations == 1
    assert snapshot.handled_turns == 1
