from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

from app.official_conversation_gateway import OfficialConversationGateway
from app.productive_organization_advisory_wiring import (
    ProductiveOrganizationAdvisoryWiring,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_organization_reference_acquisition import (
    ExplicitOrganizationReference,
)
from core.household_goals import HouseholdGoal
from core.household_projects import HouseholdProject
from domain.reminders import Reminder, ReminderStatus

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 13, tzinfo=timezone.utc)


class Manager:
    def __init__(self, items) -> None:
        self.items = tuple(items)

    def list(self):
        return self.items


class GoalService:
    manager = Manager(
        (HouseholdGoal(goal_id="g1", name="Goal", created_at=NOW, updated_at=NOW),)
    )


class ProjectService:
    manager = Manager(
        (
            HouseholdProject(
                project_id="p1",
                name="Project",
                created_at=NOW,
                updated_at=NOW,
            ),
        )
    )


class ReminderRepository:
    def list_pending(self):
        return [
            Reminder(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                title="Reminder",
                description="",
                status=ReminderStatus.PENDING,
                recurrence=None,
                due_at=NOW,
                created_at=NOW,
                updated_at=NOW,
            )
        ]


class Connection:
    def close(self) -> None:
        pass


class ReminderService:
    def _repository(self):
        return Connection(), ReminderRepository()


@dataclass(frozen=True)
class Registration:
    interceptor: object


class Registry:
    def __init__(self, *, include_projects: bool = True) -> None:
        self.services = {
            "household.goals": GoalService(),
            "resident.reminders": ReminderService(),
        }
        if include_projects:
            self.services["household.projects"] = ProjectService()

    def registration_for(self, name: str):
        service = self.services.get(name)
        if service is None:
            return None
        return Registration(SimpleNamespace(service=service))


class Turn:
    response_text = "respuesta normal"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False
    response_path = "pipeline"
    degradation_reason = "not_applicable"


class RuntimeStub:
    history = ()
    traces = ()

    def __init__(self, registry=None) -> None:
        dependencies = SimpleNamespace(official_capability_registry=registry)
        root = SimpleNamespace(dependencies=dependencies)
        self.bootstrap = SimpleNamespace(root=root)
        self.calls = []

    def converse(self, text: str, **kwargs):
        self.calls.append((text, kwargs))
        return Turn()


def _adaptation():
    evidence = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "¿Project o Reminder?"
    )
    return ExplicitDeliberationDecisionOptionAdapter().adapt(evidence)


def _references():
    return (
        ExplicitOrganizationReference(0, organization_item_id="p1"),
        ExplicitOrganizationReference(
            1,
            organization_source_reference=(
                "reminder:00000000-0000-0000-0000-000000000001"
            ),
        ),
    )


def test_wiring_reads_official_sources_and_assembles_existing_m391_6() -> None:
    wiring = ProductiveOrganizationAdvisoryWiring(RuntimeStub(Registry()))

    result = wiring.assemble(_adaptation(), _references())

    assert result is not None
    assert result.advisory.schema_version == "m391.6"
    assert result.advisory.canonical_facade == "CanonicalDecisionFacade"
    assert result.partial_organization is True
    assert result.tasks_available is False
    assert all(
        item.organization_kind is not None for item in result.advisory.assessments
    )


def test_gateway_uses_organization_branch_without_runtime_or_second_advisor() -> None:
    runtime = RuntimeStub(Registry())
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit(
        "¿Project o Reminder?",
        session_id="main",
        organization_references=_references(),
    )

    assert runtime.calls == []
    assert turn.response_path == "interceptor"
    assert turn.provider_call_performed is False
    assert turn.retrieval_performed is False
    assert turn.network_access_performed is False
    assert "sigue siendo tuya" in turn.response_text


def test_unknown_reference_falls_back_to_existing_explicit_advisory() -> None:
    runtime = RuntimeStub(Registry())
    gateway = OfficialConversationGateway(runtime)
    original = gateway._canonical_decision

    class DecisionSpy:
        def __init__(self) -> None:
            self.calls = 0

        def advise(self, options, **kwargs):
            self.calls += 1
            return original.advise(options, **kwargs)

    spy = DecisionSpy()
    gateway._canonical_decision = spy
    refs = (
        ExplicitOrganizationReference(0, organization_item_id="missing"),
    )

    turn = gateway.submit(
        "¿Project o Reminder?",
        session_id="main",
        organization_references=refs,
    )

    assert runtime.calls == []
    assert spy.calls == 1
    assert turn.response_path == "interceptor"
    assert "requiere más revisión" in turn.response_text


def test_unavailable_source_falls_back_without_guessing() -> None:
    runtime = RuntimeStub(Registry(include_projects=False))
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit(
        "¿Project o Reminder?",
        session_id="main",
        organization_references=_references(),
    )

    assert runtime.calls == []
    assert turn.response_path == "interceptor"
    assert "requiere más revisión" in turn.response_text


def test_no_references_preserves_preexisting_explicit_deliberation_path() -> None:
    runtime = RuntimeStub(Registry())
    gateway = OfficialConversationGateway(runtime)

    turn = gateway.submit("¿A o B?", session_id="main")

    assert runtime.calls == []
    assert turn.response_path == "interceptor"
    assert "requiere más revisión" in turn.response_text


def test_external_evidence_still_bypasses_all_local_advisory_wiring() -> None:
    runtime = RuntimeStub(Registry())
    gateway = OfficialConversationGateway(runtime)
    external = (object(),)

    turn = gateway.submit(
        "¿Project o Reminder?",
        session_id="main",
        external_evidence=external,
        organization_references=_references(),
    )

    assert len(runtime.calls) == 1
    assert runtime.calls[0][1]["external_evidence"] == external
    assert turn.response_text == "respuesta normal"


def test_wiring_source_has_no_m410_networking_residential_or_new_authority() -> None:
    path = ROOT / "app" / "productive_organization_advisory_wiring.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert "M410" not in source
    assert not any("network" in item for item in imports)
    assert not any("residential" in item for item in imports)
    assert "Authority(" not in source
    assert "GovernedDecisionAdvisor" not in source
    assert "CanonicalDecisionFacade().bind" not in source


def test_gateway_keeps_single_canonical_core_constructor() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    constructors = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert constructors == [52]
