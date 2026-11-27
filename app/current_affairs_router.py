from __future__ import annotations

import os
import re
import threading
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.response_presenter import (
    PresentationMode,
    ResponsePresentation,
    ResponsePresenter,
)
from app.weather_conversation_runtime import WeatherConversationInterceptionPort
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
    ResponseOriginMetadata,
)


@lru_cache(maxsize=1)
def _argentina_timezone():
    """Return Argentina time without making tzdata an import-time dependency."""
    try:
        return ZoneInfo("America/Argentina/Buenos_Aires")
    except ZoneInfoNotFoundError:
        return timezone(timedelta(hours=-3), name="ART")


@dataclass(frozen=True)
class CurrentAffairsItem:
    title: str
    source: str
    url: str
    published_at: datetime | None = None


@dataclass(frozen=True)
class CurrentAffairsFreshnessPolicy:
    label: str
    max_age: timedelta
    require_known_date: bool = True
    calendar_day_only: bool = False


@dataclass(frozen=True)
class CurrentAffairsFreshnessAssessment:
    accepted: tuple[CurrentAffairsItem, ...]
    stale_count: int
    undated_count: int
    future_count: int


@dataclass(frozen=True)
class CurrentAffairsAbstentionExplanation:
    reason_code: str
    what_happened: str
    unmet_criterion: str
    how_to_proceed: str

    def render(self) -> str:
        return "\n".join(
            (
                "No puedo responder esta consulta de actualidad con confianza.",
                f"Motivo: {self.what_happened}",
                f"Criterio no cumplido: {self.unmet_criterion}",
                f"Cómo podemos seguir: {self.how_to_proceed}",
            )
        )


@dataclass(frozen=True)
class CurrentAffairsConflict:
    left: CurrentAffairsItem
    right: CurrentAffairsItem
    topic: str


@dataclass(frozen=True)
class CurrentAffairsCacheEntry:
    created_at: datetime
    items: tuple[CurrentAffairsItem, ...]


@dataclass(frozen=True)
class CurrentAffairsConversationContext:
    query: str
    topic: str
    freshness_label: str
    items: tuple[CurrentAffairsItem, ...] = ()
    abstention: CurrentAffairsAbstentionExplanation | None = None


_GENERAL_HEADLINES_FEED = "titulares de los diarios"


class GoogleNewsRSSClient:
    """Small, dependency-free web search client backed by Google News RSS."""

    def __init__(self, *, timeout_seconds: float = 8.0) -> None:
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, *, limit: int = 5) -> tuple[CurrentAffairsItem, ...]:
        endpoint = "https://news.google.com/rss"
        if query == _GENERAL_HEADLINES_FEED:
            url = f"{endpoint}?hl=es-419&gl=AR&ceid=AR:es-419"
        else:
            encoded = urllib.parse.quote_plus(query)
            url = f"{endpoint}/search?q={encoded}&hl=es-419&gl=AR&ceid=AR:es-419"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "RobyXI2/20.47 (+local personal assistant)"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = response.read()
        root = ET.fromstring(payload)
        items: list[CurrentAffairsItem] = []
        for node in root.findall("./channel/item"):
            title = (node.findtext("title") or "").strip()
            link = (node.findtext("link") or "").strip()
            source_node = node.find("source")
            source = (
                (source_node.text or "").strip()
                if source_node is not None
                else "Fuente web"
            )
            published = self._parse_date(node.findtext("pubDate"))
            if title and link.startswith("https://"):
                items.append(CurrentAffairsItem(title, source, link, published))
            if len(items) >= limit:
                break
        return tuple(items)

    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)


