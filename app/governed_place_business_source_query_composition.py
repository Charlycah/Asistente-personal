from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Mapping

from .governed_conversational_source_selection import (
    GovernedConversationalSourceSelection,
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
    GovernedConversationalSourceSelector,
)
from .governed_information_sources import GovernedInformationSources
from .governed_source_query import (
    GovernedSourceQueryContract,
    GovernedSourceQueryResult,
)


class GovernedPlaceBusinessSourceQueryCompositionStatus(StrEnum):
    PREPARED = "prepared"
    NOT_AUTHORIZED = "not_authorized"
    UNAVAILABLE = "unavailable"
    INVALID_REQUEST = "invalid_request"


@dataclass(frozen=True)
class GovernedPlaceBusinessSourceQueryCompositionResult:
    status: GovernedPlaceBusinessSourceQueryCompositionStatus
    selection: GovernedConversationalSourceSelection | None = None
    prepared_query: GovernedSourceQueryResult | None = None
    rationale_codes: tuple[str, ...] = ()


class GovernedPlaceBusinessSourceQueryComposition:
    """Prepare a bounded Foursquare place query; never perform retrieval."""

    PROVIDER_MARKER = "foursquare"
    MAX_LIMIT = 20
    MAX_FIELDS = 12

    def __init__(
        self,
        *,
        sources: GovernedInformationSources,
        selector: GovernedConversationalSourceSelector,
        query_contract: GovernedSourceQueryContract | None = None,
    ) -> None:
        self.sources = sources
        self.selector = selector
        self.query_contract = query_contract or GovernedSourceQueryContract(sources)

    def compose(
        self,
        *,
        explicit_local_business_intent: bool,
        geographic_context: Mapping[str, str] | str | None,
        query_text: str,
        limit: int,
        fields: Iterable[str],
        request: GovernedConversationalSourceSelectionRequest,
        registered_sources: Iterable[str],
    ) -> GovernedPlaceBusinessSourceQueryCompositionResult:
        if not explicit_local_business_intent:
            return self._result(
                GovernedPlaceBusinessSourceQueryCompositionStatus.NOT_AUTHORIZED,
                "explicit_local_business_intent_required",
            )

        geography = self._bounded_geography(geographic_context)
        if geography is None:
            return self._result(
                GovernedPlaceBusinessSourceQueryCompositionStatus.NOT_AUTHORIZED,
                "explicit_bounded_geography_required",
            )

        normalized_query = " ".join(query_text.split())
        normalized_fields = self._bounded_fields(fields)
        if (
            not normalized_query
            or not 1 <= limit <= self.MAX_LIMIT
            or normalized_fields is None
        ):
            return self._result(
                GovernedPlaceBusinessSourceQueryCompositionStatus.INVALID_REQUEST,
                "bounded_query_fields_and_limit_required",
            )

        provider_ids = self._provider_source_ids(registered_sources)
        if not provider_ids:
            return self._result(
                GovernedPlaceBusinessSourceQueryCompositionStatus.UNAVAILABLE,
                "registered_foursquare_source_required",
            )

        parameters = dict(request.parameters or {})
        parameters.update(geography)
        parameters["fields"] = ",".join(normalized_fields)
        parameters["provider"] = self.PROVIDER_MARKER

        bounded_request = GovernedConversationalSourceSelectionRequest(
            text=request.text,
            topics=request.topics,
            query_text=normalized_query,
            limit=limit,
            region=request.region,
            published_after=request.published_after,
            published_before=request.published_before,
            timeout_seconds=request.timeout_seconds,
            parameters=parameters,
        )
        selection = self.selector.select(
            bounded_request,
            registered_sources=provider_ids,
        )
        if (
            selection.status is not GovernedConversationalSourceSelectionStatus.SELECTED
            or selection.query is None
        ):
            return self._result(
                GovernedPlaceBusinessSourceQueryCompositionStatus.UNAVAILABLE,
                "governed_source_selector_found_no_provider_source",
                selection=selection,
            )

        prepared = self.query_contract.prepare(selection.query)
        return GovernedPlaceBusinessSourceQueryCompositionResult(
            status=GovernedPlaceBusinessSourceQueryCompositionStatus.PREPARED,
            selection=selection,
            prepared_query=prepared,
            rationale_codes=(
                "registered_governed_foursquare_source_query_prepared",
                "explicit_geography_preserved_without_implicit_fallback",
                "composition_stops_before_retrieval",
                "discovery_does_not_authorize_reservation_or_navigation",
            ),
        )

    def _provider_source_ids(
        self,
        registered_sources: Iterable[str],
    ) -> tuple[str, ...]:
        eligible: list[str] = []
        seen: set[str] = set()
        for source_id in registered_sources:
            normalized = source_id.strip().casefold()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            if self.PROVIDER_MARKER not in normalized:
                continue
            try:
                self.sources.source_for(normalized)
            except KeyError:
                continue
            eligible.append(normalized)
        return tuple(eligible)

    @staticmethod
    def _bounded_geography(
        geographic_context: Mapping[str, str] | str | None,
    ) -> dict[str, str] | None:
        if isinstance(geographic_context, str):
            near = " ".join(geographic_context.split())
            return {"near": near} if near else None
        if not geographic_context:
            return None

        normalized = {
            str(key).strip().casefold(): str(value).strip()
            for key, value in geographic_context.items()
            if str(key).strip() and str(value).strip()
        }
        near = normalized.get("near")
        if near:
            return {"near": near}

        ll = normalized.get("ll")
        radius = normalized.get("radius")
        if ll and radius:
            return {"ll": ll, "radius": radius}

        north_east = normalized.get("ne")
        south_west = normalized.get("sw")
        if north_east and south_west:
            return {"ne": north_east, "sw": south_west}
        return None

    @classmethod
    def _bounded_fields(cls, fields: Iterable[str]) -> tuple[str, ...] | None:
        normalized = tuple(
            dict.fromkeys(field.strip().casefold() for field in fields if field.strip())
        )
        if not normalized or len(normalized) > cls.MAX_FIELDS:
            return None
        return normalized

    @staticmethod
    def _result(
        status: GovernedPlaceBusinessSourceQueryCompositionStatus,
        rationale_code: str,
        *,
        selection: GovernedConversationalSourceSelection | None = None,
    ) -> GovernedPlaceBusinessSourceQueryCompositionResult:
        return GovernedPlaceBusinessSourceQueryCompositionResult(
            status=status,
            selection=selection,
            rationale_codes=(rationale_code,),
        )
