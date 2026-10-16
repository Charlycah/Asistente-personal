from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_cognitive_judgment import GovernedJudgmentOutcome
from domain.governed_objective_memory import GovernedObjectiveState
from domain.governed_permanent_knowledge import GovernedKnowledgeKind


class Runtime:
    pass


def _now(hour: int = 20) -> datetime:
    return datetime(2026, 7, 29, hour, tzinfo=timezone.utc)


def _objective(gateway: OfficialConversationGateway, objective_id: str):
    return gateway.remember_governed_objective(
        objective_id=objective_id,
        owner="Carlos y Cristina",
        description="Resolver una necesidad doméstica concreta",
        observed_at=_now(),
        metadata={"scope": "household"},
    )


def _fact(gateway: OfficialConversationGateway):
    return gateway.remember_governed_knowledge(
        fact_id="vehicle",
        owner="Carlos y Cristina",
        subject="vehículo familiar",
        predicate="transmisión",
        value="automática",
        kind=GovernedKnowledgeKind.RESOURCE,
        source="declaración explícita del hogar",
        accepted_by=("Carlos",),
        observed_at=_now(),
    )


def _ready(gateway: OfficialConversationGateway):
    return gateway.assess_governed_cognitive_judgment(
        judgment_id="judgment-1",
        objective_ids=("trip",),
        knowledge_fact_ids=("vehicle",),
        subject="Preparación del viaje",
        evidence=("El vehículo está disponible",),
        missing_information=(),
        conflicts=(),
        risks=("Tránsito intenso",),
        prioritized_objective_ids=("trip",),
        outcome=GovernedJudgmentOutcome.READY,
        rationale="El objetivo es viable con la evidencia aceptada.",
        confidence=0.85,
        metadata={"scope": "household"},
    )


def test_m347_1_gateway_exposes_single_advisory_judgment_authority():
    snapshot = OfficialConversationGateway(Runtime()).governed_cognitive_judgment

    assert snapshot.schema_version == "m347.1"
    assert snapshot.authority.endswith(":GovernedCognitiveJudgmentAuthority")
    assert snapshot.persistence_enabled is False
    assert snapshot.autonomous_judgment_enabled is False
    assert snapshot.decision_authority is False
    assert snapshot.execution_authority is False
    assert snapshot.conversation_authority is False
    assert snapshot.recorded_judgments == 0
    assert snapshot.outcomes == tuple(GovernedJudgmentOutcome)


def test_m347_1_records_explainable_immutable_ready_judgment():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway, "trip")
    _fact(gateway)
    judgment = _ready(gateway)

    assert judgment.objective_ids == ("trip",)
    assert judgment.knowledge_fact_ids == ("vehicle",)
    assert judgment.outcome is GovernedJudgmentOutcome.READY
    assert judgment.confidence == 0.85
    assert gateway.find_governed_cognitive_judgment("judgment-1") is judgment
    assert gateway.governed_judgments_for_objective("trip") == (judgment,)
    with pytest.raises(TypeError):
        judgment.metadata["scope"] = "personal"


def test_m347_1_requires_questions_when_information_is_missing():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway, "appointment")

    with pytest.raises(DomainError, match="explicit questions"):
        gateway.assess_governed_cognitive_judgment(
            judgment_id="missing-question",
            objective_ids=("appointment",),
            subject="Organizar el turno",
            evidence=(),
            missing_information=("Horario disponible",),
            conflicts=(),
            risks=(),
            prioritized_objective_ids=(),
            outcome=GovernedJudgmentOutcome.NEEDS_CLARIFICATION,
            rationale="Falta un dato esencial.",
            confidence=0.3,
        )


def test_m347_1_requires_explicit_conflict_for_conflicted_outcome():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway, "first")
    _objective(gateway, "second")

    with pytest.raises(DomainError, match="explicit conflicts"):
        gateway.assess_governed_cognitive_judgment(
            judgment_id="conflict",
            objective_ids=("first", "second"),
            subject="Prioridad doméstica",
            evidence=("Ambos objetivos son vigentes",),
            missing_information=(),
            conflicts=(),
            risks=(),
            prioritized_objective_ids=(),
            outcome=GovernedJudgmentOutcome.CONFLICTED,
            rationale="Todavía no existe una prioridad segura.",
            confidence=0.5,
        )


def test_m347_1_rejects_completed_objectives_and_retracted_knowledge():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway, "trip")
    _fact(gateway)
    gateway.set_governed_objective_state(
        "trip", GovernedObjectiveState.COMPLETED, observed_at=_now(21)
    )

    with pytest.raises(DomainError, match="completed objectives"):
        _ready(gateway)

    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway, "trip")
    _fact(gateway)
    gateway.retract_governed_knowledge(
        "vehicle", accepted_by=("Carlos",), observed_at=_now(21)
    )
    with pytest.raises(DomainError, match="retracted knowledge"):
        _ready(gateway)


def test_m347_1_rejects_unknown_priorities_and_duplicate_ids():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway, "trip")
    _fact(gateway)

    with pytest.raises(DomainError, match="must belong"):
        gateway.assess_governed_cognitive_judgment(
            judgment_id="bad-priority",
            objective_ids=("trip",),
            subject="Preparación del viaje",
            evidence=("Vehículo disponible",),
            missing_information=(),
            conflicts=(),
            risks=(),
            prioritized_objective_ids=("unknown",),
            outcome=GovernedJudgmentOutcome.READY,
            rationale="Prioridad inválida.",
            confidence=0.8,
        )
    _ready(gateway)
    with pytest.raises(DomainError, match="already exists"):
        _ready(gateway)


def test_m347_1_has_no_disk_network_decision_execution_or_parallel_gateway():
    source = Path("domain/governed_cognitive_judgment.py").read_text(
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
    assert "authorize(" not in source
    assert "execute(" not in source


def test_m347_1_gateway_is_only_productive_judgment_composition():
    occurrences = []
    for path in Path("app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "GovernedCognitiveJudgmentAuthority()" in source:
            occurrences.append(path.as_posix())

    assert occurrences == ["app/official_conversation_gateway.py"]
