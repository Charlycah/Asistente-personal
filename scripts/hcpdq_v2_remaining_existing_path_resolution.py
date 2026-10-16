from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ExistingPathResolution:
    family: str
    prior_state: str
    authority_exists: bool
    productive_surface_exists: bool
    full_family_semantics_exposed: bool
    calibration_path_certified: bool
    resolution: str
    evidence: tuple[str, ...]
    prohibited_inference: str


_REQUIRED_EVIDENCE: dict[str, tuple[tuple[str, str], ...]] = {
    "H1": (
        (
            "scripts/diagnostics/l3_existing_authority_composition_certification.py",
            "Stage-by-stage relevance",
        ),
        ("app/unified_cognitive_coordination.py", "UnifiedCognitiveCoordinator"),
    ),
    "H2": (
        (
            "core/governed_reasoning/"
            "derived_epistemic_sufficiency_assessment.py",
            "GovernedDerivedEpistemicSufficiencyContextAssessment",
        ),
        (
            "core/governed_reasoning/"
            "derived_epistemic_sufficiency_assessment.py",
            "authorizes_stopping: bool = False",
        ),
    ),
    "H3": (
        ("core/cognitive_planning/planner.py", "CognitivePlanner"),
        (
            "tests/diagnostics/"
            "test_l3_context_sensitive_inhibition_causal_certification.py",
            "inhibition",
        ),
    ),
    "H4": (
        (
            "core/governed_reasoning/structural_knowledge_transfer.py",
            "GovernedStructuralKnowledgeTransferMatcher",
        ),
        (
            "scripts/diagnostics/whole_system_cognitive_limits_evidence_harness.py",
            "Novel-context structural transfer",
        ),
    ),
    "H5": (
        (
            "core/governed_reasoning/target_problem_structural_projection.py",
            "GovernedTargetProblemStructuralProjector",
        ),
        (
            "core/governed_reasoning/contextual_case_grounding.py",
            "GovernedContextualCaseRoleGrounder",
        ),
    ),
    "H7": (
        ("app/canonical_planning_facade.py", "CanonicalPlanningFacade"),
        (
            "app/canonical_planning_facade.py",
            "canonical planning facade is not bound to a planner",
        ),
        (
            "app/official_conversation_gateway.py",
            "CanonicalPlanningFacade()",
        ),
    ),
    "H8": (
        (
            "core/governed_reasoning/derived_reasoning_method_provenance.py",
            "GovernedReasoningMethodProvenanceContextItem",
        ),
        (
            "core/governed_reasoning/derived_reasoning_method_provenance.py",
            "selects_method: bool = False",
        ),
    ),
}


def _evidence_present(root: Path, family: str) -> bool:
    for relative, needle in _REQUIRED_EVIDENCE[family]:
        path = root / relative
        if not path.is_file() or needle not in path.read_text(
            encoding="utf-8",
            errors="ignore",
        ):
            return False
    return True


def resolve_remaining_paths(root: Path = PROJECT_ROOT) -> dict[str, object]:
    if not all(_evidence_present(root, family) for family in _REQUIRED_EVIDENCE):
        raise RuntimeError("existing-path evidence drifted; fail closed")

    rows = (
        ExistingPathResolution(
            "H1",
            "P1",
            True,
            True,
            False,
            False,
            "EXISTING_COMPOSITION_COARSE_NOT_H1_CERTIFIED",
            (
                "UnifiedCognitiveCoordinator exists.",
                "Existing A5 diagnostic finds a shared reasoning/planning/"
                "reflection/executive bundle rather than stage-specific relevance.",
            ),
            "Do not infer deterministic-reasoning path certification.",
        ),
        ExistingPathResolution(
            "H2",
            "P2",
            True,
            True,
            False,
            False,
            "DERIVED_EPISTEMIC_CONTEXT_NOT_ABSTENTION_EXECUTOR",
            (
                "GovernedDerivedEpistemicSufficiencyContextAssessment exists.",
                "Its neutral carrier explicitly has no stopping or reasoning "
                "authority.",
            ),
            "Do not equate epistemic context consumption with H2 abstention.",
        ),
        ExistingPathResolution(
            "H3",
            "P1",
            True,
            False,
            False,
            False,
            "INTERNAL_CONTEXT_SENSITIVITY_NO_OFFICIAL_H3_EVALUATION_SURFACE",
            (
                "CognitivePlanner and context-sensitive inhibition evidence exist.",
                "No official read-only productive H3 distractor interface "
                "is certified.",
            ),
            "Do not instantiate CognitivePlanner from the benchmark.",
        ),
        ExistingPathResolution(
            "H4",
            "P1",
            True,
            False,
            False,
            False,
            "STRUCTURAL_TRANSFER_AUTHORITY_NO_PRODUCTIVE_EXPOSURE",
            (
                "GovernedStructuralKnowledgeTransferMatcher exists.",
                "Whole-system diagnostic evidence covers novel-context transfer.",
            ),
            "Do not treat diagnostic/test reachability as productive exposure.",
        ),
        ExistingPathResolution(
            "H5",
            "P1",
            True,
            False,
            False,
            False,
            "GENERALIZATION_AUTHORITIES_NO_PRODUCTIVE_EXPOSURE",
            (
                "Target structural projection and contextual case grounding exist.",
                "No official read-only H5 generalization surface is certified.",
            ),
            "Do not create a benchmark generalization facade.",
        ),
        ExistingPathResolution(
            "H7",
            "P2",
            True,
            True,
            False,
            False,
            "CANONICAL_PLANNING_SURFACE_UNBOUND_AT_OFFICIAL_GATEWAY",
            (
                "CanonicalPlanningFacade exists and delegates only when bound.",
                "OfficialConversationGateway constructs CanonicalPlanningFacade "
                "unbound.",
            ),
            "Do not bind or instantiate a planner merely for benchmark coverage.",
        ),
        ExistingPathResolution(
            "H8",
            "P2",
            True,
            True,
            False,
            False,
            "DERIVED_PROVENANCE_CONTEXT_NOT_CONFLICT_RESOLUTION_EXECUTOR",
            (
                "GovernedReasoningMethodProvenanceContextItem exists.",
                "Its guard forbids selecting/recommending methods and "
                "modifying reasoning.",
            ),
            "Do not equate provenance availability with H8 conflict resolution.",
        ),
    )
    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-remaining-existing-path-resolution-v1",
        "status": "RESOLVED_NO_ADDITIONAL_FAMILY_CERTIFIED",
        "baseline": "12830-pass-0-fail-ruff-clean",
        "production_changes_authorized": False,
        "new_authority_authorized": False,
        "held_out_construction_authorized": False,
        "already_certified_family": "H6",
        "newly_certified_families": [],
        "remaining_uncertified_families": [row.family for row in rows],
        "family_results": {row.family: asdict(row) for row in rows},
        "architectural_determination": (
            "All seven families have existing capability evidence, but none has "
            "a presently certified official read-only path exposing the complete "
            "HCPDQ family semantics. Fail closed without production changes."
        ),
        "next_gate": ("HCPDQ-v2 Evaluation Exposure Gap — Contract / Go-No-Go"),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["resolution_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            resolve_remaining_paths(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
