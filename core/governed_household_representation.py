from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.household_memory import HouseholdMemoryEntry, HouseholdMemoryStatus


class HouseholdSpaceKind(StrEnum):
    HOME = "home"
    ROOM = "room"
    ZONE = "zone"


class HouseholdSpatialRelationKind(StrEnum):
    CONTAINS = "contains"
    PART_OF = "part_of"
    ADJACENT_TO = "adjacent_to"
    CONNECTED_TO = "connected_to"


class HouseholdRepresentationStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class HouseholdSpaceEvidence:
    space_id: str
    label: str
    kind: HouseholdSpaceKind
    source_reference: str
    evidence_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, label in (
            (self.space_id, "space id"),
            (self.label, "space label"),
            (self.source_reference, "source reference"),
        ):
            if not value.strip():
                raise ValueError(f"household {label} must not be blank")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("household evidence codes must not be blank")


@dataclass(frozen=True)
class HouseholdSpatialRelationEvidence:
    relation_id: str
    source_space_id: str
    relation: HouseholdSpatialRelationKind
    target_space_id: str
    source_reference: str
    evidence_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, label in (
            (self.relation_id, "relation id"),
            (self.source_space_id, "source space id"),
            (self.target_space_id, "target space id"),
            (self.source_reference, "source reference"),
        ):
            if not value.strip():
                raise ValueError(f"household {label} must not be blank")
        if self.source_space_id == self.target_space_id:
            raise ValueError("household spatial relation cannot reference itself")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("household evidence codes must not be blank")


@dataclass(frozen=True)
class GovernedHouseholdSpace:
    space_id: str
    label: str
    kind: HouseholdSpaceKind
    source_reference: str
    evidence_codes: tuple[str, ...]
    active: bool


@dataclass(frozen=True)
class GovernedHouseholdSpatialRelation:
    relation_id: str
    source_space_id: str
    relation: HouseholdSpatialRelationKind
    target_space_id: str
    source_reference: str
    evidence_codes: tuple[str, ...]
    active: bool


@dataclass(frozen=True)
class GovernedHouseholdRepresentation:
    representation_id: str
    status: HouseholdRepresentationStatus
    spaces: tuple[GovernedHouseholdSpace, ...]
    relations: tuple[GovernedHouseholdSpatialRelation, ...]
    source_entry_ids: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m392.1"
    canonical_authority: str = "internal_world_model"
    source_authority: str = "household_memory"
    read_only: bool = True
    persistence_added: bool = False
    inference_added: bool = False
    modifies_source_data: bool = False
    grants_authority: bool = False
    controls_devices: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.representation_id.startswith("household-world-"):
            raise ValueError("household representation identifier is invalid")
        if self.canonical_authority != "internal_world_model":
            raise ValueError("household representation must preserve world authority")
        if self.source_authority != "household_memory":
            raise ValueError("household representation must preserve source authority")
        if tuple(sorted(self.spaces, key=_space_sort_key)) != self.spaces:
            raise ValueError("household spaces must use canonical ordering")
        if tuple(sorted(self.relations, key=_relation_sort_key)) != self.relations:
            raise ValueError("household relations must use canonical ordering")
        if tuple(sorted(set(self.source_entry_ids))) != self.source_entry_ids:
            raise ValueError("household source ids must be unique and ordered")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.inference_added,
                self.modifies_source_data,
                self.grants_authority,
                self.controls_devices,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("household representation violates governed limits")

    def space(self, space_id: str) -> GovernedHouseholdSpace | None:
        return next((item for item in self.spaces if item.space_id == space_id), None)

    def relations_for(
        self, space_id: str, *, active_only: bool = True
    ) -> tuple[GovernedHouseholdSpatialRelation, ...]:
        return tuple(
            item
            for item in self.relations
            if space_id in (item.source_space_id, item.target_space_id)
            and (item.active or not active_only)
        )


