from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from types import MappingProxyType
from typing import Callable, Mapping
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .governed_source_query import GovernedSourceQuery
from .personal_interest_center import InterestTopic

HEALTHY_EATING_ENDPOINT = "https://www.argentina.gob.ar/salud/alimentacion-saludable"
HEALTHY_RECIPES_ENDPOINT = (
    "https://www.argentina.gob.ar/salud/alimentacion-saludable/recetas"
)
_MAX_RESPONSE_BYTES = 2_000_000
_HEALTHY_TOPICS = frozenset(
    {
        InterestTopic.HEALTHY_EATING,
        InterestTopic.EVIDENCE_BASED_NUTRITION,
        InterestTopic.HEALTHY_RECIPES,
        InterestTopic.MEDITERRANEAN_CUISINE,
        InterestTopic.ARGENTINE_CUISINE,
    }
)
_RELEVANT_TERMS = (
    "aliment",
    "salud",
    "receta",
    "verdura",
    "fruta",
    "legumbre",
    "cereal",
    "nutric",
    "porción",
    "porcion",
    "comida",
    "cocina",
)


@dataclass(frozen=True)
class ArgentinaHealthyEatingGovernedSourceSnapshot:
    schema_version: str
    source_id: str
    authority: str
    endpoints: tuple[str, ...]
    network_enabled: bool
    automatic_fetch_enabled: bool
    credentials_required: bool
    official_public_source: bool
    evidence_based: bool
    region: str


class ArgentinaHealthyEatingGovernedSourceAdapter:
    """Controlled adapter for official Argentine healthy-eating guidance."""

    SCHEMA_VERSION = "m345.4"
    SOURCE_ID = "argentina_healthy_eating"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    network_enabled = True

    def __init__(
        self,
        transport: Callable[[str, float], bytes] | None = None,
    ) -> None:
        self._transport = transport or self._http_get

    @property
    def snapshot(self) -> ArgentinaHealthyEatingGovernedSourceSnapshot:
        return ArgentinaHealthyEatingGovernedSourceSnapshot(
            schema_version=self.SCHEMA_VERSION,
            source_id=self.SOURCE_ID,
            authority=self.AUTHORITY,
            endpoints=(HEALTHY_EATING_ENDPOINT, HEALTHY_RECIPES_ENDPOINT),
            network_enabled=True,
            automatic_fetch_enabled=False,
            credentials_required=False,
            official_public_source=True,
            evidence_based=True,
            region="argentina",
        )

    def execute(
        self,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if query.source_id != self.SOURCE_ID:
            raise ValueError("Healthy-eating adapter only accepts its canonical source")
        if not query.topics.issubset(_HEALTHY_TOPICS):
            raise ValueError("Healthy-eating query contains unsupported topics")
        endpoint = self._endpoint_for(query.topics)
        payload = self._transport(endpoint, query.timeout_seconds)
        return self._parse_items(payload, query, endpoint)

    @staticmethod
    def _endpoint_for(topics: frozenset[InterestTopic]) -> str:
        if InterestTopic.HEALTHY_RECIPES in topics:
            return HEALTHY_RECIPES_ENDPOINT
        return HEALTHY_EATING_ENDPOINT

    @staticmethod
    def _parse_items(
        payload: bytes,
        query: GovernedSourceQuery,
        endpoint: str,
    ) -> tuple[Mapping[str, object], ...]:
        parser = _OfficialHealthPageParser(endpoint)
        parser.feed(payload.decode("utf-8", errors="replace"))
        items: list[Mapping[str, object]] = []
        seen: set[tuple[str, str]] = set()
        for title, source_url in parser.entries:
            folded = title.casefold()
            if not any(term in folded for term in _RELEVANT_TERMS):
                continue
            identity = (title.casefold(), source_url)
            if identity in seen:
                continue
            seen.add(identity)
            topics = set(query.topics)
            if "receta" in folded or "cocina" in folded:
                topics.add(InterestTopic.HEALTHY_RECIPES)
            if any(term in folded for term in ("guía", "guia", "gráfica", "grafica")):
                topics.add(InterestTopic.EVIDENCE_BASED_NUTRITION)
            items.append(
                MappingProxyType(
                    {
                        "source_id": (
                            ArgentinaHealthyEatingGovernedSourceAdapter.SOURCE_ID
                        ),
                        "external_id": _external_id(source_url, title),
                        "title": title,
                        "topics": tuple(sorted(topic.value for topic in topics)),
                        "tags": (
                            "alimentacion-saludable",
                            "ministerio-de-salud",
                            "evidencia-oficial",
                        ),
                        "published_at": None,
                        "time_sensitive": False,
                        "region": "argentina",
                        "verification": "confirmed",
                        "information_kind": "guidance",
                        "source_url": source_url,
                        "location": "Argentina",
                    }
                )
            )
            if len(items) >= query.limit:
                break
        return tuple(items)

    @staticmethod
    def _http_get(url: str, timeout_seconds: float) -> bytes:
        request = Request(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "es-AR,es;q=0.9",
                "User-Agent": "ROBY-XI.2",
            },
            method="GET",
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(payload) > _MAX_RESPONSE_BYTES:
            raise ValueError("Healthy-eating response exceeded the size limit")
        return payload


class _OfficialHealthPageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self._base_url = base_url
        self._capture_tag: str | None = None
        self._href: str | None = None
        self._parts: list[str] = []
        self.entries: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag not in {"a", "h2", "h3", "h4"}:
            return
        self._capture_tag = tag
        self._parts = []
        attributes = dict(attrs)
        self._href = attributes.get("href") if tag == "a" else None

    def handle_data(self, data: str) -> None:
        if self._capture_tag is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != self._capture_tag:
            return
        title = " ".join("".join(self._parts).split())
        if title:
            url = urljoin(self._base_url, self._href) if self._href else self._base_url
            self.entries.append((title, url))
        self._capture_tag = None
        self._href = None
        self._parts = []


def _external_id(source_url: str, title: str) -> str:
    tail = source_url.rstrip("/").rsplit("/", 1)[-1]
    if tail and tail not in {"alimentacion-saludable", "recetas"}:
        return tail
    return "-".join(title.casefold().split())[:120]
