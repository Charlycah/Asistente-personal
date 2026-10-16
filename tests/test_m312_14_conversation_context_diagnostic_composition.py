from __future__ import annotations

from pathlib import Path

from app.memory_consolidation import OfficialMemoryGateway
from application.brain import (
    ActiveIdentityRequest,
    ConversationContextDiagnostic,
    build_identity_memory_brain_composition,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from core.relationship_memory import RelationshipMemoryManager
from infrastructure.brain import AtomicJsonBrainRepository
from infrastructure.repositories.sqlite_household_goal_repository import (
    SQLiteHouseholdGoalRepository,
)
from infrastructure.repositories.sqlite_household_project_repository import (
    SQLiteHouseholdProjectRepository,
)


def _build_composition(tmp_path: Path):
    runtime = MemoryRuntimeIntegration(
        MemoryRuntimeConfig(
            root_path=tmp_path / "memory",
            enable_learning=False,
        )
    )
    return build_identity_memory_brain_composition(
        brain_repository=AtomicJsonBrainRepository(tmp_path / "brain"),
        memory_gateway=OfficialMemoryGateway(runtime, owner="Carlos"),
        goal_repository=SQLiteHouseholdGoalRepository(
            tmp_path / "household_goals.db"
        ),
        project_repository=SQLiteHouseholdProjectRepository(
            tmp_path / "household_projects.db"
        ),
        storage_root=tmp_path,
        relationship_memory=RelationshipMemoryManager(),
        owner="Carlos",
    )


def test_m312_14_identity_composition_exposes_context_diagnostic(
    tmp_path: Path,
) -> None:
    composition = _build_composition(tmp_path)

    assert isinstance(
        composition.conversation_context_diagnostic,
        ConversationContextDiagnostic,
    )


def test_m312_14_diagnostic_reuses_composed_preparer(tmp_path: Path) -> None:
    composition = _build_composition(tmp_path)

    assert (
        composition.conversation_context_diagnostic.preparer
        is composition.conversation_context_preparer
    )


def test_m312_14_composed_diagnostic_remains_read_only(tmp_path: Path) -> None:
    composition = _build_composition(tmp_path)

    report = composition.conversation_context_diagnostic.inspect(
        identity_request=ActiveIdentityRequest(declared_name="Carlos")
    )

    assert report.is_healthy is True
    assert report.package.is_empty is True
    assert report.findings[0].code == "package_integrity_ok"
