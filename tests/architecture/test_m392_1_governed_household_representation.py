from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.governed_household_representation import (
    GovernedHouseholdRepresentationView,
    HouseholdRepresentationStatus,
    HouseholdSpaceEvidence,
    HouseholdSpaceKind,
    HouseholdSpatialRelationEvidence,
    HouseholdSpatialRelationKind,
)
from core.household_memory import (
    HouseholdMemoryCategory,
    HouseholdMemoryEntry,
    HouseholdMemoryStatus,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 19, 45, tzinfo=timezone.utc)


def _entry(
    entry_id: str,
    *,
    title: str = "Evidencia espacial del hogar",
    status: HouseholdMemoryStatus = HouseholdMemoryStatus.ACTIVE,
) -> HouseholdMemoryEntry:
    return HouseholdMemoryEntry(
        entry_id=entry_id,
        title=title,
        details=f"Evidencia explícita {entry_id}",
        category=HouseholdMemoryCategory.NOTE,
        status=status,
        source="manual",
        created_at=NOW,
        updated_at=NOW,
    )


def _spaces() -> tuple[HouseholdSpaceEvidence, ...]:
    return (
        HouseholdSpaceEvidence(
            space_id="home",
            label="Hogar",
            kind=HouseholdSpaceKind.HOME,
            source_reference="source-home",
            evidence_codes=("explicit_household_space",),
        ),
        HouseholdSpaceEvidence(
            space_id="kitchen",
            label="Cocina",
            kind=HouseholdSpaceKind.ROOM,
            source_reference="source-kitchen",
            evidence_codes=("explicit_household_room",),
        ),
    )


def _relation() -> HouseholdSpatialRelationEvidence:
    return HouseholdSpatialRelationEvidence(
        relation_id="home-contains-kitchen",
        source_space_id="home",
        relation=HouseholdSpatialRelationKind.CONTAINS,
        target_space_id="kitchen",
        source_reference="source-relation",
        evidence_codes=("explicit_spatial_relation",),
    )


def _entries() -> tuple[HouseholdMemoryEntry, ...]:
    return (
        _entry("source-home"),
        _entry("source-kitchen"),
        _entry("source-relation"),
    )


def test_m392_1_preserves_single_internal_world_authority() -> None:
    report = InternalWorldModelFoundation().household_representation(
        _entries(),
        spaces=_spaces(),
        relations=(_relation(),),
    )
    assert report.canonical_authority == "internal_world_model"
    assert report.source_authority == "household_memory"


def test_m392_1_builds_read_only_household_representation() -> None:
    report = GovernedHouseholdRepresentationView().build(
        _entries(),
        _spaces(),
        (_relation(),),
    )
    assert report.schema_version == "m392.1"
    assert report.status is HouseholdRepresentationStatus.COMPLETE
    assert report.read_only is True
    assert report.persistence_added is False
    assert report.inference_added is False
    assert report.modifies_source_data is False
    assert report.grants_authority is False


def test_m392_1_represents_home_room_and_zone_without_inference() -> None:
    zone = HouseholdSpaceEvidence(
        space_id="counter",
        label="Mesada",
        kind=HouseholdSpaceKind.ZONE,
        source_reference="source-zone",
        evidence_codes=("explicit_household_zone",),
    )
    report = GovernedHouseholdRepresentationView().build(
        (*_entries(), _entry("source-zone")),
        (*_spaces(), zone),
    )
    assert {item.kind for item in report.spaces} == {
        HouseholdSpaceKind.HOME,
        HouseholdSpaceKind.ROOM,
        HouseholdSpaceKind.ZONE,
    }
    assert report.inference_added is False


def test_m392_1_requires_real_household_memory_source() -> None:
    with pytest.raises(ValueError, match="existing HouseholdMemory source"):
        GovernedHouseholdRepresentationView().build((), _spaces())


