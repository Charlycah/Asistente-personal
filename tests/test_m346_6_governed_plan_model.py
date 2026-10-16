from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_plan import GovernedPlanState, GovernedPlanStep


class Runtime:
    pass


def _fields():
    return {
        "plan_id": "travel-tandil-1",
        "objective": "Organizar un viaje familiar a Tandil.",
        "current_state": "Hay intención de viajar, pero faltan fechas.",
        "steps": (
            GovernedPlanStep(
                step_id="confirm-dates",
                order=1,
                description="Confirmar las fechas posibles.",
            ),
            GovernedPlanStep(
                step_id="review-route",
                order=2,
                description="Revisar ruta y condiciones del viaje.",
                depends_on=("confirm-dates",),
            ),
            GovernedPlanStep(
                step_id="authorize-booking",
                order=3,
                description="Solicitar autorización antes de reservar.",
                depends_on=("review-route",),
                requires_authorization=True,
            ),
        ),
        "expected_outcome": "Un viaje preparado sin ejecutar reservas.",
        "confidence": 75,
        "assumptions": ("El traslado será terrestre.",),
        "missing_information": ("Fechas definitivas.",),
        "dependencies": ("Disponibilidad de alojamiento.",),
        "risks": ("Cambios meteorológicos.",),
        "required_authorizations": ("Autorizar cualquier reserva.",),
        "metadata": {"origin": "official_conversation"},
    }


def test_m346_6_gateway_exposes_single_governed_plan_model():
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_plan_model

    assert snapshot.schema_version == "m346.6"
    assert snapshot.authority == "domain.governed_plan:GovernedPlanModel"
    assert snapshot.persistence_enabled is False
    assert snapshot.execution_enabled is False
    assert snapshot.autonomous_planning_enabled is False
    assert snapshot.conversation_authority is False
    assert snapshot.states == tuple(GovernedPlanState)


def test_m346_6_gateway_creates_immutable_governed_plan():
    gateway = OfficialConversationGateway(Runtime())

    plan = gateway.create_governed_plan(**_fields())

    assert plan.state is GovernedPlanState.DRAFT
    assert plan.steps[1].depends_on == ("confirm-dates",)
    assert plan.requires_authorization is True
    assert plan.metadata == {"origin": "official_conversation"}
    with pytest.raises(TypeError):
        plan.metadata["origin"] = "changed"


def test_m346_6_plan_requires_ordered_unique_valid_steps():
    gateway = OfficialConversationGateway(Runtime())
    fields = _fields()
    fields["steps"] = (
        GovernedPlanStep("later", 2, "Paso posterior."),
        GovernedPlanStep("first", 1, "Paso inicial."),
    )

    with pytest.raises(DomainError, match="ascending order"):
        gateway.create_governed_plan(**fields)


def test_m346_6_dependencies_reference_only_prior_known_steps():
    gateway = OfficialConversationGateway(Runtime())
    fields = _fields()
    fields["steps"] = (
        GovernedPlanStep(
            "first",
            1,
            "Paso inicial.",
            depends_on=("missing",),
        ),
    )

    with pytest.raises(DomainError, match="known steps"):
        gateway.create_governed_plan(**fields)


def test_m346_6_model_rejects_invalid_confidence_and_empty_plan():
    gateway = OfficialConversationGateway(Runtime())
    invalid_confidence = _fields()
    invalid_confidence["confidence"] = 101
    with pytest.raises(DomainError, match="between 0 and 100"):
        gateway.create_governed_plan(**invalid_confidence)

    empty = _fields()
    empty["steps"] = ()
    with pytest.raises(DomainError, match="at least one"):
        gateway.create_governed_plan(**empty)


def test_m346_6_model_has_no_execution_storage_or_parallel_gateway():
    source = Path("domain/governed_plan.py").read_text(encoding="utf-8")
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
            "sqlite3",
            "subprocess",
            "threading",
        }
    )
    assert "credentials.json" not in source
    assert "OfficialConversationGateway(" not in source
    assert "execute(" not in source


def test_m346_6_gateway_is_the_only_productive_model_composition():
    occurrences = []
    for path in Path("app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "GovernedPlanModel()" in source:
            occurrences.append(path.as_posix())

    assert occurrences == ["app/official_conversation_gateway.py"]
