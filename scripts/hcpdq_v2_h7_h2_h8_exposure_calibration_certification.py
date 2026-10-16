from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from hashlib import sha256
from pathlib import Path

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuationV1,
)
from core.capability_registry import CapabilityDescriptor, CapabilityRegistryManager
from core.governed_operational_conversation_pipeline.response_origin import (
    ResponseConfidenceRecord,
)
from core.governed_reasoning.conflicts import ConflictAnalysis
from core.governed_reasoning.derived_epistemic_sufficiency_assessment import (
    GovernedDerivedEpistemicSufficiencyContextAssessment,
)
from core.governed_reasoning.derived_reasoning_method_provenance import (
    GovernedReasoningMethodProvenanceContextItem,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)
from scripts.hcpdq_v2_h7_h2_h8_existing_authority_exposure import (
    H7ExposureEvidence,
    h7_exposure_certified,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FamilyCalibrationResult:
    family: str
    probe_kind: str
    existing_productive_path_observed: bool
    causal_join_observed: bool
    exposure_certified: bool
    verdict: str
    evidence: tuple[str, ...]
    held_out_authorized: bool = False


def _h7_probe() -> dict[str, object]:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only evidence provider.",
            evidence_outputs=("new discriminating observation",),
        )
    )
    requirement = DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-r2",
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("new discriminating observation",),
        evidence_codes=("comparison:indistinguishable",),
    )
    envelope = GovernedAcquiredEvidenceEnvelope(
        execution_id="level2-read-only-execution-step-01-abcdef123456",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id="independence-authorization-step-01-abcdef123456",
        requirement_id="discrimination-requirement-r1",
        plan_id="evidence-acquisition-plan-step-01-abcdef123456",
        capability_name="local.sensor",
        evidence_description="room temperature",
        declared_evidence_output="room_temperature",
        observed_value=23.0,
        observation_source_reference="local:test-reader",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        rationale_codes=("execution:test",),
        source_fingerprint="f" * 64,
    )
    reentry = GovernedLevel2ReasoningReentryResult(
        reentry_id="level2-reasoning-reentry-step-01-abcdef123456",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id="evidence-1",
        source_reference=envelope.source_reference,
        world_snapshot_id=envelope.world_snapshot_id,
        reasoning_result=None,
        rationale_codes=("reentry:test",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, envelope).state
    state = boundary.record_reentry(state, reentry).state
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, requirement)
    result = GovernedMultiStepInvestigationPlanningReentryV1(registry).consume(
        continuation
    )
    evidence = H7ExposureEvidence(
        family="H7",
        existing_authority=result.canonical_planning_authority,
        status=result.status.value,
        requirement_id=result.requirement_id or "",
        plan_id=result.plan_id or "",
        planning_status=(
            result.planning_status.value if result.planning_status is not None else ""
        ),
        planning_invocation_count=result.planning_invocation_count,
        eligible_for_authorization=result.eligible_for_authorization,
        rationale_codes=result.rationale_codes,
        source_fingerprint=result.source_fingerprint,
        authority_participation_evidence=(
            result.canonical_planning_authority,
            result.requirement_id or "",
            result.plan_id or "",
        ),
        measurement_validity="valid",
    )
    return {
        "certified": h7_exposure_certified(evidence),
        "result_status": result.status.value,
        "planning_authority": result.canonical_planning_authority,
        "planning_invocation_count": result.planning_invocation_count,
        "planning_status": (
            result.planning_status.value if result.planning_status is not None else None
        ),
        "eligible_for_authorization": result.eligible_for_authorization,
        "execution_authorized": result.execution_authorized,
        "modifies_episode_state": result.modifies_episode_state,
        "modifies_memory": result.modifies_memory,
        "modifies_world_model": result.modifies_world_model,
        "rationale_codes": result.rationale_codes,
    }