def test_m392_1_missing_relation_endpoint_requires_review() -> None:
    broken = HouseholdSpatialRelationEvidence(
        relation_id="kitchen-adjacent-hall",
        source_space_id="kitchen",
        relation=HouseholdSpatialRelationKind.ADJACENT_TO,
        target_space_id="hall",
        source_reference="source-relation",
    )
    report = GovernedHouseholdRepresentationView().build(
        _entries(),
        _spaces(),
        (broken,),
    )
    assert report.status is HouseholdRepresentationStatus.REVIEW_REQUIRED
    assert report.relations[0].active is False
    assert report.risk_codes == (
        "missing_relation_endpoint:kitchen-adjacent-hall",
    )


def test_m392_1_archived_source_is_visible_but_inactive() -> None:
    entries = (
        _entry("source-home"),
        _entry("source-kitchen", status=HouseholdMemoryStatus.ARCHIVED),
        _entry("source-relation"),
    )
    report = GovernedHouseholdRepresentationView().build(
        entries,
        _spaces(),
        (_relation(),),
    )
    kitchen = report.space("kitchen")
    assert kitchen is not None
    assert kitchen.active is False
    assert report.status is HouseholdRepresentationStatus.REVIEW_REQUIRED
    assert "archived_household_source:source-kitchen" in report.risk_codes


def test_m392_1_empty_representation_remains_explicit() -> None:
    report = GovernedHouseholdRepresentationView().build()
    assert report.status is HouseholdRepresentationStatus.EMPTY
    assert report.spaces == ()
    assert report.relations == ()
    assert report.risk_codes == ("household_representation_empty",)


def test_m392_1_same_evidence_is_deterministic() -> None:
    view = GovernedHouseholdRepresentationView()
    first = view.build(_entries(), _spaces(), (_relation(),))
    second = view.build(
        tuple(reversed(_entries())),
        tuple(reversed(_spaces())),
        (_relation(),),
    )
    assert first == second


def test_m392_1_rejects_duplicate_space_and_relation_ids() -> None:
    duplicate_space = (_spaces()[0], _spaces()[0])
    with pytest.raises(ValueError, match="space ids must be unique"):
        GovernedHouseholdRepresentationView().build(_entries(), duplicate_space)
    relation = _relation()
    with pytest.raises(ValueError, match="relation ids must be unique"):
        GovernedHouseholdRepresentationView().build(
            _entries(),
            _spaces(),
            (relation, relation),
        )


def test_m392_1_rejects_self_spatial_relation() -> None:
    with pytest.raises(ValueError, match="cannot reference itself"):
        HouseholdSpatialRelationEvidence(
            relation_id="self",
            source_space_id="home",
            relation=HouseholdSpatialRelationKind.CONNECTED_TO,
            target_space_id="home",
            source_reference="source-relation",
        )


def test_m392_1_models_are_immutable() -> None:
    report = GovernedHouseholdRepresentationView().build(
        _entries(),
        _spaces(),
        (_relation(),),
    )
    with pytest.raises(FrozenInstanceError):
        report.status = HouseholdRepresentationStatus.EMPTY
    with pytest.raises(FrozenInstanceError):
        report.spaces[0].label = "Otro"


def test_m392_1_does_not_control_devices_or_change_runtime() -> None:
    report = GovernedHouseholdRepresentationView().build(
        _entries(),
        _spaces(),
        (_relation(),),
    )
    assert report.controls_devices is False
    assert report.runtime_behavior_changed is False
    assert report.starts_background_process is False


def test_m392_1_has_no_repository_or_credentials_dependency() -> None:
    paths = (
        ROOT / "core" / "governed_household_representation.py",
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


def test_m392_1_preserves_canonical_core_constructor_line() -> None:
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


def test_m392_1_documentation_records_governed_scope() -> None:
    document = ROOT / "docs" / "M392_1_GOVERNED_HOUSEHOLD_REPRESENTATION.md"
    text = document.read_text(encoding="utf-8")
    assert "internal_world_model" in text
    assert "HouseholdMemory" in text
    assert "no crea" in text
    assert "M392.1" in (ROOT / "README.md").read_text(encoding="utf-8")
