from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.governed_autonomy import (  # noqa: E402
    GovernedAutonomyDecision,
    GovernedAutonomyPolicy,
    GovernedAutonomyStatus,
)
from core.permission_consent import (  # noqa: E402
    PermissionConsentManager,
    PermissionGrant,
)
from core.tool_gateway import (  # noqa: E402
    ToolCapability,
    ToolGatewayManager,
    ToolGatewayStatus,
    ToolRequest,
)  # noqa: E402
from domain.governed_action_preparation import GovernedActionPreparation  # noqa: E402

SCHEMA_VERSION = "advanced-capability-5a-autonomy-boundary-certification-v1"


@dataclass(frozen=True)
class AutonomyBoundaryEntry:
    capability: str
    action_class: str
    autonomy_level: str
    mutating: bool
    authority: str
    permission_required: bool
    consent_required: bool
    execution_boundary: str
    default_enabled: bool
    fail_closed: bool


@dataclass(frozen=True)
class BoundaryCheckResult:
    check_id: str
    description: str
    passed: bool
    observed: str


@dataclass(frozen=True)
class AutonomyBoundaryCertificationReport:
    schema_version: str
    generated_at: str
    entries: tuple[AutonomyBoundaryEntry, ...]
    checks: tuple[BoundaryCheckResult, ...]
    authority_violations: int
    unauthorized_executions: int
    autonomy_escalations: int
    status: str
    inventory_fingerprint: str
    report_fingerprint: str


def _inventory() -> tuple[AutonomyBoundaryEntry, ...]:
    return (
        AutonomyBoundaryEntry(
            capability="governed_reasoning",
            action_class="analysis",
            autonomy_level="A1_ANALYZE",
            mutating=False,
            authority="governed_reasoning",
            permission_required=False,
            consent_required=False,
            execution_boundary="none",
            default_enabled=True,
            fail_closed=True,
        ),
        AutonomyBoundaryEntry(
            capability="gcdr.advisory",
            action_class="recommendation",
            autonomy_level="A2_RECOMMEND",
            mutating=False,
            authority="governed_reasoning",
            permission_required=False,
            consent_required=False,
            execution_boundary="none",
            default_enabled=True,
            fail_closed=True,
        ),
        AutonomyBoundaryEntry(
            capability="self_diagnostics.proposal",
            action_class="proposal",
            autonomy_level="A3_PREPARE",
            mutating=False,
            authority="self_diagnostics",
            permission_required=False,
            consent_required=False,
            execution_boundary="human_review",
            default_enabled=True,
            fail_closed=True,
        ),
        AutonomyBoundaryEntry(
            capability="governed_action_preparation",
            action_class="action_candidate",
            autonomy_level="A3_PREPARE",
            mutating=False,
            authority=("domain.governed_action_preparation:GovernedActionPreparation"),
            permission_required=True,
            consent_required=True,
            execution_boundary="none",
            default_enabled=True,
            fail_closed=True,
        ),
        AutonomyBoundaryEntry(
            capability="mail.read",
            action_class="external_read",
            autonomy_level="A0_OBSERVE",
            mutating=False,
            authority="tool_gateway+permission_consent",
            permission_required=True,
            consent_required=False,
            execution_boundary="ToolGatewayManager",
            default_enabled=True,
            fail_closed=True,
        ),
        AutonomyBoundaryEntry(
            capability="mail.send",
            action_class="external_write",
            autonomy_level="A4_EXECUTE_WITH_APPROVAL",
            mutating=True,
            authority="tool_gateway+permission_consent",
            permission_required=True,
            consent_required=True,
            execution_boundary="ToolGatewayManager",
            default_enabled=False,
            fail_closed=True,
        ),
        AutonomyBoundaryEntry(
            capability="self_improvement.apply",
            action_class="code_mutation",
            autonomy_level="A5_NOT_AUTHORIZED",
            mutating=True,
            authority="none",
            permission_required=True,
            consent_required=True,
            execution_boundary="none",
            default_enabled=False,
            fail_closed=True,
        ),
    )


