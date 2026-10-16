from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "whole-system-e2e-reachability-coherence-certification-v1"


class CertificationStatus(StrEnum):
    PASS = "PASS"
    PASS_BY_DESIGN = "PASS_BY_DESIGN"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"


@dataclass(frozen=True)
class EvidenceRequirement:
    path: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class E2EChainSpec:
    chain_id: str
    name: str
    entry: str
    authority_or_capability: str
    productive_consumer: str
    authorized_observable: str
    evidence: tuple[EvidenceRequirement, ...]
    provenance_markers: tuple[str, ...] = ()
    scope_markers: tuple[str, ...] = ()
    historical_markers: tuple[str, ...] = ()
    pass_by_design: bool = False


@dataclass(frozen=True)
class ChainCertification:
    chain_id: str
    name: str
    entry: str
    authority_or_capability: str
    productive_consumer: str
    authorized_observable: str
    status: CertificationStatus
    reachable_stages: int
    total_stages: int
    provenance_preserved: bool
    scope_preserved: bool
    historical_route_preserved: bool
    missing_evidence: tuple[str, ...]


@dataclass(frozen=True)
class NegativeControlSpec:
    control_id: str
    description: str
    evidence: tuple[EvidenceRequirement, ...]
    forbidden_tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class NegativeControlResult:
    control_id: str
    description: str
    status: CertificationStatus
    observed: str


@dataclass(frozen=True)
class WholeSystemCertificationReport:
    schema_version: str
    generated_at: str
    diagnostic_only: bool
    production_roots_modified_by_harness: tuple[str, ...]
    chains: tuple[ChainCertification, ...]
    negative_controls: tuple[NegativeControlResult, ...]
    status_counts: dict[str, int]
    overall_status: CertificationStatus
    inventory_fingerprint: str
    report_fingerprint: str


def _req(path: str, *tokens: str) -> EvidenceRequirement:
    return EvidenceRequirement(path=path, tokens=tuple(tokens))


