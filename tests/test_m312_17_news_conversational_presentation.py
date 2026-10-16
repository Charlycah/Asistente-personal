from datetime import datetime, timedelta, timezone

from app.current_affairs_router import CurrentAffairsItem, CurrentAffairsRouter
from app.proactive_verified_runtime import ProactiveVerifiedRuntime
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 24, 12, tzinfo=timezone.utc)
URL = "https://news.google.com/rss/articles/example?oc=5"


class NewsClient:
    def search(self, query, *, limit=5):
        del query, limit
        return (
            CurrentAffairsItem(
                title="Una noticia relevante de hoy",
                source="Medio Ejemplo",
                url=URL,
                published_at=NOW - timedelta(minutes=20),
            ),
        )


def request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m312-17",
        text=text,
    )


def test_normal_news_response_never_exposes_the_url():
    router = CurrentAffairsRouter(NewsClient())

    result = router.intercept(request("noticias relevantes de hoy"), now=NOW)

    assert result is not None
    assert URL not in result.response_text
    assert "Enlace:" not in result.response_text


def test_source_followup_returns_names_without_links():
    router = CurrentAffairsRouter(NewsClient())
    router.intercept(request("noticias relevantes de hoy"), now=NOW)

    result = router.intercept(request("cuál es la fuente"), now=NOW)

    assert result is not None
    assert result.response_text == "Medio Ejemplo"
    assert URL not in result.response_text


def test_link_followup_returns_only_the_link():
    router = CurrentAffairsRouter(NewsClient())
    router.intercept(request("noticias relevantes de hoy"), now=NOW)

    result = router.intercept(request("pasame el enlace"), now=NOW)

    assert result is not None
    assert result.response_text == URL


def test_proactive_news_message_hides_the_link():
    message = ProactiveVerifiedRuntime._render_news(NewsClient().search("x")[0])

    assert URL not in message
    assert "Enlace:" not in message
    assert "Fuente: Medio Ejemplo" in message
