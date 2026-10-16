from __future__ import annotations

import ast
from pathlib import Path

from domain.reminders import ReminderService


def test_reminder_service_no_longer_exposes_list_overdue_alias() -> None:
    assert not hasattr(ReminderService, "list_overdue")


def test_reminder_service_keeps_canonical_queries() -> None:
    service = ReminderService()

    assert callable(service.list_due)
    assert callable(service.list_for_day)
    assert callable(service.list_next)


def test_reminder_service_source_has_no_pure_overdue_forwarder() -> None:
    source_path = Path("domain/reminders/services.py")
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    service_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "ReminderService"
    )

    method_names = {
        node.name
        for node in service_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    assert "list_overdue" not in method_names
