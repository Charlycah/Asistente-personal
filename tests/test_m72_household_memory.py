from datetime import datetime, timedelta, timezone

import pytest

from core.household_memory import (
    HouseholdMemoryCategory,
    HouseholdMemoryEntry,
    HouseholdMemoryManager,
    HouseholdMemoryOwner,
    HouseholdMemorySignal,
    HouseholdMemoryStatus,
    InMemoryHouseholdMemoryRepository,
)

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def make_entry(**overrides: object) -> HouseholdMemoryEntry:
    values: dict[str, object] = {
        "title": "Garantía del calefón",
        "details": "Conservar factura y revisar antes del vencimiento.",
        "category": HouseholdMemoryCategory.WARRANTY,
        "owner": HouseholdMemoryOwner.SHARED,
        "due_at": NOW - timedelta(days=1),
        "tags": ("casa", "garantía"),
        "created_at": NOW - timedelta(days=10),
        "updated_at": NOW - timedelta(days=10),
    }
    values.update(overrides)
    return HouseholdMemoryEntry(**values)


def test_entry_normalizes_enums_tags_and_dictionary() -> None:
    entry = make_entry(tags=("Casa", "garantía", "Casa"))

    assert entry.normalized_category is HouseholdMemoryCategory.WARRANTY
    assert entry.normalized_owner is HouseholdMemoryOwner.SHARED
    assert entry.normalized_tags == ("casa", "garantía")
    assert entry.to_dict()["due_at"] == entry.due_at.isoformat()


def test_entry_rejects_blank_and_naive_values() -> None:
    with pytest.raises(ValueError):
        make_entry(title=" ")
    with pytest.raises(ValueError):
        make_entry(due_at=datetime(2026, 7, 10, 12, 0))


def test_repository_saves_gets_and_lists_entries() -> None:
    repository = InMemoryHouseholdMemoryRepository()
    entry = make_entry()

    assert repository.save(entry) is entry
    assert repository.get(entry.entry_id) is entry
    assert repository.list_all() == (entry,)


def test_manager_remembers_allowed_household_information() -> None:
    manager = HouseholdMemoryManager()
    entry = manager.remember(make_entry())

    assert manager.recall("calefón") == (entry,)
    assert HouseholdMemorySignal.MEMORY_STORED in manager.snapshot().signals
    assert HouseholdMemorySignal.SCOPE_PRESERVED in manager.snapshot().signals


def test_manager_blocks_financial_or_purchase_content() -> None:
    manager = HouseholdMemoryManager()
    entry = make_entry(
        title="Comprar por Mercado Pago",
        details="Pagar la compra desde la billetera.",
    )

    with pytest.raises(PermissionError):
        manager.remember(entry)


def test_manager_requires_review_for_medical_decisions() -> None:
    manager = HouseholdMemoryManager()
    entry = make_entry(
        title="Medicación",
        details="Decidir la dosis del tratamiento.",
    )

    with pytest.raises(PermissionError):
        manager.remember(entry)


def test_manager_updates_without_changing_identity() -> None:
    manager = HouseholdMemoryManager()
    original = manager.remember(make_entry())

    updated = manager.update(
        original.entry_id,
        details="Factura guardada en la carpeta de garantías.",
        tags=("casa", "documentos"),
        now=NOW,
    )

    assert updated.entry_id == original.entry_id
    assert updated.details.startswith("Factura")
    assert updated.updated_at == NOW


def test_manager_completes_and_archives_entries() -> None:
    manager = HouseholdMemoryManager()
    entry = manager.remember(make_entry())

    completed = manager.complete(entry.entry_id, now=NOW)
    archived = manager.archive(entry.entry_id, now=NOW + timedelta(minutes=1))

    assert completed.normalized_status is HouseholdMemoryStatus.COMPLETED
    assert archived.normalized_status is HouseholdMemoryStatus.ARCHIVED


def test_recall_filters_by_owner_category_and_status() -> None:
    manager = HouseholdMemoryManager()
    shared = manager.remember(make_entry())
    manager.remember(
        make_entry(
            title="Turno odontológico",
            details="Control anual ya realizado.",
            category=HouseholdMemoryCategory.APPOINTMENT,
            owner=HouseholdMemoryOwner.PARTNER,
            status=HouseholdMemoryStatus.COMPLETED,
            entry_id="partner-entry",
        )
    )

    result = manager.recall(
        owner=HouseholdMemoryOwner.SHARED,
        category=HouseholdMemoryCategory.WARRANTY,
        status=HouseholdMemoryStatus.ACTIVE,
    )

    assert result == (shared,)


def test_due_returns_only_active_elapsed_entries() -> None:
    manager = HouseholdMemoryManager()
    elapsed = manager.remember(make_entry())
    manager.remember(
        make_entry(
            title="Mantenimiento futuro",
            details="Revisar filtro del aire acondicionado.",
            category=HouseholdMemoryCategory.MAINTENANCE,
            due_at=NOW + timedelta(days=30),
            entry_id="future-entry",
        )
    )

    assert manager.due(now=NOW) == (elapsed,)


def test_snapshot_and_prompt_expose_operational_summary() -> None:
    manager = HouseholdMemoryManager()
    manager.remember(make_entry())

    snapshot = manager.snapshot(now=NOW)
    prompt = "\n".join(snapshot.system_prompt_lines())

    assert snapshot.total_entries == 1
    assert snapshot.active_entries == 1
    assert len(snapshot.due_entries) == 1
    assert "Household Memory M72" in prompt
    assert "Garantía del calefón" in prompt


def test_manager_rejects_unknown_ids_and_invalid_limits() -> None:
    with pytest.raises(ValueError):
        HouseholdMemoryManager(recent_limit=0)

    manager = HouseholdMemoryManager()
    with pytest.raises(KeyError):
        manager.complete("missing", now=NOW)
