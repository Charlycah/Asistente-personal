from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

from app.official_conversation_gateway import OfficialConversationGateway
from scripts.hcpdq_v2_evaluation_boundary import (
    MeasurementValidity,
    capture_observable_turn,
    classify_measurement_validity,
    default_family_path_coverage,
)


@dataclass(frozen=True)
class FamilyCalibrationCertification:
    family: str
    audit_state: str
    authority_exists: bool
    official_surface_found: bool
    positive_probe_executed: bool
    authority_path_certified: bool
    held_out_authorized: bool
    verdict: str
    evidence: tuple[str, ...]


class _Turn:
    response_text = "runtime fallback"
    status = "completed"
    session_id = "calibration-runtime"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False
    response_path = "pipeline"
    degradation_reason = "not_applicable"
    rationale: tuple[str, ...] = ()


class _RuntimeStub:
    bootstrap = object()
    history: tuple[object, ...] = ()
    traces: tuple[object, ...] = ()

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def converse(self, text: str, **kwargs: object) -> _Turn:
        self.calls.append((text, kwargs))
        return _Turn()


def _h6_positive_probe() -> dict[str, Any]:
    runtime = _RuntimeStub()
    gateway = OfficialConversationGateway(runtime)
    prompt = (
        "Decisión:\n"
        "¿A o B?\n\n"
        "Criterios:\n"
        "Los criterios son seguridad y costo. Seguridad es obligatoria.\n\n"
        "Evidencia:\n"
        "A cumple seguridad. A cumple costo. "
        "B no cumple seguridad. B cumple costo."
    )
    observation = capture_observable_turn(
        case_id="CAL-H6-POS-01",
        family="H6",
        gateway=gateway,
        prompt=prompt,
    )
    validity = classify_measurement_validity(observation)
    rationale = tuple(observation.rationale)
    certified = (
        validity is MeasurementValidity.VALID
        and observation.response_path == "interceptor"
        and "explicit_complex_decision_intake" in rationale
        and "productive_gcdr_intake_integration" in rationale
        and "governed_complex_decision_reasoning" in rationale
        and runtime.calls == []
    )
    return {
        "certified": certified,
        "validity": validity.value,
        "response_path": observation.response_path,
        "rationale": rationale,
        "runtime_fallback_calls": len(runtime.calls),
        "authority_path_evidence": (
            asdict(observation.authority_path_evidence)
            if observation.authority_path_evidence is not None
            else None
        ),
    }


def certify_calibration_path_coverage() -> dict[str, Any]:
    coverage = default_family_path_coverage()
    h6_probe = _h6_positive_probe()

    evidence = {
        "H1": (
            "unified_cognitive_coordination exists",
            "no official read-only H1 reasoning path certified",
        ),
        "H2": (
            "OfficialConversationGateway exists",
            "epistemic/withholding surface exists",
            "family-specific authority path not yet calibrated",
        ),
        "H3": (
            "contextual governed reasoning authorities exist",
            "no official H3 productive evaluation surface certified",
        ),
        "H4": (
            "GovernedStructuralKnowledgeTransferMatcher exists",
            "no official productive evaluation surface certified",
        ),
        "H5": (
            "target projection/generalization authorities exist",
            "no official productive evaluation surface certified",
        ),
        "H6": (
            "OfficialConversationGateway explicit complex-decision intake",
            "productive GCDR integration",
            "governed complex decision reasoning",
            "runtime fallback bypassed by positive calibration probe",
        ),
        "H7": (
            "CanonicalPlanningFacade exists",
            "facade is unbound in OfficialConversationGateway",
            "read-only H7 execution path not certified",
        ),
        "H8": (
            "OfficialConversationGateway and epistemic/provenance surfaces exist",
            "family-specific conflict/provenance path not yet calibrated",
        ),
    }

    certified: dict[str, FamilyCalibrationCertification] = {}
    for family, item in coverage.items():
        h6 = family == "H6"
        path_certified = bool(h6 and h6_probe["certified"])
        official_surface = family in {"H2", "H6", "H7", "H8"}
        certified[family] = FamilyCalibrationCertification(
            family=family,
            audit_state=item.audit_state,
            authority_exists=True,
            official_surface_found=official_surface,
            positive_probe_executed=h6,
            authority_path_certified=path_certified,
            held_out_authorized=False,
            verdict="CERTIFIED_CALIBRATION_PATH" if path_certified else "NO_GO",
            evidence=evidence[family],
        )

    payload: dict[str, Any] = {
        "schema_version": "hcpdq-v2-calibration-path-coverage-certification-v1",
        "status": "PARTIAL_CERTIFICATION_HELD_OUT_NO_GO",
        "production_changes_authorized": False,
        "held_out_construction_authorized": False,
        "human_comparison_authorized": False,
        "family_results": {
            family: asdict(result) for family, result in certified.items()
        },
        "h6_positive_probe": h6_probe,
        "certified_family_count": sum(
            result.authority_path_certified for result in certified.values()
        ),
        "required_family_count": 8,
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
            certify_calibration_path_coverage(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
