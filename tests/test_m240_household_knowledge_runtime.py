from datetime import datetime, timezone

from app.household_knowledge import HouseholdKnowledgeService
from infrastructure.repositories.sqlite_household_memory_repository import (
    SQLiteHouseholdMemoryRepository,
)

NOW = datetime(2026, 7, 15, 15, 0, tzinfo=timezone.utc)


def test_stores_and_recalls_household_knowledge(tmp_path):
    path = tmp_path / "knowledge.db"
    service = HouseholdKnowledgeService(str(path))

    stored = service.handle(
        "Guardá como conocimiento la garantía del lavarropas vence en diciembre",
        now=NOW,
    )
    recalled = service.handle("Qué sabés del hogar sobre lavarropas", now=NOW)

    assert stored.handled is True
    assert "Guardé" in stored.response_text
    assert "lavarropas" in recalled.response_text
    assert "warranty" in recalled.response_text


def test_knowledge_persists_across_service_restart(tmp_path):
    path = tmp_path / "knowledge.db"
    HouseholdKnowledgeService(str(path)).handle(
        "Anotá como dato del hogar el teléfono del médico es 555-1234", now=NOW
    )

    recalled = HouseholdKnowledgeService(str(path)).handle(
        "Qué sabés del hogar sobre médico", now=NOW
    )

    assert "555-1234" in recalled.response_text


def test_archives_household_knowledge(tmp_path):
    service = HouseholdKnowledgeService(str(tmp_path / "knowledge.db"))
    service.handle("Guardá como conocimiento service de la caldera con Pedro", now=NOW)

    archived = service.handle("Archivá el dato caldera", now=NOW)
    recalled = service.handle("Qué sabés del hogar sobre caldera", now=NOW)

    assert archived.response_text.startswith("Archivé")
    assert "No encontré" in recalled.response_text


def test_non_knowledge_text_is_not_intercepted(tmp_path):
    service = HouseholdKnowledgeService(str(tmp_path / "knowledge.db"))
    assert service.handle("Contame una historia", now=NOW).handled is False


def test_sqlite_repository_round_trip(tmp_path):
    path = tmp_path / "knowledge.db"
    service = HouseholdKnowledgeService(str(path))
    service.handle(
        "Guardá como conocimiento mantenimiento del auto cada junio", now=NOW
    )

    entries = SQLiteHouseholdMemoryRepository(path).list_all()
    assert len(entries) == 1
    assert entries[0].normalized_category.value == "maintenance"