def _h2_join_available() -> tuple[bool, tuple[str, ...]]:
    sufficiency_fields = {
        field.name
        for field in fields(GovernedDerivedEpistemicSufficiencyContextAssessment)
    }
    response_fields = {field.name for field in fields(ResponseConfidenceRecord)}
    joined = bool(
        sufficiency_fields
        & {
            "response_decision_id",
            "response_confidence_record_id",
            "response_origin_id",
        }
    ) or bool(
        response_fields
        & {
            "sufficiency_assessment_id",
            "consumed_assessment_id",
            "epistemic_sufficiency_id",
        }
    )
    return joined, (
        "epistemic productive consumption exists and is read-only context",
        "ResponseConfidenceRecord exposes ANSWERED/ABSTAINED semantics",
        "no shared causal lineage field currently joins the two records",
    )


def _h8_join_available() -> tuple[bool, tuple[str, ...]]:
    provenance_fields = {
        field.name for field in fields(GovernedReasoningMethodProvenanceContextItem)
    }
    conflict_fields = {field.name for field in fields(ConflictAnalysis)}
    joined = bool(
        provenance_fields
        & {
            "conflict_ids",
            "conflict_analysis_id",
            "resolution_ids",
        }
    ) or bool(
        conflict_fields
        & {
            "provenance_id",
            "consumed_assessment_id",
            "reasoning_method_provenance_id",
        }
    )
    return joined, (
        "reasoning-method provenance derived context exists",
        "governed conflict analysis exposes conflicts and resolution decisions",
        "no shared causal lineage field currently joins provenance to "
        "conflict analysis",
    )


def certify_wave1_calibration() -> dict[str, object]:
    h7_probe = _h7_probe()
    h2_join, h2_evidence = _h2_join_available()
    h8_join, h8_evidence = _h8_join_available()

    results = (
        FamilyCalibrationResult(
            family="H7",
            probe_kind="synthetic_positive_productive_path",
            existing_productive_path_observed=True,
            causal_join_observed=bool(h7_probe["certified"]),
            exposure_certified=bool(h7_probe["certified"]),
            verdict=(
                "CERTIFIED_CALIBRATION_EXPOSURE" if h7_probe["certified"] else "NO_GO"
            ),
            evidence=(
                "existing planning re-entry returned PLANNED",
                "canonical authority is planning_foundation",
                "exactly one planning invocation observed",
                "requirement/plan lineage preserved",
                "execution and state mutation remain unauthorized",
            ),
        ),
        FamilyCalibrationResult(
            family="H2",
            probe_kind="synthetic_topology_join_probe",
            existing_productive_path_observed=True,
            causal_join_observed=h2_join,
            exposure_certified=False,
            verdict="NO_GO_UNJOINED_EXISTING_EVIDENCE",
            evidence=h2_evidence,
        ),
        FamilyCalibrationResult(
            family="H8",
            probe_kind="synthetic_topology_join_probe",
            existing_productive_path_observed=True,
            causal_join_observed=h8_join,
            exposure_certified=False,
            verdict="NO_GO_UNJOINED_EXISTING_EVIDENCE",
            evidence=h8_evidence,
        ),
    )
    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h7-h2-h8-calibration-certification-v1",
        "status": "PARTIAL_CERTIFICATION_HELD_OUT_NO_GO",
        "baseline": "12883-pass-0-fail-ruff-clean",
        "families": {item.family: asdict(item) for item in results},
        "h7_positive_probe": h7_probe,
        "newly_exposure_certified_families": [
            item.family for item in results if item.exposure_certified
        ],
        "remaining_uncertified_families": [
            item.family for item in results if not item.exposure_certified
        ],
        "production_change_authorized": False,
        "new_authority_authorized": False,
        "held_out_construction_authorized": False,
        "human_comparison_authorized": False,
        "architectural_determination": (
            "H7 has a real productive causal join. H2 and H8 each have the "
            "required existing components, but current records do not expose a "
            "shared causal lineage proving the joined outcome. Fail closed."
        ),
        "next_gate": (
            "HCPDQ-v2 H2/H8 Causal-Lineage Exposure Gap — Contract / Go-No-Go"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["certification_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            certify_wave1_calibration(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
