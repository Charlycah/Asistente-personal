from __future__ import annotations

from core.cognitive_memory_integration import CognitiveMemoryIntegrationResult
from core.cognitive_pipeline import CognitivePipelineResult


def test_pipeline_result_does_not_repeat_nested_result_fields() -> None:
    assert not hasattr(CognitivePipelineResult, "intent")
    assert not hasattr(CognitivePipelineResult, "used_memory")
    assert not hasattr(CognitivePipelineResult, "learned_something")


def test_memory_integration_result_does_not_repeat_recall_field() -> None:
    assert not hasattr(CognitiveMemoryIntegrationResult, "used_memory")


def test_derived_result_queries_remain_available() -> None:
    assert hasattr(CognitivePipelineResult, "called_llm")
    assert hasattr(CognitiveMemoryIntegrationResult, "learned_something")