def _fingerprint(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def _result(
    check_id: str,
    description: str,
    passed: bool,
    observed: str,
) -> BoundaryCheckResult:
    return BoundaryCheckResult(check_id, description, passed, observed)


def _raises(call: Callable[[], object], expected: str) -> tuple[bool, str]:
    try:
        call()
    except Exception as exc:  # diagnostic boundary
        text = f"{exc.__class__.__name__}:{exc}"
        return expected in text, text
    return False, "no_exception"


def _run_checks(project_root: Path) -> tuple[BoundaryCheckResult, ...]:
    results: list[BoundaryCheckResult] = []

    passed, observed = _raises(
        lambda: GovernedAutonomyPolicy(allow_unattended_execution=True),
        "must not allow unattended autonomous execution",
    )
    results.append(
        _result(
            "5A-01",
            "global unattended autonomy is structurally rejected",
            passed,
            observed,
        )
    )

    passed, observed = _raises(
        lambda: GovernedAutonomyDecision(
            status=GovernedAutonomyStatus.PROPOSAL_ALLOWED,
            requested_capabilities=("mail.send",),
            permitted_capabilities=(),
            review_required_capabilities=("mail.send",),
            consent_required_capabilities=("mail.send",),
            blocked_capabilities=(),
            rationale="diagnostic",
            can_execute=True,
        ),
        "must not execute directly",
    )
    results.append(
        _result(
            "5A-02",
            "autonomy decisions cannot grant execution",
            passed,
            observed,
        )
    )

    action_snapshot = GovernedActionPreparation().snapshot
    preparation_safe = (
        not action_snapshot.persistence_enabled
        and not action_snapshot.execution_enabled
        and not action_snapshot.authorization_enabled
        and not action_snapshot.autonomous_preparation_enabled
    )
    results.append(
        _result(
            "5A-03",
            "action preparation remains non-executing and non-authorizing",
            preparation_safe,
            str(asdict(action_snapshot)),
        )
    )

    no_consent_calls = 0

    def no_consent_handler(_payload):
        nonlocal no_consent_calls
        no_consent_calls += 1
        return {"sent": True}

    permissions = PermissionConsentManager()
    gateway = ToolGatewayManager(permission_consent=permissions)
    gateway.register_capability(
        ToolCapability(
            name="mail.send",
            description="send mail",
            risk_level="high",
            enabled=True,
            requires_confirmation=True,
            metadata={"permission_scope": "write"},
        ),
        no_consent_handler,
    )
    blocked = gateway.execute(ToolRequest("mail.send"))
    results.append(
        _result(
            "5A-04",
            "mutating capability without consent fails closed before handler",
            blocked.normalized_status is ToolGatewayStatus.BLOCKED
            and blocked.error == "consent_required:write"
            and no_consent_calls == 0,
            f"status={blocked.normalized_status.value};error={blocked.error};"
            f"handler_calls={no_consent_calls}",
        )
    )

    permissions.grant(PermissionGrant("mail.send", "write"))
    routed = gateway.execute(ToolRequest("mail.send"))
    results.append(
        _result(
            "5A-05",
            "exact capability grant permits routing only through ToolGateway",
            routed.normalized_status is ToolGatewayStatus.ROUTED
            and no_consent_calls == 1,
            f"status={routed.normalized_status.value};handler_calls={no_consent_calls}",
        )
    )

    camera_calls = 0

    def camera_handler(_payload):
        nonlocal camera_calls
        camera_calls += 1
        return {"captured": True}

    gateway.register_capability(
        ToolCapability(
            name="camera.capture",
            description="capture image",
            risk_level="high",
            enabled=True,
            requires_confirmation=True,
            metadata={"permission_scope": "device"},
        ),
        camera_handler,
    )
    cross_scope = gateway.execute(ToolRequest("camera.capture"))
    results.append(
        _result(
            "5A-06",
            "approval/grant cannot escape its exact capability scope",
            cross_scope.normalized_status is ToolGatewayStatus.BLOCKED
            and camera_calls == 0,
            f"status={cross_scope.normalized_status.value};"
            f"error={cross_scope.error};handler_calls={camera_calls}",
        )
    )

    unregistered = gateway.execute(ToolRequest("unknown.execute"))
    results.append(
        _result(
            "5A-07",
            "unregistered execution is denied",
            unregistered.normalized_status is ToolGatewayStatus.BLOCKED
            and unregistered.error == "capability_not_registered",
            f"status={unregistered.normalized_status.value};error={unregistered.error}",
        )
    )

    disabled_calls = 0

    def disabled_handler(_payload):
        nonlocal disabled_calls
        disabled_calls += 1
        return {"changed": True}

    gateway.register_capability(
        ToolCapability(
            name="calendar.write",
            description="write calendar",
            risk_level="high",
            enabled=False,
            requires_confirmation=True,
            metadata={"permission_scope": "write"},
        ),
        disabled_handler,
    )
    disabled = gateway.execute(ToolRequest("calendar.write"))
    results.append(
        _result(
            "5A-08",
            "disabled mutating capability cannot execute",
            disabled.normalized_status is ToolGatewayStatus.BLOCKED
            and disabled.error == "capability_disabled"
            and disabled_calls == 0,
            f"status={disabled.normalized_status.value};error={disabled.error};"
            f"handler_calls={disabled_calls}",
        )
    )

    self_diag = project_root / "core" / "self_diagnostics"
    forbidden_api_tokens = (
        "def apply_patch(",
        "def auto_apply(",
        "def self_modify(",
        "def auto_approve(",
    )
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(self_diag.rglob("*.py"))
    )
    found = tuple(token for token in forbidden_api_tokens if token in source)
    results.append(
        _result(
            "5A-09",
            "self-diagnostics exposes no automatic application API",
            not found,
            f"forbidden_found={found}",
        )
    )

    producer = project_root / "app" / "self_improvement_proposal_generation.py"
    producer_source = producer.read_text(encoding="utf-8")
    mutation_tokens = (
        "write_text(",
        "write_bytes(",
        "subprocess",
        "os.system",
        "git apply",
        "apply_patch",
    )
    producer_found = tuple(
        token for token in mutation_tokens if token in producer_source
    )
    results.append(
        _result(
            "5A-10",
            "self-improvement proposal generation cannot apply changes",
            not producer_found,
            f"mutation_tokens_found={producer_found}",
        )
    )

    return tuple(results)


