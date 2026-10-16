from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "whole-system-cross-capability-cognitive-integration-transfer-v1"


class CertificationStatus(StrEnum):
    PASS = "PASS"
    PASS_BY_DESIGN = "PASS_BY_DESIGN"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"


@dataclass(frozen=True)
class EvidenceRequirement:
    stage: str
    path: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    name: str
    cognitive_flow: str
    evidence: tuple[EvidenceRequirement, ...]
    expected_by_design: bool = False


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    name: str
    cognitive_flow: str
    status: CertificationStatus
    reached_stages: tuple[str, ...]
    missing_stages: tuple[str, ...]
    evidence_paths: tuple[str, ...]


@dataclass(frozen=True)
class CertificationReport:
    schema_version: str
    generated_at: str
    diagnostic_only: bool
    production_roots_modified_by_harness: tuple[str, ...]
    scenarios: tuple[ScenarioResult, ...]
    status_counts: dict[str, int]
    overall_status: CertificationStatus
    primary_gap: str
    inventory_fingerprint: str
    report_fingerprint: str


def _e(stage: str, path: str, *tokens: str) -> EvidenceRequirement:
    return EvidenceRequirement(stage, path, tuple(tokens))


def _scenarios() -> tuple[ScenarioSpec, ...]:
    return (
        ScenarioSpec(
            "CCI-01", "approved learning reaches durable governed memory",
            "learning -> human approval -> materialization -> OfficialMemoryGateway",
            (
                _e("learning", "app/curiosity_m369_learning_evaluation.py", "Learning"),
                _e(
                    "approval",
                    "app/m369_explicit_human_learning_approval.py",
                    "ExplicitHumanLearningApprovalResponse",
                ),
                _e(
                    "materialization",
                    "app/approved_learning_memory_materialization.py",
                    "ApprovedLearningMemoryMaterialization",
                ),
                _e(
                    "productive_write",
                    "app/productive_governed_learning_wiring.py",
                    "remember_governed_learning",
                    "ProductiveGovernedLearningOutcome.STORED",
                ),
                _e(
                    "e2e_test",
                    (
                        "tests/architecture/"
                        "test_post_m409_1_governed_learning_"
                        "productive_end_to_end_wiring_v1.py"
                    ),
                    "runtime.count",
                    "== 1",
                ),
            ),
        ),
        ScenarioSpec(
            "CCI-02", "learned memory is later selected into cognition",
            "approved learning -> memory -> later relevant recall -> cognitive request",
            (
                _e(
                    "approved_memory",
                    "app/productive_governed_learning_wiring.py",
                    "remember_governed_learning",
                ),
                _e(
                    "later_recall",
                    "core/memory_runtime_integration/runtime.py",
                    "def enrich",
                    "no_relevant_memory",
                    "memory_context",
                ),
                _e(
                    "cross_episode_proof",
                    (
                        "tests/architecture/"
                        "test_cross_capability_learned_memory_later_reasoning.py"
                    ),
                    "learned",
                    "cognitive_request",
                ),
            ),
        ),
        ScenarioSpec(
            "CCI-03", "mental model materially constrains a later decision",
            "mental model/context -> governed reasoning -> decision consequence",
            (
                _e(
                    "mental_model",
                    "core/adaptive_cognition/mental_models.py",
                    "MentalModel",
                ),
                _e(
                    "decision_evidence",
                    "core/mental_model_decision_evidence.py",
                    "GovernedMentalModelDecisionEvidenceProjector",
                ),
                _e("decision", "core/governed_decision_advisory.py", "Decision"),
                _e(
                    "causal_bridge",
                    "tests/architecture/test_cross_capability_mental_model_decision.py",
                    "mental",
                    "decision",
                ),
            ),
        ),
        ScenarioSpec(
            "CCI-04", "memory evidence changes planning without new authority",
            "relevant memory -> canonical planning -> recommendation",
            (
                _e(
                    "memory_runtime",
                    "core/memory_runtime_integration/runtime.py",
                    "def enrich",
                ),
                _e(
                    "planning_runtime",
                    "core/planning_runtime_integration.py",
                    "PlanningRuntimeContributor",
                ),
                _e(
                    "integration_proof",
                    "tests/architecture/test_cross_capability_memory_planning.py",
                    "memory",
                    "planning",
                ),
            ),
        ),
        ScenarioSpec(
            "CCI-05", "reflection history improves later reasoning method selection",
            "reflection/quality evidence -> later method choice -> governed reasoning",
            (
                _e(
                    "reflection",
                    "core/cognitive_maturity/reflection_learning_evidence.py",
                    "ReflectionLearningEvidenceAdapter",
                ),
                _e(
                    "historical_method_advisory",
                    "core/governed_reasoning/historical_method_advisory.py",
                    "GovernedHistoricalReasoningMethodAdvisoryV1",
                    "application_authorized",
                ),
                _e(
                    "feedback_proof",
                    (
                        "tests/architecture/"
                        "test_cci_05_governed_historical_reasoning_method_advisory.py"
                    ),
                    "METHOD_PREFERENCE_OBSERVED",
                    "application_authorized is False",
                ),
            ),
        ),
        ScenarioSpec(
            "CCI-06", "bounded structural knowledge transfer",
            (
                "source structure -> transfer candidate -> instantiation "
                "-> canonical temporary admission"
            ),
            (
                _e(
                    "candidate",
                    (
                        "docs/INTEGRATION_NOTE_RC_1_GOVERNED_STRUCTURAL_"
                        "KNOWLEDGE_TRANSFER_CANDIDATE_V1.md"
                    ),
                    "transfer",
                ),
                _e(
                    "instantiation",
                    "core/governed_reasoning/transfer_instantiation.py",
                    "class",
                ),
                _e(
                    "admission",
                    "core/governed_reasoning/transfer_admission_guard.py",
                    "class",
                ),
                _e(
                    "independent_evaluation",
                    (
                        "docs/quality/ADVANCED_CAPABILITY_4B_"
                        "INDEPENDENT_REASONING_EVALUATION.json"
                    ),
                    '"status"',
                ),
            ),
        ),
        ScenarioSpec(
            "CCI-07", "epistemic uncertainty remains visible in public explanation",
            "uncertainty/abstention -> governed decision -> authorized explanation",
            (
                _e("uncertainty", "core/governed_reasoning/explanations.py", "uncert"),
                _e(
                    "public_realization",
                    "core/decision_advisory_conversational_realization.py",
                    "DecisionAdvisoryConversationalRealizer",
                ),
                _e(
                    "independent_abstention",
                    (
                        "docs/quality/ADVANCED_CAPABILITY_4B_"
                        "INDEPENDENT_REASONING_EVALUATION.json"
                    ),
                    '"false_assertion_rate"',
                ),
            ),
        ),
        ScenarioSpec(
            "CCI-08", "personality changes delivery but not cognitive content",
            (
                "stable identity -> bounded adaptive delivery + "
                "source-owned explanation boundary"
            ),
            (
                _e(
                    "adaptive_boundary",
                    "core/adaptive_personality.py",
                    "identity_changed",
                    "creates_parallel_brain",
                ),
                _e(
                    "source_owned_explanation_boundary",
                    "core/governed_reasoning/explanations.py",
                    "ExplainableAnswerRenderer",
                    "DecisionRecord",
                    "immutable decisions",
                ),
                _e(
                    "boundary_test",
                    "tests/test_m377_adaptive_personality.py",
                    "AdaptivePersonalityAuthority",
                ),
            ),
            expected_by_design=True,
        ),
        ScenarioSpec(
            "CCI-09", "irrelevant memory is rejected rather than injected",
            "conversation text -> memory relevance -> no context when irrelevant",
            (
                _e(
                    "relevance_recall",
                    "core/memory_runtime_integration/runtime.py",
                    "no_relevant_memory",
                    "context_included",
                ),
                _e(
                    "context_builder",
                    "core/memory_prompt_context.py",
                    "class MemoryPromptContextBuilder",
                ),
                _e(
                    "negative_proof",
                    "tests/test_m366_7_contextual_memory_retrieval.py",
                    "LOW_RELEVANCE",
                ),
            ),
            expected_by_design=True,
        ),
        ScenarioSpec(
            "CCI-10", "changed conditions trigger bounded replanning",
            (
                "changed evidence/state -> progress evaluation -> bounded replanning "
                "-> revised recommendation"
            ),
            (
                _e("progress", "core/progress_evaluation.py", "PlanProgressState"),
                _e(
                    "plan_reasoning",
                    "core/plan_reasoning.py",
                    "replanning_authorized",
                    "plan_reordered",
                ),
                _e(
                    "replanning_advisory",
                    "core/governed_changed_condition_plan_revision_advisory.py",
                    "ChangedConditionEvidence",
                    "PlanRevisionAdvisory",
                    "application_authorized",
                ),
                _e(
                    "replanning_proof",
                    (
                        "tests/architecture/"
                        "test_cross_capability_changed_condition_replanning.py"
                    ),
                    "changed_condition",
                    "REVIEW_REQUIRED",
                ),
            ),
        ),
    )


