from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "docs" / "brain" / "memory_catalog.json"


def test_m312_2_catalog_is_valid_and_brain_remains_disconnected() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    assert catalog["version"] == "M312.2"
    assert catalog["canonical_brain"]["runtime_connected"] is False
    assert len(catalog["systems"]) >= 10


def test_m312_2_catalog_has_unique_system_ids_and_required_fields() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    systems = catalog["systems"]
    ids = [system["id"] for system in systems]

    assert len(ids) == len(set(ids))
    for system in systems:
        assert system["kind"]
        assert system["entry_point"]
        assert system["runtime_status"]
        assert system["brain_strategy"]
        assert system["migration_risk"] in {"low", "medium", "high"}


def test_m312_2_catalog_keeps_secrets_out_of_brain_migration() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    excluded = " ".join(catalog["excluded_from_migration"]).casefold()

    assert "credentials" in excluded
    assert "tokens" in excluded