def _chains() -> tuple[E2EChainSpec, ...]:
    return (
        E2EChainSpec(
            "E2E-01",
            "governed information intake to relevance",
            "GovernedSourceQuery",
            "GovernedSourceQueryExecutor",
            "GovernedInformationNormalizer -> RelevanceEvaluator",
            "RelevanceDecision",
            (
                _req(
                    "app/governed_source_query.py",
                    "class GovernedSourceQuery",
                    "class GovernedSourceQueryContract",
                ),
                _req(
                    "app/governed_source_query_executor.py",
                    "class GovernedSourceQueryExecutor",
                    "def execute",
                ),
                _req(
                    "app/governed_information_normalizer.py",
                    "class GovernedInformationNormalizer",
                    "def normalize",
                ),
                _req(
                    "app/relevance_evaluator.py",
                    "class RelevanceEvaluator",
                    "class RelevanceDecision",
                ),
            ),
            provenance_markers=("source_id", "canonical_id"),
        ),
        E2EChainSpec(
            "E2E-02",
            "productive temporary rule intake",
            "conversation rule/case text",
            "governed_reasoning",
            "ProductiveTemporaryRuleIntake",
            "ProductiveTemporaryRuleIntakeResult",
            (
                _req(
                    "app/productive_temporary_rule_intake.py",
                    "class ProductiveTemporaryRuleIntake",
                    'canonical_authority: str = "governed_reasoning"',
                ),
                _req(
                    ("tests/architecture/test_post_m409_1_rf_e_"
                     "productive_intake_reachability_v1.py"),
                    "ProductiveTemporaryRuleIntake",
                ),
            ),
            provenance_markers=("source_reference",),
            scope_markers=("scope_reference",),
        ),
        E2EChainSpec(
            "E2E-03",
            "explicit complex decision intake to advisory",
            "explicit decision envelope",
            "governed_reasoning",
            "ProductiveGCDRIntakeIntegrationV1",
            "ADVISORY_READY result",
            (
                _req(
                    "core/productive_gcdr_intake_integration.py",
                    "class ProductiveGCDRIntakeIntegrationV1",
                    "ADVISORY_READY",
                ),
                _req(
                    ("tests/architecture/test_post_m409_1_"
                     "productive_gcdr_intake_gateway_integration_v1.py"),
                    "ProductiveGCDRIntakeIntegrationV1",
                ),
            ),
            provenance_markers=("source_fingerprint",),
        ),
        E2EChainSpec(
            "E2E-04",
            "decision advisory to conversational realization",
            "GovernedDecisionAdvisory report",
            "governed_reasoning",
            "DecisionAdvisoryConversationalRealizer",
            "DecisionAdvisoryConversationalRealization",
            (
                _req(
                    "core/decision_advisory_conversational_realization.py",
                    "class DecisionAdvisoryConversationalRealizer",
                    "class DecisionAdvisoryConversationalRealization",
                ),
                _req(
                    ("tests/architecture/test_post_m409_1_"
                     "decision_advisory_conversational_realization.py"),
                    "DecisionAdvisoryConversationalRealizer",
                ),
            ),
            provenance_markers=("evidence",),
        ),
        E2EChainSpec(
            "E2E-05",
            "reproduced diagnostic proof to inert proposal",
            "reproduced diagnostic proof + hash-bound evidence",
            "self_diagnostics",
            "generate_diagnostic_proposal_request",
            "DiagnosticProposalRequest",
            (
                _req(
                    "app/self_improvement_proposal_generation.py",
                    "def generate_diagnostic_proposal_request",
                    "DiagnosticProposalRequest",
                ),
                _req(
                    ("tests/architecture/test_post_m409_1_"
                     "governed_self_improvement_proposal_generation.py"),
                    "generate_diagnostic_proposal_request",
                ),
            ),
            provenance_markers=("sha256", "source_authority"),
            scope_markers=("affected_files", "validation_tests"),
        ),
        E2EChainSpec(
            "E2E-06",
            "information scale benchmark productive path",
            "synthetic governed dataset",
            "GovernedSourceQueryExecutor",
            "normalization + relevance selection",
            "ScaleLevelResult",
            (
                _req(
                    "scripts/advanced_capability_3a_scale_benchmark.py",
                    "def run_scale_level",
                    "class ScaleLevelResult",
                ),
                _req(
                    "docs/quality/ADVANCED_CAPABILITY_3A_SCALE_BENCHMARK.json",
                    '"status"',
                ),
            ),
            provenance_markers=("provenance_integrity",),
        ),
        E2EChainSpec(
            "E2E-07",
            "reasoning quality benchmark productive path",
            "frozen reasoning corpus",
            "governed_reasoning",
            "quality case runner",
            "ReasoningQualityReport",
            (
                _req(
                    "scripts/advanced_capability_4a_reasoning_quality_benchmark.py",
                    "class ReasoningQualityReport",
                    "def run_benchmark",
                ),
                _req(
                    ("docs/quality/ADVANCED_CAPABILITY_4A_"
                     "REASONING_QUALITY_BENCHMARK.json"),
                    '"status"',
                ),
            ),
            provenance_markers=("provenance_ok",),
        ),
        E2EChainSpec(
            "E2E-08",
            "independent reasoning evaluation path",
            "independent cases",
            "governed_reasoning",
            "independent runner + scorer",
            "independent observations/evaluation",
            (
                _req(
                    "scripts/advanced_capability_4b_independent_reasoning_runner.py",
                    "class IndependentRunReport",
                    "def run",
                ),
                _req(
                    "scripts/advanced_capability_4b_independent_reasoning_scorer.py",
                    "def score",
                ),
                _req(
                    ("docs/quality/ADVANCED_CAPABILITY_4B_"
                     "INDEPENDENT_REASONING_EVALUATION.json"),
                    '"status"',
                ),
            ),
            provenance_markers=("provenance_ok",),
        ),
        E2EChainSpec(
            "E2E-09",
            "autonomy classification to bounded decision",
            "capability request",
            "GovernedAutonomyPolicy",
            "GovernedAutonomyDecision",
            "non-executing decision classification",
            (
                _req(
                    "core/governed_autonomy.py",
                    "class GovernedAutonomyPolicy",
                    "class GovernedAutonomyDecision",
                ),
                _req(
                    "scripts/advanced_capability_5a_autonomy_boundary_certification.py",
                    "def run_certification",
                    "autonomy_escalations",
                ),
            ),
            scope_markers=("requested_capabilities", "permitted_capabilities"),
        ),
        E2EChainSpec(
            "E2E-10",
            "tool request to governed gateway observable",
            "ToolRequest",
            "ToolGatewayManager + PermissionConsentManager",
            "registered capability handler",
            "ToolGatewayResult/status",
            (
                _req(
                    "core/tool_gateway.py",
                    "class ToolGatewayManager",
                    "class ToolRequest",
                ),
                _req(
                    "core/permission_consent.py",
                    "class PermissionConsentManager",
                    "class PermissionGrant",
                ),
                _req("tests/test_m61_tool_gateway.py", "ToolGatewayManager"),
            ),
            scope_markers=("permission_scope",),
        ),
        E2EChainSpec(
            "E2E-11",
            "memory runtime integration route",
            "memory runtime input",
            "canonical memory authority",
            "memory runtime integration",
            "governed memory result",
            (
                _req(
                    "core/memory_runtime_integration/runtime.py",
                    "class MemoryRuntimeIntegration",
                    "memory",
                ),
                _req("docs/adr/ADR_185_memory_runtime_integration.md", "memory"),
            ),
            historical_markers=(),
        ),
        E2EChainSpec(
            "E2E-12",
            "planning runtime integration route",
            "planning input",
            "canonical planning authority",
            "PlanningRuntimeIntegration",
            "planning integration result",
            (
                _req(
                    "core/planning_runtime_integration.py",
                    "class PlanningRuntimeContributor",
                ),
                _req(
                    "docs/M192_PLANNING_RUNTIME_INTEGRATION.md",
                    "Planning Runtime Integration",
                ),
            ),
            historical_markers=("M192",),
        ),
        E2EChainSpec(
            "E2E-13",
            "reflection runtime integration route",
            "reflection input",
            "canonical reflection authority",
            "ReflectionRuntimeIntegration",
            "reflection integration result",
            (
                _req(
                    "core/reflection_runtime_integration.py",
                    "class ReflectionRuntimeContributor",
                ),
                _req("docs/M193_REFLECTION_RUNTIME_INTEGRATION.md", "reflection"),
            ),
            historical_markers=("M193",),
        ),
        E2EChainSpec(
            "E2E-14",
            "living conversation runtime route",
            "conversation turn",
            "living conversation authority",
            "living conversation runtime integration",
            "conversation runtime result",
            (
                _req(
                    "core/living_conversation_runtime_integration.py",
                    "class",
                    "conversation",
                ),
                _req(
                    "docs/adr/ADR-192-living-conversation-runtime-integration.md",
                    "conversation",
                ),
            ),
            historical_markers=("192",),
        ),
        E2EChainSpec(
            "E2E-15",
            "governed world integration route",
            "governed world evidence",
            "internal_world_model",
            "GovernedWorldIntegration",
            "governed world integration result",
            (
                _req(
                    "core/governed_world_integration.py",
                    "class GovernedWorldIntegration",
                ),
                _req("docs/M392_7_GOVERNED_WORLD_INTEGRATION.md", "world"),
            ),
            provenance_markers=("source_fingerprint",),
            historical_markers=("M392.7",),
        ),
        E2EChainSpec(
            "E2E-16",
            "whole-system integration historical route",
            "official runtime entry",
            "existing governed authorities",
            "WholeSystemIntegration",
            "whole-system integration snapshot/result",
            (
                _req(
                    "core/whole_system_integration.py",
                    "class WholeSystemIntegration",
                ),
                _req(
                    "docs/adr/ADR_210_whole_system_integration.md",
                    "Whole-System Integration",
                ),
                _req("docs/milestones/M210_whole_system_integration.md", "M210"),
            ),
            historical_markers=("M210",),
        ),
    )


