from __future__ import annotations

import ast
from pathlib import Path

from domain.reminders import ReminderRepository
from domain.reminders.repository import (
    ReminderRepository as CanonicalReminderRepository,
)

ROOT = Path(__file__).resolve().parents[1]


def test_reminder_repository_has_one_canonical_protocol() -> None:
    declarations: list[Path] = []
    for path in (ROOT / "domain" / "reminders").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "ReminderRepository":
                declarations.append(path)

    assert declarations == [ROOT / "domain" / "reminders" / "repository.py"]


def test_public_reminder_repository_is_the_canonical_port() -> None:
    assert ReminderRepository is CanonicalReminderRepository


def test_obsolete_reminder_contract_module_is_removed() -> None:
    assert not (ROOT / "domain" / "reminders" / "contracts.py").exists()
