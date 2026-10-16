from __future__ import annotations

import importlib
import inspect

import pytest

ADAPTER_MODULE = "app.hcpdq_v2_h6_entry_path_isolation_adapter"


def _adapter_module():
    try:
        return importlib.import_module(ADAPTER_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED_CAUSE: missing HCPDQ-v2 H6 entry-path isolation adapter",
            pytrace=False,
        )


def test_red_requires_minimal_case_id_and_prompt_subject_boundary():
    module = _adapter_module()
    adapter = module.HCPDQV2H6EntryPathIsolationAdapter()
    request = adapter.build_subject_request("V2E-H6-001", "frozen prompt")
    assert set(request) == {"case_id", "prompt"}
    assert request["prompt"] == "frozen prompt"


def test_red_rejects_ground_truth_and_scoring_material():
    module = _adapter_module()
    adapter = module.HCPDQV2H6EntryPathIsolationAdapter()
    contaminated = {
        "case_id": "V2E-H6-001",
        "prompt": "frozen prompt",
        "expected_decision": "forbidden",
    }
    with pytest.raises(module.IsolationBoundaryViolation):
        adapter.validate_subject_request(contaminated)


def test_red_adapter_surface_has_no_ground_truth_or_scoring_parameters():
    module = _adapter_module()
    signature = inspect.signature(module.HCPDQV2H6EntryPathIsolationAdapter)
    forbidden = {"ground_truth", "expected", "score", "rubric"}
    assert forbidden.isdisjoint(signature.parameters)


def test_red_requires_fresh_context_with_no_prior_case_visibility():
    module = _adapter_module()
    adapter = module.HCPDQV2H6EntryPathIsolationAdapter()
    first = adapter.open_case("V2E-H6-001", "first")
    adapter.capture_raw(first, "raw one")
    second = adapter.open_case("V2E-H6-002", "second")
    assert first is not second
    assert adapter.visible_prior_results(second) == ()


def test_red_requires_exactly_one_attempt_and_no_retry_surface():
    module = _adapter_module()
    adapter = module.HCPDQV2H6EntryPathIsolationAdapter()
    handle = adapter.open_case("V2E-H6-001", "frozen prompt")
    adapter.mark_attempt(handle)
    with pytest.raises(module.RetryNotAuthorized):
        adapter.mark_attempt(handle)


def test_red_requires_immutable_unscored_raw_capture():
    module = _adapter_module()
    adapter = module.HCPDQV2H6EntryPathIsolationAdapter()
    handle = adapter.open_case("V2E-H6-001", "frozen prompt")
    captured = adapter.capture_raw(handle, "raw result")
    assert getattr(captured, "__dataclass_params__").frozen is True
    assert not hasattr(captured, "score")
    assert not hasattr(captured, "expected_decision")


def test_red_blocks_learning_memory_feedback_and_persistent_writes():
    module = _adapter_module()
    adapter = module.HCPDQV2H6EntryPathIsolationAdapter()
    capabilities = adapter.authorized_capabilities()
    assert capabilities["learning_write"] is False
    assert capabilities["memory_write"] is False
    assert capabilities["benchmark_feedback"] is False
    assert capabilities["persistent_state_write"] is False


def test_red_requires_existing_official_conversation_entry_path_only():
    module = _adapter_module()
    source = inspect.getsource(module)
    assert "OfficialConversationGateway" in source
    assert "CanonicalDecisionFacade(" not in source
    assert "CognitivePlanner(" not in source
    assert "expected_decision" not in source


def test_red_keeps_primary_execution_blocked_before_authorization():
    module = _adapter_module()
    adapter = module.HCPDQV2H6EntryPathIsolationAdapter()
    with pytest.raises(module.PrimaryExecutionNotAuthorized):
        adapter.execute_primary_run()
