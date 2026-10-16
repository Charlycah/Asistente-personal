from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Callable, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .governed_source_query import GovernedSourceQuery
from .personal_interest_center import InterestTopic

APPLE_SEARCH_ENDPOINT = "https://itunes.apple.com/search"
_MAX_RESPONSE_BYTES = 2_000_000
_AUDIOVISUAL_TOPICS = frozenset(
    {
        InterestTopic.CINEMA,
        InterestTopic.SERIES,
        InterestTopic.RELEASES,
        InterestTopic.SCIENCE_FICTION,
        InterestTopic.HARD_SCIENCE_FICTION,
        InterestTopic.DOCUMENTARIES,
    }
)


@dataclass(frozen=True)
class AppleAudiovisualGovernedSourceSnapshot:
    schema_version: str
    source_id: str
    authority: str
    endpoint: str
    network_enabled: bool
    automatic_fetch_enabled: bool
    credentials_required: bool
    official_public_source: bool
    supported_media: tuple[str, ...]
    storefront_country: str


class AppleAudiovisualGovernedSourceAdapter:
    """Controlled adapter for Apple's public movie and TV catalog search."""

    SCHEMA_VERSION = "m345.3"
    SOURCE_ID = "apple_audiovisual"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    network_enabled = True

    def __init__(
        self,
        transport: Callable[[str, float], bytes] | None = None,
    ) -> None:
        self._transport = transport or self._http_get

    @property
    def snapshot(self) -> AppleAudiovisualGovernedSourceSnapshot:
        return AppleAudiovisualGovernedSourceSnapshot(
            schema_version=self.SCHEMA_VERSION,
            source_id=self.SOURCE_ID,
            authority=self.AUTHORITY,
            endpoint=APPLE_SEARCH_ENDPOINT,
            network_enabled=True,
            automatic_fetch_enabled=False,
            credentials_required=False,
            official_public_source=True,
            supported_media=("movie", "tvShow"),
            storefront_country="AR",
        )

    def execute(
        self,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if query.source_id != self.SOURCE_ID:
            raise ValueError(
                "Apple audiovisual adapter only accepts its canonical source"
            )
        if not query.topics.issubset(_AUDIOVISUAL_TOPICS):
            raise ValueError("Apple audiovisual query contains unsupported topics")
        term = query.query_text or self._default_term(query.topics)
        media = self._media_for(query.topics)
        url = self._build_url(term=term, media=media, limit=query.limit)
        payload = self._transport(url, query.timeout_seconds)
        return self._parse_items(payload, query)

    @staticmethod
    def _build_url(*, term: str, media: str, limit: int) -> str:
        parameters = urlencode(
            {
                "term": term,
                "country": "AR",
                "media": media,
                "limit": min(limit, 50),
                "lang": "es_ar",
                "explicit": "No",
            }
        )
        return f"{APPLE_SEARCH_ENDPOINT}?{parameters}"

    @staticmethod
    def _parse_items(
        payload: bytes,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        document = json.loads(payload.decode("utf-8"))
        results = document.get("results", [])
        if not isinstance(results, list):
            raise ValueError("Apple audiovisual response has invalid results")
        items: list[Mapping[str, object]] = []
        for raw in results[: query.limit]:
            if not isinstance(raw, dict):
                continue
            title = _text(raw.get("trackName") or raw.get("collectionName"))
            external_id = _text(raw.get("trackId") or raw.get("collectionId"))
            if title is None or external_id is None:
                continue
            kind = str(raw.get("kind", "")).casefold()
            topics = set(query.topics)
            topics.add(InterestTopic.SERIES if "tv" in kind else InterestTopic.CINEMA)
            genre = _text(raw.get("primaryGenreName"))
            description = _text(
                raw.get("longDescription") or raw.get("shortDescription")
            )
            folded_metadata = " ".join(
                value.casefold()
                for value in (title, genre, description)
                if value is not None
            )
            if "documentary" in folded_metadata or "documental" in folded_metadata:
                topics.add(InterestTopic.DOCUMENTARIES)
            if (
                "science fiction" in folded_metadata
                or "ciencia ficcion" in folded_metadata
            ):
                topics.add(InterestTopic.SCIENCE_FICTION)
            release_date = _published_at(raw.get("releaseDate"))
            items.append(
                MappingProxyType(
                    {
                        "source_id": AppleAudiovisualGovernedSourceAdapter.SOURCE_ID,
                        "external_id": external_id,
                        "title": title,
                        "topics": tuple(sorted(topic.value for topic in topics)),
                        "tags": tuple(
                            value
                            for value in (
                                "audiovisual",
                                "apple-catalog",
                                genre,
                            )
                            if value
                        ),
                        "published_at": release_date,
                        "time_sensitive": InterestTopic.RELEASES in query.topics,
                        "region": "argentina",
                        "verification": "confirmed",
                        "information_kind": "release",
                        "source_url": _text(raw.get("trackViewUrl")),
                        "description": description,
                    }
                )
            )
        return tuple(items)

    @staticmethod
    def _media_for(topics: frozenset[InterestTopic]) -> str:
        if InterestTopic.SERIES in topics and InterestTopic.CINEMA not in topics:
            return "tvShow"
        return "movie"

    @staticmethod
    def _default_term(topics: frozenset[InterestTopic]) -> str:
        if InterestTopic.DOCUMENTARIES in topics:
            return "documentary"
        if InterestTopic.HARD_SCIENCE_FICTION in topics:
            return "hard science fiction"
        if InterestTopic.SCIENCE_FICTION in topics:
            return "science fiction"
        if InterestTopic.SERIES in topics:
            return "series"
        return "movie"

    @staticmethod
    def _http_get(url: str, timeout_seconds: float) -> bytes:
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Language": "es-AR,es;q=0.9",
                "User-Agent": "ROBY-XI.2",
            },
            method="GET",
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(payload) > _MAX_RESPONSE_BYTES:
            raise ValueError("Apple audiovisual response exceeded the size limit")
        return payload


def _text(value: object) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split())
    return cleaned or None


def _published_at(value: object) -> str | None:
    text = _text(value)
    if text is None:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()
