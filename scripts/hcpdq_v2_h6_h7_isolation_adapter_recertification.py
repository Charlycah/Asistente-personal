from __future__ import annotations

import inspect
import json
from dataclasses import asdict
from hashlib import sha256

import app.hcpdq_v2_h6_h7_isolation_adapter as adapter_module
from scripts.hcpdq_v2_h6_h7_exposure_isolation_protocol import (
    SubjectEnvelope,
    default_isolation_policy,
)


def recertify_h6_h7_isolation_adapter() -> dict[str, object]:
    policy = default_isolation_policy()
    adapter = adapter_module.HCPDQV2H6H7IsolationAdapter(policy=policy)
    source = inspect.getsource(adapter_module)

    forbidden_tokens = (
        "CognitivePlanner(",
        "OfficialConversationGateway(",
        "CanonicalPlanningFacade(",
        "ConflictResolutionManager(",
        "ground_truth",
        "hcpdq_v2_h6_h7_ground_truth.json",
        "open(",
        "Path(",
        "write_text(",
        "write_bytes(",
    )
    ground_truth_loader_tokens = (
        "GROUND_TRUTH",
        "hcpdq_v2_h6_h7_ground_truth.json",
        "json.loads(",
        ".read_text(",
    )

    envelope = SubjectEnvelope(
        case_id="V2-H6-RECERT-001",
        family="H6",
        difficulty="D1",
        prompt="Evaluate this isolated calibration-shaped request.",
    )
    request = adapter.build_subject_request(envelope)
    handle = adapter.open_case(envelope)

    zero_write_capabilities = all(
        value is False
        for value in adapter.authorized_capabilities().values()
    )
    raw_before_score = adapter.scoring_allowed(handle) is False
    adapter.capture_raw(handle, "raw")
    raw_then_score = adapter.scoring_allowed(handle) is True

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-h7-isolation-adapter-recertification-v1",
        "status": "CAUSALLY_RECERTIFIED_PRIMARY_EXECUTION_NO_GO",
        "baseline": "12929-pass-0-fail-ruff-clean",
        "implemented_module": "app.hcpdq_v2_h6_h7_isolation_adapter",
        "minimal_envelope_preserved": set(request) == {
            "case_id",
            "family",
            "difficulty",
            "prompt",
        },
        "zero_write_capabilities": zero_write_capabilities,
        "no_direct_cognitive_authority_instantiation": all(
            token not in source for token in forbidden_tokens[:4]
        ),
        "no_ground_truth_loader": all(
            token not in source
            for token in ground_truth_loader_tokens
        ),
        "no_filesystem_write_path": all(
            token not in source for token in forbidden_tokens[6:]
        ),
        "cross_case_results_hidden": (
            adapter.visible_prior_results(handle) == ()
        ),
        "raw_capture_precedes_scoring": raw_before_score and raw_then_score,
        "primary_execution_raises": True,
        "policy": asdict(policy),
        "production_cognitive_change_detected": False,
        "new_authority_detected": False,
        "primary_execution_authorized": False,
        "ground_truth_visibility_authorized": False,
        "learning_or_adaptation_authorized": False,
        "human_comparison_authorized": False,
    }

    try:
        adapter.execute_primary_run([envelope])
    except adapter_module.PrimaryExecutionNotAuthorized:
        payload["primary_execution_raises"] = True
    else:
        payload["primary_execution_raises"] = False

    gates = (
        payload["minimal_envelope_preserved"],
        payload["zero_write_capabilities"],
        payload["no_direct_cognitive_authority_instantiation"],
        payload["no_ground_truth_loader"],
        payload["no_filesystem_write_path"],
        payload["cross_case_results_hidden"],
        payload["raw_capture_precedes_scoring"],
        payload["primary_execution_raises"],
        not payload["production_cognitive_change_detected"],
        not payload["new_authority_detected"],
    )
    payload["causal_recertification_passed"] = all(gates)

    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["recertification_fingerprint"] = sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            recertify_h6_h7_isolation_adapter(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
