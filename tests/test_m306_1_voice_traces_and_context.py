from datetime import datetime, timezone
from pathlib import Path

from app.current_affairs_router import CurrentAffairsRouter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m306-1",
        text=text,
    )


def test_m306_1_personal_question_to_roby_does_not_route_to_news():
    router = CurrentAffairsRouter()

    assert router.intercept(
        _request("como esta roby"), now=datetime.now(timezone.utc)
    ) is None
    assert router.intercept(
        _request("Roby, ¿cómo estás?"), now=datetime.now(timezone.utc)
    ) is None


def test_m306_1_explicit_news_request_still_routes_to_web(monkeypatch):
    router = CurrentAffairsRouter()
    monkeypatch.setattr(router, "_retrieve", lambda *_args, **_kwargs: ())

    result = router.intercept(
        _request("Roby, contame las noticias importantes de hoy"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None


def test_m306_1_desktop_exposes_voice_startup_and_transcription_traces():
    source = (Path(__file__).parents[1] / "app" / "desktop_ui.py").read_text(
        encoding="utf-8"
    )

    assert "worker iniciado" in source
    assert "llamando start()" in source
    assert "start() completado" in source
    assert "esperando audio/transcripción" in source
    assert "texto reconocido:" in source
