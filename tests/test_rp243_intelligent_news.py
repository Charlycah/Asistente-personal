from datetime import datetime, timedelta, timezone

from app.intelligent_news import (
    IntelligentNewsEditor,
    NewsCategory,
    NewsDelivery,
    NewsItem,
    NewsSource,
)

NOW = datetime(2026, 7, 20, 15, tzinfo=timezone.utc)


def item(
    title: str,
    *,
    source: str = "Agencia Uno",
    domain: str = "agencia.example",
    official: bool = False,
    age_hours: int = 1,
    summary: str = "",
) -> NewsItem:
    news_source = NewsSource(
        name=source,
        url=f"https://{domain}/rss",
        official=official,
    )
    return NewsItem(
        title=title,
        summary=summary,
        source=news_source,
        url=f"https://{domain}/noticia",
        published_at=NOW - timedelta(hours=age_hours),
    )


def test_deduplicates_same_story_and_preserves_traceability() -> None:
    editor = IntelligentNewsEditor()
    result = editor.edit(
        (
            item("Alerta roja por tormenta severa en Buenos Aires"),
            item(
                "Buenos Aires bajo alerta roja por tormenta severa",
                source="Agencia Dos",
                domain="dos.example",
            ),
        ),
        now=NOW,
    )

    assert len(result) == 1
    assert result[0].source_count == 2
    assert result[0].traceability == ("Agencia Uno", "Agencia Dos")


def test_local_severe_weather_with_two_sources_interrupts() -> None:
    result = IntelligentNewsEditor().edit(
        (
            item("Alerta roja por tormenta severa en Buenos Aires"),
            item(
                "Buenos Aires bajo alerta roja por tormenta severa",
                source="Servicio oficial",
                domain="oficial.gob.ar",
                official=True,
            ),
        ),
        now=NOW,
    )

    assert result[0].category is NewsCategory.WEATHER
    assert result[0].delivery is NewsDelivery.INTERRUPT
    assert result[0].relevance_score >= 80


def test_unconfirmed_urgent_story_does_not_interrupt() -> None:
    result = IntelligentNewsEditor().edit(
        (item("Alerta roja por tormenta severa en Buenos Aires"),),
        now=NOW,
    )

    assert result[0].delivery is NewsDelivery.DAILY_BRIEFING


def test_official_source_can_confirm_urgent_story_by_itself() -> None:
    result = IntelligentNewsEditor().edit(
        (
            item(
                "Evacuación por incendio fuera de control en Buenos Aires",
                source="Defensa Civil",
                domain="defensacivil.gob.ar",
                official=True,
            ),
        ),
        now=NOW,
    )

    assert result[0].category is NewsCategory.EMERGENCY
    assert result[0].delivery is NewsDelivery.INTERRUPT


def test_science_story_goes_to_daily_briefing() -> None:
    result = IntelligentNewsEditor().edit(
        (
            item(
                "Nuevo descubrimiento científico sobre el espacio",
                source="Revista Ciencia",
            ),
        ),
        now=NOW,
    )

    assert result[0].category is NewsCategory.SCIENCE
    assert result[0].delivery is NewsDelivery.SILENT


def test_health_story_goes_to_daily_briefing_when_official() -> None:
    result = IntelligentNewsEditor().edit(
        (
            item(
                "Salud informa nuevas medidas de prevención del dengue",
                source="Ministerio de Salud",
                domain="salud.gob.ar",
                official=True,
            ),
        ),
        now=NOW,
    )

    assert result[0].category is NewsCategory.HEALTH
    assert result[0].delivery is NewsDelivery.DAILY_BRIEFING


def test_low_value_viral_story_stays_silent() -> None:
    result = IntelligentNewsEditor().edit(
        (item("Rumor viral sobre una celebridad de reality"),),
        now=NOW,
    )

    assert result[0].delivery is NewsDelivery.SILENT


def test_stale_and_future_items_are_discarded() -> None:
    editor = IntelligentNewsEditor()
    stale = item("Noticia económica antigua", age_hours=72)
    future = NewsItem(
        title="Noticia futura",
        summary="",
        source=NewsSource("Fuente", "https://source.example/rss"),
        url="https://source.example/future",
        published_at=NOW + timedelta(minutes=1),
    )

    assert editor.edit((stale, future), now=NOW) == ()


def test_disabled_sources_are_discarded() -> None:
    disabled = NewsSource("Fuente", "https://source.example/rss", enabled=False)
    candidate = NewsItem(
        title="Alerta meteorológica en Buenos Aires",
        summary="",
        source=disabled,
        url="https://source.example/news",
        published_at=NOW,
    )

    assert IntelligentNewsEditor().edit((candidate,), now=NOW) == ()


def test_results_are_ordered_by_delivery_and_relevance() -> None:
    result = IntelligentNewsEditor().edit(
        (
            item("Rumor viral sobre una celebridad"),
            item(
                "Alerta roja por tornado en Buenos Aires",
                source="Servicio oficial",
                domain="smn.gob.ar",
                official=True,
            ),
        ),
        now=NOW,
    )

    assert result[0].delivery is NewsDelivery.INTERRUPT
    assert result[-1].delivery is NewsDelivery.SILENT
