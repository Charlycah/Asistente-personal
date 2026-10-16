from __future__ import annotations

import ast
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from app.linked_organization_m391_6_advisory_assembly import (
    LinkedOrganizationM3916AdvisoryAssembler,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_organization_reference_acquisition import (
    ExplicitOrganizationReference,
    ExplicitOrganizationReferenceAcquirer,
)
from core.household_goals import HouseholdGoal
from core.household_projects import HouseholdProject
from core.organization_decision_exact_identity_linkage import (
    OrganizationDecisionExactIdentityLinker,
)
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceAvailability,
    OrganizationSourceKind,
    PartialCanonicalOrganizationSnapshotBuilder,
)
from core.partial_organization_m391_5_consumption import (
    PartialOrganizationM3915Consumer,
)
from domain.reminders import Reminder, ReminderStatus

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 13, tzinfo=timezone.utc)


class Goals:
    def list_goals(self):
        return (
            HouseholdGoal(goal_id="g1", name="Goal", created_at=NOW, updated_at=NOW),
        )


class Projects:
    def list_projects(self):
        return (
            HouseholdProject(
                project_id="p1", name="Project", created_at=NOW, updated_at=NOW
            ),
        )


class Reminders:
    def list_pending_reminders(self):
        return (
            Reminder(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                title="Reminder",
                description="",
                status=ReminderStatus.PENDING,
                recurrence=None,
                due_at=NOW,
                created_at=NOW,
                updated_at=NOW,
            ),
        )


def _inputs():
    evidence = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "¿Project o Reminder?"
    )
    adaptation = ExplicitDeliberationDecisionOptionAdapter().adapt(evidence)
    acquisition = ExplicitOrganizationReferenceAcquirer().acquire(
        adaptation,
        (
            ExplicitOrganizationReference(0, organization_item_id="p1"),
            ExplicitOrganizationReference(
                1,
                organization_source_reference=(
                    "reminder:00000000-0000-0000-0000-000000000001"
                ),
            ),
        ),
    )
    snapshot = PartialCanonicalOrganizationSnapshotBuilder(
        goals_port=Goals(), projects_port=Projects(), reminders_port=Reminders()
    ).build()
    linkage = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, snapshot
    )
    consumption = PartialOrganizationM3915Consumer().consume(snapshot)
    return linkage, consumption


def test_assembles_linked_organization_evidence_through_existing_m391_6() -> None:
    linkage, consumption = _inputs()
    result = LinkedOrganizationM3916AdvisoryAssembler().assemble(linkage, consumption)

    assert result.advisory.schema_version == "m391.6"
    assert result.advisory.canonical_facade == "CanonicalDecisionFacade"
    assert result.advisory.canonical_authority == "unified_cognitive_coordination"
    assert {item.option_id for item in result.advisory.assessments} == {
        item.option_id for item in linkage.options
    }
    assert all(
        item.organization_kind is not None for item in result.advisory.assessments
    )
    assert result.read_only is True
    assert result.advisory_only is True
    assert result.tasks_available is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_preserves_partial_source_boundary_and_tasks_unavailable() -> None:
    linkage, consumption = _inputs()
    result = LinkedOrganizationM3916AdvisoryAssembler().assemble(linkage, consumption)
    availability = dict(consumption.source_availability)

    assert (
        availability[OrganizationSourceKind.GOALS]
        is OrganizationSourceAvailability.AVAILABLE
    )
    assert (
        availability[OrganizationSourceKind.PROJECTS]
        is OrganizationSourceAvailability.AVAILABLE
    )
    assert (
        availability[OrganizationSourceKind.REMINDERS]
        is OrganizationSourceAvailability.AVAILABLE
    )
    assert (
        availability[OrganizationSourceKind.TASKS]
        is OrganizationSourceAvailability.UNAVAILABLE
    )
    assert result.partial_organization is True


def test_assembly_is_deterministic_and_does_not_mutate_inputs() -> None:
    linkage, consumption = _inputs()
    first = LinkedOrganizationM3916AdvisoryAssembler().assemble(linkage, consumption)
    second = LinkedOrganizationM3916AdvisoryAssembler().assemble(linkage, consumption)

    assert first == second
    assert first.source_fingerprint == second.source_fingerprint


def test_rejects_linkage_from_different_snapshot() -> None:
    linkage, consumption = _inputs()
    bad = replace(linkage, organization_fingerprint="different")
    with pytest.raises(ValueError, match="share one snapshot"):
        LinkedOrganizationM3916AdvisoryAssembler().assemble(bad, consumption)


def test_rejects_linked_item_missing_from_m391_5_report() -> None:
    linkage, consumption = _inputs()
    organization = replace(consumption.organization, recommendations=())
    bad = replace(consumption, organization=organization)
    with pytest.raises(ValueError, match="missing from M391.5"):
        LinkedOrganizationM3916AdvisoryAssembler().assemble(linkage, bad)


def test_assembly_has_no_gateway_runtime_networking_or_residential_dependency() -> None:
    path = ROOT / "app" / "linked_organization_m391_6_advisory_assembly.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    forbidden = {
        "app.official_conversation_gateway",
        "app.runtime_root_factory",
        "core.residential",
        "core.networking",
    }
    assert imports.isdisjoint(forbidden)
    assert "M410" not in source
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert "GovernedDecisionAdvisor" not in imported_names
