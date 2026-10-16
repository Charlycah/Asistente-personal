from __future__ import annotations

from dataclasses import fields
from importlib import import_module

from core.capability_registry import CapabilityDescriptor, CapabilityRegistryManager
from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)
from core.cognitive_maturity.material_self_epistemic_resolution_path_set import (
    MaterialSelfEpistemicResolutionPathSet,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
)

MODULE = "core.cognitive_maturity.current_registry_resolution_path_availability"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
CAPABILITY = "fixture.explicit_inner_continuity_evidence"
OUTPUT = "fixture.inner_continuity_output"


def _contract():
    return import_module(MODULE)


def _binding(
    *,
    capability_name: str = CAPABILITY,
    declared_evidence_output: str = OUTPUT,
) -> EpistemicResolutionBinding:
    return EpistemicResolutionBinding(
        capability_name=capability_name,
        declared_evidence_output=declared_evidence_output,
        epistemic_need_identity=IDENTITY,
        epistemic_need_source_reference="inner-continuity-report-123",
        epistemic_need_lineage_kind="explicit_inner_continuity_gap",
        provenance_authority=(
            "governed_explicit_epistemic_resolution_declaration"
        ),
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )


def _path_set(
    bindings: tuple[EpistemicResolutionBinding, ...] | None = None,
) -> MaterialSelfEpistemicResolutionPathSet:
    if bindings is None:
        bindings = (_binding(),)
    return MaterialSelfEpistemicResolutionPathSet(
        assessment_id="epistemic-sufficiency-1234567890abcdef",
        requirement_id="discrimination-requirement-1234567890abcdef",
        epistemic_need_identity=IDENTITY,
        reasoning_source_reference="scenario-123",
        world_snapshot_id="world-1",
        self_gap_source_reference="inner-continuity-report-123",
        self_gap_lineage_kind="explicit_inner_continuity_gap",
        resolution_bindings=bindings,
    )


def _registry(
    *,
    capability_name: str = CAPABILITY,
    evidence_outputs: tuple[str, ...] = (OUTPUT,),
    enabled: bool = True,
) -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name=capability_name,
            description="Fixture evidence capability.",
            evidence_outputs=evidence_outputs,
            enabled=enabled,
        )
    )
    return registry


def _observe(contract, path_set=None, registry=None):
    path_set = path_set or _path_set()
    registry = registry or _registry()
    return contract.CurrentRegistryResolutionPathAvailabilityObserver().observe(
        path_set,
        registry,
    )


def test_r1_exact_current_registry_availability_is_reported() -> None:
    contract = _contract()
    binding = _binding()

    result = _observe(contract, _path_set((binding,)), _registry())

    assert result.observations[0].binding == binding
    assert result.observations[0].status.value == "registry_available"


def test_r2_missing_capability_is_explicit_and_non_destructive() -> None:
    contract = _contract()
    binding = _binding()
    registry = CapabilityRegistryManager()

    result = _observe(contract, _path_set((binding,)), registry)

    assert result.observations[0].binding == binding
    assert result.observations[0].status.value == "not_registered"


def test_r3_evidence_declaration_mismatch_is_exact_and_fail_closed() -> None:
    contract = _contract()
    binding = _binding()
    registry = _registry(evidence_outputs=("fixture.other_output",))

    result = _observe(contract, _path_set((binding,)), registry)

    assert result.observations[0].binding == binding
    assert result.observations[0].status.value == (
        "evidence_declaration_mismatch"
    )


def test_r4_disabled_is_not_available_and_preserves_binding() -> None:
    contract = _contract()
    binding = _binding()

    result = _observe(
        contract,
        _path_set((binding,)),
        _registry(enabled=False),
    )

    assert result.observations[0].binding == binding
    assert result.observations[0].status.value == "disabled"


