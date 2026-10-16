from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumption,
)
from app.personal_initiative_engine import (
    InitiativeDisposition,
    InitiativeProposal,
)
from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus


class GovernedIndependenceLevel(StrEnum):
    LEVEL_1_CONVERSATIONAL = "level_1_conversational"
    LEVEL_2_READ_ONLY = "level_2_read_only"
    NOT_APPLICABLE = "not_applicable"


class GovernedInitiationDecision(StrEnum):
    MAY_INITIATE = "may_initiate"
    MUST_ASK = "must_ask"
    MUST_ABSTAIN = "must_abstain"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedReadOnlyCapabilityInitiationRequest:
    owner: str
    capability_name: str
    reason: str
    source_reference: str
    world_snapshot_id: str

    def __post_init__(self) -> None:
        values = (
            self.owner,
            self.capability_name,
            self.reason,
            self.source_reference,
            self.world_snapshot_id,
        )
        if any(not value.strip() for value in values):
            raise ValueError("capability initiation request fields must not be blank")


@dataclass(frozen=True)
class GovernedIndependenceAuthorizationReport:
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
    schema_version: str = "post-m409.1-independence-authorization-boundary-v1"
    adds_authority: bool = False
    read_only: bool = True
    consultative: bool = True
    execution_authorized: bool = False
    selects_capability: bool = False
    invokes_capabilities: bool = False
    creates_questions: bool = False
    modifies_registry: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.authorization_id.startswith("independence-authorization-"):
            raise ValueError("authorization identifier is invalid")
        if not self.requirement_id.startswith("discrimination-requirement-"):
            raise ValueError("authorization requires discrimination lineage")
        if not self.plan_id.startswith("evidence-acquisition-plan-"):
            raise ValueError("authorization requires planning lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("authorization must preserve source lineage")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("authorization requires rationale codes")
        if self.adds_authority or not self.read_only or not self.consultative:
            raise ValueError("authorization boundary cannot become an authority")
        if any(
            (
                self.execution_authorized,
                self.selects_capability,
                self.invokes_capabilities,
                self.creates_questions,
                self.modifies_registry,
                self.modifies_memory,
                self.modifies_world_model,
                self.executes_actions,
                self.starts_background_process,
            )
        ):
            raise ValueError("authorization boundary violates governed limits")


class GovernedIndependenceAuthorizationBoundaryV1:
    """Decide initiative eligibility without selecting or executing a capability."""

    def __init__(self, registry: CapabilityRegistryManager) -> None:
        self._registry = registry

    def evaluate(
        self,
        consumption: GovernedEvidenceAcquisitionProductiveConsumption,
        *,
        initiative_proposal: InitiativeProposal | None = None,
    ) -> GovernedIndependenceAuthorizationReport:
        planning = consumption.planning_report
        if consumption.planning_execution_authorized:
            raise ValueError("authorization requires a non-executive planning product")
        if planning.status is EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE:
            return self._result(
                consumption,
                GovernedInitiationDecision.MUST_ABSTAIN,
                GovernedIndependenceLevel.NOT_APPLICABLE,
                None,
                ("authorization:no_capability_available",),
            )
        if planning.status in {
            EvidenceAcquisitionPlanningStatus.AMBIGUOUS,
            EvidenceAcquisitionPlanningStatus.PARTIALLY_PLANNABLE,
        }:
            return self._result(
                consumption,
                GovernedInitiationDecision.REVIEW_REQUIRED,
                GovernedIndependenceLevel.NOT_APPLICABLE,
                None,
                (f"authorization:{planning.status.value}",),
            )
        if len(planning.candidates) != 1:
            return self._result(
                consumption,
                GovernedInitiationDecision.REVIEW_REQUIRED,
                GovernedIndependenceLevel.NOT_APPLICABLE,
                None,
                ("authorization:single_candidate_required",),
            )

        candidate = planning.candidates[0]
        descriptor = self._registry.capabilities.get(candidate.capability_name)
        if descriptor is None or not descriptor.enabled:
            return self._result(
                consumption,
                GovernedInitiationDecision.MUST_ABSTAIN,
                GovernedIndependenceLevel.NOT_APPLICABLE,
                candidate.capability_name,
                ("authorization:capability_unavailable",),
            )
        if candidate.declared_evidence_output not in descriptor.evidence_outputs:
            return self._result(
                consumption,
                GovernedInitiationDecision.REVIEW_REQUIRED,
                GovernedIndependenceLevel.NOT_APPLICABLE,
                candidate.capability_name,
                ("authorization:evidence_declaration_mismatch",),
            )

        scope = descriptor.normalized_interaction_scope
        if scope is CapabilityInteractionScope.HUMAN:
            return self._level_1(
                consumption,
                candidate.capability_name,
                descriptor.normalized_initiation_policy,
                initiative_proposal,
            )
        return self._level_2(consumption, candidate.capability_name, descriptor)

    def evaluate_capability_initiation(
        self,
        request: GovernedReadOnlyCapabilityInitiationRequest,
    ) -> GovernedIndependenceAuthorizationReport:
        """Evaluate direct Level-2 initiative without evidence-planning lineage."""

        descriptor = self._registry.capabilities.get(request.capability_name)
        if descriptor is None or not descriptor.enabled:
            return self._direct_result(
                request,
                GovernedInitiationDecision.MUST_ABSTAIN,
                GovernedIndependenceLevel.NOT_APPLICABLE,
                ("authorization:capability_unavailable",),
            )

        policy = descriptor.normalized_initiation_policy
        effect = descriptor.normalized_effect_class
        scope = descriptor.normalized_interaction_scope
        risk = descriptor.normalized_risk
        permission = descriptor.normalized_permission_scope

        if (
            permission is PermissionScope.NETWORK
            or scope is CapabilityInteractionScope.EXTERNAL
        ):
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:external_or_network_scope_closed",)
        elif (
            effect is CapabilityEffectClass.STATE_CHANGING
            or permission is PermissionScope.WRITE
        ):
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:state_change_not_level_2",)
        elif risk is CapabilityRisk.HIGH:
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:high_risk_not_level_2",)
        elif policy is CapabilityInitiationPolicy.NEVER:
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:autonomous_initiation_forbidden",)
        elif policy is CapabilityInitiationPolicy.HUMAN_APPROVAL:
            decision = GovernedInitiationDecision.MUST_ASK
            reasons = ("authorization:human_approval_required",)
        elif policy is CapabilityInitiationPolicy.UNDECLARED:
            decision = GovernedInitiationDecision.REVIEW_REQUIRED
            reasons = ("authorization:initiation_policy_undeclared",)
        elif effect is not CapabilityEffectClass.READ_ONLY:
            decision = GovernedInitiationDecision.REVIEW_REQUIRED
            reasons = ("authorization:read_only_effect_not_declared",)
        elif scope not in {
            CapabilityInteractionScope.INTERNAL,
            CapabilityInteractionScope.DEVICE,
        }:
            decision = GovernedInitiationDecision.REVIEW_REQUIRED
            reasons = ("authorization:level_2_scope_not_declared",)
        elif descriptor.requires_confirmation or risk is CapabilityRisk.MEDIUM:
            decision = GovernedInitiationDecision.MUST_ASK
            reasons = ("authorization:confirmation_or_medium_risk",)
        else:
            decision = GovernedInitiationDecision.MAY_INITIATE
            reasons = ("authorization:explicit_safe_level_2_eligibility",)

        return self._direct_result(
            request,
            decision,
            GovernedIndependenceLevel.LEVEL_2_READ_ONLY,
            reasons,
        )

    @staticmethod
    def _direct_result(
        request: GovernedReadOnlyCapabilityInitiationRequest,
        decision: GovernedInitiationDecision,
        level: GovernedIndependenceLevel,
        rationale_codes: tuple[str, ...],
    ) -> GovernedIndependenceAuthorizationReport:
        fingerprint = sha256(
            repr(
                (
                    request.owner,
                    request.capability_name,
                    request.reason,
                    request.source_reference,
                    request.world_snapshot_id,
                    decision.value,
                    level.value,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedIndependenceAuthorizationReport(
            authorization_id=f"independence-authorization-{fingerprint[:24]}",
            decision=decision,
            independence_level=level,
            requirement_id=f"discrimination-requirement-direct-{fingerprint[:16]}",
            plan_id=f"evidence-acquisition-plan-direct-{fingerprint[:16]}",
            capability_name=request.capability_name,
            source_reference=request.source_reference,
            world_snapshot_id=request.world_snapshot_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )

    def _level_1(
        self,
        consumption: GovernedEvidenceAcquisitionProductiveConsumption,
        capability_name: str,
        policy: CapabilityInitiationPolicy,
        initiative_proposal: InitiativeProposal | None,
    ) -> GovernedIndependenceAuthorizationReport:
        if policy is CapabilityInitiationPolicy.NEVER:
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:human_initiation_forbidden",)
        elif initiative_proposal is None:
            decision = GovernedInitiationDecision.MUST_ASK
            reasons = ("authorization:existing_initiative_gate_required",)
        elif initiative_proposal.disposition is InitiativeDisposition.DISCARD:
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:initiative_discarded",)
        elif initiative_proposal.disposition is InitiativeDisposition.DEFER:
            decision = GovernedInitiationDecision.REVIEW_REQUIRED
            reasons = ("authorization:initiative_deferred",)
        else:
            decision = GovernedInitiationDecision.MAY_INITIATE
            reasons = ("authorization:existing_initiative_admitted",)
        return self._result(
            consumption,
            decision,
            GovernedIndependenceLevel.LEVEL_1_CONVERSATIONAL,
            capability_name,
            reasons,
        )

    def _level_2(
        self,
        consumption: GovernedEvidenceAcquisitionProductiveConsumption,
        capability_name: str,
        descriptor,
    ) -> GovernedIndependenceAuthorizationReport:
        policy = descriptor.normalized_initiation_policy
        effect = descriptor.normalized_effect_class
        scope = descriptor.normalized_interaction_scope
        risk = descriptor.normalized_risk
        permission = descriptor.normalized_permission_scope

        if (
            permission is PermissionScope.NETWORK
            or scope is CapabilityInteractionScope.EXTERNAL
        ):
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:external_or_network_scope_closed",)
        elif (
            effect is CapabilityEffectClass.STATE_CHANGING
            or permission is PermissionScope.WRITE
        ):
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:state_change_not_level_2",)
        elif risk is CapabilityRisk.HIGH:
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:high_risk_not_level_2",)
        elif policy is CapabilityInitiationPolicy.NEVER:
            decision = GovernedInitiationDecision.MUST_ABSTAIN
            reasons = ("authorization:autonomous_initiation_forbidden",)
        elif policy is CapabilityInitiationPolicy.HUMAN_APPROVAL:
            decision = GovernedInitiationDecision.MUST_ASK
            reasons = ("authorization:human_approval_required",)
        elif policy is CapabilityInitiationPolicy.UNDECLARED:
            decision = GovernedInitiationDecision.REVIEW_REQUIRED
            reasons = ("authorization:initiation_policy_undeclared",)
        elif effect is not CapabilityEffectClass.READ_ONLY:
            decision = GovernedInitiationDecision.REVIEW_REQUIRED
            reasons = ("authorization:read_only_effect_not_declared",)
        elif scope not in {
            CapabilityInteractionScope.INTERNAL,
            CapabilityInteractionScope.DEVICE,
        }:
            decision = GovernedInitiationDecision.REVIEW_REQUIRED
            reasons = ("authorization:level_2_scope_not_declared",)
        elif descriptor.requires_confirmation or risk is CapabilityRisk.MEDIUM:
            decision = GovernedInitiationDecision.MUST_ASK
            reasons = ("authorization:confirmation_or_medium_risk",)
        else:
            decision = GovernedInitiationDecision.MAY_INITIATE
            reasons = ("authorization:explicit_safe_level_2_eligibility",)
        return self._result(
            consumption,
            decision,
            GovernedIndependenceLevel.LEVEL_2_READ_ONLY,
            capability_name,
            reasons,
        )

    @staticmethod
    def _result(
        consumption: GovernedEvidenceAcquisitionProductiveConsumption,
        decision: GovernedInitiationDecision,
        level: GovernedIndependenceLevel,
        capability_name: str | None,
        rationale_codes: tuple[str, ...],
    ) -> GovernedIndependenceAuthorizationReport:
        planning = consumption.planning_report
        fingerprint = sha256(
            repr(
                (
                    planning.requirement_id,
                    planning.plan_id,
                    decision.value,
                    level.value,
                    capability_name,
                    rationale_codes,
                    planning.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedIndependenceAuthorizationReport(
            authorization_id=f"independence-authorization-{fingerprint[:24]}",
            decision=decision,
            independence_level=level,
            requirement_id=planning.requirement_id,
            plan_id=planning.plan_id,
            capability_name=capability_name,
            source_reference=planning.source_reference,
            world_snapshot_id=planning.world_snapshot_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
