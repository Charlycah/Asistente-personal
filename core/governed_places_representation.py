from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.location_resolution import LocationResolutionStatus
from core.places_knowledge import PlaceKnowledgeProfile, PlaceKnowledgeStatus


class PlaceRepresentationStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedPlaceFact:
    kind: str
    name: str
    value: str
    source: str
    external_id: str | None


@dataclass(frozen=True)
class GovernedPlace:
    place_id: str
    label: str
    reference_kind: str
    owner: str
    facts: tuple[GovernedPlaceFact, ...]
    source_profile_id: str
    source_resolution_id: str
    active: bool = True


@dataclass(frozen=True)
class GovernedPlacesRepresentation:
    representation_id: str
    status: PlaceRepresentationStatus
    places: tuple[GovernedPlace, ...]
    source_profile_ids: tuple[str, ...]
    source_resolution_ids: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m392.3"
    canonical_authority: str = "internal_world_model"
    source_authorities: tuple[str, ...] = (
        "location_resolution",
        "places_knowledge",
    )
    read_only: bool = True
    persistence_added: bool = False
    inference_added: bool = False
    modifies_source_data: bool = False
    grants_authority: bool = False
    uses_live_location: bool = False
    tracks_people: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.representation_id.startswith("places-world-"):
            raise ValueError("places representation identifier is invalid")
        if self.canonical_authority != "internal_world_model":
            raise ValueError("places representation must preserve world authority")
        if self.source_authorities != (
            "location_resolution",
            "places_knowledge",
        ):
            raise ValueError("places representation source authorities are invalid")
        if tuple(sorted(self.places, key=_place_sort_key)) != self.places:
            raise ValueError("places must use canonical ordering")
        if tuple(sorted(set(self.source_profile_ids))) != self.source_profile_ids:
            raise ValueError("place profile ids must be unique and ordered")
        if tuple(sorted(set(self.source_resolution_ids))) != self.source_resolution_ids:
            raise ValueError("place resolution ids must be unique and ordered")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.inference_added,
                self.modifies_source_data,
                self.grants_authority,
                self.uses_live_location,
                self.tracks_people,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("places representation violates governed limits")

    def place(self, place_id: str) -> GovernedPlace | None:
        return next((item for item in self.places if item.place_id == place_id), None)


class GovernedPlacesRepresentationView:
    """Pure world-model view over already resolved place knowledge."""

    CANONICAL_AUTHORITY = "internal_world_model"

    def build(
        self,
        profiles: tuple[PlaceKnowledgeProfile, ...] = (),
    ) -> GovernedPlacesRepresentation:
        self._validate_unique_profiles(profiles)
        places: list[GovernedPlace] = []
        risks: list[str] = []

        for profile in profiles:
            resolution = profile.request.resolved_location
            if profile.status is not PlaceKnowledgeStatus.READY:
                risks.append(f"place_profile_not_ready:{profile.profile_id}")
                continue
            if resolution.status is not LocationResolutionStatus.RESOLVED:
                risks.append(f"location_not_resolved:{resolution.resolution_id}")
                continue
            if profile.place_label is None:
                risks.append(f"place_label_missing:{profile.profile_id}")
                continue

            facts = tuple(
                sorted(
                    (
                        GovernedPlaceFact(
                            kind=fact.kind.value,
                            name=fact.name,
                            value=fact.value,
                            source=fact.source,
                            external_id=fact.external_id,
                        )
                        for fact in profile.accepted_facts
                    ),
                    key=_fact_sort_key,
                )
            )
            places.append(
                GovernedPlace(
                    place_id=f"place:{profile.profile_id}",
                    label=profile.place_label,
                    reference_kind=resolution.request.reference_kind.value,
                    owner=profile.request.owner,
                    facts=facts,
                    source_profile_id=profile.profile_id,
                    source_resolution_id=resolution.resolution_id,
                )
            )

        canonical_places = tuple(sorted(places, key=_place_sort_key))
        canonical_risks = tuple(sorted(set(risks)))
        source_profile_ids = tuple(
            sorted(place.source_profile_id for place in canonical_places)
        )
        source_resolution_ids = tuple(
            sorted(place.source_resolution_id for place in canonical_places)
        )
        evidence_codes = (
            "authority:internal_world_model",
            "source_authority:location_resolution",
            "source_authority:places_knowledge",
        )
        fingerprint = _fingerprint(canonical_places, canonical_risks)
        return GovernedPlacesRepresentation(
            representation_id=f"places-world-{fingerprint[:16]}",
            status=self._status(canonical_places, canonical_risks),
            places=canonical_places,
            source_profile_ids=source_profile_ids,
            source_resolution_ids=source_resolution_ids,
            evidence_codes=evidence_codes,
            risk_codes=canonical_risks,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _validate_unique_profiles(
        profiles: tuple[PlaceKnowledgeProfile, ...],
    ) -> None:
        profile_ids = tuple(profile.profile_id for profile in profiles)
        if len(profile_ids) != len(set(profile_ids)):
            raise ValueError("place knowledge profile ids must be unique")

    @staticmethod
    def _status(
        places: tuple[GovernedPlace, ...],
        risks: tuple[str, ...],
    ) -> PlaceRepresentationStatus:
        if risks:
            return PlaceRepresentationStatus.REVIEW_REQUIRED
        if not places:
            return PlaceRepresentationStatus.EMPTY
        return PlaceRepresentationStatus.COMPLETE


def _fact_sort_key(fact: GovernedPlaceFact) -> tuple[str, str, str]:
    return fact.kind, fact.name.casefold(), fact.value.casefold()


def _place_sort_key(place: GovernedPlace) -> tuple[str, str]:
    return place.label.casefold(), place.place_id


def _fingerprint(
    places: tuple[GovernedPlace, ...],
    risks: tuple[str, ...],
) -> str:
    payload = "||".join(
        (
            *(
                "|".join(
                    (
                        place.place_id,
                        place.label.casefold(),
                        place.reference_kind,
                        place.owner.casefold(),
                        place.source_profile_id,
                        place.source_resolution_id,
                        ";".join(
                            "|".join(
                                (
                                    fact.kind,
                                    fact.name.casefold(),
                                    fact.value.casefold(),
                                    fact.source,
                                    fact.external_id or "none",
                                )
                            )
                            for fact in place.facts
                        ),
                    )
                )
                for place in places
            ),
            *risks,
        )
    )
    return sha256(payload.encode("utf-8")).hexdigest()
