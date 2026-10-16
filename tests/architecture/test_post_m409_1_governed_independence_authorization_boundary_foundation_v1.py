from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumptionV1,
)
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedIndependenceAuthorizationReport,
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
)
from app.personal_initiative_engine import (
    InitiativeDisposition,
    InitiativeProposal,
)
from app.relevance_evaluator import RelevanceRecipient
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


def _requirement(*missing: str) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-1234567890abcdef",
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("fact-shared",),
        missing_evidence_descriptions=missing,
        evidence_codes=("comparison:indistinguishable",),
    )


def _descriptor(
    name: str = "sensor.read",
    *,
    output: str = "room temperature",
    policy: CapabilityInitiationPolicy = CapabilityInitiationPolicy.UNDECLARED,
    effect: CapabilityEffectClass = CapabilityEffectClass.UNDECLARED,
    scope: CapabilityInteractionScope = CapabilityInteractionScope.UNDECLARED,
    risk: CapabilityRisk = CapabilityRisk.LOW,
    permission: PermissionScope = PermissionScope.NONE,
    confirmation: bool = False,
) -> CapabilityDescriptor:
    return CapabilityDescriptor(
        name=name,
        description=f"Evidence provider {name}",
        evidence_outputs=(output,),
        initiation_policy=policy,
        effect_class=effect,
        interaction_scope=scope,
        risk=risk,
        permission_scope=permission,
        requires_confirmation=confirmation,
    )


def _registry(*descriptors: CapabilityDescriptor) -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    for descriptor in descriptors:
        registry.register(descriptor)
    return registry


def _authorize(
    registry: CapabilityRegistryManager,
    requirement: DiscriminatingEvidenceRequirement | None = None,
    *,
    initiative: InitiativeProposal | None = None,
):
    productive = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        registry
    ).consume(requirement or _requirement("room temperature"))
    return GovernedIndependenceAuthorizationBoundaryV1(registry).evaluate(
        productive,
        initiative_proposal=initiative,
    )


def _initiative(disposition: InitiativeDisposition) -> InitiativeProposal:
    return InitiativeProposal(
        title="room temperature",
        recipient=RelevanceRecipient.CARLOS,
        disposition=disposition,
        priority=10,
        reasons=("test",),
    )


