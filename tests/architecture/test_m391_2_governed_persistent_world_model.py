from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.household_memory import (
    HouseholdMemoryCategory,
    HouseholdMemoryEntry,
    HouseholdMemoryStatus,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldStatus,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 15, 0, tzinfo=timezone.utc)


def _fact(
    *,
    fact_id: str = "fact-1",
    fact_key: str = "home.city",
    value: str = "San Miguel de Tucumán",
    level: EpistemicLevel = EpistemicLevel.FACT,
    source_authority: str = "canonical_memory",
) -> PersistentWorldFact:
    return PersistentWorldFact(
        fact_id=fact_id,
        domain=PersistentWorldDomain.ENVIRONMENT,
        fact_key=fact_key,
        value=value,
        source_authority=source_authority,
        source_reference=f"ref:{fact_id}",
        epistemic_level=level,
        evidence_codes=("explicit_governed_source",),
        persisted_by_source=True,
        source_updated_at=NOW,
    )


def _household(
    *,
    entry_id: str = "household-1",
    title: str = "Garantía del lavarropas",
    details: str = "La garantía vence en diciembre",
    status: HouseholdMemoryStatus = HouseholdMemoryStatus.ACTIVE,
) -> HouseholdMemoryEntry:
    return HouseholdMemoryEntry(
        entry_id=entry_id,
        title=title,
        details=details,
        category=HouseholdMemoryCategory.WARRANTY,
        status=status,
        source="manual",
        created_at=NOW,
        updated_at=NOW,
    )


def test_m391_2_preserves_single_internal_world_authority() -> None:
    foundation = InternalWorldModelFoundation()
    assert foundation.snapshot.canonical_authority == "internal_world_model"
    assert foundation.persistent_snapshot().canonical_authority == (
        "internal_world_model"
    )


def test_m391_2_builds_read_only_persistent_world_view() -> None:
    snapshot = InternalWorldModelFoundation().persistent_snapshot((_fact(),))
    assert snapshot.schema_version == "m391.2"
    assert snapshot.status is PersistentWorldStatus.COMPLETE
    assert snapshot.read_only is True
    assert snapshot.persistence_added is False
    assert snapshot.duplicates_storage is False
    assert snapshot.modifies_source_data is False
    assert snapshot.grants_authority is False


def test_m391_2_reuses_household_memory_without_new_repository() -> None:
    entry = _household()
    snapshot = InternalWorldModelFoundation().persistent_snapshot(
        household_entries=(entry,)
    )
    facts = snapshot.facts_for(PersistentWorldDomain.HOUSEHOLD)
    assert len(facts) == 1
    assert facts[0].value == entry.details
    assert facts[0].source_authority == "household_memory"
    assert facts[0].source_reference == entry.entry_id
    assert facts[0].persisted_by_source is True


def test_m391_2_archived_household_fact_remains_visible_but_inactive() -> None:
    entry = _household(status=HouseholdMemoryStatus.ARCHIVED)
    snapshot = InternalWorldModelFoundation().persistent_snapshot(
        household_entries=(entry,)
    )
    assert snapshot.facts_for(PersistentWorldDomain.HOUSEHOLD) == ()
    all_household = snapshot.facts_for(
        PersistentWorldDomain.HOUSEHOLD,
        active_only=False,
    )
    assert len(all_household) == 1
    assert all_household[0].active is False


def test_m391_2_does_not_promote_inference_to_fact() -> None:
    inference = _fact(level=EpistemicLevel.INFERENCE)
    snapshot = InternalWorldModelFoundation().persistent_snapshot((inference,))
    assert snapshot.facts[0].epistemic_level is EpistemicLevel.INFERENCE
    assert "epistemic:inference" in snapshot.evidence_codes


def test_m391_2_conflicting_facts_are_exposed_not_resolved() -> None:
    first = _fact(fact_id="fact-a", value="A")
    second = _fact(fact_id="fact-b", value="B")
    snapshot = InternalWorldModelFoundation().persistent_snapshot((second, first))
    assert snapshot.status is PersistentWorldStatus.CONFLICT_REVIEW_REQUIRED
    assert snapshot.conflict_keys == ("environment:home.city",)
    assert snapshot.resolves_conflicts is False
    assert "world_conflict:environment:home.city" in snapshot.risk_codes


def test_m391_2_non_fact_disagreement_does_not_become_fact_conflict() -> None:
    first = _fact(
        fact_id="fact-a",
        value="A",
        level=EpistemicLevel.HYPOTHESIS,
    )
    second = _fact(
        fact_id="fact-b",
        value="B",
        level=EpistemicLevel.HYPOTHESIS,
    )
    snapshot = InternalWorldModelFoundation().persistent_snapshot((first, second))
    assert snapshot.status is PersistentWorldStatus.COMPLETE
    assert snapshot.conflict_keys == ()


def test_m391_2_empty_world_remains_explicitly_empty() -> None:
    snapshot = InternalWorldModelFoundation().persistent_snapshot()
    assert snapshot.status is PersistentWorldStatus.EMPTY
    assert snapshot.facts == ()
    assert snapshot.risk_codes == ("persistent_world_empty",)
    assert snapshot.infers_missing_facts is False


def test_m391_2_same_evidence_produces_same_snapshot() -> None:
    foundation = InternalWorldModelFoundation()
    facts = (_fact(fact_id="b"), _fact(fact_id="a", fact_key="home.country"))
    assert foundation.persistent_snapshot(facts) == foundation.persistent_snapshot(
        tuple(reversed(facts))
    )


def test_m391_2_snapshot_and_facts_are_immutable() -> None:
    fact = _fact()
    snapshot = InternalWorldModelFoundation().persistent_snapshot((fact,))
    with pytest.raises(FrozenInstanceError):
        fact.value = "changed"
    with pytest.raises(FrozenInstanceError):
        snapshot.status = PersistentWorldStatus.DEGRADED


def test_m391_2_rejects_nonpersistent_or_unknown_sources() -> None:
    with pytest.raises(ValueError, match="persistent source"):
        replace(_fact(), persisted_by_source=False)
    with pytest.raises(ValueError, match="not governed"):
        replace(_fact(), source_authority="parallel_world_manager")


def test_m391_2_requires_timezone_aware_source_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(_fact(), source_updated_at=datetime(2026, 8, 7, 15, 0))


def test_m391_2_does_not_add_runtime_or_background_behavior() -> None:
    snapshot = InternalWorldModelFoundation().persistent_snapshot((_fact(),))
    assert snapshot.runtime_behavior_changed is False
    assert snapshot.starts_background_process is False


def test_m391_2_has_no_repository_or_credentials_dependency() -> None:
    paths = (
        ROOT / "core" / "persistent_world_model.py",
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


def test_m391_2_preserves_canonical_core_constructor_line() -> None:
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


def test_m391_2_documentation_records_governed_scope() -> None:
    document = (ROOT / "docs" / "M391_2_GOVERNED_PERSISTENT_WORLD_MODEL.md")
    text = document.read_text(encoding="utf-8")
    assert "internal_world_model" in text
    assert "HouseholdMemory" in text
    assert "no crea" in text
    assert "M391.2" in (ROOT / "README.md").read_text(encoding="utf-8")
