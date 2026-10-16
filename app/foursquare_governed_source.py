from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .governed_information_sources import (
    GovernedInformationSource,
    InformationAuthority,
    InformationCoverage,
    InformationEvidenceKind,
    InformationProvenance,
    InformationRegion,
    InformationSourceClassification,
    InformationSourceKind,
)
from .governed_source_query import GovernedSourceQuery
from .personal_interest_center import InterestTopic

FOURSQUARE_PLACE_SEARCH_ENDPOINT = "https://places-api.foursquare.com/places/search"
FOURSQUARE_PLACES_API_VERSION = "2025-06-17"
_MAX_RESPONSE_BYTES = 2_000_000
_ALLOWED_GEOGRAPHY = frozenset({"near", "ll", "radius", "ne", "sw"})
_ALLOWED_PARAMETERS = frozenset({"fields", "provider"}) | _ALLOWED_GEOGRAPHY


@dataclass(frozen=True)
class FoursquareGovernedSourceSnapshot:
    schema_version: str
    source_id: str
    authority: str
    endpoint: str
    network_enabled: bool
    automatic_fetch_enabled: bool
    credentials_required: bool
    provider: str


class FoursquareGovernedSourceAdapter:
    """Credential-gated adapter for bounded Foursquare Place Search."""

    SCHEMA_VERSION = "p7-c2-local-s2a"
    SOURCE_ID = "foursquare_places"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    network_enabled = True
    automatic_fetch_enabled = False
    source_declaration = GovernedInformationSource(
        source_id=SOURCE_ID,
        name="Foursquare Places",
        kind=InformationSourceKind.EDITORIAL,
        topics=frozenset(
            {InterestTopic.ARGENTINE_CUISINE, InterestTopic.CULTURE_CABA}
        ),
        classification=InformationSourceClassification(
            authority=InformationAuthority.SPECIALIZED,
            provenance=InformationProvenance.AGGREGATED,
            evidence=InformationEvidenceKind.EDITORIAL_REPORTING,
            coverage=InformationCoverage.GLOBAL,
            regions=frozenset({InformationRegion.GLOBAL}),
            confidence=60,
        ),
    )

    def __init__(
        self,
        api_key: str,
        transport: Callable[[str, float], bytes] | None = None,
    ) -> None:
        credential = api_key.strip()
        if not credential:
            raise ValueError("Foursquare service credential cannot be empty")
        self._credential = credential
        self._transport = transport or self._http_get

    @property
    def snapshot(self) -> FoursquareGovernedSourceSnapshot:
        return FoursquareGovernedSourceSnapshot(
            schema_version=self.SCHEMA_VERSION,
            source_id=self.SOURCE_ID,
            authority=self.AUTHORITY,
            endpoint=FOURSQUARE_PLACE_SEARCH_ENDPOINT,
            network_enabled=True,
            automatic_fetch_enabled=False,
            credentials_required=True,
            provider="foursquare",
        )

    def execute(
        self,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        if query.source_id != self.SOURCE_ID:
            raise ValueError("Foursquare adapter only accepts its canonical source")
        url = self._build_url(query)
        payload = self._transport(url, query.timeout_seconds)
        return self._parse_items(payload, query)

    @staticmethod
    def _build_url(query: GovernedSourceQuery) -> str:
        parameters = {
            key: value
            for key, value in dict(query.parameters or {}).items()
            if key in _ALLOWED_PARAMETERS and key != "provider"
        }
        if not FoursquareGovernedSourceAdapter._has_bounded_geography(parameters):
            raise ValueError("Foursquare place search requires explicit geography")
        if query.query_text:
            parameters["query"] = query.query_text
        parameters["limit"] = str(min(query.limit, 20))
        return f"{FOURSQUARE_PLACE_SEARCH_ENDPOINT}?{urlencode(parameters)}"

    @staticmethod
    def _has_bounded_geography(parameters: Mapping[str, str]) -> bool:
        if parameters.get("near"):
            return True
        if parameters.get("ll") and parameters.get("radius"):
            return True
        return bool(parameters.get("ne") and parameters.get("sw"))

    @staticmethod
    def _parse_items(
        payload: bytes,
        query: GovernedSourceQuery,
    ) -> tuple[Mapping[str, object], ...]:
        document = json.loads(payload.decode("utf-8"))
        results = document.get("results", [])
        if not isinstance(results, list):
            raise ValueError("Foursquare response has invalid results")
        items: list[Mapping[str, object]] = []
        for raw in results[: query.limit]:
            if not isinstance(raw, dict):
                continue
            external_id = _text(raw.get("fsq_place_id") or raw.get("fsq_id"))
            title = _text(raw.get("name"))
            if external_id is None or title is None:
                continue
            location = raw.get("location")
            location_data = location if isinstance(location, dict) else {}
            categories = raw.get("categories")
            category_names = _category_names(categories)
            items.append(
                MappingProxyType(
                    {
                        "source_id": FoursquareGovernedSourceAdapter.SOURCE_ID,
                        "external_id": external_id,
                        "title": title,
                        "topics": tuple(
                            sorted(topic.value for topic in query.topics)
                        ),
                        "tags": ("place", "business", *category_names),
                        "location": _location_label(location_data),
                        "time_sensitive": True,
                        "verification": "provider_reported",
                        "information_kind": "place_business",
                        "provider": "foursquare",
                    }
                )
            )
        return tuple(items)

    def _http_get(self, url: str, timeout_seconds: float) -> bytes:
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self._credential}",
                "X-Places-Api-Version": FOURSQUARE_PLACES_API_VERSION,
                "User-Agent": "ROBY-XI.2",
            },
            method="GET",
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(payload) > _MAX_RESPONSE_BYTES:
            raise ValueError("Foursquare response exceeded the governed size limit")
        return payload


def _text(value: object) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split())
    return cleaned or None


def _category_names(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    names: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        name = _text(item.get("name"))
        if name:
            names.append(name)
    return tuple(names)


def _location_label(value: Mapping[str, object]) -> str | None:
    for key in ("formatted_address", "locality", "region", "country"):
        label = _text(value.get(key))
        if label:
            return label
    return None
