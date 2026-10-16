from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from urllib.parse import urlsplit


class NewsCategory(str, Enum):
    LOCAL = "local"
    INTERNATIONAL = "international"
    WEATHER = "weather"
    EMERGENCY = "emergency"
    HEALTH = "health"
    ECONOMY = "economy"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    GENERAL = "general"


class NewsDelivery(str, Enum):
    INTERRUPT = "interrupt"
    DAILY_BRIEFING = "daily_briefing"
    SILENT = "silent"


@dataclass(frozen=True)
class NewsSource:
    name: str
    url: str
    categories: tuple[NewsCategory, ...] = ()
    official: bool = False
    enabled: bool = True

    @property
    def domain(self) -> str:
        return urlsplit(self.url).netloc.lower().removeprefix("www.")


@dataclass(frozen=True)
class NewsItem:
    title: str
    summary: str
    source: NewsSource
    url: str
    published_at: datetime
    location: str = ""


@dataclass(frozen=True)
class NewsCluster:
    representative: NewsItem
    items: tuple[NewsItem, ...]
    category: NewsCategory
    source_count: int
    official_source_count: int
    relevance_score: int
    delivery: NewsDelivery
    reasons: tuple[str, ...]

    @property
    def traceability(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(item.source.name for item in self.items))


@dataclass(frozen=True)
class IntelligentNewsPolicy:
    home_terms: tuple[str, ...] = (
        "argentina",
        "buenos aires",
        "caba",
        "amba",
    )
    urgent_threshold: int = 80
    briefing_threshold: int = 35
    max_age: timedelta = timedelta(days=2)
    duplicate_similarity: float = 0.58
    require_multiple_sources_for_interrupt: bool = True


