from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ExposurePolicy:
    grants_decision_authority: bool = False
    grants_routing_authority: bool = False
    grants_planning_authority: bool = False
    grants_reasoning_authority: bool = False
    grants_learning_authority: bool = False
    grants_autonomy: bool = False
    allow_memory_writes: bool = False
    allow_learning_writes: bool = False
    allow_goal_task_project_writes: bool = False
    allow_threshold_adaptation: bool = False
    allow_benchmark_state: bool = False
    allow_held_out_construction: bool = False
    allow_human_comparison: bool = False


@dataclass(frozen=True)
class ExposureRequest:
    family: str
    case_id: str
    input_payload: Any


@dataclass(frozen=True)
class ExposureEvidence:
    family: str
    existing_authority: str
    existing_productive_path: str
    authority_participation_evidence: tuple[str, ...]
    status: str
    response_path: str
    degradation_reason: str
    rationale: tuple[str, ...]
    side_effect_evidence: tuple[str, ...]
    latency_ms: float
    measurement_validity: str


@dataclass(frozen=True)
class ExposureRegistration:
    family: str
    calibration_only: bool
    exposure_certified: bool
    held_out_authorized: bool
    reuse_existing_certification: bool
    new_exposure_required: bool


@dataclass(frozen=True)
class FamilyExclusion:
    family: str
    reason: str
    classification: str = "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2"
    held_out_authorized: bool = False
    capability_absent: bool = False


_EXPOSURE_REGISTRY: dict[str, ExposureRegistration] = {
    family: ExposureRegistration(
        family=family,
        calibration_only=True,
        exposure_certified=False,
        held_out_authorized=False,
        reuse_existing_certification=False,
        new_exposure_required=True,
    )
    for family in ("H1", "H2", "H3", "H4", "H5", "H7", "H8")
}
_EXPOSURE_REGISTRY["H6"] = ExposureRegistration(
    family="H6",
    calibration_only=True,
    exposure_certified=True,
    held_out_authorized=False,
    reuse_existing_certification=True,
    new_exposure_required=False,
)


def default_exposure_policy() -> ExposurePolicy:
    return ExposurePolicy()


def default_exposure_registry() -> dict[str, ExposureRegistration]:
    return dict(_EXPOSURE_REGISTRY)


def exposure_for_family(family: str) -> ExposureRegistration:
    normalized = family.strip().upper()
    try:
        return _EXPOSURE_REGISTRY[normalized]
    except KeyError as exc:
        raise ValueError(f"unsupported HCPDQ family: {family}") from exc


def authority_exposure_certified(evidence: ExposureEvidence) -> bool:
    return bool(
        evidence.existing_authority.strip()
        and evidence.existing_productive_path.strip()
        and evidence.authority_participation_evidence
        and evidence.status.strip().casefold() in {"completed", "partial"}
        and evidence.measurement_validity.strip().casefold() == "valid"
    )


def shadow_equivalent(
    *,
    production_result: Any,
    observed_result: Any,
) -> bool:
    return production_result == observed_result


def exclude_unmeasurable_family(
    *,
    family: str,
    reason: str,
) -> FamilyExclusion:
    normalized = family.strip().upper()
    if not normalized:
        raise ValueError("family must not be empty")
    if not reason.strip():
        raise ValueError("reason must not be empty")
    return FamilyExclusion(family=normalized, reason=reason)


def held_out_authorized(
    coverage: Mapping[str, bool],
) -> bool:
    return bool(coverage) and all(coverage.values())
