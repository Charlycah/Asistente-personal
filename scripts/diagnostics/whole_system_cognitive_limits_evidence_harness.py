from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "whole-system-cognitive-limits-diagnostic-evidence-harness-v1"


class Status(StrEnum):
    PASS = "PASS"
    PASS_BY_DESIGN = "PASS_BY_DESIGN"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    NOT_PRESENT = "NOT_PRESENT"
    OUT_OF_SCOPE_BY_DESIGN = "OUT_OF_SCOPE_BY_DESIGN"


@dataclass(frozen=True)
class EvidenceCheck:
    path: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    title: str
    dimensions: tuple[str, ...]
    claim: str
    tests: tuple[str, ...]
    evidence: tuple[EvidenceCheck, ...]
    interpretation: str


@dataclass(frozen=True)
class FamilyResult:
    family_id: str
    title: str
    dimensions: tuple[str, ...]
    status: Status
    tests_passed: bool
    pytest_returncode: int
    pytest_summary: str
    evidence_reached: tuple[str, ...]
    evidence_missing: tuple[str, ...]
    interpretation: str


def _ev(path: str, *tokens: str) -> EvidenceCheck:
    return EvidenceCheck(path, tuple(tokens))


def families() -> tuple[FamilySpec, ...]:
    return (
        FamilySpec(
            "F1",
            "Capability selection by relevance",
            ("D1",),
            (
                "Selection exists, but must be distinguished from trigger/routing "
                "selection."
            ),
            (
                "tests/test_x_1_1_unified_capability_orchestrator.py",
                "tests/test_m189_cognitive_runtime_orchestration.py",
            ),
            (
                _ev("app/runtime_capability_registry.py", "semantic_triggers"),
                _ev(
                    "app/unified_capability_orchestrator.py",
                    "CapabilityExecution",
                    "registry.registrations",
                ),
            ),
            (
                "PASS means operational selection is executable; it does not by itself "
                "certify general cognitive relevance selection."
            ),
        ),
        FamilySpec(
            "F2",
            "Variable cross-capability composition",
            ("D2", "D8"),
            (
                "Existing orchestration composes capabilities; flexibility beyond "
                "declared routes remains the target boundary."
            ),
            (
                "tests/architecture/test_m395_5_orchestrator_synthesis.py",
                "tests/architecture/test_whole_system_cross_capability_cognitive_integration_transfer_certification.py",
            ),
            (
                _ev("core/cognitive_runtime_orchestration", "orchestr"),
                _ev(
                    "scripts/whole_system_cross_capability_cognitive_integration_transfer_certification.py",
                    "cognitive_flow",
                ),
            ),
            (
                "PASS certifies governed composition mechanisms, not open-ended "
                "L3 composition."
            ),
        ),
        FamilySpec(
            "F3",
            "Same-context learned knowledge reuse",
            ("D3", "D7", "D15"),
            "Approved learning must influence later cognition through governed memory.",
            (
                "tests/architecture/test_cross_capability_learned_memory_later_reasoning.py",
                "tests/architecture/test_cross_capability_memory_planning.py",
            ),
            (
                _ev(
                    "app/productive_governed_learning_wiring.py",
                    "remember_governed_learning",
                ),
                _ev("core/memory_runtime_integration/runtime.py", "memory_context"),
            ),
            "PASS is causal evidence of governed reuse inside certified memory "
            "pathways.",
        ),
        FamilySpec(
            "F4",
            "Novel-context structural transfer",
            ("D4", "D6", "D7", "D15"),
            "Structural knowledge can be projected, matched, instantiated, and "
            "admitted for review in a novel target context.",
            (
                "tests/architecture/test_post_m409_1_rc_1_governed_structural_knowledge_transfer_candidate_v1.py",
                "tests/architecture/test_post_m409_1_rc_1_3_governed_transfer_instantiation_package_v1.py",
                "tests/architecture/test_post_m409_1_rc_1_4_governed_transfer_admission_guard_v1.py",
            ),
            (
                _ev(
                    "core/governed_reasoning/structural_knowledge_transfer.py",
                    "TRANSFER_CANDIDATE",
                    "AMBIGUOUS",
                ),
                _ev("core/governed_reasoning/transfer_instantiation.py", "class"),
                _ev(
                    "core/governed_reasoning/transfer_admission_guard.py",
                    "ADMITTED_FOR_REVIEW",
                ),
            ),
            "PASS demonstrates bounded structural transfer machinery; productive "
            "conversational reachability is assessed separately.",
        ),
        FamilySpec(
            "F5",
            "Negative transfer rejection",
            ("D5", "D6", "D14", "D15"),
            "Invalid or unauthorized transfer must be rejected rather than "
            "generalized.",
            (
                "tests/architecture/test_post_m409_1_rc_1_governed_structural_knowledge_transfer_candidate_v1.py",
                "tests/architecture/test_post_m409_1_rc_1_4_governed_transfer_admission_guard_v1.py",
            ),
            (
                _ev(
                    "core/governed_reasoning/transfer_admission_guard.py",
                    "SCOPE_MISMATCH",
                    "PROVENANCE_MISMATCH",
                    "UNSUPPORTED",
                ),
                _ev(
                    "core/governed_reasoning/structural_knowledge_transfer.py",
                    "NO_TRANSFER",
                ),
            ),
            (
                "PASS_BY_DESIGN is expected when bounded transfer rejects "
                "structural/scope/provenance mismatch."
            ),
        ),
        FamilySpec(
            "F6",
            "Analogy versus superficial similarity",
            ("D6", "D7"),
            (
                "Transfer must rely on structural role correspondence, "
                "not mere lexical similarity."
            ),
            (
                "tests/architecture/test_post_m409_1_rc_1_governed_structural_knowledge_transfer_candidate_v1.py",
            ),
            (
                _ev(
                    "core/governed_reasoning/structural_knowledge_transfer.py",
                    "correspondences",
                ),
                _ev(
                    "core/governed_reasoning/target_problem_structural_projection.py",
                    "PROJECTED",
                    "AMBIGUOUS",
                ),
            ),
            (
                (
                    "PASS establishes structural discrimination within the bounded "
                    "transfer grammar; broader analogy remains unproven unless "
                    "adversarial evidence exists."
                ),
            ),
        ),
        FamilySpec(
            "F7",
            "Provenance and owner/scope preservation",
            ("D14", "D15"),
            (
                "Composition and transfer must preserve provenance and isolation "
                "boundaries."
            ),
            (
                "tests/architecture/test_post_m409_1_rc_1_4_governed_transfer_admission_guard_v1.py",
                "tests/architecture/test_whole_system_cross_capability_cognitive_integration_transfer_certification.py",
            ),
            (
                _ev(
                    "core/governed_reasoning/transfer_admission_guard.py",
                    "PROVENANCE_MISMATCH",
                    "SCOPE_MISMATCH",
                ),
            ),
            (
                "PASS certifies explicit transfer boundary guards; whole-chain "
                "preservation is bounded by existing cross-capability evidence."
            ),
        ),
        FamilySpec(
            "F8",
            "Novelty, curiosity, and spontaneous inhibition",
            ("D9", "D10", "D12"),
            (
                "Existing novelty/curiosity/spontaneity mechanisms must be executable "
                "and governable, including inhibition."
            ),
            (
                (
                    "tests/architecture/"
                    "test_post_m409_1_curiosity_relevance_initiative_consumption_v1.py"
                ),
                (
                    "tests/architecture/"
                    "test_post_m409_1_productive_conversational_curiosity_wiring_v1.py"
                ),
                "tests/test_m94_conversational_opportunity_detection.py",
                "tests/test_m95_conversation_timing_engine.py",
            ),
            (
                _ev("core/living_conversation/detection.py", "novelty"),
                _ev("core/living_conversation/timing.py", "spontaneous"),
                _ev("core/cognitive_maturity", "curiosity"),
            ),
            "PASS demonstrates bounded/productive mechanisms; internally derived "
            "general cognitive surprise is a separate higher bar.",
        ),
        FamilySpec(
            "F9",
            "Improvisation and recomposition",
            ("D11", "D8"),
            (
                (
                    "Search for evidence that a strategy is synthesized rather than "
                    "selected from a predeclared scenario."
                ),
            ),
            (
                "tests/architecture/test_m395_5_orchestrator_synthesis.py",
                "tests/test_m189_cognitive_runtime_orchestration.py",
            ),
            (
                _ev("core/cognitive_planning", "plan"),
                _ev("core/cognitive_runtime_orchestration", "orchestr"),
            ),
            (
                "A green test set is insufficient for PASS: unless tests prove "
                "non-preprogrammed strategy synthesis, this family remains PARTIAL."
            ),
        ),
        FamilySpec(
            "F10",
            "Changed conditions and bounded cognitive recomposition",
            ("D13", "D1", "D2"),
            (
                "Changed evidence should invalidate affected assumptions and produce "
                "bounded revision advisory without autonomy escalation."
            ),
            (
                "tests/architecture/test_cross_capability_changed_condition_replanning.py",
            ),
            (
                _ev(
                    "core/governed_changed_condition_plan_revision_advisory.py",
                    "application_authorized",
                ),
                _ev("core/plan_reasoning.py", "replanning_authorized"),
            ),
            (
                "PASS certifies changed-condition advisory; automatic replanning "
                "remains outside the frozen autonomy boundary."
            ),
        ),
    )


