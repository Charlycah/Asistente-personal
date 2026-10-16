from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.governed_people_representation import (
    GovernedPeopleRepresentationView,
    PersonEvidence,
    PersonRelationshipEvidence,
    PersonRepresentationStatus,
    PersonRoleKind,
)
from core.personal_identity_and_session_profiles.models import (
    IdentityScope,
    PersonalIdentityProfile,
)
from core.relationship_memory import RelationshipMemoryKind, RelationshipMemoryRecord

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 20, 0, tzinfo=timezone.utc)


def _profile() -> PersonalIdentityProfile:
    return PersonalIdentityProfile(
        profile_id="home-profile",
        display_name="Perfil hogar",
        owner="Owner",
        scope=IdentityScope.SHARED,
        participants=("Owner", "Partner"),
    )


def _people() -> tuple[PersonEvidence, ...]:
    return (
        PersonEvidence(
            person_id="owner",
            display_name="Owner",
            role=PersonRoleKind.OWNER,
            source_profile_id="home-profile",
            evidence_codes=("explicit_identity_profile",),
        ),
        PersonEvidence(
            person_id="partner",
            display_name="Partner",
            role=PersonRoleKind.PARTICIPANT,
            source_profile_id="home-profile",
            evidence_codes=("explicit_profile_participant",),
        ),
    )


def _record() -> RelationshipMemoryRecord:
    return RelationshipMemoryRecord(
        record_id="relationship-owner",
        content="Preferencia relacional explícita",
        kind=RelationshipMemoryKind.USER_PREFERENCE,
        confidence=0.9,
        reason="evidencia de prueba",
        created_at=NOW,
    )


def _relationship() -> PersonRelationshipEvidence:
    return PersonRelationshipEvidence(
        relationship_id="owner-preference",
        person_id="owner",
        label="preferencia registrada",
        source_record_id="relationship-owner",
        evidence_codes=("explicit_relationship_link",),
    )


def test_m392_2_preserves_internal_world_authority() -> None:
    report = InternalWorldModelFoundation().people_representation(
        (_profile(),),
        people=_people(),
        relationship_records=(_record(),),
        relationships=(_relationship(),),
    )
    assert report.canonical_authority == "internal_world_model"
    assert report.identity_source_authority == "personal_identity_profile"
    assert report.relationship_source_authority == "relationship_memory"


def test_m392_2_builds_read_only_people_representation() -> None:
    report = GovernedPeopleRepresentationView().build((_profile(),), _people())
    assert report.schema_version == "m392.2"
    assert report.status is PersonRepresentationStatus.COMPLETE
    assert report.read_only is True
    assert report.persistence_added is False
    assert report.duplicates_profiles is False
    assert report.modifies_source_data is False
    assert report.grants_authority is False


def test_m392_2_people_must_be_declared_by_real_profile() -> None:
    report = GovernedPeopleRepresentationView().build((), _people())
    assert report.status is PersonRepresentationStatus.REVIEW_REQUIRED
    assert all(not person.active for person in report.people)
    assert report.risk_codes == (
        "missing_identity_profile:owner",
        "missing_identity_profile:partner",
    )


def test_m392_2_rejects_name_not_declared_by_profile() -> None:
    stranger = PersonEvidence(
        person_id="stranger",
        display_name="Stranger",
        role=PersonRoleKind.KNOWN_PERSON,
        source_profile_id="home-profile",
    )
    report = GovernedPeopleRepresentationView().build((_profile(),), (stranger,))
    assert report.status is PersonRepresentationStatus.REVIEW_REQUIRED
    assert report.people[0].active is False
    assert report.risk_codes == ("person_not_declared_by_profile:stranger",)


def test_m392_2_relationship_requires_explicit_record_reference() -> None:
    report = GovernedPeopleRepresentationView().build(
        (_profile(),),
        _people(),
        (),
        (_relationship(),),
    )
    assert report.status is PersonRepresentationStatus.REVIEW_REQUIRED
    assert report.relationships[0].active is False
    assert report.risk_codes == (
        "missing_relationship_record:owner-preference",
    )


def test_m392_2_relationship_requires_known_active_person() -> None:
    relation = PersonRelationshipEvidence(
        relationship_id="unknown-link",
        person_id="unknown",
        label="vínculo explícito",
        source_record_id="relationship-owner",
    )
    report = GovernedPeopleRepresentationView().build(
        (_profile(),),
        _people(),
        (_record(),),
        (relation,),
    )
    assert report.status is PersonRepresentationStatus.REVIEW_REQUIRED
    assert report.risk_codes == (
        "missing_person_for_relationship:unknown-link",
    )


def test_m392_2_explicit_relationship_is_active() -> None:
    report = GovernedPeopleRepresentationView().build(
        (_profile(),),
        _people(),
        (_record(),),
        (_relationship(),),
    )
    assert report.status is PersonRepresentationStatus.COMPLETE
    assert report.relationships[0].active is True
    assert report.person("owner") is not None


def test_m392_2_empty_representation_is_explicit() -> None:
    report = GovernedPeopleRepresentationView().build()
    assert report.status is PersonRepresentationStatus.EMPTY
    assert report.people == ()
    assert report.relationships == ()


def test_m392_2_same_evidence_is_deterministic() -> None:
    view = GovernedPeopleRepresentationView()
    first = view.build(
        (_profile(),),
        _people(),
        (_record(),),
        (_relationship(),),
    )
    second = view.build(
        (_profile(),),
        tuple(reversed(_people())),
        (_record(),),
        (_relationship(),),
    )
    assert first == second


def test_m392_2_rejects_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="person ids must be unique"):
        GovernedPeopleRepresentationView().build(
            (_profile(),),
            (_people()[0], _people()[0]),
        )
    relation = _relationship()
    with pytest.raises(ValueError, match="relationship ids must be unique"):
        GovernedPeopleRepresentationView().build(
            (_profile(),),
            _people(),
            (_record(),),
            (relation, relation),
        )


def test_m392_2_models_are_immutable() -> None:
    report = GovernedPeopleRepresentationView().build((_profile(),), _people())
    with pytest.raises(FrozenInstanceError):
        report.status = PersonRepresentationStatus.EMPTY
    with pytest.raises(FrozenInstanceError):
        report.people[0].display_name = "Changed"


def test_m392_2_never_infers_people_or_relationship_ownership() -> None:
    report = GovernedPeopleRepresentationView().build(
        (_profile(),),
        _people(),
        (_record(),),
        (_relationship(),),
    )
    assert report.infers_people is False
    assert report.infers_relationship_ownership is False
    assert report.runtime_behavior_changed is False
    assert report.starts_background_process is False


def test_m392_2_has_no_repository_or_credentials_dependency() -> None:
    paths = (
        ROOT / "core" / "governed_people_representation.py",
        ROOT / "app" / "internal_world_model_foundation.py",
    )
    source = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "sqlite" not in source.casefold()
    assert "Repository(" not in source
    assert "threading" not in source
    assert "asyncio" not in source
    assert "sleep(" not in source


def test_m392_2_preserves_canonical_core_constructor_line() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]


def test_m392_2_documentation_declares_no_parallel_manager() -> None:
    document = (ROOT / "docs" / "M392_2_GOVERNED_PEOPLE.md").read_text(
        encoding="utf-8"
    )
    assert "internal_world_model" in document
    assert "PeopleManager" in document
    assert "no crea" in document
    assert "relationship_memory" in document