def test_explicit_safe_read_only_level_2_can_be_eligible_without_execution() -> None:
    registry = _registry(
        _descriptor(
            policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.INTERNAL,
            permission=PermissionScope.READ,
        )
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.MAY_INITIATE
    assert result.independence_level is GovernedIndependenceLevel.LEVEL_2_READ_ONLY
    assert result.capability_name == "sensor.read"
    assert not result.execution_authorized
    assert not result.selects_capability
    assert not result.invokes_capabilities
    assert not result.executes_actions


def test_undeclared_initiation_policy_fails_closed_to_review() -> None:
    registry = _registry(
        _descriptor(
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.INTERNAL,
            permission=PermissionScope.READ,
        )
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.REVIEW_REQUIRED
    assert "authorization:initiation_policy_undeclared" in result.rationale_codes


def test_human_approval_policy_requires_ask_without_execution() -> None:
    registry = _registry(
        _descriptor(
            policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.INTERNAL,
            permission=PermissionScope.READ,
        )
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.MUST_ASK
    assert not result.creates_questions
    assert not result.execution_authorized


def test_state_changing_candidate_cannot_receive_level_2_eligibility() -> None:
    registry = _registry(
        _descriptor(
            policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect=CapabilityEffectClass.STATE_CHANGING,
            scope=CapabilityInteractionScope.DEVICE,
            permission=PermissionScope.WRITE,
        )
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.MUST_ABSTAIN
    assert "authorization:state_change_not_level_2" in result.rationale_codes


def test_network_or_external_scope_remains_closed() -> None:
    registry = _registry(
        _descriptor(
            policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.EXTERNAL,
            permission=PermissionScope.NETWORK,
        )
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.MUST_ABSTAIN
    assert "authorization:external_or_network_scope_closed" in result.rationale_codes


def test_ambiguous_planning_requires_review_and_selects_nothing() -> None:
    registry = _registry(
        _descriptor(
            "sensor.a",
            policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.INTERNAL,
            permission=PermissionScope.READ,
        ),
        _descriptor(
            "sensor.b",
            policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.INTERNAL,
            permission=PermissionScope.READ,
        ),
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.REVIEW_REQUIRED
    assert result.capability_name is None
    assert not result.selects_capability


def test_partially_plannable_never_promotes_to_may_initiate() -> None:
    registry = _registry(
        _descriptor(
            policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.INTERNAL,
            permission=PermissionScope.READ,
        )
    )
    result = _authorize(
        registry,
        _requirement("room temperature", "heating system state"),
    )

    assert result.decision is GovernedInitiationDecision.REVIEW_REQUIRED
    assert result.independence_level is GovernedIndependenceLevel.NOT_APPLICABLE


def test_no_capability_available_must_abstain() -> None:
    result = _authorize(_registry())

    assert result.decision is GovernedInitiationDecision.MUST_ABSTAIN
    assert result.independence_level is GovernedIndependenceLevel.NOT_APPLICABLE


def test_human_source_reuses_existing_initiative_for_level_1() -> None:
    registry = _registry(
        _descriptor(
            "human.evidence",
            policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.HUMAN,
        )
    )
    result = _authorize(
        registry,
        initiative=_initiative(InitiativeDisposition.INITIATE),
    )

    assert result.decision is GovernedInitiationDecision.MAY_INITIATE
    assert (
        result.independence_level
        is GovernedIndependenceLevel.LEVEL_1_CONVERSATIONAL
    )
    assert not result.creates_questions
    assert not result.executes_actions


def test_human_source_without_existing_initiative_gate_must_ask() -> None:
    registry = _registry(
        _descriptor(
            "human.evidence",
            policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.HUMAN,
        )
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.MUST_ASK
    assert "authorization:existing_initiative_gate_required" in result.rationale_codes


def test_android_like_device_read_requires_explicit_initiation_policy() -> None:
    registry = _registry(
        _descriptor(
            "android.sensor.read",
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.DEVICE,
            permission=PermissionScope.DEVICE,
        )
    )
    result = _authorize(registry)

    assert result.decision is GovernedInitiationDecision.REVIEW_REQUIRED
    assert not result.invokes_capabilities


def test_lineage_and_non_authority_contract_are_preserved() -> None:
    registry = _registry(
        _descriptor(
            policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect=CapabilityEffectClass.READ_ONLY,
            scope=CapabilityInteractionScope.INTERNAL,
            permission=PermissionScope.READ,
        )
    )
    requirement = _requirement("room temperature")
    result = _authorize(registry, requirement)

    assert result.requirement_id == requirement.requirement_id
    assert result.source_reference == requirement.source_reference
    assert result.world_snapshot_id == requirement.world_snapshot_id
    defaults = {
        field.name: field.default
        for field in fields(GovernedIndependenceAuthorizationReport)
    }
    assert defaults["adds_authority"] is False
    assert defaults["execution_authorized"] is False
    assert defaults["invokes_capabilities"] is False


def test_boundary_has_no_execution_or_external_bypass() -> None:
    source = inspect.getsource(GovernedIndependenceAuthorizationBoundaryV1)
    tree = ast.parse(source)
    for forbidden in (
        "OfficialCapabilityGateway",
        "OfficialConversationGateway",
        "OfficialMemoryGateway",
        "requests.",
        "socket.",
        "subprocess.",
    ):
        assert forbidden not in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {"execute", "emit", "remember", "persist", "acquire", "invoke"}
        )
        for node in ast.walk(tree)
    )


def test_capability_initiation_metadata_defaults_fail_closed() -> None:
    descriptor = CapabilityDescriptor(
        name="legacy.read",
        description="Existing capability without new autonomy metadata",
        evidence_outputs=("room temperature",),
    )

    assert (
        descriptor.normalized_initiation_policy
        is CapabilityInitiationPolicy.UNDECLARED
    )
    assert descriptor.normalized_effect_class is CapabilityEffectClass.UNDECLARED
    assert (
        descriptor.normalized_interaction_scope
        is CapabilityInteractionScope.UNDECLARED
    )


def test_runtime_registry_propagates_explicit_initiation_metadata() -> None:
    from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry

    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="safe.read",
        description="Explicit safe read provider",
        interceptor=object(),
        evidence_outputs=("room temperature",),
        initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.INTERNAL,
        permission_scope=PermissionScope.READ,
    )

    descriptor = registry.registration_for("safe.read").descriptor
    assert (
        descriptor.normalized_initiation_policy
        is CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS
    )
    assert descriptor.normalized_effect_class is CapabilityEffectClass.READ_ONLY
    assert (
        descriptor.normalized_interaction_scope
        is CapabilityInteractionScope.INTERNAL
    )
