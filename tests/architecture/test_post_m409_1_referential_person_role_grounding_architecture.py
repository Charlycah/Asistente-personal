from __future__ import annotations

import ast
import inspect

from core.turn_local_person_perspective import (
    TurnLocalPersonPerspectiveEvidence,
    TurnLocalPersonPerspectiveEvidenceProducer,
)


def test_producer_has_no_llm_memory_identity_or_relationship_dependencies() -> None:
    module = inspect.getmodule(TurnLocalPersonPerspectiveEvidenceProducer)
    assert module is not None
    tree = ast.parse(inspect.getsource(module))
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    forbidden = {
        "core.llm_provider",
        "core.relationship_memory",
        "core.governed_people_representation",
        "core.personal_identity_and_session_profiles",
        "app.identity_context_access",
    }
    assert imports.isdisjoint(forbidden)


def test_evidence_contract_has_no_persistence_or_execution_power() -> None:
    evidence = TurnLocalPersonPerspectiveEvidenceProducer().analyze(
        "Marta compró un libro."
    )
    for name in (
        "persists_results",
        "creates_person",
        "creates_relationship",
        "creates_memory",
        "modifies_memory",
        "modifies_identity",
        "modifies_profile",
        "modifies_world_model",
        "modifies_grounding_state",
        "uses_provider",
        "uses_retrieval",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert getattr(evidence, name) is False


def test_evidence_is_frozen_turn_local_data_not_runtime_authority() -> None:
    assert hasattr(TurnLocalPersonPerspectiveEvidence, "__dataclass_fields__")
    assert "intercept" not in TurnLocalPersonPerspectiveEvidenceProducer.__dict__
    assert "execute" not in TurnLocalPersonPerspectiveEvidenceProducer.__dict__
    assert "save" not in TurnLocalPersonPerspectiveEvidenceProducer.__dict__
