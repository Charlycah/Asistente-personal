from __future__ import annotations

import inspect
import json
from dataclasses import asdict, dataclass
from hashlib import sha256

from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from app.context_continuity_runtime import OfficialContextContinuityRuntimeGateway
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


@dataclass(frozen=True)
class ShadowScopeResolution:
    family: str
    shadow_surface_exists: bool
    ordinary_productive_path_wired: bool
    family_semantics_fully_exposed: bool
    disposition: str
    rationale: tuple[str, ...]
    production_change_authorized: bool = False
    red_authorized: bool = False
    held_out_authorized: bool = False


def _contains_call(function: object, token: str) -> bool:
    return token in inspect.getsource(function)


def audit_h1_h3_shadow_observability() -> dict[str, object]:
    shadow_source = inspect.getsource(CognitivePlannerShadowRuntime)
    registry_intercept = OfficialRuntimeCapabilityRegistry.intercept
    registry_execute = OfficialRuntimeCapabilityRegistry.execute_registration
    continuity_enrich = OfficialContextContinuityRuntimeGateway.enrich

    ordinary_plan_observed = _contains_call(
        registry_intercept,
        "cognitive_planner_shadow.observe(",
    )
    capability_observed = _contains_call(
        registry_execute,
        "observe_capability_selection(",
    )
    context_observed = _contains_call(
        continuity_enrich,
        "observe_context_selection(",
    )
    read_only_contract = (
        "without affecting execution or responses" in shadow_source
        and "CognitivePlanner()" in shadow_source
    )

    h1 = ShadowScopeResolution(
        family="H1",
        shadow_surface_exists=read_only_contract,
        ordinary_productive_path_wired=ordinary_plan_observed,
        family_semantics_fully_exposed=False,
        disposition="EXCLUDE_H1_FROM_HCPDQ_V2_MEASURABLE_SCOPE",
        rationale=(
            "Ordinary runtime turns do invoke the existing shadow planner.",
            "The shadow exposes intent, needs, tools, evidence, policy and "
            "decision-context observability.",
            "H1 requires deterministic reasoning-path semantics, but the shadow "
            "plan is advisory and does not expose stage-specific reasoning "
            "execution or a causal reasoning-path outcome.",
            "Using shadow plan metadata as H1 would overclaim observability.",
        ),
    )
    h3 = ShadowScopeResolution(
        family="H3",
        shadow_surface_exists=read_only_contract,
        ordinary_productive_path_wired=(
            ordinary_plan_observed and context_observed and capability_observed
        ),
        family_semantics_fully_exposed=False,
        disposition="EXCLUDE_H3_FROM_HCPDQ_V2_MEASURABLE_SCOPE",
        rationale=(
            "Ordinary runtime turns populate shadow planning observations.",
            "Existing runtime paths also observe selected conversation context "
            "and governed capability selection.",
            "Those assessors compare planned versus selected context/capability, "
            "but they do not expose the semantic negation, quoted-span and "
            "distractor evidence required for complete H3 certification.",
            "Creating benchmark semantic labels would cross the evaluation boundary.",
        ),
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h1-h3-shadow-observability-audit-v1",
        "status": "RESOLVED_EXCLUDE_H1_H3_FROM_V2_MEASURABLE_SCOPE",
        "baseline": "12898-pass-0-fail-ruff-clean",
        "families": {
            "H1": asdict(h1),
            "H3": asdict(h3),
        },
        "shadow_runtime_existing_authority": "CognitivePlanner",
        "shadow_runtime_is_observer": True,
        "ordinary_plan_observation_wired": ordinary_plan_observed,
        "context_observation_wired": context_observed,
        "capability_observation_wired": capability_observed,
        "new_authority_authorized": False,
        "benchmark_semantic_classifier_authorized": False,
        "production_change_authorized": False,
        "preimplementation_red_authorized": False,
        "held_out_authorized": False,
        "architectural_determination": (
            "The existing shadow path is real and productively wired, but its "
            "observable records do not expose the complete causal semantics of "
            "H1 or H3. Because no read-only adapter can recover semantics that "
            "are absent from the records, H1/H3 must be excluded from HCPDQ-v2 "
            "rather than creating benchmark-specific production observability."
        ),
        "next_gate": (
            "HCPDQ-v2 Measurable Family Set — Final Scope Freeze / "
            "Held-Out Readiness Decision"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["audit_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            audit_h1_h3_shadow_observability(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
