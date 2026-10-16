from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ExposurePriority:
    family: str
    priority: int
    disposition: str
    exposure_candidate: str
    causal_evidence_strength: str
    architectural_risk: str
    expected_effort: str
    rationale: tuple[str, ...]
    held_out_authorized: bool = False
    production_semantic_change_authorized: bool = False


_REQUIRED: tuple[tuple[str, str], ...] = (
    (
        "app/governed_multistep_investigation_planning_reentry.py",
        "new_plan_produced_by_existing_planning",
    ),
    (
        "core/governed_reasoning/derived_epistemic_sufficiency_assessment.py",
        "authorizes_stopping: bool = False",
    ),
    (
        "core/governed_reasoning/derived_reasoning_method_provenance.py",
        "selects_method: bool = False",
    ),
    (
        "app/cognitive_planner_shadow_runtime.py",
        "Observe plans and outcomes without affecting execution or responses.",
    ),
    (
        "core/governed_reasoning/structural_knowledge_transfer.py",
        "GovernedStructuralKnowledgeTransferMatcher",
    ),
    (
        "core/governed_reasoning/target_problem_structural_projection.py",
        "GovernedTargetProblemStructuralProjector",
    ),
)


def _evidence_stable(root: Path) -> bool:
    return all(
        (root / relative).is_file()
        and needle
        in (root / relative).read_text(
            encoding="utf-8",
            errors="ignore",
        )
        for relative, needle in _REQUIRED
    )


def audit_and_prioritize(
    root: Path = PROJECT_ROOT,
) -> dict[str, object]:
    if not _evidence_stable(root):
        raise RuntimeError("exposure prioritization evidence drifted; fail closed")

    priorities = (
        ExposurePriority(
            family="H7",
            priority=1,
            disposition="PROCEED_TO_EXPOSURE_CONTRACT",
            exposure_candidate=(
                "GovernedMultiStepInvestigationPlanningReentryV1/"
                "existing evidence-acquisition planning"
            ),
            causal_evidence_strength="HIGH",
            architectural_risk="LOW_MEDIUM",
            expected_effort="MEDIUM",
            rationale=(
                (
                    "Existing productive re-entry explicitly invokes existing "
                    "planning once."
                ),
                (
                    "Lineage, invocation count, eligibility and failure states are "
                    "observable."
                ),
                "Do not generalize investigation planning into all H7 semantics yet.",
            ),
        ),
        ExposurePriority(
            family="H2",
            priority=2,
            disposition="PROCEED_TO_EXPOSURE_CONTRACT",
            exposure_candidate=(
                "epistemic sufficiency + existing conversation withholding evidence"
            ),
            causal_evidence_strength="MEDIUM_HIGH",
            architectural_risk="LOW_MEDIUM",
            expected_effort="MEDIUM",
            rationale=(
                "Epistemic sufficiency has a productive read-only context consumer.",
                "The consumer explicitly does not invoke stopping or reasoning.",
                "Certification must join existing epistemic lineage to an existing "
                "withhold/abstain decision without letting the observer decide.",
            ),
        ),
        ExposurePriority(
            family="H8",
            priority=3,
            disposition="PROCEED_TO_EXPOSURE_CONTRACT",
            exposure_candidate=(
                "reasoning provenance + governed source/evidence observability"
            ),
            causal_evidence_strength="MEDIUM",
            architectural_risk="MEDIUM",
            expected_effort="MEDIUM",
            rationale=(
                "Derived provenance context already preserves canonical authority.",
                "Its guard forbids method selection and reasoning modification.",
                (
                    "A valid H8 exposure still needs existing conflict-resolution "
                    "evidence."
                ),
            ),
        ),
        ExposurePriority(
            family="H1",
            priority=4,
            disposition="AUDIT_OBSERVABLE_SHADOW_PATH_FIRST",
            exposure_candidate="CognitivePlannerShadowRuntime/read-only observability",
            causal_evidence_strength="MEDIUM",
            architectural_risk="MEDIUM",
            expected_effort="MEDIUM_HIGH",
            rationale=(
                (
                    "An existing shadow runtime explicitly observes without affecting "
                    "output."
                ),
                "It already exposes decision-context/kernel observability by session.",
                (
                    "Current cognitive composition remains too coarse for H1 "
                    "certification."
                ),
            ),
        ),
        ExposurePriority(
            family="H3",
            priority=5,
            disposition="AUDIT_OBSERVABLE_SHADOW_PATH_FIRST",
            exposure_candidate=(
                "existing cognitive shadow context/capability assessments"
            ),
            causal_evidence_strength="MEDIUM_LOW",
            architectural_risk="MEDIUM_HIGH",
            expected_effort="HIGH",
            rationale=(
                "Context-sensitive planning/inhibition evidence exists.",
                "Benchmark direct CognitivePlanner instantiation remains forbidden.",
                "Need proof that ordinary productive turns populate read-only shadow "
                "evidence for negation/quoted-span/distractor behavior.",
            ),
        ),
        ExposurePriority(
            family="H4",
            priority=6,
            disposition="DEFER_OR_EXCLUDE_UNLESS_PRODUCTIVE_CONSUMER_FOUND",
            exposure_candidate="none presently certified",
            causal_evidence_strength="HIGH_INTERNAL_LOW_EXPOSURE",
            architectural_risk="HIGH",
            expected_effort="HIGH",
            rationale=(
                "Structural-transfer authority and causal tests exist internally.",
                "No official productive read-only consumer is currently certified.",
                (
                    "Do not create an HCPDQ structural-transfer facade to force "
                    "measurability."
                ),
            ),
        ),
        ExposurePriority(
            family="H5",
            priority=7,
            disposition="DEFER_OR_EXCLUDE_UNLESS_PRODUCTIVE_CONSUMER_FOUND",
            exposure_candidate="none presently certified",
            causal_evidence_strength="HIGH_INTERNAL_LOW_EXPOSURE",
            architectural_risk="HIGH",
            expected_effort="HIGH",
            rationale=(
                "Target projection and contextual grounding authorities exist.",
                "Their complete generalization composition lacks productive exposure.",
                "Exclude from v2 rather than construct benchmark-only composition.",
            ),
        ),
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-existing-authority-exposure-prioritization-v1",
        "status": "AUDITED_PRIORITIZED_HELD_OUT_NO_GO",
        "baseline": "12855-pass-0-fail-ruff-clean",
        "already_certified_family": "H6",
        "priority_order": [item.family for item in priorities],
        "families": {item.family: asdict(item) for item in priorities},
        "immediate_contract_wave": ["H7", "H2", "H8"],
        "shadow_observability_wave": ["H1", "H3"],
        "defer_or_exclude_wave": ["H4", "H5"],
        "new_authority_authorized": False,
        "production_semantic_change_authorized": False,
        "held_out_construction_authorized": False,
        "human_comparison_authorized": False,
        "architectural_determination": (
            "Prioritize existing productive consumers and read-only shadow evidence; "
            "defer or exclude families whose only currently proven reachability is "
            "internal/test-level rather than create benchmark-specific authority."
        ),
        "next_gate": (
            "HCPDQ-v2 H7/H2/H8 Existing-Authority Exposure — Contract / Go-No-Go"
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
            audit_and_prioritize(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
