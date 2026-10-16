from __future__ import annotations

from datetime import datetime, timezone

from app.cognitive_runtime_sources import OperationalCognitiveSource
from app.runtime_root_factory import build_runtime_root
from core.cognitive_runtime_orchestration import CognitiveRuntimeStageStatus
from core.llm_provider import LLMRequest

NOW = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


def test_normal_conversation_does_not_activate_cognitive_sources():
    source = OperationalCognitiveSource()
    kwargs = dict(owner="Carlos", session_id="main", text="Hola", now=NOW)
    assert source.reasoning(**kwargs) is None
    assert source.planning(**kwargs) is None
    assert source.reflection(**kwargs) is None
    assert source.coordination(**kwargs) is None


def test_explicit_cognitive_request_builds_only_relevant_advisory_artifact():
    source = OperationalCognitiveSource()
    kwargs = dict(
        owner="Carlos",
        session_id="main",
        text="Analizá cognitivamente este problema",
        now=NOW,
    )
    assert source.reasoning(**kwargs) is not None
    assert source.planning(**kwargs) is None
    assert source.reflection(**kwargs) is None
    assert source.coordination(**kwargs) is None


def test_official_runtime_registers_cognitive_capability(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    names = tuple(item.name for item in registry.interface_snapshot())
    assert "cognitive.guided_analysis" in names


def test_official_runtime_connects_governed_cognitive_contributors(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    composition = build_runtime_root().compose()
    runtime = composition.preparation.dependencies.cognitive_runtime
    assert tuple(item.name for item in runtime.contributors) == (
        "adaptive_conversation_intelligence",
        "conversational_repair_intelligence",
        "conversational_grounding_intelligence",
        "conversational_commitment_intelligence",
        "adaptive_conversation_operational_consolidation",
        "living_conversation",
        "reasoning",
        "planning",
        "reflection",
        "executive",
        "local_library_evidence",
        "visual_context",
    )


def test_cognitive_orchestrator_enriches_explicit_request(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    composition = build_runtime_root().compose()
    runtime = composition.preparation.dependencies.cognitive_runtime
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Analizá cognitivamente este problema",
        request=LLMRequest(prompt="Analizá cognitivamente este problema"),
        now=NOW,
    )
    assert result.activated_stages == (
        "adaptive_conversation_intelligence",
        "conversational_repair_intelligence",
        "conversational_grounding_intelligence",
        "conversational_commitment_intelligence",
        "adaptive_conversation_operational_consolidation",
        "reasoning",
    )
    assert result.contributions[5].status is CognitiveRuntimeStageStatus.SKIPPED
    assert all(
        result.contributions[index].status is CognitiveRuntimeStageStatus.SKIPPED
        for index in (7, 8, 9)
    )
    assert "Contexto cognitivo gobernado" in result.request.prompt
