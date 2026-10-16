from __future__ import annotations

from datetime import datetime, timezone

from application.brain import BrainQuery, GoalProjectBrainAdapter
from core.household_goals import HouseholdGoal
from core.household_projects import HouseholdProject
from domain.brain import BrainMemoryStatus, BrainMemoryType


class GoalRepository:
    def __init__(self, goals=()):
        self.goals = tuple(goals)

    def list_all(self):
        return self.goals


class ProjectRepository:
    def __init__(self, projects=()):
        self.projects = tuple(projects)

    def list_all(self):
        return self.projects


def test_adapter_reads_goals_and_projects_without_writing() -> None:
    now = datetime(2026, 7, 23, tzinfo=timezone.utc)
    adapter = GoalProjectBrainAdapter(
        goal_repository=GoalRepository(
            [HouseholdGoal(name="Mejorar Roby", created_at=now, updated_at=now)]
        ),
        project_repository=ProjectRepository(
            [HouseholdProject(name="M312", created_at=now, updated_at=now)]
        ),
        owner="Carlos",
    )

    memories = adapter.recall(BrainQuery(), now=now)

    assert {memory.source for memory in memories} == {
        "household_goal",
        "household_project",
    }
    assert all(memory.normalized_type is BrainMemoryType.GOAL for memory in memories)
    assert all(memory.metadata["read_only"] is True for memory in memories)


def test_adapter_maps_completed_items_to_resolved() -> None:
    now = datetime(2026, 7, 23, tzinfo=timezone.utc)
    goal = HouseholdGoal(
        name="Terminar etapa",
        status="completed",
        progress_percent=100,
        created_at=now,
        updated_at=now,
    )
    adapter = GoalProjectBrainAdapter(
        goal_repository=GoalRepository([goal]),
        project_repository=ProjectRepository(),
        owner="Carlos",
    )

    memory = adapter.recall(BrainQuery(), now=now)[0]

    assert memory.normalized_status is BrainMemoryStatus.RESOLVED
    assert memory.memory_id.startswith("goal:")


def test_adapter_rejects_blank_owner() -> None:
    try:
        GoalProjectBrainAdapter(
            goal_repository=GoalRepository(),
            project_repository=ProjectRepository(),
            owner=" ",
        )
    except ValueError as error:
        assert "owner" in str(error)
    else:
        raise AssertionError("blank owner should be rejected")
