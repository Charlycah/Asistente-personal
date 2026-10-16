from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_context_representation import GovernedContextRepresentation
from core.governed_household_representation import GovernedHouseholdRepresentation
from core.governed_objects_representation import GovernedObjectsRepresentation
from core.governed_people_representation import GovernedPeopleRepresentation
from core.governed_places_representation import GovernedPlacesRepresentation
from core.governed_timeline_representation import GovernedTimelineRepresentation


class WorldIntegrationStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedWorldIntegrationSnapshot:
    integration_id: str
    status: WorldIntegrationStatus
    household: GovernedHouseholdRepresentation
    people: GovernedPeopleRepresentation
    places: GovernedPlacesRepresentation
    objects: GovernedObjectsRepresentation
    timeline: GovernedTimelineRepresentation
    context: GovernedContextRepresentation
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m392.7"
    canonical_authority: str = "internal_world_model"
    read_only: bool = True
    persistence_added: bool = False
    inference_added: bool = False
    source_data_modified: bool = False
    authority_added: bool = False
    automation_added: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "internal_world_model":
            raise ValueError("world integration must preserve world authority")
        sources = (
            self.household,
            self.people,
            self.places,
            self.objects,
            self.timeline,
            self.context,
        )
        if any(
            item.canonical_authority != self.canonical_authority for item in sources
        ):
            raise ValueError("world domains must preserve the canonical authority")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.inference_added,
                self.source_data_modified,
                self.authority_added,
                self.automation_added,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("world integration violates governed limits")


class GovernedWorldIntegrationView:
    """Pure composition of the six governed M392 world representations."""

    def build(
        self,
        household: GovernedHouseholdRepresentation,
        people: GovernedPeopleRepresentation,
        places: GovernedPlacesRepresentation,
        objects: GovernedObjectsRepresentation,
        timeline: GovernedTimelineRepresentation,
        context: GovernedContextRepresentation,
    ) -> GovernedWorldIntegrationSnapshot:
        domains = (household, people, places, objects, timeline, context)
        risks = self._risk_codes(domains)
        fingerprint = self._fingerprint(domains, risks)
        return GovernedWorldIntegrationSnapshot(
            integration_id=f"integrated-world-{fingerprint[:16]}",
            status=self._status(domains, risks),
            household=household,
            people=people,
            places=places,
            objects=objects,
            timeline=timeline,
            context=context,
            evidence_codes=(
                "authority:internal_world_model",
                "source:m392.1:household",
                "source:m392.2:people",
                "source:m392.3:places",
                "source:m392.4:objects",
                "source:m392.5:timeline",
                "source:m392.6:context",
                "integration:composition_only",
            ),
            risk_codes=risks,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _risk_codes(domains: tuple[object, ...]) -> tuple[str, ...]:
        risks: list[str] = []
        names = ("household", "people", "places", "objects", "timeline", "context")
        for name, domain in zip(names, domains, strict=True):
            status = str(getattr(domain, "status").value)
            if status == "review_required":
                risks.append(f"domain_review_required:{name}")
        return tuple(risks)

    @staticmethod
    def _status(
        domains: tuple[object, ...], risks: tuple[str, ...]
    ) -> WorldIntegrationStatus:
        if risks:
            return WorldIntegrationStatus.REVIEW_REQUIRED
        statuses = tuple(str(getattr(item, "status").value) for item in domains)
        if all(status == "empty" for status in statuses):
            return WorldIntegrationStatus.EMPTY
        return WorldIntegrationStatus.COMPLETE

    @staticmethod
    def _fingerprint(domains: tuple[object, ...], risks: tuple[str, ...]) -> str:
        payload = "|".join(
            (
                *(str(getattr(item, "source_fingerprint")) for item in domains),
                *risks,
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()