def test_r5_zero_one_many_paths_remain_observational_and_non_selective() -> None:
    contract = _contract()
    first = _binding(capability_name="fixture.alpha")
    second = _binding(
        capability_name="fixture.beta",
        declared_evidence_output="fixture.beta_output",
    )
    registry = CapabilityRegistryManager()
    registry.register_many(
        (
            CapabilityDescriptor(
                name="fixture.alpha",
                description="Alpha fixture.",
                evidence_outputs=(OUTPUT,),
            ),
            CapabilityDescriptor(
                name="fixture.beta",
                description="Beta fixture.",
                evidence_outputs=("fixture.beta_output",),
            ),
        )
    )

    zero = _observe(contract, _path_set(()), registry)
    one = _observe(contract, _path_set((first,)), registry)
    many = _observe(contract, _path_set((first, second)), registry)

    assert zero.observations == ()
    assert tuple(item.binding for item in one.observations) == (first,)
    assert tuple(item.binding for item in many.observations) == (first, second)
    for result in (zero, one, many):
        assert not hasattr(result, "selected_path")
        assert not hasattr(result, "preferred_path")
        assert not hasattr(result, "best_path")


def test_r6_all_paths_are_auditable_and_s4_w_order_is_preserved() -> None:
    contract = _contract()
    first = _binding(capability_name="fixture.missing")
    second = _binding(
        capability_name="fixture.disabled",
        declared_evidence_output="fixture.disabled_output",
    )
    third = _binding(
        capability_name="fixture.available",
        declared_evidence_output="fixture.available_output",
    )
    registry = CapabilityRegistryManager()
    registry.register_many(
        (
            CapabilityDescriptor(
                name="fixture.disabled",
                description="Disabled fixture.",
                evidence_outputs=("fixture.disabled_output",),
                enabled=False,
            ),
            CapabilityDescriptor(
                name="fixture.available",
                description="Available fixture.",
                evidence_outputs=("fixture.available_output",),
            ),
        )
    )

    result = _observe(contract, _path_set((first, second, third)), registry)

    assert tuple(item.binding for item in result.observations) == (
        first,
        second,
        third,
    )
    assert tuple(item.status.value for item in result.observations) == (
        "not_registered",
        "disabled",
        "registry_available",
    )


def test_r7_material_anchor_and_binding_lineages_are_preserved() -> None:
    contract = _contract()
    binding = _binding()
    path_set = _path_set((binding,))
    before = (path_set, binding)

    result = _observe(contract, path_set, _registry())

    assert (path_set, binding) == before
    assert result.assessment_id == path_set.assessment_id
    assert result.requirement_id == path_set.requirement_id
    assert result.epistemic_need_identity == path_set.epistemic_need_identity
    assert result.reasoning_source_reference == path_set.reasoning_source_reference
    assert result.world_snapshot_id == path_set.world_snapshot_id
    assert result.self_gap_source_reference == path_set.self_gap_source_reference
    assert result.self_gap_lineage_kind == path_set.self_gap_lineage_kind
    assert result.observations[0].binding == binding


def test_r8_registry_only_observer_is_read_only_and_subordinate() -> None:
    contract = _contract()
    defaults = {
        field.name: field.default
        for field in fields(
            contract.CurrentRegistryResolutionPathAvailabilityObserver
        )
    }

    assert defaults["read_only"] is True
    assert defaults["derivational"] is True
    for field_name in (
        "mutates_capability_registry",
        "performs_semantic_capability_search",
        "discovers_substitute_resolution_paths",
        "infers_resolution_semantics",
        "consults_runtime_capability_graph",
        "reconstructs_runtime_capability_graph",
        "assesses_runtime_readiness",
        "inspects_runtime_lifecycle",
        "inspects_runtime_residents",
        "ranks_sources",
        "ranks_capabilities",
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "acquires_evidence",
        "creates_questions",
        "assigns_question_worthiness",
        "assigns_relevance",
        "invokes_curiosity",
        "creates_goals",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "modifies_memory",
        "creates_learning_candidate",
        "executes_actions",
        "grants_authority",
        "claims_subjective_experience",
        "claims_consciousness",
    ):
        assert defaults[field_name] is False
