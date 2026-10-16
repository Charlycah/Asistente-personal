from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.always_on_personal_runtime_wiring import (
    build_continuous_cognitive_loop_from_environment,
)
from core.household_goals import GoalStatus, HouseholdGoal
from core.household_projects import HouseholdProject, ProjectStatus

NOW = datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc)


def _loop(*, goals=(), projects=(), commitments=None):
    return build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        open_commitments=commitments,
        active_goals=lambda: goals,
        active_projects=lambda: projects,
        ambient_activity=None,
    )


def test_active_goal_with_next_step_reaches_single_cognitive_agenda():
    goal = HouseholdGoal(
        goal_id="g-1",
        name="Terminar inventario",
        status=GoalStatus.ACTIVE,
        next_step="Revisar integración",
    )
    loop = _loop(goals=(goal,))
    snapshot = loop.agenda_manager.refresh(now=NOW)
    item = next(item for item in snapshot.items if item.key == "goal:g-1")
    assert item.kind.value == "goal"
    assert "household_goals" in item.sources


def test_goal_without_next_step_or_target_date_is_not_admitted():
    goal = HouseholdGoal(
        goal_id="g-quiet",
        name="Algún día",
        status=GoalStatus.ACTIVE,
    )
    loop = _loop(goals=(goal,))
    snapshot = loop.agenda_manager.refresh(now=NOW)
    assert all(item.key != "goal:g-quiet" for item in snapshot.items)


def test_active_goal_with_target_date_is_admitted():
    goal = HouseholdGoal(
        goal_id="g-date",
        name="Objetivo con fecha",
        status=GoalStatus.ACTIVE,
        target_date=date(2026, 8, 30),
    )
    loop = _loop(goals=(goal,))
    snapshot = loop.agenda_manager.refresh(now=NOW)
    assert any(item.key == "goal:g-date" for item in snapshot.items)


def test_closed_project_is_not_admitted():
    project = HouseholdProject(
        project_id="p-closed",
        name="Proyecto cerrado",
        status=ProjectStatus.COMPLETED,
        next_step="No debe aparecer",
    )
    loop = _loop(projects=(project,))
    snapshot = loop.agenda_manager.refresh(now=NOW)
    assert all(item.key != "project:p-closed" for item in snapshot.items)


def test_active_project_requires_next_step():
    project = HouseholdProject(
        project_id="p-1",
        name="Proyecto ROBY",
        status=ProjectStatus.ACTIVE,
        next_step="Validar Lote A",
    )
    loop = _loop(projects=(project,))
    snapshot = loop.agenda_manager.refresh(now=NOW)
    item = next(item for item in snapshot.items if item.key == "project:p-1")
    assert item.kind.value == "project"
    assert "household_projects" in item.sources


def test_open_commitments_existing_contract_still_composes():
    loop = _loop(commitments=lambda: 2)
    snapshot = loop.agenda_manager.refresh(now=NOW)
    item = next(item for item in snapshot.items if item.key == "commitments:open")
    assert item.kind.value == "commitment"
    assert "open_commitments" in item.sources


def test_source_failure_is_locally_degraded():
    def broken_goals():
        raise RuntimeError("goal source unavailable")

    loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        active_goals=broken_goals,
        active_projects=lambda: (
            SimpleNamespace(
                project_id="p-ok",
                name="Proyecto sano",
                normalized_status=SimpleNamespace(value="active"),
                next_step="Continuar",
            ),
        ),
    )
    snapshot = loop.agenda_manager.refresh(now=NOW)
    assert any(item.key == "project:p-ok" for item in snapshot.items)
    assert "household_goals" in snapshot.operational_health.source_failures
