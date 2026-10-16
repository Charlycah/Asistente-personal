from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_objective_memory import GovernedObjectiveState
from domain.governed_plan import GovernedPlanStep


class Runtime:
    pass


def _now(hour: int = 10) -> datetime:
    return datetime(2026, 7, 29, hour, tzinfo=timezone.utc)


def _gateway_with_plan():
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
        current_state="Faltan fecha y transporte.",
        steps=(
            GovernedPlanStep("dates", 1, "Confirmar fechas."),
            GovernedPlanStep(
                "route",
                2,
                "Revisar la ruta.",
                depends_on=("dates",),
            ),
        ),
        expected_outcome="Viaje organizado sin ejecutar reservas.",
        confidence=60,
        missing_information=("Fecha definitiva.", "Transporte."),
    )
    gateway.link_governed_objective_plan(
        "travel", plan.plan_id, observed_at=_now(11)
    )
    gateway.track_governed_plan_continuity("travel", plan)
    return gateway, plan


def test_m346_8_gateway_exposes_single_continuity_authority():
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_plan_continuity

    assert snapshot.schema_version == "m346.8"
    assert snapshot.authority.endswith(":GovernedPlanContinuity")
    assert snapshot.persistence_enabled is False
    assert snapshot.execution_enabled is False
    assert snapshot.autonomous_revision_enabled is False
    assert snapshot.conversation_authority is False


def test_m346_8_tracks_existing_linked_plan_without_duplication():
    gateway, original = _gateway_with_plan()

    assert gateway.current_governed_plan("travel", "travel-plan") is original
    assert gateway.governed_plan_history("travel", "travel-plan") == (original,)
    with pytest.raises(DomainError, match="already tracked"):
        gateway.track_governed_plan_continuity("travel", original)


def test_m346_8_review_preserves_identity_and_increments_revision():
    gateway, original = _gateway_with_plan()

    revised = gateway.review_governed_plan(
        "travel",
        "travel-plan",
        reason="Se confirmó el transporte.",
        changes={
            "current_state": "La camioneta está disponible; falta la fecha.",
            "missing_information": ("Fecha definitiva.",),
            "confidence": 75,
        },
        impacted_step_ids=("route",),
        observed_at=_now(12),
    )

    assert revised.plan_id == original.plan_id
    assert revised.revision == 2
    assert revised.supersedes_revision == 1
    assert original.revision == 1
    assert gateway.governed_plan_history("travel", "travel-plan") == (
        original,
        revised,
    )
    review = gateway.governed_plan_reviews("travel", "travel-plan")[0]
    assert review.changed_fields == (
        "current_state",
        "missing_information",
        "confidence",
    )
    assert review.impacted_step_ids == ("route",)


def test_m346_8_no_effective_change_does_not_create_revision():
    gateway, original = _gateway_with_plan()

    unchanged = gateway.review_governed_plan(
        "travel",
        "travel-plan",
        reason="La información fue repetida.",
        changes={"confidence": original.confidence},
        observed_at=_now(12),
    )

    assert unchanged is original
    assert gateway.governed_plan_history("travel", "travel-plan") == (original,)
    assert gateway.governed_plan_reviews("travel", "travel-plan") == ()


def test_m346_8_review_rejects_unknown_impacts_and_completed_objective():
    gateway, _ = _gateway_with_plan()

    with pytest.raises(DomainError, match="current plan steps"):
        gateway.review_governed_plan(
            "travel",
            "travel-plan",
            reason="Cambio de ruta.",
            changes={"confidence": 70},
            impacted_step_ids=("missing-step",),
            observed_at=_now(12),
        )
    gateway.set_governed_objective_state(
        "travel", GovernedObjectiveState.COMPLETED, observed_at=_now(13)
    )
    with pytest.raises(DomainError, match="completed objectives"):
        gateway.review_governed_plan(
            "travel",
            "travel-plan",
            reason="Intento tardío.",
            changes={"confidence": 80},
            observed_at=_now(14),
        )


def test_m346_8_requires_link_before_tracking_and_known_plan_for_review():
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
        current_state="Inicio.",
        steps=(GovernedPlanStep("first", 1, "Primer paso."),),
        expected_outcome="Plan preparado.",
        confidence=50,
    )

    with pytest.raises(DomainError, match="must link"):
        gateway.track_governed_plan_continuity("travel", plan)
    with pytest.raises(DomainError, match="unknown tracked plan"):
        gateway.review_governed_plan(
            "travel",
            "travel-plan",
            reason="Nueva evidencia.",
            changes={"confidence": 60},
            observed_at=_now(11),
        )


def test_m346_8_continuity_has_no_disk_network_execution_or_parallel_gateway():
    source = Path("domain/governed_plan_continuity.py").read_text(encoding="utf-8")
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


def test_m346_8_gateway_is_the_only_productive_continuity_composition():
    occurrences = []
    for path in Path("app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "GovernedPlanContinuity()" in source:
            occurrences.append(path.as_posix())

    assert occurrences == ["app/official_conversation_gateway.py"]
