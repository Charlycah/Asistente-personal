from datetime import datetime, timezone

import app.current_affairs_router as current_affairs_module
from app.current_affairs_router import CurrentAffairsItem, CurrentAffairsRouter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


class FakeNews:
    def __init__(self, items):
        self.items = tuple(items)
        self.calls = []

    def search(self, query, *, limit=5):
        self.calls.append(query)
        return self.items[:limit]


def _request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m304-1",
        text=text,
    )


def test_m304_1_current_weather_is_not_captured_as_news():
    client = FakeNews(())
    router = CurrentAffairsRouter(client)

    result = router.intercept(
        _request("Hola Roby, cómo está el clima"),
        now=datetime(2026, 7, 22, 12, tzinfo=timezone.utc),
    )

    assert result is None
    assert client.calls == []


def test_m304_1_weather_news_remains_an_explicit_news_request():
    item = CurrentAffairsItem(
        "Alerta meteorológica para Buenos Aires",
        "Fuente",
        "https://example.test/weather-news",
        datetime(2026, 7, 22, 10, tzinfo=timezone.utc),
    )
    client = FakeNews((item,))
    router = CurrentAffairsRouter(client)

    result = router.intercept(
        _request("Roby, noticias del clima"),
        now=datetime(2026, 7, 22, 12, tzinfo=timezone.utc),
    )

    assert result is not None
    assert client.calls


def test_m304_1_generic_relevant_news_only_accepts_local_today():
    today = CurrentAffairsItem(
        "Una noticia importante de hoy",
        "Fuente de hoy",
        "https://example.test/today",
        datetime(2026, 7, 22, 11, tzinfo=timezone.utc),
    )
    yesterday_local = CurrentAffairsItem(
        "Una noticia importante de ayer",
        "Fuente de ayer",
        "https://example.test/yesterday",
        datetime(2026, 7, 22, 1, tzinfo=timezone.utc),
    )
    router = CurrentAffairsRouter(FakeNews((today, yesterday_local)))

    result = router.intercept(
        _request("Roby, tenés alguna noticia relevante?"),
        now=datetime(2026, 7, 22, 14, tzinfo=timezone.utc),
    )

    assert result is not None
    assert "Una noticia importante de hoy" in result.response_text
    assert "Una noticia importante de ayer" not in result.response_text
    assert "hoy, 08:00" in result.response_text


def test_m304_1_news_today_abstains_instead_of_using_old_items():
    old = CurrentAffairsItem(
        "Una noticia vieja",
        "Fuente vieja",
        "https://example.test/old",
        datetime(2026, 7, 20, 12, tzinfo=timezone.utc),
    )
    router = CurrentAffairsRouter(FakeNews((old,)))

    result = router.intercept(
        _request("Roby, hay alguna noticia relevante?"),
        now=datetime(2026, 7, 22, 14, tzinfo=timezone.utc),
    )

    assert result is not None
    assert "No encontré publicaciones suficientemente recientes" in result.response_text
    assert "Una noticia vieja" not in result.response_text


def test_m304_2_timezone_falls_back_without_tzdata(monkeypatch):
    current_affairs_module._argentina_timezone.cache_clear()

    def missing_timezone(_key):
        raise current_affairs_module.ZoneInfoNotFoundError

    monkeypatch.setattr(current_affairs_module, "ZoneInfo", missing_timezone)
    fallback = current_affairs_module._argentina_timezone()

    assert fallback.utcoffset(None).total_seconds() == -3 * 60 * 60
    current_affairs_module._argentina_timezone.cache_clear()
