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
SCHEMA_VERSION = "l3-adversarial-flexible-composition-evidence-v1"


class Status(StrEnum):
    PASS = "PASS"
    PASS_BY_DESIGN = "PASS_BY_DESIGN"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"


@dataclass(frozen=True)
class AdversarialControl:
    control_id: str
    title: str
    claim: str
    nodeids: tuple[str, ...]
    evidence_paths: tuple[str, ...]
    expected_status: Status
    l3_support: bool
    interpretation: str


@dataclass(frozen=True)
class ControlResult:
    control_id: str
    title: str
    status: Status
    pytest_returncode: int
    pytest_summary: str
    evidence_present: tuple[str, ...]
    evidence_missing: tuple[str, ...]
    l3_support: bool
    interpretation: str


def controls() -> tuple[AdversarialControl, ...]:
    transfer = (
        "tests/architecture/"
        "test_post_m409_1_rc_1_governed_structural_knowledge_transfer_candidate_v1.py"
    )
    return (
        AdversarialControl(
            "A1",
            "Same structure, different vocabulary/domain",
            "Structural transfer must survive domain and entity-word changes.",
            (
                f"{transfer}::test_cross_domain_structure_matches_without_shared_entity_words",
                f"{transfer}::test_structural_matching_ignores_concrete_domain_terms",
            ),
            (
                "core/governed_reasoning/structural_knowledge_transfer.py",
                "core/governed_reasoning/contextual_semantic_grounding.py",
            ),
            Status.PASS,
            True,
            (
                "Supports bounded structural abstraction: transfer is not dependent "
                "on shared entity vocabulary."
            ),
        ),
        AdversarialControl(
            "A2",
            "Same vocabulary, different relational structure",
            "Lexical overlap must not manufacture structural transfer.",
            (
                f"{transfer}::test_same_words_with_different_relational_structure_do_not_transfer",
            ),
            (
                "core/governed_reasoning/structural_knowledge_transfer.py",
            ),
            Status.PASS,
            True,
            (
                "Supports negative-transfer discrimination inside the certified "
                "structural grammar."
            ),
        ),
        AdversarialControl(
            "A3",
            "Relevant source plus structural distractor",
            (
                "When more than one structurally compatible source exists, the system "
                "must not invent a preference."
            ),
            (
                f"{transfer}::test_two_structurally_compatible_sources_require_review",
            ),
            (
                "core/governed_reasoning/structural_knowledge_transfer.py",
            ),
            Status.PASS_BY_DESIGN,
            False,
            (
                "Governance is correct, but this exposes an L3 boundary: the matcher "
                "returns AMBIGUOUS rather than selecting among compatible sources "
                "using broader cognitive context."
            ),
        ),
        AdversarialControl(
            "A4",
            "Changed conditions without autonomy escalation",
            (
                "Changed conditions may produce revision advisory but must not "
                "authorize automatic replanning."
            ),
            (
                "tests/architecture/test_cross_capability_changed_condition_replanning.py",
            ),
            (
                "core/governed_changed_condition_plan_revision_advisory.py",
                "core/plan_reasoning.py",
            ),
            Status.PASS_BY_DESIGN,
            False,
            (
                "Bounded recomposition advisory is certified; automatic strategy "
                "replacement remains intentionally unauthorized."
            ),
        ),
        AdversarialControl(
            "A5",
            "Contributor-set flexibility",
            (
                "General L3 would require evidence that contributor selection itself "
                "changes because the problem requires it."
            ),
            (
                "tests/test_m189_cognitive_runtime_orchestration.py",
            ),
            (
                "core/cognitive_runtime_orchestration/runtime.py",
            ),
            Status.PARTIAL,
            False,
            (
                "The cognitive runtime executes the contributor tuple supplied at "
                "construction time. Executable composition exists, but problem-driven "
                "dynamic contributor selection is not demonstrated."
            ),
        ),
        AdversarialControl(
            "A6",
            "Implicit capability composition without explicit clause routing",
            (
                "General L3 would require composition not reducible to explicit "
                "separator splitting and ordered registry traversal."
            ),
            (
                "tests/test_x_1_1_unified_capability_orchestrator.py",
            ),
            (
                "app/unified_capability_orchestrator.py",
                "app/runtime_capability_registry.py",
            ),
            Status.PARTIAL,
            False,
            (
                "The official orchestrator is useful and governed, but composition "
                "is still driven by clause separators plus ordered registrations."
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


def _run_pytest(root: Path, nodeids: tuple[str, ...]) -> tuple[int, str]:
    cp = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *nodeids],
        cwd=root,
        text=True,
        capture_output=True,
    )
    output = (cp.stdout + "\n" + cp.stderr).strip()
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return cp.returncode, lines[-1] if lines else "no pytest output"


def _source_boundary_assertions(root: Path) -> dict[str, bool]:
    cognitive_runtime = (
        root / "core/cognitive_runtime_orchestration/runtime.py"
    ).read_text(encoding="utf-8")
    orchestrator = (
        root / "app/unified_capability_orchestrator.py"
    ).read_text(encoding="utf-8")
    transfer = (
        root / "core/governed_reasoning/structural_knowledge_transfer.py"
    ).read_text(encoding="utf-8")
    target_projection = (
        root / "core/governed_reasoning/target_problem_structural_projection.py"
    ).read_text(encoding="utf-8")
    return {
        "contributors_are_constructor_supplied": (
            "contributors: tuple[CognitiveRuntimeContributor, ...] = ()"
            in cognitive_runtime
            and "for contributor in self.contributors:" in cognitive_runtime
        ),
        "capability_composition_uses_explicit_clause_split": (
            "_SEPARATOR = re.compile" in orchestrator
            and "clauses = self._split_clauses(request.text)" in orchestrator
            and "for registration in self.registry.registrations:" in orchestrator
        ),
        "structural_transfer_can_be_ambiguous": (
            "StructuralKnowledgeTransferStatus.AMBIGUOUS" in transfer
            and "multiple_compatible_structures" in transfer
        ),
        "target_projection_is_bounded_to_certified_family": (
            '_FAMILY_ID = "exclusive_dependency_capability_loss_v1"'
            in target_projection
            and "target projection family is not certified" in target_projection
        ),
    }


def run(root: Path = PROJECT_ROOT) -> dict[str, object]:
    before = _production_fingerprint(root)
    results: list[ControlResult] = []
    for control in controls():
        rc, summary = _run_pytest(root, control.nodeids)
        present = tuple(
            path for path in control.evidence_paths if (root / path).exists()
        )
        missing = tuple(
            path for path in control.evidence_paths if not (root / path).exists()
        )
        if rc != 0 or missing:
            status = Status.FAIL
        else:
            status = control.expected_status
        results.append(
            ControlResult(
                control_id=control.control_id,
                title=control.title,
                status=status,
                pytest_returncode=rc,
                pytest_summary=summary,
                evidence_present=present,
                evidence_missing=missing,
                l3_support=control.l3_support,
                interpretation=control.interpretation,
            )
        )
    boundaries = _source_boundary_assertions(root)
    after = _production_fingerprint(root)
    if before != after:
        raise RuntimeError("production fingerprint changed during L3 diagnostics")

    counts = {
        status.value: sum(item.status is status for item in results)
        for status in Status
    }
    hard_fail = any(item.status is Status.FAIL for item in results)
    bounded_abstraction = all(
        next(item for item in results if item.control_id == cid).status is Status.PASS
        for cid in ("A1", "A2")
    )
    governance_preserved = all(
        next(item for item in results if item.control_id == cid).status
        is Status.PASS_BY_DESIGN
        for cid in ("A3", "A4")
    )
    l3_certified = (
        not hard_fail
        and bounded_abstraction
        and governance_preserved
        and all(item.l3_support for item in results)
        and not any(boundaries.values())
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "diagnostic_only": True,
        "production_roots_modified_by_harness": [],
        "controls": [asdict(item) for item in results],
        "status_counts": counts,
        "source_boundary_assertions": boundaries,
        "production_fingerprint_before": before,
        "production_fingerprint_after": after,
        "production_fingerprint_preserved": before == after,
        "bounded_structural_abstraction_demonstrated": bounded_abstraction,
        "governed_refusal_and_advisory_preserved": governance_preserved,
        "l3_flexible_cognitive_composition_certified": l3_certified,
        "l3_status": "PASS" if l3_certified else "PARTIAL",
        "l3_gap": (
            None
            if l3_certified
            else (
                "Problem-driven dynamic selection/recomposition across existing "
                "capabilities is not causally demonstrated beyond bounded structural "
                "transfer, constructor-supplied contributors, explicit clause routing, "
                "and advisory-only changed-condition handling."
            )
        ),
        "architectural_gate": (
            "CERTIFICATION_CANDIDATE" if l3_certified else "GO_NO_GO_REQUIRED"
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