class CurrentAffairsRouter:
    """Routes changing facts to fresh web retrieval instead of model memory."""

    _RECENCY = re.compile(
        r"\b(hoy|ahora|actual(?:es|idad|mente)?|reciente(?:s|mente)?|"
        r"últim[oa]s?|ultim[oa]s?|nuev(?:o|os|a|as)|novedad(?:es)?|"
        r"esta\s+(?:mañana|tarde|noche|semana|quincena)|este\s+(?:mes|año)|"
        r"en\s+las\s+últimas\s+\d+\s+(?:horas?|días?|semanas?|meses?)|"
        r"desde\s+(?:ayer|anoche|el\s+lunes|el\s+martes|el\s+miércoles|"
        r"el\s+miercoles|el\s+jueves|el\s+viernes|el\s+sábado|el\s+sabado|"
        r"el\s+domingo)|ayer|anoche|mañana|qué\s+pasó|que\s+paso|"
        r"qué\s+está\s+pasando|que\s+esta\s+pasando|noticias?)\b",
        re.IGNORECASE,
    )
    _ESA_ACRONYM = re.compile(r"\bESA\b")
    _DYNAMIC = re.compile(
        r"\b(nasa|spacex|openai|apple|microsoft|windows|linux|android|ios|"
        r"dólar|dolar|euro|economía|economia|inflación|inflacion|elecciones?|"
        r"gobierno|presidente|congreso|ucrania|rusia|israel|gaza|bolsa|"
        r"acciones?|mercados?|criptomonedas?|bitcoin|boca|river|fútbol|futbol|"
        r"partido|resultado|misi(?:ó|o)n(?:es)?|lanzamientos?|versiones?|"
        r"actualizaciones?|política|politica|internacional(?:es)?|deportes?|"
        r"arte|cultura|ciencia|científic(?:o|a|os|as)|salud|medicina|"
        r"médic(?:o|a|os|as)|"
        r"tormentas?|temporales?|huracanes?|tornados?|inundaciones?|sequías?|sequias?|"
        r"terremotos?|sismos?|tsunamis?|volcanes?|incendios?|desastres?|emergencias?|"
        r"ambiente|medioambiente|clima|energía|energia|tecnología|tecnologia|"
        r"sociedad|educación|educacion|seguridad|justicia|argentina|mundo|planeta|"
        r"precio(?:s)?|cotización|cotizacion|CEO|director|ministro|ley(?:es)?|"
        r"reglamento(?:s)?|normativa(?:s)?|temporada|estreno(?:s)?)\b",
        re.IGNORECASE,
    )
    _RECENT_TOPIC_QUESTION = re.compile(
        r"\b(?:qué|que)\s+(?:hay\s+de\s+nuevo|se\s+sabe|pasó|paso|"
        r"está\s+pasando|esta\s+pasando)\s+(?:con|sobre|de|en)\b|"
        r"\b(?:cómo|como)\s+(?:viene|sigue|está|esta)\b|"
        r"\b(?:poneme|ponme|contame|decime|dame)\s+al\s+día\b",
        re.IGNORECASE,
    )
    _GENERAL_NEWS_REQUEST = re.compile(
        r"(?P<headlines>^[\s¿¡]*(?:roby[\s,:]+)?(?:dame|decime|mostrame|pasame)\s+"
        r"(?:los\s+)?titulares(?:\s+de\s+los\s+diarios)?"
        r"(?:[\s,]+roby)?[\s.!?]*$)|"

        r"^[\s¿¡]*(?:roby[\s,:]+)?(?:dame|decime|contame|mostrame|busc[aá](?:me)?)"
        r"\s+(?:las?\s+)?[uú]ltimas?\s+noticias?"
        r"(?:[\s,]+roby)?[\s.!?]*$|"
        r"^[\s¿¡]*(?:roby[\s,:]+)?ten[eé]s\s+alguna\s+noticia"
        r"(?:\s+(?:importante|relevante|destacada|reciente))?"
        r"(?:[\s,]+roby)?[\s.!?]*$|"

        r"\b(?:noticias?|novedades?|resumen|panorama|actualidad)\b.*"
        r"\b(?:relevantes?|importantes?|destacadas?|principales?|del\s+d[ií]a|"
        r"de\s+hoy|argentina|mundo|internacional(?:es)?)\b|"
        r"\b(?:qué|que)\s+(?:pasó|paso|está\s+pasando|esta\s+pasando)"
        r"\s+(?:hoy\s+)?(?:en\s+)?(?:argentina|el\s+mundo|el\s+planeta)\b",
        re.IGNORECASE,
    )
    _EXPAND_HEADLINE = re.compile(
        r"^[\s¿¡]*(?:roby[\s,:]+)?(?:ampli[aá](?:me)?|desarroll[aá](?:me)?|"
        r"contame\s+m[aá]s\s+(?:sobre|de))\s+(.+?)[.!?]*$",
        re.IGNORECASE,
    )

    _STABLE_RECENCY_FALSE_POSITIVE = re.compile(
        r"\b(última\s+cena|ultima\s+cena|último\s+teorema|ultimo\s+teorema|"
        r"último\s+mohicano|ultimo\s+mohicano|última\s+pregunta|"
        r"ultima\s+pregunta|nuevo\s+testamento|edad\s+moderna)\b",
        re.IGNORECASE,
    )
    _EXPLICIT_WEB = re.compile(
        r"\b(busca(?:me)?|buscá(?:me)?|buscar|revisá|revisa|consultá|consulta)\b.*"
        r"\b(internet|web|noticias?|fuentes?)\b",
        re.IGNORECASE,
    )
    _NASA_MISSION_INFORMATION = re.compile(
        r"^\s*(?:roby[\s,:]+)?"
        r"(?:busc[aá](?:me)?|buscar|consult[aá]|revis[aá])\s+"
        r"(?:en\s+(?:internet|(?:la\s+)?web)\s+)?"
        r"(?:informaci[oó]n|noticias)\s+(?:sobre|de)\s+"
        r"(?=.*\bnasa\b).*\bmisi[oó]n(?:es)?\b",
        re.IGNORECASE,
    )

    @classmethod
    def is_recent_nasa_mission_information_request(cls, text: str) -> bool:
        return bool(
            cls._NASA_MISSION_INFORMATION.search(text) and cls._RECENCY.search(text)
        )

    _ROBY_PERSONAL_STATUS = re.compile(
        r"^\s*(?:hola\s+)?(?:roby|robi|robby|robbie|ruby|rubi)[,;:!?\s-]*"
        r"(?:c[oó]mo\s+(?:est[aá]s?|and[aá]s?|vas)|todo\s+bien|"
        r"qu[eé]\s+tal|c[oó]mo\s+te\s+sent[ií]s)\b|"
        r"^\s*(?:c[oó]mo\s+(?:est[aá]s?|and[aá]s?|vas)|todo\s+bien|"
        r"qu[eé]\s+tal)\s+(?:roby|robi|robby|robbie|ruby|rubi)\b",
        re.IGNORECASE,
    )
    _PREDICTION = re.compile(
        r"\b(quién gana|quien gana|va a ganar|pronóstico entre|pronostico entre|"
        r"predicción|prediccion)\b",
        re.IGNORECASE,
    )
    _LINK_FOLLOWUP = re.compile(
        r"\b(enlace(?:s)?|link(?:s)?|url(?:s)?)\b",
        re.IGNORECASE,
    )
    _SOURCE_FOLLOWUP = re.compile(
        r"\b(de dónde|de donde|fuente(?:s)?)\b",
        re.IGNORECASE,
    )
    _WHY_ABSTAINED_FOLLOWUP = re.compile(
        r"\b(?:por qué|por que)\s+(?:no\s+)?(?:respondiste|respondés|respondes|"
        r"podés responder|podes responder)\b",
        re.IGNORECASE,
    )
    _ELLIPTICAL_FOLLOWUP = re.compile(
        r"^\s*(?:¿?\s*)?(?:y|qué hay de|que hay de|qué pasa con|que pasa con)\s+"
        r"(.+?)[?!.]*\s*$",
        re.IGNORECASE,
    )
    _TEMPORAL_ONLY_FOLLOWUP = re.compile(
        r"^\s*(?:¿?\s*)?(?:y\s+)?(?:hoy|ahora|ayer|anoche|desde\s+ayer|"
        r"esta\s+(?:mañana|tarde|noche|semana)|este\s+mes|"
        r"en\s+las\s+últimas\s+\d+\s+(?:horas?|días?|semanas?|meses?))"
        r"[?!.]*\s*$",
        re.IGNORECASE,
    )
    _EXPLICIT_WINDOW = re.compile(
        r"(?:en\s+)?las?\s+(?:últimas|ultimas)\s+(\d+)\s+"
        r"(horas?|días?|dias|semanas?|meses?)",
        re.IGNORECASE,
    )
    _TODAY_WINDOW = re.compile(
        r"\b(hoy|ahora|esta\s+(?:mañana|tarde|noche))\b",
        re.IGNORECASE,
    )
    _SINCE_YESTERDAY_WINDOW = re.compile(
        r"\b(desde\s+(?:ayer|anoche)|ayer|anoche)\b",
        re.IGNORECASE,
    )
    _THIS_WEEK_WINDOW = re.compile(
        r"\b(esta\s+semana|última\s+semana|ultima\s+semana)\b",
        re.IGNORECASE,
    )
    _THIS_MONTH_WINDOW = re.compile(
        r"\b(este\s+mes|último\s+mes|ultimo\s+mes)\b",
        re.IGNORECASE,
    )
    _CURRENT_STATUS_WINDOW = re.compile(
        r"\b(actual(?:es|idad|mente)?|quién\s+es\s+el\s+actual|"
        r"quien\s+es\s+el\s+actual)\b",
        re.IGNORECASE,
    )
    _EXPLICIT_NEWS = re.compile(
        r"\b(noticias?|novedades?|actualidad|publicaciones?|fuentes?)\b",
        re.IGNORECASE,
    )
    _CONTRADICTION_GROUPS = (
        (
            ("aprueba", "aprobó", "aprobo", "autoriza", "confirmó", "confirmo"),
            ("rechaza", "rechazó", "rechazo", "deniega", "niega", "desmiente"),
        ),
        (
            ("sube", "aumenta", "crece", "avanza"),
            ("baja", "cae", "retrocede", "desciende"),
        ),
        (("gana", "ganó", "gano", "vence"), ("pierde", "perdió", "perdio", "cae ante")),
        (
            ("se realizará", "se realizara", "sigue en pie", "confirma el lanzamiento"),
            ("se cancela", "cancela", "canceló", "cancelo", "se pospone", "aplaza"),
        ),
    )

    def __init__(
        self,
        client: GoogleNewsRSSClient | None = None,
        *,
        enabled: bool = True,
        cache_ttl: timedelta = timedelta(minutes=12),
    ) -> None:
        self.client = client or GoogleNewsRSSClient()
        self.enabled = enabled
        self.cache_ttl = cache_ttl
        self._cache: dict[str, CurrentAffairsCacheEntry] = {}
        self._last_by_session: dict[str, tuple[CurrentAffairsItem, ...]] = {}
        self._context_by_session: dict[str, CurrentAffairsConversationContext] = {}
        self._shown_headlines: dict[str, tuple[CurrentAffairsItem, ...]] = {}
        self._lock = threading.Lock()

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        original_text = re.sub(
            r"\bmoticia(s?)\b", r"noticia\1", request.text.strip(), flags=re.IGNORECASE
        )

        expansion = self._EXPAND_HEADLINE.match(original_text)
        if expansion and request.session_id in self._shown_headlines:
            return self._expand_headline(request.session_id, expansion[1], now=now)

        context = self._context_by_session.get(request.session_id)
        if self._LINK_FOLLOWUP.search(original_text):
            prior = self._last_by_session.get(request.session_id)
            if prior:
                return GovernedOperationalInterception(
                    response_text=self._render_links(prior),
                    rationale="current_affairs_links_recalled",
                    origin=ResponseOriginMetadata.web_recent(
                        evidence_count=len(prior),
                        reason_code="current_affairs_links_recalled",
                    ),
                )
        if self._SOURCE_FOLLOWUP.search(original_text):
            prior = self._last_by_session.get(request.session_id)
            if prior:
                return GovernedOperationalInterception(
                    response_text=self._render_sources(prior),
                    rationale="current_affairs_sources_recalled",
                    origin=ResponseOriginMetadata.web_recent(
                        evidence_count=len(prior),
                        reason_code="current_affairs_sources_recalled",
                    ),
                )
        if (
            self._WHY_ABSTAINED_FOLLOWUP.search(original_text)
            and context
            and context.abstention
        ):
            return self._abstain(context.abstention)

        text = self._resolve_contextual_followup(original_text, context)
        if text is None or not self._should_search(text):
            return None
        general_news = self._GENERAL_NEWS_REQUEST.search(text)
        query = (
            _GENERAL_HEADLINES_FEED
            if general_news and general_news["headlines"]
            else self._clean_query(text)
        )
        policy = self._freshness_policy(text)
        self._shown_headlines.pop(request.session_id, None)
        topic = self._topic_from_query(query)
        if not self.enabled:
            explanation = CurrentAffairsAbstentionExplanation(
                reason_code="web_search_disabled",
                what_happened="la búsqueda web de actualidad está desactivada",
                unmet_criterion=(
                    "la respuesta necesita una consulta reciente y verificable"
                ),
                how_to_proceed=(
                    "activá ROBY_CURRENT_AFFAIRS_ENABLED o reformulá la pregunta "
                    "como conocimiento general no dependiente de la actualidad"
                ),
            )
            self._remember_context(
                request.session_id, query, topic, policy, abstention=explanation
            )
            return self._abstain(explanation)

        try:
            items = self._retrieve(query, now=now)
        except Exception:
            explanation = CurrentAffairsAbstentionExplanation(
                reason_code="web_retrieval_failed",
                what_happened=(
                    "falló la consulta a las fuentes web y no pude verificar "
                    "información reciente"
                ),
                unmet_criterion=(
                    "una respuesta de actualidad debe apoyarse en fuentes "
                    "recuperadas durante esta consulta"
                ),
                how_to_proceed=(
                    "reintentá cuando haya conexión. Prefiero no responder de "
                    "memoria ni completar la respuesta con datos potencialmente "
                    "desactualizados"
                ),
            )
            self._remember_context(
                request.session_id, query, topic, policy, abstention=explanation
            )
            return self._abstain(explanation)

        assessment = self._assess_freshness(items, now=now, policy=policy)
        used_recent_fallback = False
        if (
            not assessment.accepted
            and policy.calendar_day_only
            and self._GENERAL_NEWS_REQUEST.search(text)
            and not self._TODAY_WINDOW.search(text)
        ):
            recent_policy = CurrentAffairsFreshnessPolicy(
                "últimas 48 horas", timedelta(hours=48)
            )
            assessment = self._assess_freshness(items, now=now, policy=recent_policy)
            policy = recent_policy
            used_recent_fallback = bool(assessment.accepted)
        if not assessment.accepted:
            explanation = self._explain_freshness_abstention(assessment, policy=policy)
            self._remember_context(
                request.session_id, query, topic, policy, abstention=explanation
            )
            return self._abstain(explanation)

        items = assessment.accepted
        self._last_by_session[request.session_id] = items
        self._remember_context(request.session_id, query, topic, policy, items=items)
        conflicts = self._detect_conflicts(items)
        if conflicts:
            return GovernedOperationalInterception(
                response_text=self._render_conflicts(conflicts, items, now=now),
                rationale="current_affairs_sources_conflict_disclosed",
                origin=ResponseOriginMetadata.web_recent_conflicted(
                    evidence_count=len(items),
                    reason_code="current_affairs_sources_conflict_disclosed",
                ),
            )
        self._shown_headlines[request.session_id] = items[:4]
        summary = self._render_summary(items, now=now, policy=policy)
        if used_recent_fallback:
            summary = (
                "No encontré publicaciones de hoy. Estas son de las últimas 48 horas.\n"
                + summary
            )
        return GovernedOperationalInterception(
            response_text=summary,
            rationale="current_affairs_web_retrieval_completed_high_confidence",
            origin=ResponseOriginMetadata.web_recent(
                evidence_count=len(items),
                reason_code="current_affairs_web_retrieval_completed",
            ),
        )

    def _expand_headline(
        self, session_id: str, reference: str, *, now: datetime
    ) -> GovernedOperationalInterception:
        shown = self._shown_headlines[session_id]
        reference = reference.strip(" ¿?¡!.,«»\"").casefold()
        number = re.fullmatch(
            r"(?:(?:la|el)\s+)?(?:(?:noticia|titular|n[uú]mero)\s+)?(\d{1,2})",
            reference,
        )
        if number:
            index = int(number[1]) - 1
            matches = shown[index:index + 1] if index >= 0 else ()
        else:
            reference = re.sub(r"^(?:(?:lo|la noticia)\s+de|sobre)\s+", "", reference)
            matches = tuple(
                item for item in shown if reference and reference in item.title.casefold()
            )
        if len(matches) != 1:
            return GovernedOperationalInterception(
                response_text="Indicame el número o una parte del titular que querés ampliar.",
                rationale="current_affairs_headline_choice_required",
            )

        selected = matches[0]
        topic = selected.title.removesuffix(f" - {selected.source}")
        terms = self._headline_terms(topic)
        try:
            related = self._retrieve(topic, now=now)
        except (OSError, ValueError, ET.ParseError):
            related = ()
        policy = CurrentAffairsFreshnessPolicy("últimas 48 horas", timedelta(hours=48))
        fresh = self._assess_freshness(related, now=now, policy=policy).accepted
        details = tuple(
            item
            for item in fresh
            if item.title.casefold() != selected.title.casefold()
            and item.url != selected.url
            and len(terms & self._headline_terms(item.title))
            >= max(2, (len(terms) + 1) // 2)
        )[:3]
        self._last_by_session[session_id] = (selected, *details)
        if details:
            lines = "\n".join(f"- {item.title} — {item.source}" for item in details)
            response = (
                f"Sobre «{topic}»: encontré estos titulares relacionados:\n{lines}\n"
                "La búsqueda permite contrastar titulares. Podés pedirme las fuentes."
            )
        else:
            response = (
                f"Sobre «{topic}», de {selected.source}, no encontré información "
                "adicional pertinente para ampliarlo con confianza."
            )
        return GovernedOperationalInterception(
            response_text=response,
            rationale="current_affairs_headline_expanded",
            origin=ResponseOriginMetadata.web_recent(
                evidence_count=1 + len(details),
                reason_code="current_affairs_headline_expanded",
            ),
        )

    @staticmethod
    def _headline_terms(title: str) -> set[str]:
        return {
            word
            for word in re.findall(r"\w+", title.casefold())
            if len(word) >= 4
            and word not in {"para", "sobre", "como", "cómo", "desde", "tras"}
        }

    def _resolve_contextual_followup(
        self,
        text: str,
        context: CurrentAffairsConversationContext | None,
    ) -> str | None:
        if self._should_search(text):
            return text
        if context is None:
            return None
        if self._TEMPORAL_ONLY_FOLLOWUP.match(text):
            temporal = text.strip(" ¿?¡!.,")
            temporal = re.sub(r"^y\s+", "", temporal, flags=re.IGNORECASE)
            return f"{temporal} noticias de {context.topic}"
        match = self._ELLIPTICAL_FOLLOWUP.match(text)
        if not match:
            return None
        new_topic = match.group(1).strip(" ¿?¡!.,")
        if not new_topic:
            return None
        return f"últimas noticias de {new_topic}"

    def _remember_context(
        self,
        session_id: str,
        query: str,
        topic: str,
        policy: CurrentAffairsFreshnessPolicy,
        *,
        items: tuple[CurrentAffairsItem, ...] = (),
        abstention: CurrentAffairsAbstentionExplanation | None = None,
    ) -> None:
        self._context_by_session[session_id] = CurrentAffairsConversationContext(
            query=query,
            topic=topic,
            freshness_label=policy.label,
            items=items,
            abstention=abstention,
        )

    @staticmethod
    def _topic_from_query(query: str) -> str:
        topic = re.sub(
            r"\b(?:últimas?|ultimas?|noticias?|hoy|ahora|ayer|anoche|"
            r"esta\s+semana|este\s+mes|desde\s+ayer|en\s+las\s+últimas\s+"
            r"\d+\s+(?:horas?|días?|dias|semanas?|meses?)|de|sobre)\b",
            " ",
            query,
            flags=re.IGNORECASE,
        )
        cleaned = " ".join(topic.split()).strip(" ¿?¡!.,")
        return cleaned or query

    @classmethod
    def _freshness_policy(cls, text: str) -> CurrentAffairsFreshnessPolicy:
        explicit = cls._EXPLICIT_WINDOW.search(text)
        if explicit:
            amount = max(1, int(explicit.group(1)))
            unit = explicit.group(2).casefold()
            if unit.startswith("hora"):
                age = timedelta(hours=amount)
                unit_label = "hora" if amount == 1 else "horas"
            elif unit.startswith(("día", "dia")):
                age = timedelta(days=amount)
                unit_label = "día" if amount == 1 else "días"
            elif unit.startswith("semana"):
                age = timedelta(weeks=amount)
                unit_label = "semana" if amount == 1 else "semanas"
            else:
                age = timedelta(days=31 * amount)
                unit_label = "mes" if amount == 1 else "meses"
            return CurrentAffairsFreshnessPolicy(
                label=f"últimas {amount} {unit_label}",
                max_age=age,
            )
        if cls._TODAY_WINDOW.search(text) or cls._GENERAL_NEWS_REQUEST.search(text):
            return CurrentAffairsFreshnessPolicy(
                "hoy",
                timedelta(hours=36),
                calendar_day_only=True,
            )
        if cls._SINCE_YESTERDAY_WINDOW.search(text):
            return CurrentAffairsFreshnessPolicy("desde ayer", timedelta(hours=60))
        if cls._THIS_WEEK_WINDOW.search(text):
            return CurrentAffairsFreshnessPolicy("esta semana", timedelta(days=8))
        if cls._THIS_MONTH_WINDOW.search(text):
            return CurrentAffairsFreshnessPolicy("este mes", timedelta(days=35))
        if cls._CURRENT_STATUS_WINDOW.search(text):
            return CurrentAffairsFreshnessPolicy("estado actual", timedelta(days=120))
        return CurrentAffairsFreshnessPolicy("información reciente", timedelta(days=45))

    @staticmethod
    def _assess_freshness(
        items: tuple[CurrentAffairsItem, ...],
        *,
        now: datetime,
        policy: CurrentAffairsFreshnessPolicy,
    ) -> CurrentAffairsFreshnessAssessment:
        now_utc = now.astimezone(timezone.utc)
        local_today = now.astimezone(_argentina_timezone()).date()
        accepted: list[CurrentAffairsItem] = []
        stale_count = 0
        undated_count = 0
        future_count = 0
        for item in items:
            if item.published_at is None:
                if policy.require_known_date:
                    undated_count += 1
                else:
                    accepted.append(item)
                continue
            published = item.published_at
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            published_utc = published.astimezone(timezone.utc)
            age = now_utc - published_utc
            published_local_date = published.astimezone(_argentina_timezone()).date()
            if age < timedelta():
                future_count += 1
            elif policy.calendar_day_only and published_local_date != local_today:
                stale_count += 1
            elif age <= policy.max_age:
                accepted.append(item)
            else:
                stale_count += 1
        return CurrentAffairsFreshnessAssessment(
            accepted=tuple(accepted),
            stale_count=stale_count,
            undated_count=undated_count,
            future_count=future_count,
        )

    @classmethod
    def _filter_by_freshness(
        cls,
        items: tuple[CurrentAffairsItem, ...],
        *,
        now: datetime,
        policy: CurrentAffairsFreshnessPolicy,
    ) -> tuple[CurrentAffairsItem, ...]:
        return cls._assess_freshness(items, now=now, policy=policy).accepted

    @staticmethod
    def _explain_freshness_abstention(
        assessment: CurrentAffairsFreshnessAssessment,
        *,
        policy: CurrentAffairsFreshnessPolicy,
    ) -> CurrentAffairsAbstentionExplanation:
        if not any(
            (assessment.stale_count, assessment.undated_count, assessment.future_count)
        ):
            happened = "la búsqueda no devolvió publicaciones utilizables"
            next_step = (
                "probá con un tema más específico o volvé a intentar cuando haya "
                "nuevas publicaciones"
            )
            code = "no_sources_found"
        else:
            details: list[str] = []
            if assessment.stale_count:
                details.append(
                    f"{assessment.stale_count} fuente(s) eran más antiguas que "
                    f"{policy.label}"
                )
            if assessment.undated_count:
                details.append(
                    f"{assessment.undated_count} fuente(s) no informaban fecha"
                )
            if assessment.future_count:
                details.append(
                    f"{assessment.future_count} fuente(s) tenían una fecha futura "
                    "inconsistente"
                )
            happened = (
                "No encontré publicaciones suficientemente recientes. "
                "Descarté las fuentes encontradas: " + "; ".join(details)
            )
            next_step = (
                "ampliá el período solicitado o pedime que busque nuevamente; "
                "no usaré información vieja o fuera de vigencia sin avisarte"
            )
            code = "freshness_requirements_not_met"
        return CurrentAffairsAbstentionExplanation(
            reason_code=code,
            what_happened=happened,
            unmet_criterion=(
                "necesito al menos una fuente con fecha conocida dentro de "
                f"{policy.label}"
            ),
            how_to_proceed=next_step,
        )

    def _should_search(self, text: str) -> bool:
        if self._ROBY_PERSONAL_STATUS.search(text):
            return False
        if self._STABLE_RECENCY_FALSE_POSITIVE.search(text):
            return False
        if WeatherConversationInterceptionPort.is_weather_request(
            text
        ) and not self._EXPLICIT_NEWS.search(text):
            return False
        if self._EXPLICIT_WEB.search(text):
            return True
        if self._RECENT_TOPIC_QUESTION.search(text):
            return True
        if self._GENERAL_NEWS_REQUEST.search(text):
            return True
        if self._PREDICTION.search(text) and self._DYNAMIC.search(text):
            return True
        return bool(
            self._RECENCY.search(text)
            and (self._DYNAMIC.search(text) or self._ESA_ACRONYM.search(text))
        )

    def _retrieve(self, query: str, *, now: datetime) -> tuple[CurrentAffairsItem, ...]:
        key = query.casefold()
        with self._lock:
            cached = self._cache.get(key)
            if cached and now - cached.created_at <= self.cache_ttl:
                return cached.items
        if query == _GENERAL_HEADLINES_FEED:
            batches = (self.client.search(query, limit=20),)
            max_items = 20
        else:
            topics = self._split_topics(query)
            with ThreadPoolExecutor(max_workers=min(3, len(topics))) as executor:
                batches = tuple(executor.map(self.client.search, topics))
            max_items = 5
        unique: list[CurrentAffairsItem] = []
        seen: set[str] = set()
        for batch in batches:
            for item in batch:
                identity = item.title.casefold()
                if identity not in seen:
                    unique.append(item)
                    seen.add(identity)
                if len(unique) >= max_items:
                    break
        result = tuple(unique)
        with self._lock:
            self._cache[key] = CurrentAffairsCacheEntry(now, result)
        return result

    @staticmethod
    def _split_topics(query: str) -> tuple[str, ...]:
        parts = re.split(r"\s+(?:y|versus|vs\.?|compará|compara)\s+", query, maxsplit=2)
        cleaned = tuple(part.strip(" ,¿?¡!") for part in parts if part.strip(" ,¿?¡!"))
        return cleaned or (query,)

    @staticmethod
    def _clean_query(text: str) -> str:
        query = re.sub(r"\broby\b", "", text, flags=re.IGNORECASE)
        query = re.sub(
            r"\b(qué podés decirme de|que podes decirme de|sabés algo de|"
            r"sabes algo de|contame sobre|decime sobre)\b",
            "",
            query,
            flags=re.IGNORECASE,
        )
        return " ".join(query.strip(" ¿?¡!,.").split())

    @classmethod
    def _detect_conflicts(
        cls, items: tuple[CurrentAffairsItem, ...]
    ) -> tuple[CurrentAffairsConflict, ...]:
        conflicts: list[CurrentAffairsConflict] = []
        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                if left.source.casefold() == right.source.casefold():
                    continue
                if not cls._titles_share_topic(left.title, right.title):
                    continue
                if cls._titles_are_opposed(left.title, right.title):
                    topic = cls._shared_topic_label(left.title, right.title)
                    conflicts.append(CurrentAffairsConflict(left, right, topic))
        return tuple(conflicts)

    @classmethod
    def _titles_are_opposed(cls, left: str, right: str) -> bool:
        left_norm = left.casefold()
        right_norm = right.casefold()
        for positive, negative in cls._CONTRADICTION_GROUPS:
            left_positive = any(term in left_norm for term in positive)
            left_negative = any(term in left_norm for term in negative)
            right_positive = any(term in right_norm for term in positive)
            right_negative = any(term in right_norm for term in negative)
            if (left_positive and right_negative) or (left_negative and right_positive):
                return True
        return False

    @staticmethod
    def _titles_share_topic(left: str, right: str) -> bool:
        stopwords = {
            "ante",
            "como",
            "con",
            "del",
            "desde",
            "dice",
            "el",
            "en",
            "la",
            "las",
            "los",
            "para",
            "por",
            "que",
            "se",
            "según",
            "segun",
            "sobre",
            "tras",
            "una",
            "uno",
            "unos",
            "y",
        }

        def tokenize(value: str) -> set[str]:
            return {
                token
                for token in re.findall(r"[a-záéíóúñ0-9]+", value.casefold())
                if len(token) > 3 and token not in stopwords
            }

        common = tokenize(left) & tokenize(right)
        return len(common) >= 2

    @staticmethod
    def _shared_topic_label(left: str, right: str) -> str:
        left_words = re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9]+", left)
        right_folded = right.casefold()
        shared = [
            word
            for word in left_words
            if len(word) > 3 and word.casefold() in right_folded
        ]
        return " ".join(shared[:4]) or "el mismo hecho"

    @staticmethod
    def _render_conflicts(
        conflicts: tuple[CurrentAffairsConflict, ...],
        items: tuple[CurrentAffairsItem, ...],
        *,
        now: datetime,
    ) -> str:
        lines = [
            "Encontré versiones contradictorias sobre este tema. "
            "No voy a presentar una de ellas como un hecho confirmado.",
        ]
        shown: set[str] = set()
        for conflict in conflicts[:2]:
            lines.append(f"Sobre {conflict.topic}:")
            for item in (conflict.left, conflict.right):
                identity = item.url.casefold()
                if identity in shown:
                    continue
                shown.add(identity)
                age = CurrentAffairsRouter._age_label(item.published_at, now)
                suffix = f" — {item.source}"
                if age:
                    suffix += f", {age}"
                lines.append(f"- {item.title}{suffix}.")
        remaining = [item for item in items if item.url.casefold() not in shown]
        if remaining:
            lines.append("Otras publicaciones relacionadas:")
            for item in remaining[:2]:
                lines.append(f"- {item.title} — {item.source}.")
        lines.append(
            "La confianza queda reducida hasta que aparezca una confirmación "
            "más sólida. Podés pedirme las fuentes para revisarlas."
        )
        return "\n".join(lines)

    @staticmethod
    def _render_summary(
        items: tuple[CurrentAffairsItem, ...],
        *,
        now: datetime,
        policy: CurrentAffairsFreshnessPolicy,
    ) -> str:
        if policy.calendar_day_only:
            opening = "Revisé las publicaciones de hoy. Esto es lo principal:"
        else:
            opening = "Revisé las publicaciones más recientes. Esto es lo principal:"
        lines = [opening]
        for number, item in enumerate(items[:4], start=1):
            age = CurrentAffairsRouter._publication_label(
                item.published_at,
                now,
                policy=policy,
            )
            suffix = f" — {item.source}"
            if age:
                suffix += f", {age}"
            lines.append(f"{number}. {item.title}{suffix}.")
        lines.append(
            "La información proviene de una búsqueda web reciente. "
            "Podés pedirme las fuentes y te las muestro."
        )
        return "\n".join(lines)

    @staticmethod
    def _publication_label(
        published_at: datetime | None,
        now: datetime,
        *,
        policy: CurrentAffairsFreshnessPolicy,
    ) -> str:
        if published_at is None:
            return "fecha no informada"
        if policy.calendar_day_only:
            published = published_at
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            local = published.astimezone(_argentina_timezone())
            return f"hoy, {local:%H:%M}"
        return CurrentAffairsRouter._age_label(published_at, now)

    @staticmethod
    def _render_sources(items: tuple[CurrentAffairsItem, ...]) -> str:
        sources = tuple(dict.fromkeys(item.source.strip() for item in items))
        presenter = ResponsePresenter()
        return "\n".join(
            presenter.present(
                ResponsePresentation(source=source),
                mode=PresentationMode.SOURCE_ONLY,
            )
            for source in sources[:5]
            if source
        )

    @staticmethod
    def _render_links(items: tuple[CurrentAffairsItem, ...]) -> str:
        links = tuple(dict.fromkeys(item.url.strip() for item in items))
        presenter = ResponsePresenter()
        return "\n".join(
            presenter.present(
                ResponsePresentation(link=link),
                mode=PresentationMode.LINK_ONLY,
            )
            for link in links[:5]
            if link
        )

    @staticmethod
    def _age_label(published_at: datetime | None, now: datetime) -> str:
        if published_at is None:
            return "fecha no informada"
        delta = max(timedelta(), now.astimezone(timezone.utc) - published_at)
        if delta < timedelta(hours=24):
            hours = max(1, int(delta.total_seconds() // 3600))
            return f"hace {hours} h"
        return f"hace {delta.days} día{'s' if delta.days != 1 else ''}"

    @staticmethod
    def _abstain(
        explanation: CurrentAffairsAbstentionExplanation,
    ) -> GovernedOperationalInterception:
        return GovernedOperationalInterception(
            response_text=explanation.render(),
            rationale=f"current_affairs_abstained:{explanation.reason_code}",
            origin=ResponseOriginMetadata.abstained_web(
                reason_code=f"current_affairs_{explanation.reason_code}",
            ),
        )


def build_current_affairs_router_from_environment() -> CurrentAffairsRouter:
    enabled = os.getenv("ROBY_CURRENT_AFFAIRS_ENABLED", "true").strip().casefold()
    timeout = float(os.getenv("ROBY_CURRENT_AFFAIRS_TIMEOUT_SECONDS", "8"))
    ttl_minutes = int(os.getenv("ROBY_CURRENT_AFFAIRS_CACHE_MINUTES", "12"))
    return CurrentAffairsRouter(
        GoogleNewsRSSClient(timeout_seconds=timeout),
        enabled=enabled not in {"0", "false", "no"},
        cache_ttl=timedelta(minutes=max(1, ttl_minutes)),
    )
