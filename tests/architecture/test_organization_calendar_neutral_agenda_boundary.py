from __future__ import annotations

import ast
from pathlib import Path

from core.agenda_evidence import AgendaEventEvidence

ROOT = Path(__file__).resolve().parents[2]


def test_organization_core_uses_neutral_agenda_evidence_boundary() -> None:
    evidence = AgendaEventEvidence(
        agenda_id="event-1",
        title="Consulta médica",
        source_reference="calendar:event:event-1",
    )
    assert evidence.agenda_id == "event-1"
    assert evidence.title == "Consulta médica"

    for relative in (
        "core/partial_canonical_organization_snapshot.py",
        "core/productive_organization_evidence_projection.py",
    ):
        path = ROOT / relative
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert "AgendaEventEvidence" in source
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (
                    node.module is not None
                    and node.module.startswith("infrastructure.calendar")
                ), relative
            elif isinstance(node, ast.Import):
                assert not any(
                    alias.name.startswith("infrastructure.calendar")
                    for alias in node.names
                ), relative
