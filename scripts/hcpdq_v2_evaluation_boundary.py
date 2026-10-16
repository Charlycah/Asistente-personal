from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from enum import StrEnum
from time import perf_counter
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class EvaluationTimeout(TimeoutError):
    """Raised when an evaluation call exceeds its mechanically enforced deadline."""


class MeasurementValidity(StrEnum):
    VALID = "valid"
    WITHHELD = "withheld"
    FAILED = "failed"
    DEGRADED = "degraded"
    INVALID_ROUTE = "invalid_route"
    TIMEOUT = "timeout"
    INFRASTRUCTURE_ERROR = "infrastructure_error"
    UNCLASSIFIABLE = "unclassifiable"


@dataclass(frozen=True)
class AuthorityPathEvidence:
    participated_node_ids: tuple[str, ...]
    first_interruption_node_id: str | None
    evidence_fingerprint: str
    read_only: bool = True
    grants_authority: bool = False


@dataclass(frozen=True)
class ObservableTurn:
    case_id: str
    family: str
    raw_response: str | None
    turn_status: str
    response_path: str
    degradation_reason: str
    rationale: tuple[str, ...]
    provider_call_performed: bool
    retrieval_performed: bool
    network_access_performed: bool
    latency_ms: float
    authority_path_evidence: AuthorityPathEvidence | None
    authority_violation: bool
    unauthorized_side_effect: bool
    infrastructure_error: str | None
    timeout: bool


@dataclass(frozen=True)
class FamilyPathCoverage:
    family: str
    audit_state: str
    existing_interface: str
    requires_calibration: bool = True
    held_out_authorized: bool = False


@dataclass(frozen=True)
class ObservabilityPolicy:
    allow_memory_writes: bool = False
    allow_learning_writes: bool = False
    allow_threshold_adaptation: bool = False
    allow_self_improvement: bool = False
    allow_benchmark_semantic_routing: bool = False
    allow_held_out_construction: bool = False
    allow_human_comparison: bool = False
    calibration_only: bool = True


_FAMILY_PATHS: dict[str, FamilyPathCoverage] = {
    "H1": FamilyPathCoverage(
        family="H1",
        audit_state="P1",
        existing_interface="existing_reasoning_path_unresolved_for_calibration",
    ),
    "H2": FamilyPathCoverage(
        family="H2",
        audit_state="P2",
        existing_interface="OfficialConversationGateway",
    ),
    "H3": FamilyPathCoverage(
        family="H3",
        audit_state="P1",
        existing_interface="existing_contextual_reasoning_path_unresolved",
    ),
    "H4": FamilyPathCoverage(
        family="H4",
        audit_state="P1",
        existing_interface="existing_structural_transfer_path_unresolved",
    ),
    "H5": FamilyPathCoverage(
        family="H5",
        audit_state="P1",
        existing_interface="existing_generalization_path_unresolved",
    ),
    "H6": FamilyPathCoverage(
        family="H6",
        audit_state="P3",
        existing_interface="OfficialConversationGateway",
    ),
    "H7": FamilyPathCoverage(
        family="H7",
        audit_state="P2",
        existing_interface="CanonicalPlanningFacade(existing authority)",
    ),
    "H8": FamilyPathCoverage(
        family="H8",
        audit_state="P2",
        existing_interface="OfficialConversationGateway",
    ),
}


def default_observability_policy() -> ObservabilityPolicy:
    return ObservabilityPolicy()


def default_family_path_coverage() -> dict[str, FamilyPathCoverage]:
    return dict(_FAMILY_PATHS)


def interface_for_family(family: str) -> FamilyPathCoverage:
    normalized = family.strip().upper()
    try:
        return _FAMILY_PATHS[normalized]
    except KeyError as exc:
        raise ValueError(f"unsupported HCPDQ family: {family}") from exc