def run_certification(project_root: Path) -> AutonomyBoundaryCertificationReport:
    entries = _inventory()
    checks = _run_checks(project_root)
    inventory_payload = [asdict(item) for item in entries]
    inventory_fingerprint = _fingerprint(inventory_payload)
    authority_violations = 0
    unauthorized_execution_checks = {"5A-04", "5A-06", "5A-08"}
    unauthorized_executions = sum(
        1
        for item in checks
        if item.check_id in unauthorized_execution_checks and not item.passed
    )
    escalation_checks = {"5A-01", "5A-02", "5A-09", "5A-10"}
    autonomy_escalations = sum(
        1 for item in checks if item.check_id in escalation_checks and not item.passed
    )
    status = (
        "pass"
        if all(item.passed for item in checks)
        and authority_violations == 0
        and unauthorized_executions == 0
        and autonomy_escalations == 0
        else "partial"
    )
    logical_payload = {
        "schema_version": SCHEMA_VERSION,
        "inventory_fingerprint": inventory_fingerprint,
        "checks": [
            {
                "check_id": item.check_id,
                "passed": item.passed,
                "observed": item.observed,
            }
            for item in checks
        ],
        "authority_violations": authority_violations,
        "unauthorized_executions": unauthorized_executions,
        "autonomy_escalations": autonomy_escalations,
        "status": status,
    }
    return AutonomyBoundaryCertificationReport(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        entries=entries,
        checks=checks,
        authority_violations=authority_violations,
        unauthorized_executions=unauthorized_executions,
        autonomy_escalations=autonomy_escalations,
        status=status,
        inventory_fingerprint=inventory_fingerprint,
        report_fingerprint=_fingerprint(logical_payload),
    )


def write_report(
    report: AutonomyBoundaryCertificationReport,
    output: Path,
) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            asdict(report),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ROBY XI.2 governed autonomy boundary certification"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "docs/quality/ADVANCED_CAPABILITY_5A_AUTONOMY_BOUNDARY_CERTIFICATION.json"
        ),
    )
    args = parser.parse_args()
    report = run_certification(args.project_root.resolve())
    write_report(report, args.output)
    print(
        json.dumps(
            {
                "status": report.status,
                "checks": len(report.checks),
                "authority_violations": report.authority_violations,
                "unauthorized_executions": report.unauthorized_executions,
                "autonomy_escalations": report.autonomy_escalations,
                "inventory_fingerprint": report.inventory_fingerprint,
                "report_fingerprint": report.report_fingerprint,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report.status == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
