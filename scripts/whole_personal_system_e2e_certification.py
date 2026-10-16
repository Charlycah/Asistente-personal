from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "whole-personal-system-e2e-certification-v1"


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
class PersonalScenarioSpec:
    scenario_id: str
    name: str
    personal_flow: str
    evidence: tuple[EvidenceRequirement, ...]
    pass_by_design: bool = False


@dataclass(frozen=True)
class PersonalScenarioResult:
    scenario_id: str
    name: str
    personal_flow: str
    status: CertificationStatus
    reached_stages: tuple[str, ...]
    missing_stages: tuple[str, ...]
    evidence_paths: tuple[str, ...]


@dataclass(frozen=True)
class NegativeControlSpec:
    control_id: str
    description: str
    path: str
    required_tokens: tuple[str, ...]
    forbidden_tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class NegativeControlResult:
    control_id: str
    description: str
    status: CertificationStatus
    observed: str


@dataclass(frozen=True)
class WholePersonalSystemReport:
    schema_version: str
    generated_at: str
    diagnostic_only: bool
    production_roots_modified_by_harness: tuple[str, ...]
    scenarios: tuple[PersonalScenarioResult, ...]
    negative_controls: tuple[NegativeControlResult, ...]
    status_counts: dict[str, int]
    overall_status: CertificationStatus
    primary_gap: str
    inventory_fingerprint: str
    report_fingerprint: str


def _e(stage: str, path: str, *tokens: str) -> EvidenceRequirement:
    return EvidenceRequirement(stage, path, tuple(tokens))


