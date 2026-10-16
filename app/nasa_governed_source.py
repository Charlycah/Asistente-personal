from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Callable, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .governed_source_query import GovernedSourceQuery
from .personal_interest_center import InterestTopic

NASA_IMAGES_SEARCH_ENDPOINT = "https://images-api.nasa.gov/search"
_MAX_RESPONSE_BYTES = 2_000_000
_ALLOWED_MEDIA_TYPES = frozenset({"audio", "image", "video"})
_TOPIC_TERMS = {
    InterestTopic.SPACE_EXPLORATION: "space exploration",
    InterestTopic.NASA_MISSIONS: "NASA mission",
    InterestTopic.INTERNATIONAL_SPACE_STATION: "International Space Station",
    InterestTopic.JAMES_WEBB_SPACE_TELESCOPE: "James Webb Space Telescope",
}


@dataclass(frozen=True)
class NasaGovernedSourceSnapshot:
    schema_version: str
    source_id: str
    authority: str
    endpoint: str
    network_enabled: bool
    automatic_fetch_enabled: bool
    credentials_required: bool


class NasaGovernedSourceAdapter:
    """Controlled adapter for NASA's official Image and Video Library."""

    SCHEMA_VERSION = "m344.2"
    SOURCE_ID = "nasa"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    network_enabled = True

    def __init__(
        self,
        transport: Callable[[str, float], bytes] | None = None,
    ) -> None:
        self._transport = transport or self._http_get

    @property
    def snapshot(self) -> NasaGovernedSourceSnapshot:
        return NasaGovernedSourceSnapshot(
            schema_version=self.SCHEMA_VERSION,
            source_id=self.SOURCE_ID,
            authority=self.AUTHORITY,
            endpoint=NASA_IMAGES_SEARCH_ENDPOINT,
            network_enabled=True,
            automatic_fetch_enabled=False,
            credentials_required=False,
        )

    def execute(
        self,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if query.source_id != self.SOURCE_ID:
            raise ValueError("NASA adapter only accepts the NASA governed source")
        url = self._build_url(query)
        payload = self._transport(url, query.timeout_seconds)
        document = json.loads(payload.decode("utf-8"))
        return self._parse_items(document, query)

    @staticmethod
    def _build_url(query: GovernedSourceQuery) -> str:
        search_text = query.query_text or " ".join(
            _TOPIC_TERMS[topic]
            for topic in sorted(query.topics, key=lambda item: item.value)
        )
        media_type = query.parameters.get("media_type", "image")
        if media_type not in _ALLOWED_MEDIA_TYPES:
            raise ValueError("NASA media_type must be audio, image, or video")
        parameters = {
            "q": search_text,
            "media_type": media_type,
            "page_size": str(query.limit),
        }
        if query.published_after is not None:
            parameters["year_start"] = str(query.published_after.year)
        if query.published_before is not None:
            parameters["year_end"] = str(query.published_before.year)
        return f"{NASA_IMAGES_SEARCH_ENDPOINT}?{urlencode(parameters)}"

    @staticmethod
    def _parse_items(
        document: object,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if not isinstance(document, dict):
            raise ValueError("NASA response root must be an object")
        collection = document.get("collection")
        if not isinstance(collection, dict):
            raise ValueError("NASA response has no collection")
        items = collection.get("items", [])
        if not isinstance(items, list):
            raise ValueError("NASA response items must be a list")
        parsed: list[Mapping[str, object]] = []
        for item in items[: query.limit]:
            normalized = NasaGovernedSourceAdapter._parse_item(item, query)
            if normalized is not None:
                parsed.append(MappingProxyType(normalized))
        return tuple(parsed)

    @staticmethod
    def _parse_item(
        item: object,
        query: GovernedSourceQuery,
    ) -> dict[str, object] | None:
        if not isinstance(item, dict):
            return None
        data = item.get("data")
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            return None
        record = data[0]
        external_id = str(record.get("nasa_id", "")).strip()
        title = str(record.get("title", "")).strip()
        if not external_id or not title:
            return None
        links = item.get("links")
        preview_url = None
        if isinstance(links, list) and links and isinstance(links[0], dict):
            preview_url = links[0].get("href")
        return {
            "source_id": "nasa",
            "external_id": external_id,
            "title": title,
            "description": str(record.get("description", "")).strip(),
            "published_at": _iso_datetime(record.get("date_created")),
            "topics": tuple(sorted(topic.value for topic in query.topics)),
            "tags": tuple(_strings(record.get("keywords"))),
            "location": _optional_text(record.get("location")),
            "center": _optional_text(record.get("center")),
            "media_type": _optional_text(record.get("media_type")),
            "preview_url": preview_url,
            "verification": "confirmed",
            "information_kind": "discovery",
        }

    @staticmethod
    def _http_get(url: str, timeout_seconds: float) -> bytes:
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "ROBY-XI.2"},
            method="GET",
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(payload) > _MAX_RESPONSE_BYTES:
            raise ValueError("NASA response exceeded the governed size limit")
        return payload


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _iso_datetime(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return None
