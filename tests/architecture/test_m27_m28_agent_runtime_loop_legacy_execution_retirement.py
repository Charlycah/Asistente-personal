from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_agent_runtime_loop_legacy_execution_lineage_remains_retired() -> None:
    retired = (
        "core/agent_runtime.py",
        "core/agent_loop.py",
        "tests/test_m27_agent_runtime.py",
        "tests/test_m28_agent_loop.py",
        "tests/test_m32_agent_llm_integration.py",
        "tests/test_m40_agent_loop_cognitive_integration.py",
    )
    for relative_path in retired:
        assert not (ROOT / relative_path).exists()

    preserved = (
        "core/llm_service.py",
        "core/provider_router.py",
        "core/cognitive_pipeline.py",
        "core/runtime_composition_root/root.py",
    )
    for relative_path in preserved:
        assert (ROOT / relative_path).exists()

    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert "M27/M28 Agent Runtime / Agent Loop Retirement Boundary" in rules

    m395 = (
        ROOT / "tests" / "architecture" / "test_m395_1_neutral_contract_boundaries.py"
    ).read_text(encoding="utf-8")
    assert '"core/agent_loop.py"' not in m395
    assert '"core/agent_runtime.py"' not in m395
