from __future__ import annotations

import ast
from pathlib import Path

import application.reminders as reminder_application
import core.governed_reasoning as governed_reasoning
from core.governed_reasoning import ExplainableAnswerRenderer
from core.governed_reasoning.orchestrator import GovernedReasoningOrchestrator

ROOT = Path(__file__).resolve().parents[1]


def test_reasoning_orchestrator_depends_directly_on_renderer() -> None:
    source = (ROOT / "core" / "governed_reasoning" / "orchestrator.py").read_text(
        encoding="utf-8"
    )
    assert "explanation_renderer: ExplainableAnswerRenderer" in source
    assert "ReasoningExplanationManager" not in source


def test_reasoning_manager_wrapper_is_removed_from_public_api() -> None:
    assert not hasattr(governed_reasoning, "ReasoningExplanationManager")
    assert ExplainableAnswerRenderer is governed_reasoning.ExplainableAnswerRenderer


def test_pending_reminder_use_case_is_removed_from_public_api() -> None:
    assert not hasattr(reminder_application, "ListPendingRemindersUseCase")

    path = ROOT / "application" / "reminders" / "use_cases.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    assert "ListPendingRemindersUseCase" not in classes


def test_orchestrator_constructor_has_no_renaming_service_boundary() -> None:
    parameters = GovernedReasoningOrchestrator.__init__.__annotations__
    assert "explanation_renderer" in parameters
    assert "explanation_manager" not in parameters
