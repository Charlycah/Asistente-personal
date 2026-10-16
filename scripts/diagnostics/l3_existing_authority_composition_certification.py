from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

from app.canonical_decision_facade import CANONICAL_DECISION_COMPONENTS
from app.canonical_planning_facade import CANONICAL_PLANNING_COMPONENTS
from app.cognitive_runtime_sources import OperationalCognitiveSource
from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.cognitive_planning import CognitivePlanner, ToolRequirement
from core.cognitive_runtime_orchestration import CognitiveRuntimeOrchestrator
from core.executive_cognitive_runtime import ExecutiveCognitiveRuntimeContributor
from core.llm_provider import LLMRequest
from core.planning_runtime_integration import PlanningRuntimeContributor
from core.reasoning_runtime_integration import ReasoningRuntimeContributor
from core.reflection_runtime_integration import ReflectionRuntimeContributor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "l3-existing-authority-composition-certification-v1"
NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


class Status(StrEnum):
    PASS = "PASS"
    PASS_BY_DESIGN = "PASS_BY_DESIGN"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    title: str
    status: Status
    evidence: tuple[str, ...]
    conclusion: str


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


def _official_cognitive_runtime() -> CognitiveRuntimeOrchestrator:
    source = OperationalCognitiveSource()
    return CognitiveRuntimeOrchestrator(
        (
            ReasoningRuntimeContributor(source.reasoning),
            PlanningRuntimeContributor(source.planning),
            ReflectionRuntimeContributor(source.reflection),
            ExecutiveCognitiveRuntimeContributor(source.coordination),
        )
    )


def _activated_stages(text: str) -> tuple[str, ...]:
    result = _official_cognitive_runtime().enrich(
        owner="Carlos",
        session_id="diagnostic",
        text=text,
        request=LLMRequest(prompt=text),
        now=NOW,
    )
    return result.activated_stages


def _role(component) -> str:
    return component.role.value


def _operational(component) -> bool:
    return bool(component.operational)


