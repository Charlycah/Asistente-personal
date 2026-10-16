from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from types import MappingProxyType
from typing import Callable, Mapping
from urllib.request import Request, urlopen

from .governed_source_query import GovernedSourceQuery
from .personal_interest_center import InterestTopic

CULTURA_CABA_AGENDA_ENDPOINT = (
    "https://turismo.buenosaires.gob.ar/es/article/que-hacer-esta-semana"
)
_MAX_RESPONSE_BYTES = 2_000_000
_CULTURAL_TOPICS = frozenset(
    {
        InterestTopic.CULTURE_CABA,
        InterestTopic.MUSIC,
        InterestTopic.THEATRE,
        InterestTopic.MUSEUMS,
        InterestTopic.FREE_ACTIVITIES,
    }
)


@dataclass(frozen=True)
class CulturaCabaGovernedSourceSnapshot:
    schema_version: str
    source_id: str
    authority: str
    endpoint: str
    network_enabled: bool
    automatic_fetch_enabled: bool
    credentials_required: bool
    official_public_source: bool


class CulturaCabaGovernedSourceAdapter:
    """Controlled adapter for the official current Buenos Aires agenda page."""

    SCHEMA_VERSION = "m345.2"
    SOURCE_ID = "cultura_caba"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    network_enabled = True

    def __init__(
        self,
        transport: Callable[[str, float], bytes] | None = None,
    ) -> None:
        self._transport = transport or self._http_get

    @property
    def snapshot(self) -> CulturaCabaGovernedSourceSnapshot:
        return CulturaCabaGovernedSourceSnapshot(
            schema_version=self.SCHEMA_VERSION,
            source_id=self.SOURCE_ID,
            authority=self.AUTHORITY,
            endpoint=CULTURA_CABA_AGENDA_ENDPOINT,
            network_enabled=True,
            automatic_fetch_enabled=False,
            credentials_required=False,
            official_public_source=True,
        )

    def execute(
        self,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if query.source_id != self.SOURCE_ID:
            raise ValueError(
                "Cultura CABA adapter only accepts the Cultura CABA source"
            )
        if not query.topics.issubset(_CULTURAL_TOPICS):
            raise ValueError("Cultura CABA query contains unsupported topics")
        payload = self._transport(
            CULTURA_CABA_AGENDA_ENDPOINT,
            query.timeout_seconds,
        )
        document = payload.decode("utf-8", errors="replace")
        return self._parse_items(document, query)

    @staticmethod
    def _parse_items(
        document: str,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        parser = _AgendaHeadingParser()
        parser.feed(document)
        search_terms = _query_terms(query.query_text)
        selected = [
            title
            for title in parser.titles
            if not search_terms or _matches(title, search_terms)
        ]
        if not selected and search_terms:
            selected = list(parser.titles)
        items: list[Mapping[str, object]] = []
        for index, title in enumerate(selected[: query.limit], start=1):
            external_id = f"agenda-{_slug(title)}-{index}"
            items.append(
                MappingProxyType(
                    {
                        "source_id": CulturaCabaGovernedSourceAdapter.SOURCE_ID,
                        "external_id": external_id,
                        "title": title,
                        "topics": tuple(
                            sorted(topic.value for topic in query.topics)
                        ),
                        "tags": ("cultura", "caba", "agenda-oficial"),
                        "location": "Ciudad Autónoma de Buenos Aires",
                        "is_free": _looks_free(title),
                        "time_sensitive": True,
                        "region": "caba",
                        "verification": "confirmed",
                        "information_kind": "event",
                        "source_url": CULTURA_CABA_AGENDA_ENDPOINT,
                    }
                )
            )
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
            raise ValueError("Cultura CABA response exceeded the governed size limit")
        return payload


class _AgendaHeadingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._inside_heading = False
        self._parts: list[str] = []
        self.titles: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        del attrs
        if tag.casefold() in {"h2", "h3"}:
            self._inside_heading = True
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_heading:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._inside_heading or tag.casefold() not in {"h2", "h3"}:
            return
        title = " ".join("".join(self._parts).split())
        self._inside_heading = False
        self._parts = []
        if title and _fold(title) not in {
            "mas informacion",
            "tambien te puede interesar",
        }:
            self.titles.append(title)


def _query_terms(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    ignored = {
        "agenda",
        "actividad",
        "actividades",
        "caba",
        "cultura",
        "cultural",
        "culturales",
        "evento",
        "eventos",
    }
    return tuple(
        word
        for word in re.findall(r"[a-z]+", _fold(value))
        if len(word) > 2 and word not in ignored
    )


def _matches(title: str, terms: tuple[str, ...]) -> bool:
    folded = _fold(title)
    return any(_fold(term) in folded for term in terms)


def _looks_free(title: str) -> bool:
    folded = _fold(title)
    return any(term in folded for term in ("gratis", "gratuito", "gratuita", "libre"))


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", _fold(value)).strip("-")
    return slug[:72] or "evento"


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