class IntelligentNewsEditor:
    """Deterministic local editorial layer for fresh news items."""

    _CATEGORY_TERMS: tuple[tuple[NewsCategory, tuple[str, ...]], ...] = (
        (
            NewsCategory.EMERGENCY,
            (
                "evacuacion",
                "catastrofe",
                "terremoto",
                "incendio",
                "explosion",
                "inundacion",
                "derrumbe",
                "apagón",
                "apagon",
            ),
        ),
        (
            NewsCategory.WEATHER,
            (
                "alerta meteorologica",
                "tormenta",
                "granizo",
                "tornado",
                "ola de calor",
                "ola polar",
                "viento fuerte",
            ),
        ),
        (
            NewsCategory.HEALTH,
            (
                "salud",
                "hospital",
                "brote",
                "epidemia",
                "vacuna",
                "medicamento",
                "dengue",
            ),
        ),
        (
            NewsCategory.ECONOMY,
            (
                "economia",
                "inflacion",
                "dolar",
                "banco",
                "impuesto",
                "tarifa",
                "mercado",
            ),
        ),
        (
            NewsCategory.SCIENCE,
            (
                "ciencia",
                "investigacion",
                "descubrimiento",
                "nasa",
                "espacio",
            ),
        ),
        (
            NewsCategory.TECHNOLOGY,
            (
                "tecnologia",
                "software",
                "inteligencia artificial",
                "ciberseguridad",
                "robot",
            ),
        ),
        (
            NewsCategory.INTERNATIONAL,
            (
                "guerra",
                "conflicto",
                "ucrania",
                "rusia",
                "gaza",
                "israel",
                "onu",
            ),
        ),
    )
    _URGENT_TERMS = (
        "alerta roja",
        "evacuacion",
        "emergencia",
        "peligro",
        "riesgo extremo",
        "corte total",
        "apagón",
        "apagon",
        "terremoto",
        "tornado",
        "incendio fuera de control",
    )
    _LOW_VALUE_TERMS = (
        "horoscopo",
        "celebridad",
        "viral",
        "reality",
        "rumor",
    )
    _STOPWORDS = {
        "a",
        "al",
        "ante",
        "con",
        "de",
        "del",
        "el",
        "en",
        "la",
        "las",
        "los",
        "para",
        "por",
        "que",
        "se",
        "su",
        "un",
        "una",
        "y",
    }

    def __init__(self, policy: IntelligentNewsPolicy | None = None) -> None:
        self.policy = policy or IntelligentNewsPolicy()

    def edit(
        self,
        items: tuple[NewsItem, ...],
        *,
        now: datetime,
    ) -> tuple[NewsCluster, ...]:
        fresh = tuple(item for item in items if self._is_fresh(item, now=now))
        groups = self._cluster(fresh)
        clusters = tuple(self._assess(group) for group in groups)
        return tuple(
            sorted(
                clusters,
                key=lambda cluster: (
                    cluster.delivery is NewsDelivery.INTERRUPT,
                    cluster.relevance_score,
                    cluster.representative.published_at,
                ),
                reverse=True,
            )
        )

    def _is_fresh(self, item: NewsItem, *, now: datetime) -> bool:
        published = item.published_at
        current = now
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        age = current.astimezone(timezone.utc) - published.astimezone(timezone.utc)
        return timedelta() <= age <= self.policy.max_age and item.source.enabled

    def _cluster(self, items: tuple[NewsItem, ...]) -> tuple[tuple[NewsItem, ...], ...]:
        groups: list[list[NewsItem]] = []
        for item in sorted(items, key=lambda value: value.published_at, reverse=True):
            for group in groups:
                if self._similar(item.title, group[0].title):
                    group.append(item)
                    break
            else:
                groups.append([item])
        return tuple(tuple(group) for group in groups)

    def _similar(self, left: str, right: str) -> bool:
        left_tokens = self._tokens(left)
        right_tokens = self._tokens(right)
        if not left_tokens or not right_tokens:
            return False
        overlap = len(left_tokens & right_tokens)
        union = len(left_tokens | right_tokens)
        return overlap / union >= self.policy.duplicate_similarity

    def _assess(self, items: tuple[NewsItem, ...]) -> NewsCluster:
        representative = max(items, key=lambda item: item.published_at)
        combined = " ".join(
            f"{item.title} {item.summary} {item.location}" for item in items
        )
        normalized = self._normalize(combined)
        category = self._classify(normalized)
        domains = {item.source.domain for item in items if item.source.domain}
        official_count = sum(item.source.official for item in items)
        score, reasons = self._score(
            normalized,
            category=category,
            source_count=len(domains),
            official_count=official_count,
        )
        delivery = self._delivery(
            score,
            source_count=len(domains),
            official_count=official_count,
            category=category,
        )
        return NewsCluster(
            representative=representative,
            items=items,
            category=category,
            source_count=len(domains),
            official_source_count=official_count,
            relevance_score=score,
            delivery=delivery,
            reasons=tuple(reasons),
        )

    def _classify(self, normalized: str) -> NewsCategory:
        for category, terms in self._CATEGORY_TERMS:
            if any(self._normalize(term) in normalized for term in terms):
                return category
        if any(self._normalize(term) in normalized for term in self.policy.home_terms):
            return NewsCategory.LOCAL
        return NewsCategory.GENERAL

    def _score(
        self,
        normalized: str,
        *,
        category: NewsCategory,
        source_count: int,
        official_count: int,
    ) -> tuple[int, list[str]]:
        score = 10
        reasons: list[str] = []
        if category in {NewsCategory.EMERGENCY, NewsCategory.WEATHER}:
            score += 35
            reasons.append("posible impacto inmediato")
        elif category is NewsCategory.HEALTH:
            score += 22
            reasons.append("relevancia sanitaria")
        elif category in {NewsCategory.LOCAL, NewsCategory.ECONOMY}:
            score += 15
            reasons.append("impacto personal o local posible")
        if any(self._normalize(term) in normalized for term in self.policy.home_terms):
            score += 20
            reasons.append("cercanía geográfica")
        if any(self._normalize(term) in normalized for term in self._URGENT_TERMS):
            score += 30
            reasons.append("lenguaje de urgencia")
        if source_count >= 2:
            score += 12
            reasons.append("confirmación independiente")
        if official_count:
            score += 10
            reasons.append("fuente oficial")
        if any(self._normalize(term) in normalized for term in self._LOW_VALUE_TERMS):
            score -= 30
            reasons.append("bajo valor personal")
        return max(0, min(score, 100)), reasons

    def _delivery(
        self,
        score: int,
        *,
        source_count: int,
        official_count: int,
        category: NewsCategory,
    ) -> NewsDelivery:
        evidence_ok = source_count >= 2 or official_count >= 1
        urgent_category = category in {NewsCategory.EMERGENCY, NewsCategory.WEATHER}
        if score >= self.policy.urgent_threshold and urgent_category:
            if not self.policy.require_multiple_sources_for_interrupt or evidence_ok:
                return NewsDelivery.INTERRUPT
        if score >= self.policy.briefing_threshold:
            return NewsDelivery.DAILY_BRIEFING
        return NewsDelivery.SILENT

    @classmethod
    def _tokens(cls, value: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", cls._normalize(value))
            if len(token) > 2 and token not in cls._STOPWORDS
        }

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value.casefold())
        return "".join(char for char in decomposed if not unicodedata.combining(char))
