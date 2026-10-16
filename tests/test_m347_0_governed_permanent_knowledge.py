from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_permanent_knowledge import (
    GovernedKnowledgeKind,
    GovernedKnowledgeState,
)


class Runtime:
    pass


def _now(hour: int = 20) -> datetime:
    return datetime(2026, 7, 29, hour, tzinfo=timezone.utc)


def _remember(gateway: OfficialConversationGateway, *, fact_id: str = "vehicle"):
    return gateway.remember_governed_knowledge(
        fact_id=fact_id,
        owner="Carlos y Cristina",
        subject="vehículo familiar",
        predicate="transmisión",
        value="automática",
        kind=GovernedKnowledgeKind.RESOURCE,
        source="declaración explícita del hogar",
        accepted_by=("Carlos",),
        observed_at=_now(),
        metadata={"scope": "household"},
    )


def test_m347_0_gateway_exposes_single_permanent_knowledge_authority():
    snapshot = OfficialConversationGateway(Runtime()).governed_permanent_knowledge

    assert snapshot.schema_version == "m347.0"
    assert snapshot.authority.endswith(":GovernedPermanentKnowledge")
    assert snapshot.persistence_enabled is False
    assert snapshot.automatic_learning_enabled is False
    assert snapshot.conversation_authority is False
    assert snapshot.inference_enabled is False
    assert snapshot.active_facts == 0
    assert snapshot.total_revisions == 0
    assert snapshot.kinds == tuple(GovernedKnowledgeKind)


def test_m347_0_remembers_explicit_immutable_household_fact():
    gateway = OfficialConversationGateway(Runtime())
    fact = _remember(gateway)

    assert fact.revision == 1
    assert fact.state is GovernedKnowledgeState.ACTIVE
    assert gateway.find_governed_knowledge("vehicle") is fact
    assert gateway.active_governed_knowledge(
        owner="Carlos y Cristina", kind=GovernedKnowledgeKind.RESOURCE
    ) == (fact,)
    with pytest.raises(TypeError):
        fact.metadata["scope"] = "personal"


def test_m347_0_requires_explicit_acceptance_and_timezone():
    gateway = OfficialConversationGateway(Runtime())
    fields = dict(
        fact_id="home",
        owner="Carlos y Cristina",
        subject="Roby",
        predicate="residencia canónica",
        value="laptop del hogar",
        kind=GovernedKnowledgeKind.HOUSEHOLD,
        source="decisión del hogar",
    )

    with pytest.raises(DomainError, match="explicit acceptance"):
        gateway.remember_governed_knowledge(
            **fields, accepted_by=(), observed_at=_now()
        )
    naive_fields = {**fields, "fact_id": "home-naive"}
    with pytest.raises(DomainError, match="timezone-aware"):
        gateway.remember_governed_knowledge(
            **naive_fields,
            accepted_by=("Carlos",),
            observed_at=datetime(2026, 7, 29),
        )


def test_m347_0_revises_same_fact_with_immutable_history():
    gateway = OfficialConversationGateway(Runtime())
    original = _remember(gateway)
    revised = gateway.revise_governed_knowledge(
        original.fact_id,
        value="automática de seis marchas",
        source="corrección explícita del hogar",
        accepted_by=("Carlos", "Cristina"),
        observed_at=_now(21),
        metadata={"reason": "precision"},
    )

    assert revised.fact_id == original.fact_id
    assert revised.revision == 2
    assert revised.supersedes_revision == 1
    assert original.value == "automática"
    assert gateway.governed_knowledge_history(original.fact_id) == (
        original,
        revised,
    )
    assert gateway.governed_permanent_knowledge.total_revisions == 2


def test_m347_0_retracts_without_deleting_history():
    gateway = OfficialConversationGateway(Runtime())
    original = _remember(gateway)
    retracted = gateway.retract_governed_knowledge(
        original.fact_id,
        accepted_by=("Carlos",),
        observed_at=_now(21),
    )

    assert retracted.state is GovernedKnowledgeState.RETRACTED
    assert retracted.revision == 2
    assert gateway.active_governed_knowledge() == ()
    assert gateway.governed_knowledge_history(original.fact_id)[0] is original
    with pytest.raises(DomainError, match="cannot be revised"):
        gateway.revise_governed_knowledge(
            original.fact_id,
            value="otro valor",
            source="intento posterior",
            accepted_by=("Carlos",),
            observed_at=_now(22),
        )


def test_m347_0_rejects_duplicate_or_unknown_fact_ids():
    gateway = OfficialConversationGateway(Runtime())
    _remember(gateway)

    with pytest.raises(DomainError, match="already exists"):
        _remember(gateway)
    with pytest.raises(DomainError, match="unknown fact_id"):
        gateway.retract_governed_knowledge(
            "missing", accepted_by=("Carlos",), observed_at=_now()
        )


def test_m347_0_has_no_disk_network_inference_or_parallel_gateway():
    source = Path("domain/governed_permanent_knowledge.py").read_text(
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
    assert "conversation history" not in source.lower()


def test_m347_0_gateway_is_only_productive_knowledge_composition():
    occurrences = []
    for path in Path("app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "GovernedPermanentKnowledge()" in source:
            occurrences.append(path.as_posix())

    assert occurrences == ["app/official_conversation_gateway.py"]
