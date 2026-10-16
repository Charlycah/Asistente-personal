from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_cognitive_judgment import GovernedJudgmentOutcome
from domain.governed_proactive_care import (
    GovernedCareKind,
    GovernedCareUrgency,
)


class Runtime:
    pass


def _now() -> datetime:
    return datetime(2026, 7, 30, 1, tzinfo=timezone.utc)


def _objective(gateway: OfficialConversationGateway):
    return gateway.remember_governed_objective(
        objective_id="safe-trip",
        owner="Carlos y Cristina",
        description="Viajar de forma segura",
        observed_at=_now(),
    )


def _judgment(
    gateway: OfficialConversationGateway,
    *,
    judgment_id: str = "weather-judgment",
    outcome: GovernedJudgmentOutcome = GovernedJudgmentOutcome.READY,
):
    missing = (
        ("Pronóstico actualizado",)
        if outcome is GovernedJudgmentOutcome.NEEDS_CLARIFICATION
        else ()
    )
    questions = ("¿Cuál es el pronóstico actualizado?",) if missing else ()
    return gateway.assess_governed_cognitive_judgment(
        judgment_id=judgment_id,
        objective_ids=("safe-trip",),
        subject="Condiciones para el viaje",
        evidence=("Existe alerta de tormenta",),
        missing_information=missing,
        conflicts=(),
        risks=("Granizo durante el trayecto",),
        prioritized_objective_ids=(
            ("safe-trip",)
            if outcome is GovernedJudgmentOutcome.READY
            else ()
        ),
        outcome=outcome,
        rationale="Conviene evitar exposición innecesaria al riesgo.",
        confidence=0.9 if outcome is GovernedJudgmentOutcome.READY else 0.4,
        clarification_questions=questions,
    )


def _proposal(gateway: OfficialConversationGateway):
    return gateway.propose_governed_proactive_care(
        judgment_id="weather-judgment",
        proposal_id="care-1",
        beneficiaries=("Carlos", "Cristina"),
        kind=GovernedCareKind.WARN,
        urgency=GovernedCareUrgency.HIGH,
        situation="Alerta de tormenta antes del viaje",
        rationale="El juicio vigente identifica riesgo de granizo.",
        proposed_message="Conviene demorar la salida hasta que pase la tormenta.",
        suggested_response="Revisar el horario de salida antes de autorizar cambios.",
        evidence=("Existe alerta de tormenta",),
        risks=("Granizo durante el trayecto",),
        metadata={"scope": "household"},
    )


def test_m347_2_gateway_exposes_single_proactive_care_authority():
    snapshot = OfficialConversationGateway(Runtime()).governed_proactive_care

    assert snapshot.schema_version == "m347.2"
    assert snapshot.authority.endswith(":GovernedProactiveCare")
    assert snapshot.persistence_enabled is False
    assert snapshot.autonomous_monitoring_enabled is False
    assert snapshot.autonomous_notification_enabled is False
    assert snapshot.authorization_authority is False
    assert snapshot.execution_authority is False
    assert snapshot.conversation_authority is False
    assert snapshot.recorded_proposals == 0
    assert snapshot.kinds == tuple(GovernedCareKind)
    assert snapshot.urgencies == tuple(GovernedCareUrgency)


def test_m347_2_records_explainable_immutable_care_proposal():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway)
    _judgment(gateway)
    proposal = _proposal(gateway)

    assert proposal.judgment_id == "weather-judgment"
    assert proposal.objective_ids == ("safe-trip",)
    assert proposal.authorization_required is True
    assert gateway.find_governed_care_proposal("care-1") is proposal
    assert gateway.governed_care_proposals_for_objective("safe-trip") == (proposal,)
    assert gateway.governed_care_proposals_for_beneficiary("Cristina") == (proposal,)
    with pytest.raises(TypeError):
        proposal.metadata["scope"] = "personal"


def test_m347_2_requires_ready_cognitive_judgment():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway)
    _judgment(
        gateway,
        judgment_id="uncertain",
        outcome=GovernedJudgmentOutcome.NEEDS_CLARIFICATION,
    )

    with pytest.raises(DomainError, match="ready cognitive judgment"):
        gateway.propose_governed_proactive_care(
            judgment_id="uncertain",
            proposal_id="care-uncertain",
            beneficiaries=("Carlos",),
            kind=GovernedCareKind.INFORM,
            urgency=GovernedCareUrgency.NORMAL,
            situation="Pronóstico incompleto",
            rationale="Falta información.",
            proposed_message="Todavía no hay datos suficientes.",
            suggested_response="Consultar el pronóstico.",
            evidence=(),
            risks=(),
        )


def test_m347_2_requires_explicit_beneficiaries_and_authorization():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway)
    _judgment(gateway)

    with pytest.raises(DomainError, match="explicit beneficiaries"):
        gateway.propose_governed_proactive_care(
            judgment_id="weather-judgment",
            proposal_id="no-beneficiary",
            beneficiaries=(),
            kind=GovernedCareKind.WARN,
            urgency=GovernedCareUrgency.HIGH,
            situation="Tormenta",
            rationale="Existe riesgo.",
            proposed_message="Conviene esperar.",
            suggested_response="Revisar la salida.",
            evidence=("Alerta",),
            risks=("Granizo",),
        )
    fields = dict(
        proposal_id="no-authorization",
        beneficiaries=("Carlos",),
        kind=GovernedCareKind.WARN,
        urgency=GovernedCareUrgency.HIGH,
        situation="Tormenta",
        rationale="Existe riesgo.",
        proposed_message="Conviene esperar.",
        suggested_response="Revisar la salida.",
        evidence=("Alerta",),
        risks=("Granizo",),
        authorization_required=False,
    )
    with pytest.raises(DomainError, match="must require authorization"):
        gateway.propose_governed_proactive_care(
            judgment_id="weather-judgment", **fields
        )


def test_m347_2_rejects_unknown_judgment_and_mismatched_lineage():
    gateway = OfficialConversationGateway(Runtime())
    with pytest.raises(DomainError, match="unknown governed judgment"):
        gateway.propose_governed_proactive_care(
            judgment_id="unknown", proposal_id="unknown-care"
        )

    _objective(gateway)
    _judgment(gateway)
    with pytest.raises(DomainError, match="objective_ids must match"):
        gateway.propose_governed_proactive_care(
            judgment_id="weather-judgment",
            proposal_id="bad-lineage",
            objective_ids=("other",),
            beneficiaries=("Carlos",),
            kind=GovernedCareKind.SUGGEST,
            urgency=GovernedCareUrgency.NORMAL,
            situation="Viaje",
            rationale="Cuidado preventivo.",
            proposed_message="Conviene revisar la salida.",
            suggested_response="Confirmar horario.",
            evidence=("Alerta",),
            risks=("Granizo",),
        )


def test_m347_2_rejects_duplicate_proposal_ids():
    gateway = OfficialConversationGateway(Runtime())
    _objective(gateway)
    _judgment(gateway)
    _proposal(gateway)

    with pytest.raises(DomainError, match="already exists"):
        _proposal(gateway)


def test_m347_2_has_no_disk_network_monitoring_execution_or_parallel_gateway():
    source = Path("domain/governed_proactive_care.py").read_text(encoding="utf-8")
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
    assert "notify(" not in source
    assert "authorize(" not in source
    assert "execute(" not in source


def test_m347_2_gateway_is_only_productive_care_composition():
    occurrences = []
    for path in Path("app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "GovernedProactiveCare()" in source:
            occurrences.append(path.as_posix())

    assert occurrences == ["app/official_conversation_gateway.py"]
