from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_objective_memory import GovernedObjectiveState


class Runtime:
    pass


def _now(hour: int = 10) -> datetime:
    return datetime(2026, 7, 29, hour, tzinfo=timezone.utc)


def test_m346_7_gateway_exposes_single_governed_objective_memory():
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_objective_memory

    assert snapshot.schema_version == "m346.7"
    assert snapshot.authority.endswith(":GovernedObjectiveMemory")
    assert snapshot.persistence_enabled is False
    assert snapshot.execution_enabled is False
    assert snapshot.autonomous_detection_enabled is False
    assert snapshot.conversation_authority is False
    assert snapshot.remembered_objectives == 0
    assert snapshot.states == tuple(GovernedObjectiveState)


def test_m346_7_remembers_immutable_explicit_objective_context():
    gateway = OfficialConversationGateway(Runtime())

    objective = gateway.remember_governed_objective(
        objective_id="vacaciones-2026",
        owner="Carlos y Cristina",
        description="Organizar las próximas vacaciones.",
        observed_at=_now(),
        context=("Viajan juntos.",),
        metadata={"origin": "official_conversation"},
    )

    assert objective.state is GovernedObjectiveState.ACTIVE
    assert objective.context == ("Viajan juntos.",)
    assert gateway.find_governed_objective("vacaciones-2026") is objective
    with pytest.raises(TypeError):
        objective.metadata["origin"] = "changed"


def test_m346_7_active_objectives_are_filterable_by_owner():
    gateway = OfficialConversationGateway(Runtime())
    gateway.remember_governed_objective(
        objective_id="carlos-goal",
        owner="Carlos",
        description="Objetivo de Carlos.",
        observed_at=_now(),
    )
    gateway.remember_governed_objective(
        objective_id="cristina-goal",
        owner="Cristina",
        description="Objetivo de Cristina.",
        observed_at=_now(),
    )

    active_ids = tuple(
        item.objective_id for item in gateway.active_governed_objectives()
    )
    assert active_ids == ("carlos-goal", "cristina-goal")
    assert tuple(
        item.objective_id
        for item in gateway.active_governed_objectives(owner="Cristina")
    ) == ("cristina-goal",)


def test_m346_7_objective_lifecycle_preserves_history_and_continuity():
    gateway = OfficialConversationGateway(Runtime())
    original = gateway.remember_governed_objective(
        objective_id="travel",
        owner="Carlos y Cristina",
        description="Preparar un viaje.",
        observed_at=_now(),
    )

    paused = gateway.set_governed_objective_state(
        "travel", GovernedObjectiveState.PAUSED, observed_at=_now(11)
    )
    completed = gateway.set_governed_objective_state(
        "travel", GovernedObjectiveState.COMPLETED, observed_at=_now(12)
    )

    assert original.state is GovernedObjectiveState.ACTIVE
    assert paused.state is GovernedObjectiveState.PAUSED
    assert completed.state is GovernedObjectiveState.COMPLETED
    assert gateway.active_governed_objectives() == ()


def test_m346_7_objective_links_to_existing_governed_plan_identity():
    gateway = OfficialConversationGateway(Runtime())
    gateway.remember_governed_objective(
        objective_id="travel",
        owner="Carlos y Cristina",
        description="Preparar un viaje.",
        observed_at=_now(),
    )

    linked = gateway.link_governed_objective_plan(
        "travel", "travel-plan-1", observed_at=_now(11)
    )
    unchanged = gateway.link_governed_objective_plan(
        "travel", "travel-plan-1", observed_at=_now(12)
    )

    assert linked.plan_ids == ("travel-plan-1",)
    assert unchanged.plan_ids == ("travel-plan-1",)


def test_m346_7_rejects_duplicates_unknown_ids_and_naive_time():
    gateway = OfficialConversationGateway(Runtime())
    fields = {
        "objective_id": "travel",
        "owner": "Carlos y Cristina",
        "description": "Preparar un viaje.",
        "observed_at": _now(),
    }
    gateway.remember_governed_objective(**fields)

    with pytest.raises(DomainError, match="already remembered"):
        gateway.remember_governed_objective(**fields)
    with pytest.raises(DomainError, match="unknown objective_id"):
        gateway.link_governed_objective_plan("missing", "plan-1")
    fields["objective_id"] = "naive"
    fields["observed_at"] = datetime(2026, 7, 29)
    with pytest.raises(DomainError, match="timezone-aware"):
        gateway.remember_governed_objective(**fields)


def test_m346_7_memory_has_no_disk_network_execution_or_parallel_gateway():
    source = Path("domain/governed_objective_memory.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint(
        {
            "asyncio",
            "json",
            "pathlib",
            "requests",
            "sqlite3",
            "subprocess",
            "threading",
        }
    )
    assert "credentials.json" not in source
    assert "OfficialConversationGateway(" not in source
    assert "execute(" not in source


def test_m346_7_gateway_is_the_only_productive_memory_composition():
    occurrences = []
    for path in Path("app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "GovernedObjectiveMemory()" in source:
            occurrences.append(path.as_posix())

    assert occurrences == ["app/official_conversation_gateway.py"]
