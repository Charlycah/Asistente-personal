from __future__ import annotations

import ast
import inspect
from datetime import datetime, timezone
from pathlib import Path

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.llm_provider import LLMRequest
from core.memory_planning_evidence import (
    METADATA_KEY,
    MemoryPlanningEvidence,
    encode_memory_planning_evidence,
)
from core.reasoning_runtime_integration import ReasoningRuntimeContributor

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 6, 1, 30, tzinfo=timezone.utc)


class _SourceSpy:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return None


def _memory_evidence(*, category: str) -> MemoryPlanningEvidence:
    return MemoryPlanningEvidence(
        memory_id="private:7",
        owner="Carlos",
        scope="private",
        content=(
            "Si un recurso exclusivo falla y no existe alternativa, "
            "la capacidad dependiente queda indisponible."
        ),
        category=category,
        confidence=0.96,
        recall_score=0.91,
        provenance="governed_human_approved_learning",
    )


def _request(*items: MemoryPlanningEvidence) -> LLMRequest:
    metadata: dict[str, str] = {}
    if items:
        metadata[METADATA_KEY] = encode_memory_planning_evidence(tuple(items))
    return LLMRequest(prompt="Analizá la dependencia del sistema", metadata=metadata)


def test_g11_reasoning_contributor_forwards_recalled_stable_knowledge_only() -> None:
    spy = _SourceSpy()
    contributor = ReasoningRuntimeContributor(spy)
    stable = _memory_evidence(category="stable_knowledge")

    contributor.contribute(
        owner="Carlos",
        session_id="g11-session",
        text="Analizá la dependencia del sistema",
        request=_request(stable),
        now=NOW,
    )

    assert len(spy.calls) == 1
    assert spy.calls[0]["recalled_memory_evidence"] == (stable,)


def test_g11_reasoning_contributor_does_not_promote_preferences_to_reasoning() -> None:
    spy = _SourceSpy()
    contributor = ReasoningRuntimeContributor(spy)
    preference = _memory_evidence(category="user_preference")

    contributor.contribute(
        owner="Carlos",
        session_id="g11-session",
        text="Analizá la dependencia del sistema",
        request=_request(preference),
        now=NOW,
    )

    assert len(spy.calls) == 1
    assert spy.calls[0]["recalled_memory_evidence"] == ()


def test_g11_canonical_source_exposes_explicit_recalled_memory_seam() -> None:
    signature = inspect.signature(CanonicalProductiveReasoningSource.__call__)

    parameter = signature.parameters["recalled_memory_evidence"]
    assert parameter.default == ()
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_g11_existing_official_gateway_exposes_same_recalled_memory_seam() -> None:
    signature = inspect.signature(
        OfficialGovernedReasoningRuntimeGateway.evaluate_productive_episode
    )

    parameter = signature.parameters["recalled_memory_evidence"]
    assert parameter.default == ()
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_g11_reuses_existing_memory_selection_and_reasoning_authorities() -> None:
    contributor_path = ROOT / "core" / "reasoning_runtime_integration.py"
    source_path = ROOT / "app" / "governed_reasoning_runtime.py"
    contributor_source = contributor_path.read_text(encoding="utf-8")
    source = source_path.read_text(encoding="utf-8")
    contributor_tree = ast.parse(contributor_source)
    source_tree = ast.parse(source)

    classes = {
        node.name
        for tree in (contributor_tree, source_tree)
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }
    assert "ReasoningRuntimeContributor" in classes
    assert "CanonicalProductiveReasoningSource" in classes
    assert "OfficialGovernedReasoningRuntimeGateway" in classes
    assert "RecalledMemoryReasoningGateway" not in classes
    assert "SourceNeutralReasoningGateway" not in classes
    assert "MemoryRuntimeIntegration(" not in contributor_source
    assert "CognitiveMemoryRecall(" not in contributor_source
    assert "OfficialMemoryGateway(" not in contributor_source
    assert "ExternalEvidence" not in contributor_source