def _production_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for dirname in ("app", "core", "domain"):
        base = root / dirname
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _evidence_ok(root: Path, check: EvidenceCheck) -> bool:
    path = root / check.path
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="replace")
        return all(token.casefold() in text.casefold() for token in check.tokens)
    if path.is_dir():
        text = "\n".join(
            p.read_text(encoding="utf-8", errors="replace")
            for p in path.rglob("*.py")
            if p.is_file()
        )
        return all(token.casefold() in text.casefold() for token in check.tokens)
    return False


def _run_pytest(root: Path, tests: tuple[str, ...]) -> tuple[int, str]:
    cmd = [sys.executable, "-m", "pytest", "-q", *tests]
    cp = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    output = (cp.stdout + "\n" + cp.stderr).strip()
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    summary = lines[-1] if lines else "no pytest output"
    return cp.returncode, summary


def _classify(spec: FamilySpec, tests_passed: bool, evidence_complete: bool) -> Status:
    if not tests_passed:
        return Status.FAIL
    if not evidence_complete:
        return Status.PARTIAL
    if spec.family_id == "F5":
        return Status.PASS_BY_DESIGN
    if spec.family_id == "F9":
        return Status.PARTIAL
    return Status.PASS


def run(root: Path = PROJECT_ROOT) -> dict[str, object]:
    before = _production_fingerprint(root)
    specs = families()
    unique_tests = tuple(dict.fromkeys(test for spec in specs for test in spec.tests))
    print(
        f"[diagnostic] shared executable suite: {len(unique_tests)} test files",
        file=sys.stderr,
        flush=True,
    )
    shared_rc, shared_summary = _run_pytest(root, unique_tests)
    shared_passed = shared_rc == 0
    results: list[FamilyResult] = []
    for spec in specs:
        print(
            f"[diagnostic] classify {spec.family_id} {spec.title}",
            file=sys.stderr,
            flush=True,
        )
        reached = tuple(e.path for e in spec.evidence if _evidence_ok(root, e))
        missing = tuple(e.path for e in spec.evidence if not _evidence_ok(root, e))
        status = _classify(spec, shared_passed, not missing)
        results.append(
            FamilyResult(
                family_id=spec.family_id,
                title=spec.title,
                dimensions=spec.dimensions,
                status=status,
                tests_passed=shared_passed,
                pytest_returncode=shared_rc,
                pytest_summary=shared_summary,
                evidence_reached=reached,
                evidence_missing=missing,
                interpretation=spec.interpretation,
            )
        )
    after = _production_fingerprint(root)
    if before != after:
        raise RuntimeError("production fingerprint changed during diagnostic harness")
    counts = {
        status.value: sum(r.status is status for r in results) for status in Status
    }
    dimensions: dict[str, list[str]] = {}
    for r in results:
        for d in r.dimensions:
            dimensions.setdefault(d, []).append(f"{r.family_id}:{r.status.value}")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "diagnostic_only": True,
        "production_roots_modified_by_harness": [],
        "shared_test_files": unique_tests,
        "shared_pytest_returncode": shared_rc,
        "shared_pytest_summary": shared_summary,
        "production_fingerprint_before": before,
        "production_fingerprint_after": after,
        "production_fingerprint_preserved": before == after,
        "families": [asdict(r) for r in results],
        "status_counts": counts,
        "dimension_evidence_index": dimensions,
        "l2_governed_cross_capability_transfer_supported": all(
            next(r for r in results if r.family_id == fid).status
            in {Status.PASS, Status.PASS_BY_DESIGN}
            for fid in ("F3", "F4", "F5", "F7", "F10")
        ),
        "l3_flexible_cognitive_composition_certified": False,
        "l3_reason": (
            "F9 deliberately remains PARTIAL until non-preprogrammed strategy "
            "synthesis is causally demonstrated."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    payload = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 1 if report["status_counts"][Status.FAIL.value] else 0


if __name__ == "__main__":
    raise SystemExit(main())
