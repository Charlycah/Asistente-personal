from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.memory_planning_evidence import MemoryPlanningEvidence

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 6, 10, 30, tzinfo=timezone.utc)
SCOPE = "g12-structural-reuse"
TARGET = (
    "La expedición necesita como único medio el puente norte para cruzar el río. "
    "El puente norte quedó inutilizable y carece de ruta alternativa."
)
RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


def _evidence(
    *,
    memory_id: str = "private:7",
    category: str = "stable_knowledge",
    content: str = RULE,
) -> MemoryPlanningEvidence:
    return MemoryPlanningEvidence(
        memory_id=memory_id,
        owner="Carlos",
        scope="private",
        content=content,
        category=category,
        confidence=0.96,
        recall_score=0.91,
        provenance="governed_human_approved_learning",
    )



def _semantic_result(result):
    return (
        result.status,
        result.decision.status,
        result.decision.outcome,
        result.decision.conclusion,
        result.decision.confidence_score,
        result.decision.confidence_rationale,
        result.decision.limitations,
        result.decision.assumptions,
        tuple(
            (
                item.rule_id,
                item.rule_version,
                item.status,
                item.output_claim.fingerprint if item.output_claim else None,
            )
            for item in result.inference_run.results
        ),
    )


def _evaluate(*evidence: MemoryPlanningEvidence):
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = gateway.evaluate_productive_episode(
        owner="Carlos",
        session_id=SCOPE,
        text=TARGET,
        now=NOW,
        turn_id="g12-turn",
        scope_reference=SCOPE,
        observe_productive_intake=False,
        recalled_memory_evidence=tuple(evidence),
    )
    return gateway, episode


def test_g12_applicable_recalled_stable_knowledge_changes_governed_reasoning() -> None:
    _, without_memory = _evaluate()
    _, with_memory = _evaluate(_evidence())

    assert _semantic_result(with_memory.result) != _semantic_result(
        without_memory.result
    )


def test_g12_official_gateway_exposes_same_turn_structural_reuse_reference() -> None:
    gateway, _ = _evaluate(_evidence())

    reference_ids = gateway.productive_recalled_knowledge_reference_ids(
        owner="Carlos",
        session_id=SCOPE,
        turn_id="g12-turn",
    )

    assert reference_ids


def test_g12_user_preference_cannot_change_governed_reasoning() -> None:
    _, without_memory = _evaluate()
    _, with_preference = _evaluate(_evidence(category="user_preference"))

    assert _semantic_result(with_preference.result) == _semantic_result(
        without_memory.result
    )


def test_g12_unstructured_stable_knowledge_cannot_change_governed_reasoning() -> None:
    _, without_memory = _evaluate()
    gateway, with_unstructured = _evaluate(
        _evidence(content="El puente norte es importante para la expedición.")
    )

    assert _semantic_result(with_unstructured.result) == _semantic_result(
        without_memory.result
    )
    assert gateway.productive_recalled_knowledge_reference_ids(
        owner="Carlos",
        session_id=SCOPE,
        turn_id="g12-turn",
    ) == ()


def test_g12_reuses_existing_structural_and_reasoning_authorities() -> None:
    path = ROOT / "app" / "governed_reasoning_runtime.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    classes = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }

    assert "OfficialGovernedReasoningRuntimeGateway" in classes
    assert "RecalledMemoryReasoningGateway" not in classes
    assert "RecalledKnowledgeReasoner" not in classes
    assert "MemoryRuntimeIntegration(" not in source
    assert "CognitiveMemoryRecall(" not in source
    assert "OfficialMemoryGateway(" not in source
    assert "ExternalEvidence" not in source
    assert "GovernedRecalledKnowledgeStructuralProjector" in source
    assert "GovernedTargetProblemStructuralProjector" in source
    assert "GovernedStructuralKnowledgeTransferMatcher" in source
