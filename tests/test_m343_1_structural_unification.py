from __future__ import annotations

import ast
from pathlib import Path

from app.canonical_cognitive_core import CanonicalCognitiveCoreDomain
from app.official_conversation_gateway import OfficialConversationGateway

PRODUCTION_ROOTS = (
    Path("app"),
    Path("application"),
    Path("core"),
    Path("domain"),
    Path("engines"),
    Path("handlers"),
    Path("infrastructure"),
    Path("interfaces"),
    Path("m3"),
    Path("m4"),
    Path("m5"),
    Path("m6"),
    Path("m7"),
)

REMOVED_EMPTY_RESIDUES = (
    "application/reminders/cancel_reminder.py",
    "application/reminders/complete_reminder.py",
    "application/reminders/create_reminder.py",
    "application/reminders/list_pending.py",
    "application/reminders/snooze_reminder.py",
    "core/cognitive_runtime_orchestration/__init__.py.tmp",
    "core/tests/test_health.py",
    "core/tests/test_metrics_reporter.py",
    "domain/reminders.py",
    "domain/reminders/README.md",
    "infrastructure/db/schema.sql",
    "tests/test_memory.py",
    "tests/test_orchestrator.py",
    "tests/test_reminders.py",
)


def _production_python_files():
    for root in PRODUCTION_ROOTS:
        yield from root.rglob("*.py")


def test_demonstrably_empty_residues_were_removed() -> None:
    remaining = [path for path in REMOVED_EMPTY_RESIDUES if Path(path).exists()]
    assert remaining == []


def test_only_package_markers_may_be_empty_python_files() -> None:
    unexpected = [
        path.as_posix()
        for path in _production_python_files()
        if path.stat().st_size == 0 and path.name != "__init__.py"
    ]
    assert unexpected == []


def test_production_has_one_canonical_cognitive_core_constructor() -> None:
    constructors: list[tuple[str, int]] = []

    for path in _production_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if (
                isinstance(function, ast.Name)
                and function.id == "CanonicalCognitiveCore"
            ):
                constructors.append((path.as_posix(), node.lineno))

    assert constructors == [("app/official_conversation_gateway.py", 52)]


def test_gateway_core_contains_every_domain_once() -> None:
    class RuntimeStub:
        bootstrap = object()
        history = ()
        traces = ()

    gateway = OfficialConversationGateway(RuntimeStub())
    components = gateway.canonical_cognitive_core.components

    assert tuple(component.domain for component in components) == tuple(
        CanonicalCognitiveCoreDomain
    )
    assert len({component.domain for component in components}) == len(components)