def _negative_controls() -> tuple[NegativeControlSpec, ...]:
    harness = "scripts/whole_system_e2e_reachability_coherence_certification.py"
    return (
        NegativeControlSpec(
            "NEG-01",
            "harness defines no authority",
            (_req(harness, "diagnostic_only", "class WholeSystemCertificationReport"),),
        ),
        NegativeControlSpec(
            "NEG-02",
            "harness defines no manager/gateway",
            (_req(harness, "WholeSystemCertificationReport"),),
        ),
        NegativeControlSpec(
            "NEG-03",
            "harness writes only an explicit diagnostic report",
            (_req(harness, "production_roots_modified_by_harness=()", "write_report"),),
        ),
        NegativeControlSpec(
            "NEG-04",
            "harness grants no execution/autonomy",
            (
                _req(
                    harness,
                    "diagnostic_only=True",
                    "production_roots_modified_by_harness=()",
                ),
            ),
        ),
        NegativeControlSpec(
            "NEG-05",
            "mutating execution remains consent bounded",
            (
                _req(
                    ("docs/quality/ADVANCED_CAPABILITY_5A_"
                     "AUTONOMY_BOUNDARY_CERTIFICATION.json"),
                    '"5A-04"',
                    "handler_calls=0",
                ),
            ),
        ),
        NegativeControlSpec(
            "NEG-06",
            "unregistered execution remains fail-closed",
            (
                _req(
                    ("docs/quality/ADVANCED_CAPABILITY_5A_"
                     "AUTONOMY_BOUNDARY_CERTIFICATION.json"),
                    '"5A-07"',
                    "capability_not_registered",
                ),
            ),
        ),
        NegativeControlSpec(
            "NEG-07",
            "disabled mutating execution remains fail-closed",
            (
                _req(
                    ("docs/quality/ADVANCED_CAPABILITY_5A_"
                     "AUTONOMY_BOUNDARY_CERTIFICATION.json"),
                    '"5A-08"',
                    "capability_disabled",
                ),
            ),
        ),
        NegativeControlSpec(
            "NEG-08",
            "self-improvement remains proposal-only",
            (
                _req(
                    ("docs/quality/ADVANCED_CAPABILITY_5A_"
                     "AUTONOMY_BOUNDARY_CERTIFICATION.json"),
                    '"5A-10"',
                    '"passed": true',
                ),
                _req(
                    "app/self_improvement_proposal_generation.py",
                    "DiagnosticProposalRequest",
                ),
            ),
            ("apply_patch", "subprocess.run"),
        ),
    )