class GovernedHouseholdRepresentationView:
    """Pure household-space view over explicit HouseholdMemory evidence."""

    CANONICAL_AUTHORITY = "internal_world_model"
    SOURCE_AUTHORITY = "household_memory"

    def build(
        self,
        household_entries: tuple[HouseholdMemoryEntry, ...] = (),
        spaces: tuple[HouseholdSpaceEvidence, ...] = (),
        relations: tuple[HouseholdSpatialRelationEvidence, ...] = (),
    ) -> GovernedHouseholdRepresentation:
        entries = {entry.entry_id: entry for entry in household_entries}
        self._validate_unique_ids(spaces, relations)
        self._validate_sources(entries, spaces, relations)
        known_space_ids = {space.space_id for space in spaces}
        missing_endpoints = self._missing_endpoints(relations, known_space_ids)

        governed_spaces = tuple(
            sorted(
                (
                    GovernedHouseholdSpace(
                        space_id=space.space_id,
                        label=space.label,
                        kind=space.kind,
                        source_reference=space.source_reference,
                        evidence_codes=space.evidence_codes,
                        active=self._source_active(entries[space.source_reference]),
                    )
                    for space in spaces
                ),
                key=_space_sort_key,
            )
        )
        governed_relations = tuple(
            sorted(
                (
                    GovernedHouseholdSpatialRelation(
                        relation_id=relation.relation_id,
                        source_space_id=relation.source_space_id,
                        relation=relation.relation,
                        target_space_id=relation.target_space_id,
                        source_reference=relation.source_reference,
                        evidence_codes=relation.evidence_codes,
                        active=(
                            self._source_active(entries[relation.source_reference])
                            and relation.relation_id not in missing_endpoints
                        ),
                    )
                    for relation in relations
                ),
                key=_relation_sort_key,
            )
        )
        archived_sources = tuple(
            sorted(
                entry_id
                for entry_id in {
                    *(space.source_reference for space in spaces),
                    *(relation.source_reference for relation in relations),
                }
                if not self._source_active(entries[entry_id])
            )
        )
        risks = tuple(
            [f"missing_relation_endpoint:{item}" for item in missing_endpoints]
            + [f"archived_household_source:{item}" for item in archived_sources]
            + (["household_representation_empty"] if not spaces else [])
        )
        status = self._status(spaces, missing_endpoints, archived_sources)
        source_entry_ids = tuple(
            sorted(
                {
                    *(space.source_reference for space in spaces),
                    *(relation.source_reference for relation in relations),
                }
            )
        )
        evidence_codes = (
            "authority:internal_world_model",
            "source_authority:household_memory",
            *tuple(
                sorted(
                    {
                        *(code for item in spaces for code in item.evidence_codes),
                        *(code for item in relations for code in item.evidence_codes),
                    }
                )
            ),
        )
        fingerprint = _fingerprint(governed_spaces, governed_relations, risks)
        return GovernedHouseholdRepresentation(
            representation_id=f"household-world-{fingerprint[:16]}",
            status=status,
            spaces=governed_spaces,
            relations=governed_relations,
            source_entry_ids=source_entry_ids,
            evidence_codes=evidence_codes,
            risk_codes=risks,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _validate_unique_ids(
        spaces: tuple[HouseholdSpaceEvidence, ...],
        relations: tuple[HouseholdSpatialRelationEvidence, ...],
    ) -> None:
        space_ids = tuple(item.space_id for item in spaces)
        relation_ids = tuple(item.relation_id for item in relations)
        if len(space_ids) != len(set(space_ids)):
            raise ValueError("household space ids must be unique")
        if len(relation_ids) != len(set(relation_ids)):
            raise ValueError("household relation ids must be unique")

    @staticmethod
    def _validate_sources(
        entries: dict[str, HouseholdMemoryEntry],
        spaces: tuple[HouseholdSpaceEvidence, ...],
        relations: tuple[HouseholdSpatialRelationEvidence, ...],
    ) -> None:
        references = {
            *(space.source_reference for space in spaces),
            *(relation.source_reference for relation in relations),
        }
        missing = tuple(
            sorted(reference for reference in references if reference not in entries)
        )
        if missing:
            raise ValueError(
                "household spatial evidence requires existing HouseholdMemory source"
            )

    @staticmethod
    def _missing_endpoints(
        relations: tuple[HouseholdSpatialRelationEvidence, ...],
        known_space_ids: set[str],
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                relation.relation_id
                for relation in relations
                if relation.source_space_id not in known_space_ids
                or relation.target_space_id not in known_space_ids
            )
        )

    @staticmethod
    def _source_active(entry: HouseholdMemoryEntry) -> bool:
        return entry.normalized_status is not HouseholdMemoryStatus.ARCHIVED

    @staticmethod
    def _status(
        spaces: tuple[HouseholdSpaceEvidence, ...],
        missing_endpoints: tuple[str, ...],
        archived_sources: tuple[str, ...],
    ) -> HouseholdRepresentationStatus:
        if not spaces:
            return HouseholdRepresentationStatus.EMPTY
        if missing_endpoints or archived_sources:
            return HouseholdRepresentationStatus.REVIEW_REQUIRED
        return HouseholdRepresentationStatus.COMPLETE


def _space_sort_key(space: GovernedHouseholdSpace) -> tuple[str, str]:
    return (space.kind.value, space.space_id)


def _relation_sort_key(
    relation: GovernedHouseholdSpatialRelation,
) -> tuple[str, str, str, str]:
    return (
        relation.source_space_id,
        relation.relation.value,
        relation.target_space_id,
        relation.relation_id,
    )


def _fingerprint(
    spaces: tuple[GovernedHouseholdSpace, ...],
    relations: tuple[GovernedHouseholdSpatialRelation, ...],
    risks: tuple[str, ...],
) -> str:
    payload = "\n".join(
        (
            *(
                "|".join(
                    (
                        item.space_id,
                        item.label,
                        item.kind.value,
                        item.source_reference,
                        ",".join(item.evidence_codes),
                        str(item.active),
                    )
                )
                for item in spaces
            ),
            *(
                "|".join(
                    (
                        item.relation_id,
                        item.source_space_id,
                        item.relation.value,
                        item.target_space_id,
                        item.source_reference,
                        ",".join(item.evidence_codes),
                        str(item.active),
                    )
                )
                for item in relations
            ),
            *(f"risk:{risk}" for risk in risks),
        )
    )
    return sha256(payload.encode("utf-8")).hexdigest()
