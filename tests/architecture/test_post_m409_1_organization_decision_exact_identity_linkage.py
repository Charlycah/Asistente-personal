from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

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
    OrganizationDecisionIdentityKind,
    OrganizationDecisionOptionLinkageOutcome,
)
from core.partial_canonical_organization_snapshot import (
    PartialCanonicalOrganizationSnapshotBuilder,
)
from domain.reminders.entities import Reminder
from domain.reminders.enums import ReminderStatus

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 13, 9, 0, tzinfo=timezone.utc)


class GoalsPort:
    def list_goals(self):
        return (
            HouseholdGoal(
                name="Goal visible",
                goal_id="goal-1",
                created_at=NOW,
                updated_at=NOW,
            ),
        )


class ProjectsPort:
    def list_projects(self):
        return (
            HouseholdProject(
                name="Proyecto ROBY",
                project_id="project-1",
                created_at=NOW,
                updated_at=NOW,
            ),
        )


class EmptyRemindersPort:
    def list_pending_reminders(self):
        return ()


class RemindersPort:
    def list_pending_reminders(self):
        return (
            Reminder(
                id=UUID(int=1),
                title="Recordatorio visible",
                description=None,
                due_at=datetime(2026, 8, 14, 9, 0, tzinfo=timezone.utc),
                status=ReminderStatus.PENDING,
                recurrence=None,
                created_at=NOW,
                updated_at=NOW,
            ),
        )


def _adaptation():
    evidence = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "¿Proyecto ROBY o recordatorio visible?"
    )
    return ExplicitDeliberationDecisionOptionAdapter().adapt(evidence)


def _snapshot(reminders=True):
    reminder_port = RemindersPort() if reminders else EmptyRemindersPort()
    return PartialCanonicalOrganizationSnapshotBuilder(
        GoalsPort(), ProjectsPort(), reminder_port
    ).build()


def _acquire(*refs):
    adaptation = _adaptation()
    acquisition = ExplicitOrganizationReferenceAcquirer().acquire(
        adaptation, tuple(refs)
    )
    return adaptation, acquisition


def test_explicit_item_id_links_without_changing_option_identity() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(0, organization_item_id="project-1")
    )
    result = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, _snapshot()
    )
    assert result.options[0].option_id == adaptation.options[0].option_id
    assert result.options[0].organization_item_id == "project-1"
    assert result.options[0].title == adaptation.options[0].title
    assert result.options[0].explicit_preference == 0.0
    assert adaptation.options[0].organization_item_id is None
    assert result.bindings[0].identity_kind is (
        OrganizationDecisionIdentityKind.EXPLICIT_ITEM_ID
    )


def test_explicit_source_reference_links_exactly_and_preserves_lineage() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(
            1,
            organization_source_reference=(
                "reminder:00000000-0000-0000-0000-000000000001"
            ),
        )
    )
    snapshot = _snapshot()
    result = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, snapshot
    )
    assert result.outcomes[1].outcome is OrganizationDecisionOptionLinkageOutcome.LINKED
    assert result.bindings[0].organization_fingerprint == snapshot.source_fingerprint
    assert result.bindings[0].identity_kind is (
        OrganizationDecisionIdentityKind.EXPLICIT_SOURCE_REFERENCE
    )


def test_no_reference_stays_neutral() -> None:
    adaptation, acquisition = _acquire()
    result = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, _snapshot()
    )
    assert all(
        item.outcome is OrganizationDecisionOptionLinkageOutcome.NO_REFERENCE
        for item in result.outcomes
    )
    assert result.options == adaptation.options
    assert result.bindings == ()


def test_unknown_reference_on_available_or_empty_source_is_unknown() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(
            1, organization_source_reference="reminder:missing"
        )
    )
    result = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, _snapshot(reminders=False)
    )
    assert result.outcomes[1].outcome is (
        OrganizationDecisionOptionLinkageOutcome.UNKNOWN_REFERENCE
    )


def test_task_source_reference_reports_source_unavailable() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(0, organization_source_reference="task:t1")
    )
    result = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, _snapshot()
    )
    assert result.outcomes[0].outcome is (
        OrganizationDecisionOptionLinkageOutcome.SOURCE_UNAVAILABLE
    )
    assert result.options[0].organization_item_id is None


def test_unknown_reference_does_not_fall_back_to_equal_title() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(
            0, organization_source_reference="project:not-project-1"
        )
    )
    result = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, _snapshot()
    )
    assert adaptation.options[0].title == "Proyecto ROBY"
    assert result.outcomes[0].outcome is (
        OrganizationDecisionOptionLinkageOutcome.UNKNOWN_REFERENCE
    )
    assert result.options[0].organization_item_id is None


def test_unsupported_source_namespace_fails_closed() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(0, organization_source_reference="note:n1")
    )
    with pytest.raises(ValueError):
        OrganizationDecisionExactIdentityLinker().link(
            adaptation, acquisition, _snapshot()
        )


def test_linker_preserves_scenario_causal_and_preference_fields() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(0, organization_item_id="project-1")
    )
    before = adaptation.options[0]
    after = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, _snapshot()
    ).options[0]
    assert after.scenario_hypothesis_id == before.scenario_hypothesis_id
    assert after.causal_relation_id == before.causal_relation_id
    assert after.explicit_preference == before.explicit_preference


def test_linker_is_deterministic() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(0, organization_item_id="project-1"),
        ExplicitOrganizationReference(
            1,
            organization_source_reference=(
                "reminder:00000000-0000-0000-0000-000000000001"
            ),
        ),
    )
    linker = OrganizationDecisionExactIdentityLinker()
    snapshot = _snapshot()
    assert linker.link(adaptation, acquisition, snapshot) == linker.link(
        adaptation, acquisition, snapshot
    )


def test_linker_has_no_advisory_runtime_or_semantic_matching_dependencies() -> None:
    path = ROOT / "core" / "organization_decision_exact_identity_linkage.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    forbidden = (
        "core.intelligent_personal_organization",
        "app.canonical_decision_facade",
        "app.official_conversation_gateway",
        "app.runtime_root_factory",
    )
    assert all(item not in imports for item in forbidden)
    assert "GovernedDecisionAdvisor" not in source
    assert "fuzzy" not in source.casefold()
    assert "llm" not in source.casefold()
    assert "casefold" not in source


def test_same_organization_item_for_two_options_is_ambiguous_for_both() -> None:
    adaptation, acquisition = _acquire(
        ExplicitOrganizationReference(0, organization_item_id="project-1"),
        ExplicitOrganizationReference(1, organization_item_id="project-1"),
    )
    result = OrganizationDecisionExactIdentityLinker().link(
        adaptation, acquisition, _snapshot()
    )
    assert tuple(item.outcome for item in result.outcomes) == (
        OrganizationDecisionOptionLinkageOutcome.AMBIGUOUS_REFERENCE,
        OrganizationDecisionOptionLinkageOutcome.AMBIGUOUS_REFERENCE,
    )
    assert all(item.organization_item_id is None for item in result.options)
    assert result.bindings == ()
