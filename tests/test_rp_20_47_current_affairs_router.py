from datetime import datetime, timedelta, timezone

from app.current_affairs_router import CurrentAffairsItem, CurrentAffairsRouter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


class FakeNews:
    def __init__(self):
        self.calls = []

    def search(self, query, *, limit=5):
        self.calls.append(query)
        return (
            CurrentAffairsItem(
                "NASA anuncia una nueva etapa de su programa lunar",
                "NASA",
                "https://example.test/nasa",
                datetime(2026, 7, 19, 9, tzinfo=timezone.utc),
            ),
        )


def request(text, session="s1"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session,
        text=text,
    )


def test_latest_nasa_missions_are_routed_to_web():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("qué podés decirme de las últimas misiones de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "publicaciones más recientes" in result.response_text
    assert "NASA anuncia" in result.response_text
    assert client.calls


def test_stable_question_does_not_use_web():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("qué es la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is None
    assert client.calls == []


def test_sports_prediction_requires_current_web_evidence():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("tenés un pronóstico entre Argentina y España, quién gana"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert result.origin is not None
    assert result.origin.origin == "web_recent"
    assert client.calls


def test_cache_avoids_repeated_network_calls():
    client = FakeNews()
    router = CurrentAffairsRouter(client, cache_ttl=timedelta(minutes=15))
    now = datetime(2026, 7, 19, 12, tzinfo=timezone.utc)
    query = request("últimas noticias de la NASA")
    router.intercept(query, now=now)
    router.intercept(query, now=now + timedelta(minutes=2))
    assert len(client.calls) == 1


def test_sources_can_be_recalled_in_same_session():
    router = CurrentAffairsRouter(FakeNews())
    now = datetime(2026, 7, 19, 12, tzinfo=timezone.utc)
    router.intercept(request("últimas noticias de la NASA"), now=now)
    sources = router.intercept(request("de dónde salió eso"), now=now)
    assert sources is not None
    assert sources.response_text == "NASA"


def test_failure_abstains_instead_of_using_model_memory():
    class Broken:
        def search(self, query, *, limit=5):
            raise OSError("offline")

    router = CurrentAffairsRouter(Broken())
    result = router.intercept(
        request("últimas noticias de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "Prefiero no responder de memoria" in result.response_text


def test_generic_whats_new_question_routes_without_known_entity():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("qué hay de nuevo con la misión Artemis"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert client.calls


def test_relative_time_expression_routes_dynamic_topic():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("qué pasó con OpenAI desde ayer"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert client.calls


def test_current_role_question_routes_to_web():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("quién es el actual CEO de Microsoft"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert client.calls


def test_stable_title_with_last_word_does_not_trigger_web():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("de qué trata La última pregunta de Asimov"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is None
    assert client.calls == []


def test_how_is_topic_going_routes_to_current_affairs():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("cómo viene la misión Artemis"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert client.calls


def test_recent_web_answer_has_explicit_origin_metadata():
    from core.governed_operational_conversation_pipeline import (
        ResponseConfidence,
        ResponseOrigin,
    )

    router = CurrentAffairsRouter(FakeNews())
    result = router.intercept(
        request("últimas noticias de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert result.origin.origin is ResponseOrigin.WEB_RECENT
    assert result.origin.confidence is ResponseConfidence.HIGH
    assert result.origin.freshness == "recent"
    assert result.origin.verifiable is True
    assert result.origin.abstained is False


def test_failed_current_search_is_explicitly_abstained():
    from core.governed_operational_conversation_pipeline import (
        ResponseConfidence,
        ResponseOrigin,
    )

    class Broken:
        def search(self, query, *, limit=5):
            raise OSError("offline")

    router = CurrentAffairsRouter(Broken())
    result = router.intercept(
        request("últimas noticias de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert result.origin.origin is ResponseOrigin.WEB_RECENT
    assert result.origin.confidence is ResponseConfidence.WITHHELD
    assert result.origin.abstained is True
    assert result.origin.verifiable is False


def test_conflicting_sources_are_disclosed_and_confidence_is_reduced():
    from core.governed_operational_conversation_pipeline import ResponseConfidence

    class ConflictingNews:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "NASA confirma el lanzamiento de Artemis para agosto",
                    "Agencia A",
                    "https://example.test/a",
                    datetime(2026, 7, 19, 9, tzinfo=timezone.utc),
                ),
                CurrentAffairsItem(
                    "NASA cancela el lanzamiento de Artemis previsto para agosto",
                    "Agencia B",
                    "https://example.test/b",
                    datetime(2026, 7, 19, 10, tzinfo=timezone.utc),
                ),
            )

    router = CurrentAffairsRouter(ConflictingNews())
    result = router.intercept(
        request("últimas noticias de la NASA sobre Artemis"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "versiones contradictorias" in result.response_text
    assert (
        "No voy a presentar una de ellas como un hecho confirmado"
        in result.response_text
    )
    assert "Agencia A" in result.response_text
    assert "Agencia B" in result.response_text
    assert result.origin.confidence is ResponseConfidence.MEDIUM
    assert result.origin.freshness == "recent_but_conflicting"
    assert result.origin.abstained is False


def test_different_sources_without_opposed_claims_remain_high_confidence():
    from core.governed_operational_conversation_pipeline import ResponseConfidence

    class CompatibleNews:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "NASA prepara el lanzamiento de Artemis para agosto",
                    "Agencia A",
                    "https://example.test/a",
                    datetime(2026, 7, 19, 9, tzinfo=timezone.utc),
                ),
                CurrentAffairsItem(
                    "Artemis completa una revisión técnica antes del lanzamiento",
                    "Agencia B",
                    "https://example.test/b",
                    datetime(2026, 7, 19, 10, tzinfo=timezone.utc),
                ),
            )

    router = CurrentAffairsRouter(CompatibleNews())
    result = router.intercept(
        request("últimas noticias de la NASA sobre Artemis"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "versiones contradictorias" not in result.response_text
    assert result.origin.confidence is ResponseConfidence.HIGH


def test_today_discards_articles_older_than_maximum_age():
    class MixedAges:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "NASA informa una novedad de hoy",
                    "NASA",
                    "https://example.test/fresh",
                    datetime(2026, 7, 19, 8, tzinfo=timezone.utc),
                ),
                CurrentAffairsItem(
                    "NASA informa una novedad antigua",
                    "Archivo",
                    "https://example.test/old",
                    datetime(2026, 7, 15, 8, tzinfo=timezone.utc),
                ),
            )

    result = CurrentAffairsRouter(MixedAges()).intercept(
        request("qué noticias hay hoy de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "novedad de hoy" in result.response_text
    assert "novedad antigua" not in result.response_text


def test_explicit_last_hours_abstains_when_every_source_is_too_old():
    class OldOnly:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "OpenAI publica una actualización anterior",
                    "Medio",
                    "https://example.test/old",
                    datetime(2026, 7, 18, 8, tzinfo=timezone.utc),
                ),
            )

    result = CurrentAffairsRouter(OldOnly()).intercept(
        request("noticias de OpenAI en las últimas 6 horas"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "últimas 6 horas" in result.response_text
    assert "información vieja" in result.response_text
    assert result.origin.abstained is True


def test_unknown_publication_date_is_rejected_for_current_information():
    class Undated:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "Microsoft anuncia cambios",
                    "Medio",
                    "https://example.test/undated",
                    None,
                ),
            )

    result = CurrentAffairsRouter(Undated()).intercept(
        request("últimas noticias de Microsoft"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "No encontré publicaciones suficientemente recientes" in result.response_text
    assert result.origin.abstained is True


def test_this_week_accepts_sources_from_recent_days():
    class ThisWeek:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "ESA completa una revisión esta semana",
                    "ESA",
                    "https://example.test/esa",
                    datetime(2026, 7, 14, 12, tzinfo=timezone.utc),
                ),
            )

    result = CurrentAffairsRouter(ThisWeek()).intercept(
        request("qué pasó esta semana con la ESA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "ESA completa" in result.response_text
    assert result.origin.abstained is False


def test_abstention_explains_web_failure_and_required_criterion():
    class Broken:
        def search(self, query, *, limit=5):
            raise OSError("offline")

    result = CurrentAffairsRouter(Broken()).intercept(
        request("últimas noticias de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "Motivo:" in result.response_text
    assert "falló la consulta" in result.response_text
    assert "Criterio no cumplido:" in result.response_text
    assert "Cómo podemos seguir:" in result.response_text
    assert result.rationale.endswith("web_retrieval_failed")


def test_abstention_explains_how_many_sources_were_stale_or_undated():
    class InvalidFreshness:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "NASA publica un informe antiguo",
                    "Archivo",
                    "https://example.test/old",
                    datetime(2026, 7, 10, 8, tzinfo=timezone.utc),
                ),
                CurrentAffairsItem(
                    "NASA publica una noticia sin fecha",
                    "Medio",
                    "https://example.test/undated",
                    None,
                ),
            )

    result = CurrentAffairsRouter(InvalidFreshness()).intercept(
        request("qué noticias hay hoy de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "1 fuente(s) eran más antiguas" in result.response_text
    assert "1 fuente(s) no informaban fecha" in result.response_text
    assert (
        "al menos una fuente con fecha conocida dentro de hoy"
        in result.response_text
    )
    assert result.rationale.endswith("freshness_requirements_not_met")


def test_empty_results_explain_that_no_usable_sources_were_found():
    class Empty:
        def search(self, query, *, limit=5):
            return ()

    result = CurrentAffairsRouter(Empty()).intercept(
        request("últimas noticias de OpenAI"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert "no devolvió publicaciones utilizables" in result.response_text
    assert "tema más específico" in result.response_text
    assert result.rationale.endswith("no_sources_found")


def test_elliptical_entity_followup_reuses_current_affairs_context():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    now = datetime(2026, 7, 19, 12, tzinfo=timezone.utc)

    router.intercept(request("últimas noticias de la NASA"), now=now)
    result = router.intercept(request("¿y SpaceX?"), now=now)

    assert result is not None
    assert any("SpaceX" in call for call in client.calls)
    assert len(client.calls) == 2


def test_temporal_followup_reuses_previous_topic():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    now = datetime(2026, 7, 19, 12, tzinfo=timezone.utc)

    router.intercept(request("últimas noticias de OpenAI"), now=now)
    result = router.intercept(request("¿y esta semana?"), now=now)

    assert result is not None
    assert any("OpenAI" in call and "esta semana" in call for call in client.calls)


def test_abstention_reason_can_be_recalled_from_context():
    class Empty:
        def search(self, query, *, limit=5):
            return ()

    router = CurrentAffairsRouter(Empty())
    now = datetime(2026, 7, 19, 12, tzinfo=timezone.utc)
    router.intercept(request("últimas noticias de OpenAI"), now=now)

    result = router.intercept(request("¿por qué no respondiste?"), now=now)

    assert result is not None
    assert "no devolvió publicaciones utilizables" in result.response_text
    assert result.origin.abstained is True


def test_current_affairs_context_is_isolated_by_session():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    now = datetime(2026, 7, 19, 12, tzinfo=timezone.utc)

    router.intercept(request("últimas noticias de la NASA", session="a"), now=now)
    result = router.intercept(request("¿y SpaceX?", session="b"), now=now)

    assert result is None
    assert len(client.calls) == 1


def test_new_nasa_mission_question_never_falls_back_to_model_memory():
    client = FakeNews()
    router = CurrentAffairsRouter(client)

    result = router.intercept(
        request("Roby, tenés información de alguna nueva misión de la NASA"),
        now=datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
    )

    assert result is not None
    assert result.origin.origin.value == "web_recent"
    assert "NASA anuncia" in result.response_text
    assert client.calls


def test_relevant_news_of_the_day_routes_to_web_without_named_topic():
    client = FakeNews()
    router = CurrentAffairsRouter(client)
    result = router.intercept(
        request("¿Tenés alguna noticia relevante del día?"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )
    assert result is not None
    assert result.origin.origin.value == "web_recent"
    assert client.calls


def test_broad_argentina_and_world_news_categories_route_to_web():
    prompts = (
        "Noticias políticas de hoy en Argentina",
        "¿Qué pasó hoy en el mundo?",
        "Últimas noticias internacionales",
        "Novedades de deportes y arte",
        "Noticias recientes de ciencia y medicina",
        "¿Hay alertas actuales por tormentas o terremotos?",
    )
    for prompt in prompts:
        client = FakeNews()
        result = CurrentAffairsRouter(client).intercept(
            request(prompt),
            now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
        )
        assert result is not None, prompt
        assert result.origin.origin.value == "web_recent", prompt
        assert client.calls, prompt
