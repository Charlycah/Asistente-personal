from __future__ import annotations

import ast
import inspect

import pytest

from app.hcpdq_v2_h6_entry_path_isolation_adapter import (
    HCPDQV2H6EntryPathIsolationAdapter,
    PrimaryExecutionNotAuthorized,
)


def _source_tree():
    source = inspect.getsource(
        __import__(
            "app.hcpdq_v2_h6_entry_path_isolation_adapter",
            fromlist=["*"],
        )
    )
    return source, ast.parse(source)


def test_adapter_reuses_official_gateway_without_parallel_authority():
    source, tree = _source_tree()
    assert "OfficialConversationGateway" in source
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "OfficialConversationGateway" in calls
    assert "CanonicalDecisionFacade" not in calls
    assert "CognitivePlanner" not in calls


def test_adapter_has_no_benchmark_file_or_scoring_dependency():
    source, tree = _source_tree()
    assert "ground_truth.json" not in source
    assert "held_out_cases.json" not in source
    functions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not any("score" in name.lower() for name in functions)


def test_adapter_has_no_persistent_write_api():
    _, tree = _source_tree()
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "write_text" not in calls
    assert "write_bytes" not in calls
    assert "dump" not in calls


def test_adapter_remains_fail_closed_for_primary_execution():
    adapter = HCPDQV2H6EntryPathIsolationAdapter()
    with pytest.raises(PrimaryExecutionNotAuthorized):
        adapter.execute_primary_run()


def test_adapter_capabilities_remain_read_only():
    capabilities = HCPDQV2H6EntryPathIsolationAdapter().authorized_capabilities()
    assert capabilities == {
        "learning_write": False,
        "memory_write": False,
        "benchmark_feedback": False,
        "persistent_state_write": False,
    }
