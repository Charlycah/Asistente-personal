from __future__ import annotations

import json
from html import unescape
from types import MappingProxyType
from typing import Callable, Mapping
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from .governed_information_sources import (
    GovernedInformationSource,
    InformationAuthority,
    InformationCoverage,
    InformationEvidenceKind,
    InformationProvenance,
    InformationRegion,
    InformationSourceCapability,
    InformationSourceClassification,
    InformationSourceKind,
)
from .governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryOrder,
)

WIKIMEDIA_COMMONS_API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"
_MAX_RESULTS = 20
_THUMBNAIL_WIDTH = 640
_MAX_RESPONSE_BYTES = 2_000_000
_EXTMETADATA_FIELDS = (
    "Artist",
    "Credit",
    "LicenseShortName",
    "LicenseUrl",
)


class WikimediaCommonsGovernedSourceAdapter:
    """Bounded read-only adapter for Wikimedia Commons visual search."""

    SOURCE_ID = "wikimedia_commons"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    network_enabled = True
    automatic_fetch_enabled = False
    source_declaration = GovernedInformationSource(
        source_id=SOURCE_ID,
        name="Wikimedia Commons",
        kind=InformationSourceKind.EDITORIAL,
        topics=frozenset(),
        capabilities=frozenset(
            {
                InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY,
                InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY,
            }
        ),
        classification=InformationSourceClassification(
            authority=InformationAuthority.GENERAL,
            provenance=InformationProvenance.AGGREGATED,
            evidence=InformationEvidenceKind.EDITORIAL_REPORTING,
            coverage=InformationCoverage.GLOBAL,
            regions=frozenset({InformationRegion.GLOBAL}),
            confidence=60,
        ),
    )

    def __init__(
        self,
        user_agent: str,
        transport: Callable[[str, float], bytes] | None = None,
    ) -> None:
        normalized_user_agent = user_agent.strip()
        if not normalized_user_agent:
            raise ValueError("Wikimedia Commons User-Agent cannot be empty")
        self._user_agent = normalized_user_agent
        self._transport = transport or self._http_get

    def execute(
        self,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if query.source_id != self.SOURCE_ID:
            raise ValueError(
                "Wikimedia Commons adapter only accepts its canonical source"
            )
        url = self._build_url(query)
        payload = self._transport(url, query.timeout_seconds)
        document = json.loads(payload.decode("utf-8"))
        return self._parse_items(document, query)

    @staticmethod
    def _build_url(query: GovernedSourceQuery) -> str:
        if not query.query_text:
            raise ValueError("Wikimedia Commons query text cannot be empty")
        parameters = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query.query_text,
            "gsrnamespace": "6",
            "gsrlimit": str(min(query.limit, _MAX_RESULTS)),
            "prop": "imageinfo",
            "iiprop": "url|mime|mediatype|timestamp|user|extmetadata",
            "iilimit": "1",
            "iiurlwidth": str(_THUMBNAIL_WIDTH),
            "iiextmetadatalanguage": "en",
            "iiextmetadatafilter": "|".join(_EXTMETADATA_FIELDS),
        }
        if query.order is GovernedSourceQueryOrder.NEWEST_FIRST:
            parameters["gsrsort"] = "create_timestamp_desc"
        return f"{WIKIMEDIA_COMMONS_API_ENDPOINT}?{urlencode(parameters)}"

    @classmethod
    def _parse_items(
        cls,
        document: object,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if not isinstance(document, dict):
            raise ValueError("Wikimedia Commons response root must be an object")
        query_data = document.get("query")
        if not isinstance(query_data, dict):
            raise ValueError("Wikimedia Commons response has no query object")
        pages = query_data.get("pages")
        if not isinstance(pages, dict):
            raise ValueError("Wikimedia Commons response has no pages object")
        parsed: list[Mapping[str, object]] = []
        for page in list(pages.values())[: min(query.limit, _MAX_RESULTS)]:
            normalized = cls._parse_item(page)
            if normalized is not None:
                parsed.append(MappingProxyType(normalized))
        return tuple(parsed)

    @staticmethod
    def _parse_item(page: object) -> dict[str, object] | None:
        if not isinstance(page, dict):
            return None
        title = _text(page.get("title"))
        page_id = _text(page.get("pageid"))
        imageinfo = page.get("imageinfo")
        if not title or not page_id:
            return None
        if not isinstance(imageinfo, list) or not imageinfo:
            return None
        info = imageinfo[0]
        if not isinstance(info, dict):
            return None
        mime = (_text(info.get("mime")) or "").casefold()
        if not mime.startswith("image/"):
            return None
        thumb_value = _text(info.get("thumburl"))
        if thumb_value is not None:
            preview_url = _https_url(thumb_value)
            if preview_url is None:
                return None
        else:
            preview_url = _https_url(info.get("url"))
            if preview_url is None:
                return None
        metadata = info.get("extmetadata")
        if not isinstance(metadata, dict):
            metadata = {}
        result: dict[str, object] = {
            "source_id": WikimediaCommonsGovernedSourceAdapter.SOURCE_ID,
            "external_id": page_id,
            "title": title,
            "media_type": "image",
            "preview_url": preview_url,
            "verification": "provider_metadata",
        }
        optional = {
            "source_url": _https_url(info.get("descriptionurl")),
            "published_at": _text(info.get("timestamp")),
            "uploader": _text(info.get("user")),
            "artist": _metadata_text(metadata, "Artist"),
            "credit": _metadata_text(metadata, "Credit"),
            "license_short_name": _metadata_text(
                metadata, "LicenseShortName"
            ),
            "license_url": _https_url(
                _metadata_text(metadata, "LicenseUrl")
            ),
        }
        result.update(
            {key: value for key, value in optional.items() if value is not None}
        )
        return result

    def _http_get(self, url: str, timeout_seconds: float) -> bytes:
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": self._user_agent,
            },
            method="GET",
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(payload) > _MAX_RESPONSE_BYTES:
            raise ValueError(
                "Wikimedia Commons response exceeded the governed size limit"
            )
        return payload


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _metadata_text(metadata: Mapping[str, object], key: str) -> str | None:
    entry = metadata.get(key)
    if not isinstance(entry, dict):
        return None
    value = _text(entry.get("value"))
    if value is None:
        return None
    return unescape(value)


def _https_url(value: object) -> str | None:
    text = _text(value)
    if text is None:
        return None
    parsed = urlparse(text)
    if parsed.scheme.casefold() != "https" or not parsed.netloc:
        return None
    return text