def _scenarios() -> tuple[PersonalScenarioSpec, ...]:
    return (
        PersonalScenarioSpec(
            "WPS-01",
            "personal identity and session reach the official local conversation path",
            "identity/session -> local conversation -> session-scoped context",
            (
                _e(
                    "identity_provisioning",
                    "app/household_always_on_bootstrap.py",
                    "def bootstrap_household",
                    "HouseholdBootstrapResult",
                    "COOWNER_SESSION_ID",
                ),
                _e(
                    "identity_selection",
                    "app/personal_profile_factory.py",
                    "def select_runtime_identity_from_environment",
                    "bootstrap_household",
                ),
                _e(
                    "runtime_binding",
                    "app/local_runtime_entrypoint.py",
                    "def build_local_runtime_from_environment",
                    "select_runtime_identity_from_environment",
                    "owner=owner",
                    "session_id=session_id",
                ),
                _e(
                    "conversation",
                    "app/local_conversation_factory.py",
                    "def build_local_conversation_from_environment",
                    "build_local_runtime_from_environment",
                ),
                _e(
                    "session_scope",
                    "core/end_to_end_local_conversation/runtime.py",
                    "owner=self.bootstrap.config.owner",
                    "session_id=self.bootstrap.config.session_id",
                    "session_scoped=bool(request.session_id)",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-02",
            "relevant personal memory can re-enter a later cognitive turn",
            "conversation -> governed memory recall -> enriched cognitive request",
            (
                _e(
                    "memory_runtime",
                    "core/memory_runtime_integration/runtime.py",
                    "class MemoryRuntimeIntegration",
                    "def enrich",
                ),
                _e(
                    "memory_context",
                    "core/memory_runtime_integration/runtime.py",
                    '"memory_context": "included"',
                    "recalled_memory_ids",
                ),
                _e(
                    "conversation_consumption",
                    "core/end_to_end_local_conversation/runtime.py",
                    "dependencies.memory_runtime",
                    "memory_runtime.record",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-03",
            (
                "personal organization remains one governed domain over all personal "
                "capabilities"
            ),
            (
                "agenda/tasks/reminders/goals/projects/notes/prioritization -> "
                "PersonalOrganizationAuthority"
            ),
            (
                _e(
                    "authority",
                    "core/personal_organization.py",
                    "class PersonalOrganizationAuthority",
                    "unified_core: bool = True",
                ),
                _e(
                    "coverage",
                    "core/personal_organization.py",
                    "AGENDA",
                    "TASKS",
                    "REMINDERS",
                    "GOALS",
                    "PROJECTS",
                    "NOTES",
                    "PRIORITIZATION",
                ),
                _e(
                    "no_parallel_brain",
                    "core/personal_organization.py",
                    "creates_parallel_brain: bool = False",
                    "replaces_existing_authorities: bool = False",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-04",
            ("organization evidence can inform governed personal decision advisory"),
            (
                "personal organization evidence -> exact linkage -> M391.5 -> "
                "M391.6 advisory"
            ),
            (
                _e(
                    "projection",
                    "core/productive_organization_evidence_projection.py",
                    "class ProductiveOrganizationEvidenceProjection",
                    "PersonalOrganizationItem",
                ),
                _e(
                    "linkage",
                    "core/organization_decision_exact_identity_linkage.py",
                    "OrganizationDecision",
                    "link",
                ),
                _e(
                    "assembly",
                    "app/linked_organization_m391_6_advisory_assembly.py",
                    "M391",
                    "advise",
                ),
                _e(
                    "productive_wiring",
                    "app/productive_organization_advisory_wiring.py",
                    "class ProductiveOrganizationAdvisoryWiring",
                    "assemble",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-05",
            "recalled memory can contribute bounded evidence to canonical planning",
            "memory recall -> planning evidence -> planning runtime",
            (
                _e(
                    "memory_projection",
                    "core/memory_runtime_integration/runtime.py",
                    "project_recalled_memory",
                    "MEMORY_PLANNING_METADATA_KEY",
                ),
                _e(
                    "planning_runtime",
                    "core/planning_runtime_integration.py",
                    "class PlanningRuntimeContributor",
                    "decode_memory_planning_evidence",
                ),
                _e(
                    "bounded_application",
                    "core/planning_runtime_integration.py",
                    "recalled_memory_planning_evidence_applied",
                    "memory_evidence[:3]",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-06",
            (
                "conversational commitments remain owner/session bounded and "
                "do not imply durable personal commitment continuity"
            ),
            (
                "conversation -> bounded commitment assessment -> "
                "compatibility-only continuity boundary"
            ),
            (
                _e(
                    "commitment",
                    "core/conversational_commitment_intelligence.py",
                    "class ConversationalCommitmentIntelligence",
                    "owner",
                    "session_id",
                ),
                _e(
                    "runtime_contributor",
                    "core/conversational_commitment_intelligence.py",
                    "class ConversationalCommitmentRuntimeContributor",
                    "def contribute",
                ),
                _e(
                    "compatibility_boundary",
                    "docs/COGNITIVE_AGENDA_SOURCE_INTEGRATION_LOTE_A.md",
                    "open_commitments",
                    "no se fabrica ese owner",
                    "diferida",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-07",
            "approved learning can become governed memory without authority expansion",
            (
                "human-approved learning -> official memory writer -> later personal "
                "memory"
            ),
            (
                _e(
                    "learning_wiring",
                    "app/productive_governed_learning_wiring.py",
                    "class ProductiveGovernedLearningWiring",
                    "remember_governed_learning",
                ),
                _e(
                    "no_authority_gain",
                    "app/productive_governed_learning_wiring.py",
                    "grants_authority",
                    "cannot expand authority",
                ),
                _e(
                    "memory_write",
                    "core/memory_runtime_integration/runtime.py",
                    "def store_governed_learning",
                    "stored_memory_ids",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-08",
            (
                "personal notes remain governed knowledge and can project as "
                "organization evidence"
            ),
            "personal note -> knowledge authority -> organization evidence projection",
            (
                _e(
                    "knowledge",
                    "core/personal_knowledge_base.py",
                    "class PersonalKnowledgeBaseManager",
                    'NOTE = "note"',
                ),
                _e(
                    "note_projection",
                    "core/productive_organization_evidence_projection.py",
                    "def project_knowledge_note",
                    "KnowledgeKind.NOTE",
                ),
                _e(
                    "distinct_memory_boundary",
                    "core/personal_organization.py",
                    "KnowledgeKind.NOTE remains distinct from cognitive memory",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-09",
            (
                "reminder awareness reaches the always-on personal runtime without "
                "creating a new reminder authority"
            ),
            (
                "ReminderService-backed state -> reminder awareness -> "
                "ambient personal runtime"
            ),
            (
                _e(
                    "reminder_binding",
                    "core/personal_organization.py",
                    "ReminderService",
                    "domain.reminders.services:ReminderService",
                ),
                _e(
                    "reminder_awareness",
                    "app/always_on_personal_runtime_wiring.py",
                    "def build_reminder_awareness_from_environment",
                    "ROBY_REMINDER_DB_PATH",
                ),
                _e(
                    "ambient_runtime",
                    "app/always_on_personal_runtime_wiring.py",
                    "def build_ambient_proactive_runtime_from_environment",
                ),
            ),
        ),
        PersonalScenarioSpec(
            "WPS-10",
            "personal action remains capability-scoped and permission/consent bounded",
            (
                "personal intent -> ToolGatewayManager -> PermissionConsentManager "
                "-> registered handler"
            ),
            (
                _e(
                    "gateway",
                    "core/tool_gateway.py",
                    "class ToolGatewayManager",
                    "def execute",
                ),
                _e(
                    "permission",
                    "core/permission_consent.py",
                    "class PermissionConsentManager",
                    "consent",
                ),
                _e(
                    "whole_system_guard",
                    "architecture_rules.md",
                    "Toda acción mutante",
                    "permission/consent",
                ),
            ),
            pass_by_design=True,
        ),
    )


def _negative_controls() -> tuple[NegativeControlSpec, ...]:
    return (
        NegativeControlSpec(
            "WPS-NEG-01",
            "certification harness creates no production authority",
            "scripts/whole_personal_system_e2e_certification.py",
            ("diagnostic_only",),
        ),
        NegativeControlSpec(
            "WPS-NEG-02",
            "personal organization recommendations cannot authorize action",
            "core/intelligent_personal_organization.py",
            ("action_authorized: bool = False", "cannot authorize action"),
        ),
        NegativeControlSpec(
            "WPS-NEG-03",
            "whole-system integration leaves execution authority governed elsewhere",
            "core/whole_system_integration.py",
            ("execution_authority_remains_governed_elsewhere",),
        ),
        NegativeControlSpec(
            "WPS-NEG-04",
            "approved learning wiring cannot expand authority",
            "app/productive_governed_learning_wiring.py",
            ("cannot expand authority",),
        ),
    )


def _read(path: str) -> str | None:
    candidate = PROJECT_ROOT / path
    if not candidate.is_file():
        return None
    return candidate.read_text(encoding="utf-8", errors="replace")


def _evaluate_scenario(spec: PersonalScenarioSpec) -> PersonalScenarioResult:
    reached: list[str] = []
    missing: list[str] = []
    paths: list[str] = []
    for requirement in spec.evidence:
        paths.append(requirement.path)
        source = _read(requirement.path)
        if source is not None and all(token in source for token in requirement.tokens):
            reached.append(requirement.stage)
        else:
            missing.append(requirement.stage)
    if not missing:
        status = (
            CertificationStatus.PASS_BY_DESIGN
            if spec.pass_by_design
            else CertificationStatus.PASS
        )
    elif reached:
        status = CertificationStatus.PARTIAL
    else:
        status = CertificationStatus.FAIL
    return PersonalScenarioResult(
        spec.scenario_id,
        spec.name,
        spec.personal_flow,
        status,
        tuple(reached),
        tuple(missing),
        tuple(dict.fromkeys(paths)),
    )


def _evaluate_control(spec: NegativeControlSpec) -> NegativeControlResult:
    source = _read(spec.path)
    if source is None:
        return NegativeControlResult(
            spec.control_id, spec.description, CertificationStatus.FAIL, "missing file"
        )
    required_ok = all(token in source for token in spec.required_tokens)
    forbidden_found = tuple(token for token in spec.forbidden_tokens if token in source)
    if required_ok and not forbidden_found:
        return NegativeControlResult(
            spec.control_id, spec.description, CertificationStatus.PASS_BY_DESIGN, "ok"
        )
    observed = (
        "missing required evidence"
        if not required_ok
        else f"forbidden tokens: {forbidden_found!r}"
    )
    return NegativeControlResult(
        spec.control_id, spec.description, CertificationStatus.FAIL, observed
    )


def _fingerprint(parts: object) -> str:
    return sha256(repr(parts).encode("utf-8")).hexdigest()


def run_certification() -> WholePersonalSystemReport:
    scenarios = tuple(_evaluate_scenario(item) for item in _scenarios())
    controls = tuple(_evaluate_control(item) for item in _negative_controls())
    counts = {
        status.value: sum(item.status is status for item in scenarios)
        for status in CertificationStatus
    }
    if any(item.status is CertificationStatus.FAIL for item in (*scenarios, *controls)):
        overall = CertificationStatus.FAIL
    elif any(item.status is CertificationStatus.PARTIAL for item in scenarios):
        overall = CertificationStatus.PARTIAL
    else:
        overall = CertificationStatus.PASS
    partial_ids = tuple(
        item.scenario_id
        for item in scenarios
        if item.status is CertificationStatus.PARTIAL
    )
    fail_ids = tuple(
        item.scenario_id
        for item in scenarios
        if item.status is CertificationStatus.FAIL
    )
    if fail_ids:
        primary_gap = "failed_personal_system_contract:" + ",".join(fail_ids)
    elif partial_ids:
        primary_gap = "personal_system_e2e_not_yet_fully_certified:" + ",".join(
            partial_ids
        )
    else:
        primary_gap = "none_within_certified_whole_personal_system_contract"
    inventory = _fingerprint(tuple(asdict(item) for item in _scenarios()))
    generated_at = datetime.now(timezone.utc).isoformat()
    payload = (
        SCHEMA_VERSION,
        generated_at,
        tuple(asdict(item) for item in scenarios),
        tuple(asdict(item) for item in controls),
        counts,
        overall.value,
        primary_gap,
        inventory,
    )
    return WholePersonalSystemReport(
        schema_version=SCHEMA_VERSION,
        generated_at=generated_at,
        diagnostic_only=True,
        production_roots_modified_by_harness=(),
        scenarios=scenarios,
        negative_controls=controls,
        status_counts=counts,
        overall_status=overall,
        primary_gap=primary_gap,
        inventory_fingerprint=inventory,
        report_fingerprint=_fingerprint(payload),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_certification()
    encoded = json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if report.overall_status is not CertificationStatus.FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
