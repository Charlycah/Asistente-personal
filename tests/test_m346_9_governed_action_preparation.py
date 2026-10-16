from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_action_preparation import GovernedActionKind
from domain.governed_objective_memory import GovernedObjectiveState
from domain.governed_plan import GovernedPlanStep


class Runtime:
    pass


def _now() -> datetime:
    return datetime(2026, 7, 29, 20, tzinfo=timezone.utc)


def _gateway_with_plan(*, authorization: bool = True):
    gateway = OfficialConversationGateway(Runtime())
    gateway.remember_governed_objective(
        objective_id="travel",
        owner="Carlos y Cristina",
        description="Preparar un viaje.",
        observed_at=_now(),
    )
    plan = gateway.create_governed_plan(
        plan_id="travel-plan",
        objective="Preparar un viaje.",
        current_state="Fechas confirmadas.",
        steps=(
            GovernedPlanStep(
                "calendar",
                1,
                "Preparar un evento de calendario.",
                requires_authorization=authorization,
            ),
        ),
        expected_outcome="Acción preparada sin ejecución.",
        confidence=80,
    )
    gateway.link_governed_objective_plan("travel", plan.plan_id)
    gateway.track_governed_plan_continuity("travel", plan)
    return gateway, plan


def test_m346_9_gateway_exposes_single_action_preparation_authority():
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_action_preparation

    assert snapshot.schema_version == "m346.9"
    assert snapshot.authority.endswith(":GovernedActionPreparation")
    assert snapshot.persistence_enabled is False
    assert snapshot.execution_enabled is False
    assert snapshot.authorization_enabled is False
    assert snapshot.autonomous_preparation_enabled is False
    assert snapshot.conversation_authority is False
    assert snapshot.prepared_candidates == 0
    assert snapshot.kinds == tuple(GovernedActionKind)


def test_m346_9_prepares_candidate_from_current_governed_plan_step():
    gateway, plan = _gateway_with_plan()

    candidate = gateway.prepare_governed_action(
        "travel",
        plan.plan_id,
        action_id="calendar-candidate",
        step_id="calendar",
        description="Preparar fecha del viaje para revisión.",
        kind=GovernedActionKind.CALENDAR,
        parameters={"date": "2026-08-15"},
    )

    assert candidate.objective_id == "travel"
    assert candidate.plan_id == plan.plan_id
    assert candidate.plan_revision == plan.revision
    assert candidate.required_authorizations == (
        "explicit_user_authorization",
    )
    assert gateway.find_governed_action_candidate(candidate.action_id) is candidate
    assert gateway.governed_action_candidates("travel", plan.plan_id) == (
        candidate,
    )


def test_m346_9_candidate_is_immutable_and_never_authorized_or_executed():
    gateway, plan = _gateway_with_plan()
    candidate = gateway.prepare_governed_action(
        "travel",
        plan.plan_id,
        action_id="document-candidate",
        step_id="calendar",
        description="Preparar borrador.",
        kind=GovernedActionKind.DOCUMENT,
        parameters={"format": "txt"},
        metadata={"origin": "official_conversation"},
    )

    with pytest.raises(TypeError):
        candidate.parameters["format"] = "pdf"
    assert not hasattr(candidate, "execute")
    assert not hasattr(candidate, "authorize")


def test_m346_9_uses_explicit_plan_authorization_when_available():
    gateway = OfficialConversationGateway(Runtime())
    gateway.remember_governed_objective(
        objective_id="mail",
        owner="Carlos",
        description="Preparar un correo.",
        observed_at=_now(),
    )
    plan = gateway.create_governed_plan(
        plan_id="mail-plan",
        objective="Preparar un correo.",
        current_state="Falta aprobación.",
        steps=(GovernedPlanStep("draft", 1, "Preparar borrador."),),
        expected_outcome="Correo listo para revisar.",
        confidence=90,
        required_authorizations=("Carlos confirma destinatario y contenido.",),
    )
    gateway.link_governed_objective_plan("mail", plan.plan_id)
    gateway.track_governed_plan_continuity("mail", plan)

    candidate = gateway.prepare_governed_action(
        "mail",
        plan.plan_id,
        action_id="mail-candidate",
        step_id="draft",
        description="Preparar el borrador de correo.",
        kind=GovernedActionKind.COMMUNICATION,
    )

    assert candidate.required_authorizations == plan.required_authorizations


def test_m346_9_rejects_non_authorizable_unknown_or_duplicate_candidates():
    gateway, plan = _gateway_with_plan(authorization=False)

    with pytest.raises(DomainError, match="requires explicit authorization"):
        gateway.prepare_governed_action(
            "travel",
            plan.plan_id,
            action_id="unsafe",
            step_id="calendar",
            description="No autorizable.",
            kind=GovernedActionKind.OTHER,
        )
    with pytest.raises(DomainError, match="current plan step"):
        gateway.prepare_governed_action(
            "travel",
            plan.plan_id,
            action_id="unknown-step",
            step_id="missing",
            description="Paso inexistente.",
            kind=GovernedActionKind.OTHER,
            required_authorizations=("Confirmación explícita.",),
        )
    gateway.prepare_governed_action(
        "travel",
        plan.plan_id,
        action_id="duplicate",
        step_id="calendar",
        description="Primera preparación.",
        kind=GovernedActionKind.OTHER,
        required_authorizations=("Confirmación explícita.",),
    )
    with pytest.raises(DomainError, match="already prepared"):
        gateway.prepare_governed_action(
            "travel",
            plan.plan_id,
            action_id="duplicate",
            step_id="calendar",
            description="Segunda preparación.",
            kind=GovernedActionKind.OTHER,
            required_authorizations=("Confirmación explícita.",),
        )


def test_m346_9_rejects_completed_objective():
    gateway, plan = _gateway_with_plan()
    gateway.set_governed_objective_state(
        "travel", GovernedObjectiveState.COMPLETED, observed_at=_now()
    )

    with pytest.raises(DomainError, match="completed objectives"):
        gateway.prepare_governed_action(
            "travel",
            plan.plan_id,
            action_id="late",
            step_id="calendar",
            description="Preparación tardía.",
            kind=GovernedActionKind.CALENDAR,
        )


def test_m346_9_preparation_has_no_disk_network_execution_or_gateway():
    source = Path("domain/governed_action_preparation.py").read_text(
        encoding="utf-8"
    )
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


def test_m346_9_gateway_is_only_productive_action_preparation_composition():
    occurrences = []
    for path in Path("app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "GovernedActionPreparation()" in source:
            occurrences.append(path.as_posix())

    assert occurrences == ["app/official_conversation_gateway.py"]
