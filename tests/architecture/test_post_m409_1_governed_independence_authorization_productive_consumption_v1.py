from __future__ import annotations

import ast
import inspect
from dataclasses import fields

import pytest

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationReport,
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
    GovernedIndependenceAuthorizationProductiveConsumptionV1,
)


def _report(
    decision: GovernedInitiationDecision,
    level: GovernedIndependenceLevel,
    *,
    capability_name: str | None = "sensor.read",
    rationale: tuple[str, ...] = ("authorization:test",),
) -> GovernedIndependenceAuthorizationReport:
    return GovernedIndependenceAuthorizationReport(
        authorization_id="independence-authorization-1234567890abcdef12345678",
        decision=decision,
        independence_level=level,
        requirement_id="discrimination-requirement-1234567890abcdef",
        plan_id="evidence-acquisition-plan-1234567890abcdef",
        capability_name=capability_name,
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        rationale_codes=rationale,
        source_fingerprint="authorization-source-fingerprint",
    )


def _consume(
    decision: GovernedInitiationDecision,
    level: GovernedIndependenceLevel,
    *,
    capability_name: str | None = "sensor.read",
    rationale: tuple[str, ...] = ("authorization:test",),
) -> GovernedIndependenceAuthorizationProductiveConsumption:
    return GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
        _report(
            decision,
            level,
            capability_name=capability_name,
            rationale=rationale,
        )
    )


def test_level_2_may_initiate_is_eligible_but_never_executable() -> None:
    result = _consume(
        GovernedInitiationDecision.MAY_INITIATE,
        GovernedIndependenceLevel.LEVEL_2_READ_ONLY,
    )

    assert result.eligible_for_next_governed_gate
    assert not result.execution_authorized
    assert not result.selects_capability
    assert not result.invokes_capabilities
    assert not result.executes_actions


def test_level_1_may_initiate_does_not_emit_conversation() -> None:
    result = _consume(
        GovernedInitiationDecision.MAY_INITIATE,
        GovernedIndependenceLevel.LEVEL_1_CONVERSATIONAL,
        capability_name="human.evidence",
    )

    assert result.eligible_for_next_governed_gate
    assert not result.creates_questions
    assert not result.emits_conversation
    assert not result.execution_authorized


@pytest.mark.parametrize(
    "decision",
    (
        GovernedInitiationDecision.MUST_ASK,
        GovernedInitiationDecision.MUST_ABSTAIN,
        GovernedInitiationDecision.REVIEW_REQUIRED,
    ),
)
def test_non_admitted_decisions_are_terminal_at_this_surface(
    decision: GovernedInitiationDecision,
) -> None:
    result = _consume(
        decision,
        GovernedIndependenceLevel.LEVEL_2_READ_ONLY,
    )

    assert result.decision is decision
    assert not result.eligible_for_next_governed_gate
    assert not result.execution_authorized
    assert not result.invokes_capabilities


def test_exact_authorization_lineage_and_rationale_are_preserved() -> None:
    report = _report(
        GovernedInitiationDecision.MUST_ASK,
        GovernedIndependenceLevel.LEVEL_2_READ_ONLY,
        rationale=(
            "authorization:human_approval_required",
            "authorization:lineage-test",
        ),
    )

    result = GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
        report
    )

    assert result.authorization_report is report
    assert result.authorization_id == report.authorization_id
    assert result.requirement_id == report.requirement_id
    assert result.plan_id == report.plan_id
    assert result.capability_name == report.capability_name
    assert result.source_reference == report.source_reference
    assert result.world_snapshot_id == report.world_snapshot_id
    assert result.rationale_codes == report.rationale_codes


def test_productive_consumption_does_not_recalculate_authorization() -> None:
    source = inspect.getsource(
        GovernedIndependenceAuthorizationProductiveConsumptionV1
    )

    for forbidden in (
        "CapabilityRegistryManager",
        "CapabilityDescriptor",
        "CapabilityInitiationPolicy",
        "CapabilityEffectClass",
        "CapabilityRisk",
        "PermissionScope",
        "PersonalInitiativeEngine",
    ):
        assert forbidden not in source


def test_productive_contract_has_no_operational_bypass() -> None:
    defaults = {
        field.name: field.default
        for field in fields(
            GovernedIndependenceAuthorizationProductiveConsumption
        )
    }
    for field_name in (
        "execution_authorized",
        "selects_capability",
        "invokes_capabilities",
        "creates_questions",
        "emits_conversation",
        "modifies_registry",
        "modifies_memory",
        "modifies_world_model",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[field_name] is False

    source = inspect.getsource(
        GovernedIndependenceAuthorizationProductiveConsumptionV1
    )
    tree = ast.parse(source)
    for forbidden in (
        "OfficialConversationGateway",
        "OfficialMemoryGateway",
        "OfficialCapabilityGateway",
        "GovernedEpistemicCuriosity",
        "requests.",
        "socket.",
        "subprocess.",
        "android",
    ):
        assert forbidden not in source.lower() if forbidden == "android" else (
            forbidden not in source
        )
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {
                "execute",
                "invoke",
                "emit",
                "ask",
                "persist",
                "remember",
                "select",
            }
        )
        for node in ast.walk(tree)
    )


def test_productive_contract_rejects_forged_eligibility() -> None:
    report = _report(
        GovernedInitiationDecision.MUST_ABSTAIN,
        GovernedIndependenceLevel.NOT_APPLICABLE,
        capability_name=None,
    )

    with pytest.raises(ValueError, match="eligibility"):
        GovernedIndependenceAuthorizationProductiveConsumption(
            authorization_report=report,
            authorization_id=report.authorization_id,
            decision=report.decision,
            independence_level=report.independence_level,
            requirement_id=report.requirement_id,
            plan_id=report.plan_id,
            capability_name=report.capability_name,
            source_reference=report.source_reference,
            world_snapshot_id=report.world_snapshot_id,
            rationale_codes=report.rationale_codes,
            source_fingerprint="forged",
            eligible_for_next_governed_gate=True,
        )
