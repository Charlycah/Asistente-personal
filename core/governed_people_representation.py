from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.personal_identity_and_session_profiles.models import PersonalIdentityProfile
from core.relationship_memory import RelationshipMemoryRecord


class PersonRepresentationStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"


class PersonRoleKind(StrEnum):
    OWNER = "owner"
    PARTICIPANT = "participant"
    KNOWN_PERSON = "known_person"


@dataclass(frozen=True)
class PersonEvidence:
    person_id: str
    display_name: str
    role: PersonRoleKind
    source_profile_id: str
    evidence_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, label in (
            (self.person_id, "person id"),
            (self.display_name, "display name"),
            (self.source_profile_id, "source profile id"),
        ):
            if not value.strip():
                raise ValueError(f"{label} must not be blank")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("person evidence codes must not be blank")


@dataclass(frozen=True)
class PersonRelationshipEvidence:
    relationship_id: str
    person_id: str
    label: str
    source_record_id: str
    evidence_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (self.relationship_id, "relationship id"),
            (self.person_id, "person id"),
            (self.label, "relationship label"),
            (self.source_record_id, "source record id"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be blank")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("relationship evidence codes must not be blank")


@dataclass(frozen=True)
class GovernedPerson:
    person_id: str
    display_name: str
    role: PersonRoleKind
    source_profile_id: str
    evidence_codes: tuple[str, ...]
    active: bool = True


@dataclass(frozen=True)
class GovernedPersonRelationship:
    relationship_id: str
    person_id: str
    label: str
    source_record_id: str
    evidence_codes: tuple[str, ...]
    active: bool = True


@dataclass(frozen=True)
class GovernedPeopleRepresentation:
    representation_id: str
    status: PersonRepresentationStatus
    people: tuple[GovernedPerson, ...]
    relationships: tuple[GovernedPersonRelationship, ...]
    source_profile_ids: tuple[str, ...]
    source_record_ids: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m392.2"
    canonical_authority: str = "internal_world_model"
    identity_source_authority: str = "personal_identity_profile"
    relationship_source_authority: str = "relationship_memory"
    read_only: bool = True
    persistence_added: bool = False
    duplicates_profiles: bool = False
    modifies_source_data: bool = False
    infers_people: bool = False
    infers_relationship_ownership: bool = False
    grants_authority: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "internal_world_model":
            raise ValueError("people representation must preserve canonical authority")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.duplicates_profiles,
                self.modifies_source_data,
                self.infers_people,
                self.infers_relationship_ownership,
                self.grants_authority,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("people representation violates governed limits")

    def person(self, person_id: str) -> GovernedPerson | None:
        normalized = person_id.casefold()
        return next(
            (item for item in self.people if item.person_id.casefold() == normalized),
            None,
        )


class GovernedPeopleRepresentationView:
    """Pure governed projection over explicit identity and relationship evidence."""

    CANONICAL_AUTHORITY = "internal_world_model"

    def build(
        self,
        profiles: tuple[PersonalIdentityProfile, ...] = (),
        people: tuple[PersonEvidence, ...] = (),
        relationship_records: tuple[RelationshipMemoryRecord, ...] = (),
        relationships: tuple[PersonRelationshipEvidence, ...] = (),
    ) -> GovernedPeopleRepresentation:
        self._validate_unique_ids(people, relationships)
        profile_map = {item.profile_id: item for item in profiles}
        record_map = {item.record_id: item for item in relationship_records}
        risks: list[str] = []
        governed_people: list[GovernedPerson] = []
        for item in people:
            profile = profile_map.get(item.source_profile_id)
            active = profile is not None and self._person_matches_profile(item, profile)
            if profile is None:
                risks.append(f"missing_identity_profile:{item.person_id}")
            elif not active:
                risks.append(f"person_not_declared_by_profile:{item.person_id}")
            governed_people.append(
                GovernedPerson(
                    person_id=item.person_id,
                    display_name=item.display_name,
                    role=item.role,
                    source_profile_id=item.source_profile_id,
                    evidence_codes=tuple(sorted(set(item.evidence_codes))),
                    active=active,
                )
            )
        person_ids = {item.person_id for item in governed_people if item.active}
        governed_relations: list[GovernedPersonRelationship] = []
        for item in relationships:
            active = (
                item.person_id in person_ids
                and item.source_record_id in record_map
            )
            if item.person_id not in person_ids:
                risks.append(f"missing_person_for_relationship:{item.relationship_id}")
            if item.source_record_id not in record_map:
                risks.append(f"missing_relationship_record:{item.relationship_id}")
            governed_relations.append(
                GovernedPersonRelationship(
                    relationship_id=item.relationship_id,
                    person_id=item.person_id,
                    label=item.label,
                    source_record_id=item.source_record_id,
                    evidence_codes=tuple(sorted(set(item.evidence_codes))),
                    active=active,
                )
            )
        ordered_people = tuple(sorted(governed_people, key=lambda item: item.person_id))
        ordered_relations = tuple(
            sorted(governed_relations, key=lambda item: item.relationship_id)
        )
        ordered_risks = tuple(sorted(set(risks)))
        status = self._status(ordered_people, ordered_relations, ordered_risks)
        profile_ids = tuple(sorted({item.source_profile_id for item in ordered_people}))
        record_ids = tuple(
            sorted({item.source_record_id for item in ordered_relations})
        )
        evidence_codes = tuple(
            sorted(
                {
                    *(code for item in ordered_people for code in item.evidence_codes),
                    *(
                        code
                        for item in ordered_relations
                        for code in item.evidence_codes
                    ),
                }
            )
        )
        fingerprint = self._fingerprint(
            ordered_people,
            ordered_relations,
            ordered_risks,
        )
        return GovernedPeopleRepresentation(
            representation_id=f"people-world-{fingerprint[:16]}",
            status=status,
            people=ordered_people,
            relationships=ordered_relations,
            source_profile_ids=profile_ids,
            source_record_ids=record_ids,
            evidence_codes=evidence_codes,
            risk_codes=ordered_risks,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _person_matches_profile(
        person: PersonEvidence,
        profile: PersonalIdentityProfile,
    ) -> bool:
        allowed = {
            profile.owner.casefold(),
            *(name.casefold() for name in profile.participants),
        }
        return person.display_name.casefold() in allowed

    @staticmethod
    def _validate_unique_ids(
        people: tuple[PersonEvidence, ...],
        relationships: tuple[PersonRelationshipEvidence, ...],
    ) -> None:
        person_ids = tuple(item.person_id for item in people)
        relation_ids = tuple(item.relationship_id for item in relationships)
        if len(person_ids) != len(set(person_ids)):
            raise ValueError("person ids must be unique")
        if len(relation_ids) != len(set(relation_ids)):
            raise ValueError("relationship ids must be unique")

    @staticmethod
    def _status(
        people: tuple[GovernedPerson, ...],
        relationships: tuple[GovernedPersonRelationship, ...],
        risks: tuple[str, ...],
    ) -> PersonRepresentationStatus:
        if risks:
            return PersonRepresentationStatus.REVIEW_REQUIRED
        if not people and not relationships:
            return PersonRepresentationStatus.EMPTY
        return PersonRepresentationStatus.COMPLETE

    @staticmethod
    def _fingerprint(
        people: tuple[GovernedPerson, ...],
        relationships: tuple[GovernedPersonRelationship, ...],
        risks: tuple[str, ...],
    ) -> str:
        payload = "\n".join(
            (
                *(f"person:{item.person_id}|{item.display_name}|{item.role.value}|"
                  f"{item.source_profile_id}|{item.active}" for item in people),
                *(f"relationship:{item.relationship_id}|{item.person_id}|{item.label}|"
                  f"{item.source_record_id}|{item.active}" for item in relationships),
                *(f"risk:{item}" for item in risks),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()
