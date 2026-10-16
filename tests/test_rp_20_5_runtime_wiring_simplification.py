from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import app.runtime_environment_ports as ports
import app.runtime_environment_wiring as wiring
import app.runtime_root_factory as factory
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

WIRING_BUILDERS = (
    "build_camera_conversation_from_environment",
    "build_gmail_runtime_from_environment",
    "build_household_goals_from_environment",
    "build_household_knowledge_from_environment",
    "build_household_projects_from_environment",
    "build_mail_reader_conversation_from_environment",
    "build_memory_runtime_from_environment",
    "build_reminder_conversation_from_environment",
    "build_voice_runtime_from_environment",
    "build_weather_conversation_from_environment",
)


def test_runtime_factory_reexports_environment_builders() -> None:
    for name in WIRING_BUILDERS:
        assert getattr(factory, name) is getattr(wiring, name)


def test_runtime_factory_contains_only_composition_not_environment_parsing() -> None:
    tree = ast.parse(Path("app/runtime_root_factory.py").read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    defined_functions = {
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    assert "infrastructure.config.settings_loader" not in imported_modules
    assert defined_functions == {"build_runtime_root"}


@dataclass(frozen=True)
class _HandledResult:
    handled: bool
    response_text: str


class _Service:
    def handle(self, text: str, *, now):
        del now
        return _HandledResult(handled=True, response_text=f"respuesta:{text}")


def test_shared_operational_interceptor_preserves_specialized_rationale() -> None:
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="estado del proyecto",
    )
    interceptor = ports.HouseholdProjectConversationInterceptionPort(_Service())

    result = interceptor.intercept(request, now=datetime.now(timezone.utc))

    assert result is not None
    assert result.response_text == "respuesta:estado del proyecto"
    assert result.rationale == "household_project_conversation_completed"