def _requirement_ok(root: Path, req: EvidenceRequirement) -> bool:
    path = root / req.path
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return all(token.casefold() in text.casefold() for token in req.tokens)


def _scenario_result(root: Path, spec: ScenarioSpec) -> ScenarioResult:
    reached = tuple(req.stage for req in spec.evidence if _requirement_ok(root, req))
    missing = tuple(
        req.stage for req in spec.evidence if not _requirement_ok(root, req)
    )
    if not reached:
        status = CertificationStatus.FAIL
    elif not missing:
        status = (
            CertificationStatus.PASS_BY_DESIGN
            if spec.expected_by_design
            else CertificationStatus.PASS
        )
    else:
        status = CertificationStatus.PARTIAL
    return ScenarioResult(
        scenario_id=spec.scenario_id,
        name=spec.name,
        cognitive_flow=spec.cognitive_flow,
        status=status,
        reached_stages=reached,
        missing_stages=missing,
        evidence_paths=tuple(req.path for req in spec.evidence),
    )


def _fingerprint_inventory(root: Path) -> str:
    digest = sha256()
    for relative in ("app", "core", "domain"):
        base = root / relative
        for path in sorted(base.rglob("*.py")):
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def run_certification(root: Path = PROJECT_ROOT) -> CertificationReport:
    scenarios = tuple(_scenario_result(root, spec) for spec in _scenarios())
    counts = {
        status.value: sum(item.status is status for item in scenarios)
        for status in CertificationStatus
    }
    overall = (
        CertificationStatus.FAIL
        if counts[CertificationStatus.FAIL.value]
        else CertificationStatus.PARTIAL
        if counts[CertificationStatus.PARTIAL.value]
        else CertificationStatus.PASS
    )
    inventory = _fingerprint_inventory(root)
    logical = {
        "schema_version": SCHEMA_VERSION,
        "scenarios": [asdict(item) for item in scenarios],
        "inventory_fingerprint": inventory,
    }
    report_fingerprint = sha256(
        json.dumps(logical, sort_keys=True, default=str).encode()
    ).hexdigest()
    return CertificationReport(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        diagnostic_only=True,
        production_roots_modified_by_harness=(),
        scenarios=scenarios,
        status_counts=counts,
        overall_status=overall,
        primary_gap="none_within_certified_cross_capability_contract",
        inventory_fingerprint=inventory,
        report_fingerprint=report_fingerprint,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_certification()
    payload = json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report.overall_status is not CertificationStatus.FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
