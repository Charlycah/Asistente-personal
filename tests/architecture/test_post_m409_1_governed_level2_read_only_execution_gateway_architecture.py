from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import fields

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ReadOnlyExecutionGatewayV1,
)
from app.official_capability_gateway import OfficialCapabilityGateway
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


def test_level2_execution_reuses_existing_official_gateway_not_new_executor():
    source = inspect.getsource(GovernedLevel2ReadOnlyExecutionGatewayV1)
    assert "OfficialRuntimeCapabilityRegistry" in source
    assert "AutonomousExecutor" not in source
    assert "Level2Executor" not in source
    assert "requests." not in source
    assert "socket." not in source
    assert "subprocess." not in source
    assert "OfficialMemoryGateway" not in source
    assert "OfficialConversationGateway" not in source


def test_official_runtime_delegates_evidence_read_to_single_official_gateway():
    source = inspect.getsource(
        OfficialRuntimeCapabilityRegistry.execute_read_only_evidence_registration
    )
    assert "self.gateway.execute_read_only_evidence" in source
    gateway_source = inspect.getsource(
        OfficialCapabilityGateway.execute_read_only_evidence
    )
    tree = ast.parse(textwrap.dedent(gateway_source))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    reader_calls = [
        node for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "read_evidence"
    ]
    assert len(reader_calls) == 1


def test_evidence_envelope_is_non_recursive_non_persistent_and_not_truth():
    defaults = {
        field.name: field.default for field in fields(GovernedAcquiredEvidenceEnvelope)
    }
    for name in (
        "establishes_truth",
        "persists_results",
        "creates_questions",
        "modifies_memory",
        "modifies_world_model",
        "permits_retry",
        "triggers_reasoning_reentry",
        "starts_background_process",
    ):
        assert defaults[name] is False
    assert defaults["read_only"] is True
    assert defaults["canonical_execution_gateway"] == "OfficialCapabilityGateway"
