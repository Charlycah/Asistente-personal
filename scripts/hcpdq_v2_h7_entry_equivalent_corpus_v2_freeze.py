from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuationV1,
)
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityRegistryManager,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
CORPUS = BENCHMARKS / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_CORPUS_V2.json"
CERT = BENCHMARKS / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_CORPUS_V2_CERTIFICATE.json"


def _requirement(case_number: int, *, reused: bool):
    suffix = f"{case_number:03d}"
    requirement_id = (
        f"discrimination-requirement-h7v2-initial-{suffix}"
        if reused
        else f"discrimination-requirement-h7v2-next-{suffix}"
    )
    return {
        "requirement_id": requirement_id,
        "hypothesis_ids": ["h1", "h2"],
        "source_reference": f"hcpdq-v2-h7v2-source-{suffix}",
        "world_snapshot_id": f"hcpdq-v2-h7v2-snapshot-{suffix}",
        "known_elements": [f"held-out-observation-{suffix}"],
        "missing_evidence_descriptions": ["independent registry source"],
        "evidence_codes": ["comparison:indistinguishable"],
    }


def _case(case_number: int, family: str):
    suffix = f"{case_number:03d}"
    new_requirement = _requirement(case_number, reused=family == "D3")
    initial_id = (
        new_requirement["requirement_id"]
        if family == "D3"
        else f"discrimination-requirement-h7v2-initial-{suffix}"
    )
    requirement = None if family == "D2" else new_requirement
    return {
        "case_id": f"V2I-H7V2-{suffix}",
        "scenario": (
            f"Independent H7 v2 held-out case {suffix}; productive state and "
            "requirement are frozen structurally."
        ),
        "pre_continuation_state": {
            "episode_id": f"investigation-episode-h7v2-{suffix}",
            "originating_reasoning_id": f"h7v2-reasoning-{suffix}",
            "source_reference": f"hcpdq-v2-h7v2-source-{suffix}",
            "world_snapshot_id": f"hcpdq-v2-h7v2-snapshot-{suffix}",
            "requirement_ids": [initial_id],
            "plan_ids": [f"h7v2-prior-plan-{suffix}"],
            "authorization_ids": [f"h7v2-prior-auth-{suffix}"],
            "execution_ids": [f"h7v2-prior-execution-{suffix}"],
            "reentry_ids": [f"h7v2-prior-reentry-{suffix}"],
            "consumed_acquisitions": 1,
            "current_step": 1,
            "status": "awaiting_requirement",
            "stopping_reason": "none",
        },
        "requirement": requirement,
        "registry_capabilities": [
            {
                "name": "local.sensor",
                "description": "Local read-only evidence provider.",
                "evidence_outputs": ["independent registry source"],
            }
        ],
    }


def _state(data):
    return GovernedInvestigationEpisodeState(
        episode_id=data["episode_id"],
        originating_reasoning_id=data["originating_reasoning_id"],
        source_reference=data["source_reference"],
        world_snapshot_id=data["world_snapshot_id"],
        requirement_ids=tuple(data["requirement_ids"]),
        plan_ids=tuple(data["plan_ids"]),
        authorization_ids=tuple(data["authorization_ids"]),
        execution_ids=tuple(data["execution_ids"]),
        reentry_ids=tuple(data["reentry_ids"]),
        consumed_acquisitions=data["consumed_acquisitions"],
        current_step=data["current_step"],
        status=GovernedInvestigationEpisodeStatus(data["status"]),
        stopping_reason=GovernedInvestigationStoppingReason(
            data["stopping_reason"]
        ),
    )


def _requirement_object(data):
    if data is None:
        return None
    return DiscriminatingEvidenceRequirement(
        requirement_id=data["requirement_id"],
        hypothesis_ids=tuple(data["hypothesis_ids"]),
        source_reference=data["source_reference"],
        world_snapshot_id=data["world_snapshot_id"],
        known_elements=tuple(data["known_elements"]),
        missing_evidence_descriptions=tuple(
            data["missing_evidence_descriptions"]
        ),
        evidence_codes=tuple(data["evidence_codes"]),
    )


