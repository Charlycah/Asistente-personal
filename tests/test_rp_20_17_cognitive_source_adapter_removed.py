from pathlib import Path


def test_cognitive_source_adapter_is_removed():
    source = Path("app/cognitive_runtime_sources.py").read_text(encoding="utf-8")
    assert "class CognitiveSourceAdapter" not in source


def test_runtime_root_uses_bound_cognitive_source_methods_directly():
    source = Path("app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert "CognitiveSourceAdapter" not in source
    assert "reasoning_source = CanonicalProductiveReasoningSource(" in source
    assert "governed_reasoning_runtime" in source
    assert "planning_source = cognitive_source.planning" in source
    assert "reflection_source = cognitive_source.reflection" in source
    assert "executive_source = cognitive_source.coordination" in source


def test_cognitive_contributors_call_sources_directly():
    modules = (
        "core/reasoning_runtime_integration.py",
        "core/planning_runtime_integration.py",
        "core/reflection_runtime_integration.py",
        "core/executive_cognitive_runtime.py",
    )
    for module in modules:
        source = Path(module).read_text(encoding="utf-8")
        assert "self.source.resolve(" not in source
        assert "self.source(" in source
