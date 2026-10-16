from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationReport,
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
)


@dataclass(frozen=True)
class GovernedIndependenceAuthorizationProductiveConsumption:
    """Expose an existing authorization decision without operationalizing it."""

    authorization_report: GovernedIndependenceAuthorizationReport
    authorization_id: str
    decision: GovernedInitiationDecision
    independence_level: GovernedIndependenceLevel
    requirement_id: str
    plan_id: str
    capability_name: str | None
    source_reference: str
    world_snapshot_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-independence-authorization-productive-consumption-v1"
    )
    canonical_authority: str = "governed_independence_authorization_boundary"
    read_only: bool = True
    consultative: bool = True
    eligible_for_next_governed_gate: bool = False
    execution_authorized: bool = False
    selects_capability: bool = False
    invokes_capabilities: bool = False
    creates_questions: bool = False
    emits_conversation: bool = False
    modifies_registry: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        report = self.authorization_report
        preserved = (
            self.authorization_id == report.authorization_id
            and self.decision is report.decision
            and self.independence_level is report.independence_level
            and self.requirement_id == report.requirement_id
            and self.plan_id == report.plan_id
            and self.capability_name == report.capability_name
            and self.source_reference == report.source_reference
            and self.world_snapshot_id == report.world_snapshot_id
            and self.rationale_codes == report.rationale_codes
        )
        if not preserved:
            raise ValueError("productive consumption must preserve authorization")
        if self.eligible_for_next_governed_gate != (
            self.decision is GovernedInitiationDecision.MAY_INITIATE
        ):
            raise ValueError("eligibility must derive only from authorization decision")
        if not self.read_only or not self.consultative or any(
            (
                self.execution_authorized,
                self.selects_capability,
                self.invokes_capabilities,
                self.creates_questions,
                self.emits_conversation,
                self.modifies_registry,
                self.modifies_memory,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("productive authorization violates governed limits")


class GovernedIndependenceAuthorizationProductiveConsumptionV1:
    """Preserve and expose a boundary result; never recalculate authorization."""

    @staticmethod
    def consume(
        report: GovernedIndependenceAuthorizationReport,
    ) -> GovernedIndependenceAuthorizationProductiveConsumption:
        fingerprint = sha256(
            repr(
                (
                    report.authorization_id,
                    report.decision.value,
                    report.independence_level.value,
                    report.requirement_id,
                    report.plan_id,
                    report.capability_name,
                    report.source_reference,
                    report.world_snapshot_id,
                    report.rationale_codes,
                    report.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedIndependenceAuthorizationProductiveConsumption(
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
            source_fingerprint=fingerprint,
            eligible_for_next_governed_gate=(
                report.decision is GovernedInitiationDecision.MAY_INITIATE
            ),
        )