def _registry(items):
    registry = CapabilityRegistryManager()
    for item in items:
        registry.register(
            CapabilityDescriptor(
                name=item["name"],
                description=item["description"],
                evidence_outputs=tuple(item["evidence_outputs"]),
            )
        )
    return registry


def materialize_and_probe(case):
    state = _state(case["pre_continuation_state"])
    requirement = _requirement_object(case["requirement"])
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1()
    product = continuation.consume(state, requirement)
    reentry = GovernedMultiStepInvestigationPlanningReentryV1(
        _registry(case["registry_capabilities"])
    ).consume(product)
    return {
        "case_id": case["case_id"],
        "continuation_decision": product.decision.value,
        "resulting_state_status": product.resulting_state.status.value,
        "current_step": product.current_step,
        "remaining_acquisitions": product.remaining_acquisitions,
        "eligible_for_existing_planning": (
            product.eligible_for_existing_planning
        ),
        "planning_reentry_status": reentry.status.value,
        "planning_invocation_count": reentry.planning_invocation_count,
    }


def build():
    families = ("D1",) * 4 + ("D2",) * 4 + ("D3",) * 4
    cases = [
        _case(number, family)
        for number, family in enumerate(families, start=1)
    ]
    corpus_core = {
        "schema_version": "hcpdq-v2-h7-entry-equivalent-corpus-v2",
        "namespace": "V2I-H7V2",
        "status": "FROZEN_ENTRY_PATH_EQUIVALENT",
        "case_count": 12,
        "cases": cases,
    }
    canonical = json.dumps(
        corpus_core,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    corpus_core["freeze_sha256"] = sha256(canonical.encode()).hexdigest()
    CORPUS.write_text(
        json.dumps(corpus_core, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    observations = [materialize_and_probe(case) for case in cases]
    counts = {}
    for item in observations:
        key = (
            item["continuation_decision"],
            item["planning_reentry_status"],
        )
        counts[key] = counts.get(key, 0) + 1

    certificate = {
        "schema_version": (
            "hcpdq-v2-h7-entry-equivalent-corpus-v2-certificate-v1"
        ),
        "status": "REAL_DRY_PROBE_CERTIFIED_AND_FROZEN",
        "corpus_file": CORPUS.name,
        "corpus_file_sha256": sha256(CORPUS.read_bytes()).hexdigest(),
        "corpus_freeze_sha256": corpus_core["freeze_sha256"],
        "case_count": 12,
        "materialized_productive_type_count": 12,
        "materialization_failures": 0,
        "exact_types_materialized": [
            "GovernedInvestigationEpisodeState",
            "DiscriminatingEvidenceRequirement or None",
            "GovernedMultiStepInvestigationProductiveContinuation",
            "GovernedInvestigationPlanningReentryResult",
        ],
        "dry_probe_method": (
            "reconstruct each frozen case through exact productive "
            "constructors, then invoke productive continuation and planning "
            "re-entry without ground truth"
        ),
        "observed_topology_counts": [
            {
                "continuation_decision": decision,
                "planning_reentry_status": status,
                "count": count,
            }
            for (decision, status), count in sorted(counts.items())
        ],
        "case_level_outputs_persisted": False,
        "ground_truth_created_or_opened": False,
        "scoring_performed": False,
        "roby_learning_or_writeback": False,
        "old_h7_corpus_mutated": False,
        "old_h7_run_mutated": False,
        "execution_authorized": False,
        "next_gate": "HCPDQ-v2 H7 — Preflight + Primary Execution",
    }
    canonical_cert = json.dumps(
        certificate,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    certificate["certificate_fingerprint"] = sha256(
        canonical_cert.encode()
    ).hexdigest()
    CERT.write_text(
        json.dumps(
            certificate,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return corpus_core, certificate, observations


if __name__ == "__main__":
    corpus, certificate, observations = build()
    print(
        json.dumps(
            {
                "freeze_sha256": corpus["freeze_sha256"],
                "certificate_fingerprint": (
                    certificate["certificate_fingerprint"]
                ),
                "observations": observations,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