def evaluate(root: Path = PROJECT_ROOT) -> dict[str, object]:
    before = _production_fingerprint(root)

    generic = _activated_stages("Hola, contame algo breve.")
    reasoning_request = _activated_stages(
        "Analizá cognitivamente si estas dos alternativas son equivalentes."
    )
    planning_request = _activated_stages(
        "Planificá cómo estudiar este problema sin ejecutar ninguna acción."
    )
    reflection_request = _activated_stages(
        "Reflexioná sobre por qué esta explicación podría estar incompleta."
    )
    expected_bundle = ("reasoning", "planning", "reflection", "executive")

    a5_bundle_is_coarse = (
        generic == ()
        and reasoning_request == expected_bundle
        and planning_request == expected_bundle
        and reflection_request == expected_bundle
    )

    planner = CognitivePlanner()
    novel_text = (
        "¿Te acordás de nuestra restricción anterior y qué clima hay hoy "
        "para evaluar la decisión?"
    )
    shadow_plan = planner.plan(novel_text)
    shadow_multitool = shadow_plan.required_tools == (
        ToolRequirement.MEMORY,
        ToolRequirement.WEATHER,
    )
    no_explicit_clause_separator = all(
        token not in novel_text.casefold()
        for token in (
            ";",
            " además ",
            " tambien ",
            " también ",
            " despues ",
            " después ",
        )
    )

    planning_shadow = next(
        item
        for item in CANONICAL_PLANNING_COMPONENTS
        if item.key == "cognitive_planner_shadow"
    )
    decision_primary = next(
        item
        for item in CANONICAL_DECISION_COMPONENTS
        if item.key == "unified_cognitive_coordination"
    )
    decision_shadow = next(
        item
        for item in CANONICAL_DECISION_COMPONENTS
        if item.key == "cognitive_planning_shadow_decision"
    )

    novel_operational_text = (
        "Evaluá mi restricción anterior junto con el clima actual y proponé "
        "cómo debería decidir, sin ejecutar nada."
    )
    scenario = UnifiedCognitiveCoordinator._detect_scenario(novel_operational_text)

    a6_shadow_can_represent = (
        shadow_multitool
        and no_explicit_clause_separator
        and _role(planning_shadow) == "shadow"
        and not _operational(planning_shadow)
    )
    a6_shadow_decision_nonoperational = _role(
        decision_shadow
    ) == "shadow" and not _operational(decision_shadow)

    gates = (
        GateResult(
            gate_id="A5",
            title="Problem-driven cognitive stage relevance",
            status=Status.PARTIAL,
            evidence=(
                f"generic_activated_stages={generic}",
                f"reasoning_prompt_activated_stages={reasoning_request}",
                f"planning_prompt_activated_stages={planning_request}",
                f"reflection_prompt_activated_stages={reflection_request}",
                f"coarse_bundle_confirmed={a5_bundle_is_coarse}",
            ),
            conclusion=(
                "The official source distinguishes cognitive versus non-cognitive "
                "turns, but its current trigger is shared by reasoning, planning, "
                "reflection, and executive coordination. Stage-by-stage relevance "
                "selection is therefore not causally demonstrated."
            ),
        ),
        GateResult(
            gate_id="A6",
            title="Novel advisory composition through existing authorities",
            status=Status.PARTIAL,
            evidence=(
                (
                    "shadow_required_tools="
                    f"{tuple(item.value for item in shadow_plan.required_tools)}"
                ),
                f"shadow_multitool_without_explicit_clause_split={a6_shadow_can_represent}",
                f"planning_shadow_role={_role(planning_shadow)}",
                f"planning_shadow_operational={_operational(planning_shadow)}",
                f"decision_primary_role={_role(decision_primary)}",
                f"decision_primary_operational={_operational(decision_primary)}",
                f"novel_primary_scenario={scenario}",
                f"decision_shadow_nonoperational={a6_shadow_decision_nonoperational}",
            ),
            conclusion=(
                "Existing shadow planning can represent a multi-need composition "
                "without explicit clause routing, but it is intentionally "
                "non-operational. The operational Decision primary does not recognize "
                "the novel problem outside its predeclared scenarios. A6 therefore "
                "cannot close by certification alone."
            ),
        ),
        GateResult(
            gate_id="G1",
            title="Execution authority remains unchanged",
            status=Status.PASS_BY_DESIGN,
            evidence=(
                "planning_shadow_remains_nonoperational",
                "decision_shadow_remains_nonoperational",
                "no_new_execution_route_created",
            ),
            conclusion=(
                "The diagnostic preserves the authority map and does not promote "
                "shadow components or bypass the official execution authority."
            ),
        ),
    )

    after = _production_fingerprint(root)
    if before != after:
        raise RuntimeError("production fingerprint changed during certification")

    counts = {
        status.value: sum(item.status is status for item in gates) for status in Status
    }
    a5_closed = (
        next(item for item in gates if item.gate_id == "A5").status is Status.PASS
    )
    a6_closed = (
        next(item for item in gates if item.gate_id == "A6").status is Status.PASS
    )
    existing_authority_closure = a5_closed and a6_closed

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline": "12615_passed_ruff_clean_user_validated",
        "diagnostic_only": True,
        "production_roots_modified_by_certification": [],
        "production_fingerprint_before": before,
        "production_fingerprint_after": after,
        "production_fingerprint_preserved": before == after,
        "gates": [asdict(item) for item in gates],
        "status_counts": counts,
        "a5_certified": a5_closed,
        "a6_certified": a6_closed,
        "existing_authority_composition_certified": existing_authority_closure,
        "closure_status": "PASS" if existing_authority_closure else "PARTIAL",
        "architectural_result": (
            "CERTIFICATION_ONLY_CLOSURE"
            if existing_authority_closure
            else "MINIMAL_PRODUCTION_CONTRACT_JUSTIFIED"
        ),
        "production_authorized": False,
        "next_gate": (
            "closure_documentation"
            if existing_authority_closure
            else "minimal_production_contract_a5_a6"
        ),
    }


def _run_self_tests(root: Path) -> tuple[int, str]:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/diagnostics/test_l3_existing_authority_composition_certification.py",
        ],
        cwd=root,
        text=True,
        capture_output=True,
    )
    output = (cp.stdout + "\n" + cp.stderr).strip()
    clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
    matches = re.findall(
        r"\b\d+\s+(?:passed|failed|error|errors|skipped)\b[^\n]*",
        clean,
        flags=re.IGNORECASE,
    )
    summary = matches[-1].strip() if matches else "no pytest summary"
    return cp.returncode, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--with-self-tests", action="store_true")
    args = parser.parse_args()

    report = evaluate()
    if args.with_self_tests:
        rc, summary = _run_self_tests(PROJECT_ROOT)
        report["self_test_returncode"] = rc
        report["self_test_summary"] = summary
        if rc != 0:
            report["architectural_result"] = "DIAGNOSTIC_HARNESS_FAILURE"

    payload = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 1 if report.get("self_test_returncode", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