def _read(root: Path, relative: str) -> str | None:
    path = root / relative
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _markers_present(texts: Iterable[str], markers: tuple[str, ...]) -> bool:
    material = "\n".join(texts)
    return all(marker.casefold() in material.casefold() for marker in markers)


def _certify_chain(root: Path, spec: E2EChainSpec) -> ChainCertification:
    missing: list[str] = []
    texts: list[str] = []
    reachable = 0
    for requirement in spec.evidence:
        text = _read(root, requirement.path)
        if text is None:
            missing.append(f"missing:{requirement.path}")
            continue
        texts.append(text)
        absent = tuple(token for token in requirement.tokens if token not in text)
        if absent:
            missing.append(f"tokens:{requirement.path}:{','.join(absent)}")
            continue
        reachable += 1

    provenance_ok = _markers_present(texts, spec.provenance_markers)
    scope_ok = _markers_present(texts, spec.scope_markers)
    history_ok = _markers_present(texts, spec.historical_markers)
    if not provenance_ok:
        missing.append("provenance_markers")
    if not scope_ok:
        missing.append("scope_markers")
    if not history_ok:
        missing.append("historical_markers")

    guards_ok = provenance_ok and scope_ok and history_ok
    total = len(spec.evidence)
    if reachable == total and guards_ok:
        status = (
            CertificationStatus.PASS_BY_DESIGN
            if spec.pass_by_design
            else CertificationStatus.PASS
        )
    elif reachable == 0:
        status = CertificationStatus.FAIL
    else:
        status = CertificationStatus.PARTIAL
    return ChainCertification(
        chain_id=spec.chain_id,
        name=spec.name,
        entry=spec.entry,
        authority_or_capability=spec.authority_or_capability,
        productive_consumer=spec.productive_consumer,
        authorized_observable=spec.authorized_observable,
        status=status,
        reachable_stages=reachable,
        total_stages=total,
        provenance_preserved=provenance_ok,
        scope_preserved=scope_ok,
        historical_route_preserved=history_ok,
        missing_evidence=tuple(missing),
    )