def _text_value(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    candidate = getattr(value, "value", value)
    return str(candidate)


def _authority_path_evidence(gateway: Any) -> AuthorityPathEvidence | None:
    snapshot = getattr(gateway, "cognitive_turn_dossiers", None)
    dossier = getattr(snapshot, "latest_dossier", None)
    if dossier is None:
        return None
    return AuthorityPathEvidence(
        participated_node_ids=tuple(
            str(item) for item in getattr(dossier, "participated_node_ids", ())
        ),
        first_interruption_node_id=getattr(
            dossier,
            "first_interruption_node_id",
            None,
        ),
        evidence_fingerprint=str(getattr(dossier, "evidence_fingerprint", "")),
    )


def capture_observable_turn(
    *,
    case_id: str,
    family: str,
    gateway: Any,
    prompt: str,
) -> ObservableTurn:
    """Capture existing turn evidence without adding cognitive authority."""
    started = perf_counter()
    turn = gateway.converse(prompt)
    latency_ms = (perf_counter() - started) * 1000.0
    return ObservableTurn(
        case_id=case_id,
        family=family,
        raw_response=getattr(turn, "response_text", None),
        turn_status=_text_value(getattr(turn, "status", None), "unknown"),
        response_path=_text_value(
            getattr(turn, "response_path", None),
            "unknown",
        ),
        degradation_reason=_text_value(
            getattr(turn, "degradation_reason", None),
            "unknown",
        ),
        rationale=tuple(str(item) for item in getattr(turn, "rationale", ())),
        provider_call_performed=bool(getattr(turn, "provider_call_performed", False)),
        retrieval_performed=bool(getattr(turn, "retrieval_performed", False)),
        network_access_performed=bool(getattr(turn, "network_access_performed", False)),
        latency_ms=latency_ms,
        authority_path_evidence=_authority_path_evidence(gateway),
        authority_violation=False,
        unauthorized_side_effect=False,
        infrastructure_error=None,
        timeout=False,
    )


def classify_measurement_validity(
    observation: ObservableTurn,
) -> MeasurementValidity:
    """Decide whether an observation is interpretable before cognitive scoring."""
    if observation.infrastructure_error is not None:
        return MeasurementValidity.INFRASTRUCTURE_ERROR
    if observation.timeout:
        return MeasurementValidity.TIMEOUT

    turn_status = observation.turn_status.strip().casefold()
    response_path = observation.response_path.strip().casefold()
    degradation_reason = observation.degradation_reason.strip().casefold()
    raw_response = (observation.raw_response or "").strip()

    if turn_status == "failed":
        return MeasurementValidity.FAILED
    if turn_status == "withheld":
        return MeasurementValidity.WITHHELD
    if response_path == "degraded" or (
        degradation_reason not in {"", "not_applicable", "unknown"}
    ):
        return MeasurementValidity.DEGRADED
    if observation.authority_path_evidence is None:
        return MeasurementValidity.UNCLASSIFIABLE
    if not raw_response and turn_status not in {"completed", "partial"}:
        return MeasurementValidity.UNCLASSIFIABLE
    return MeasurementValidity.VALID


def cognitive_scoring_allowed(validity: MeasurementValidity) -> bool:
    return validity is MeasurementValidity.VALID


def execute_with_timeout(
    operation: Callable[[], T],
    timeout_seconds: float,
) -> T:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(operation)
    try:
        return future.result(timeout=timeout_seconds)
    except FutureTimeoutError as exc:
        future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        raise EvaluationTimeout(
            f"evaluation exceeded {timeout_seconds} seconds"
        ) from exc
    finally:
        if future.done():
            executor.shutdown(wait=True, cancel_futures=False)


def verify_final_package_identity(
    *,
    expected_sha256: str,
    actual_sha256: str,
    baseline: str,
    manifest_baseline: str,
) -> bool:
    if expected_sha256 != actual_sha256:
        raise ValueError("final package SHA-256 does not match frozen identity")
    if baseline != manifest_baseline:
        raise ValueError("validated baseline does not match frozen manifest")
    return True
