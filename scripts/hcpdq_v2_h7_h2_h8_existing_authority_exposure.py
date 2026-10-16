from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

_NOT_VALIDLY_MEASURABLE = "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2"


@dataclass(frozen=True)
class Wave1ExposurePolicy:
    allow_plan_execution: bool = False
    allow_planner_binding: bool = False
    allow_new_planning_authority: bool = False
    allow_response_decision: bool = False
    allow_stopping_decision: bool = False
    allow_epistemic_threshold_change: bool = False
    allow_source_ranking: bool = False
    allow_claim_selection: bool = False
    allow_conflict_policy_change: bool = False
    allow_held_out_construction: bool = False
    allow_human_comparison: bool = False
    allow_persistence_or_adaptation: bool = False
    allow_new_authority: bool = False


@dataclass(frozen=True)
class H7ExposureEvidence:
    family: str
    existing_authority: str
    status: str
    requirement_id: str
    plan_id: str
    planning_status: str
    planning_invocation_count: int
    eligible_for_authorization: bool
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    authority_participation_evidence: tuple[str, ...]
    measurement_validity: str


@dataclass(frozen=True)
class H2ExposureEvidence:
    family: str
    sufficiency_assessment_id: str
    consumed_assessment_id: str
    derived_context_available: bool
    response_decision: str
    response_confidence: str
    verification_state: str
    reason_code: str
    causal_join_evidence: tuple[str, ...]
    measurement_validity: str


@dataclass(frozen=True)
class H8ExposureEvidence:
    family: str
    provenance_id: str
    consumed_assessment_id: str
    conflict_ids: tuple[str, ...]
    resolution_statuses: tuple[str, ...]
    selected_claim_ids: tuple[str, ...]
    requires_review: bool
    confidence: float
    authority_participation_evidence: tuple[str, ...]
    measurement_validity: str


_EXPOSURE_KINDS = {
    "H7": "existing_planning_reentry",
    "H2": "epistemic_response_decision_join",
    "H8": "provenance_conflict_resolution_join",
}


def default_wave1_exposure_policy() -> Wave1ExposurePolicy:
    return Wave1ExposurePolicy()


def exposure_kind_for_family(family: str) -> str:
    normalized = family.strip().upper()
    try:
        return _EXPOSURE_KINDS[normalized]
    except KeyError as exc:
        raise ValueError(f"unsupported HCPDQ-v2 wave-1 family: {family}") from exc


def h7_exposure_certified(evidence: H7ExposureEvidence) -> bool:
    participation = set(evidence.authority_participation_evidence)
    return bool(
        evidence.family.strip().upper() == "H7"
        and evidence.existing_authority == "planning_foundation"
        and evidence.status.strip().casefold() == "planned"
        and evidence.requirement_id
        and evidence.plan_id
        and evidence.planning_invocation_count == 1
        and evidence.requirement_id in participation
        and evidence.plan_id in participation
        and evidence.existing_authority in participation
        and evidence.rationale_codes
        and evidence.source_fingerprint
        and evidence.measurement_validity.strip().casefold() == "valid"
    )


def h2_exposure_certified(evidence: H2ExposureEvidence) -> bool:
    joined = tuple(item for item in evidence.causal_join_evidence if item)
    return bool(
        evidence.family.strip().upper() == "H2"
        and evidence.sufficiency_assessment_id
        and evidence.consumed_assessment_id
        and evidence.derived_context_available
        and evidence.response_decision.strip().casefold() in {"answered", "abstained"}
        and evidence.response_confidence
        and evidence.verification_state
        and evidence.reason_code
        and len(joined) >= 2
        and evidence.sufficiency_assessment_id in joined
        and evidence.measurement_validity.strip().casefold() == "valid"
    )


def h8_exposure_certified(evidence: H8ExposureEvidence) -> bool:
    statuses = tuple(item.strip().casefold() for item in evidence.resolution_statuses)
    participation = set(evidence.authority_participation_evidence)
    return bool(
        evidence.family.strip().upper() == "H8"
        and evidence.provenance_id
        and evidence.consumed_assessment_id
        and evidence.conflict_ids
        and len(evidence.conflict_ids) == len(statuses)
        and any(status == "resolved" for status in statuses)
        and evidence.selected_claim_ids
        and "governed_reasoning" in participation
        and any(conflict_id in participation for conflict_id in evidence.conflict_ids)
        and evidence.measurement_validity.strip().casefold() == "valid"
    )


def measurement_failure_classification(
    *,
    causal_join_present: bool,
    degraded: bool,
) -> str:
    if not causal_join_present or degraded:
        return _NOT_VALIDLY_MEASURABLE
    return "MEASUREMENT_EVIDENCE_PRESENT"


def held_out_authorized(coverage: Mapping[str, bool]) -> bool:
    return bool(coverage) and all(coverage.values())