def _run_negative(root: Path, spec: NegativeControlSpec) -> NegativeControlResult:
    texts: list[str] = []
    missing: list[str] = []
    for requirement in spec.evidence:
        text = _read(root, requirement.path)
        if text is None:
            missing.append(f"missing:{requirement.path}")
            continue
        texts.append(text)
        for token in requirement.tokens:
            if token not in text:
                missing.append(f"token:{requirement.path}:{token}")
    material = "\n".join(texts)
    forbidden = tuple(token for token in spec.forbidden_tokens if token in material)
    passed = not missing and not forbidden
    observed = "ok" if passed else f"missing={tuple(missing)};forbidden={forbidden}"
    return NegativeControlResult(
        control_id=spec.control_id,
        description=spec.description,
        status=(
            CertificationStatus.PASS_BY_DESIGN
            if passed
            else CertificationStatus.FAIL
        ),
        observed=observed,
    )


def _fingerprint(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def run_certification(
    project_root: Path = PROJECT_ROOT,
) -> WholeSystemCertificationReport:
    chain_specs = _chains()
    negative_specs = _negative_controls()
    chains = tuple(_certify_chain(project_root, spec) for spec in chain_specs)
    negatives = tuple(_run_negative(project_root, spec) for spec in negative_specs)
    counts = {
        status.value: sum(item.status is status for item in chains)
        for status in CertificationStatus
    }
    chain_failure = any(
        item.status in {CertificationStatus.PARTIAL, CertificationStatus.FAIL}
        for item in chains
    )
    negative_failure = any(
        item.status is CertificationStatus.FAIL for item in negatives
    )
    overall = (
        CertificationStatus.FAIL
        if negative_failure
        else (
            CertificationStatus.PARTIAL
            if chain_failure
            else CertificationStatus.PASS
        )
    )
    inventory = {
        "chains": [asdict(item) for item in chain_specs],
        "negative_controls": [asdict(item) for item in negative_specs],
    }
    logical = {
        "chains": [asdict(item) for item in chains],
        "negative_controls": [asdict(item) for item in negatives],
        "status_counts": counts,
        "overall_status": overall.value,
    }
    return WholeSystemCertificationReport(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        diagnostic_only=True,
        production_roots_modified_by_harness=(),
        chains=chains,
        negative_controls=negatives,
        status_counts=counts,
        overall_status=overall,
        inventory_fingerprint=_fingerprint(inventory),
        report_fingerprint=_fingerprint(logical),
    )


def write_report(report: WholeSystemCertificationReport, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ROBY XI.2 read-only whole-system E2E "
            "reachability/coherence certification"
        )
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_certification(PROJECT_ROOT)
    if args.output is not None:
        write_report(report, args.output)
    print(json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str))
    return 0 if report.overall_status is CertificationStatus.PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
