from __future__ import annotations

from dataclasses import dataclass, fields
from importlib import import_module

import pytest

from core.cognitive_maturity.canonical_runtime_readiness_projection import (
    CanonicalRuntimeReadinessProjectionObservation,
    CanonicalRuntimeReadinessProjectionStatus,
)
from core.cognitive_maturity.current_registry_resolution_path_availability import (
    CurrentRegistryResolutionPathAvailabilityObservation,
    CurrentRegistryResolutionPathAvailabilityStatus,
)
from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)
from core.cognitive_maturity.explicit_epistemic_suitability import (
    ExplicitEpistemicSuitability,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
)

MODULE = "core.cognitive_maturity.governed_selection_eligibility"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY


def _contract():
    return import_module(MODULE)


@dataclass(frozen=True)
class _CanonicalReadiness:
    capability_id: str
    ready: bool
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def _binding(
    name: str = "fixture.alpha",
    output: str = "fixture.alpha_output",
    *,
    identity: str = IDENTITY,
    source_reference: str = "inner-continuity-report-123",
    lineage_kind: str = "explicit_inner_continuity_gap",
) -> EpistemicResolutionBinding:
    return EpistemicResolutionBinding(
        capability_name=name,
        declared_evidence_output=output,
        epistemic_need_identity=identity,
        epistemic_need_source_reference=source_reference,
        epistemic_need_lineage_kind=lineage_kind,
        provenance_authority=(
            "governed_explicit_epistemic_resolution_declaration"
        ),
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )


def _suitability(binding: EpistemicResolutionBinding) -> ExplicitEpistemicSuitability:
    return ExplicitEpistemicSuitability(
        capability_name=binding.capability_name,
        declared_evidence_output=binding.declared_evidence_output,
        epistemic_need_identity=binding.epistemic_need_identity,
        epistemic_need_source_reference=binding.epistemic_need_source_reference,
        epistemic_need_lineage_kind=binding.epistemic_need_lineage_kind,
        provenance_authority="governed_explicit_epistemic_suitability_declaration",
        evidence_codes=("explicit_epistemic_suitability",),
    )


def _runtime_observation(
    binding: EpistemicResolutionBinding,
    *,
    registry_status=(
        CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE
    ),
    runtime_status=CanonicalRuntimeReadinessProjectionStatus.AVAILABLE,
    ready: bool | None = True,
) -> CanonicalRuntimeReadinessProjectionObservation:
    registry_observation = CurrentRegistryResolutionPathAvailabilityObservation(
        binding=binding,
        status=registry_status,
    )
    readiness = None
    if ready is not None:
        readiness = _CanonicalReadiness(
            capability_id=binding.capability_name,
            ready=ready,
        )
    return CanonicalRuntimeReadinessProjectionObservation(
        registry_observation=registry_observation,
        status=runtime_status,
        runtime_readiness=readiness,
    )


def _assess(contract, suitability, observation):
    return contract.GovernedSelectionEligibilityAssessment().assess(
        suitability,
        observation,
    )


def test_r1_requires_exact_governed_evidence_anchors() -> None:
    contract = _contract()
    binding = _binding()
    suitability = _suitability(binding)
    observation = _runtime_observation(binding)

    result = _assess(contract, suitability, observation)

    assert result is not None
    assert result.suitability == suitability
    assert result.runtime_observation == observation
    assert result.eligible_for_selection is True
    with pytest.raises(TypeError):
        _assess(contract, IDENTITY, observation)
    with pytest.raises(TypeError):
        _assess(contract, suitability, binding)


def test_r2_requires_exact_same_path_correspondence() -> None:
    contract = _contract()
    binding = _binding()
    suitability = _suitability(binding)
    mismatches = (
        _binding(identity="roby.self.other"),
        _binding(name="fixture.beta"),
        _binding(output="fixture.other_output"),
        _binding(source_reference="inner-continuity-report-other"),
        _binding(lineage_kind="other_lineage"),
    )

    for mismatch in mismatches:
        assert _assess(
            contract,
            suitability,
            _runtime_observation(mismatch),
        ) is None


def test_r3_registry_available_is_mandatory_without_negating_suitability() -> None:
    contract = _contract()
    binding = _binding()
    suitability = _suitability(binding)
    blocked_statuses = (
        CurrentRegistryResolutionPathAvailabilityStatus.NOT_REGISTERED,
        CurrentRegistryResolutionPathAvailabilityStatus.EVIDENCE_DECLARATION_MISMATCH,
        CurrentRegistryResolutionPathAvailabilityStatus.DISABLED,
    )

    for status in blocked_statuses:
        result = _assess(
            contract,
            suitability,
            _runtime_observation(binding, registry_status=status),
        )
        assert result is not None
        assert result.suitability == suitability
        assert result.eligible_for_selection is False
        assert not hasattr(result, "unsuitable")


def test_r4_canonical_positive_runtime_readiness_is_mandatory() -> None:
    contract = _contract()
    binding = _binding()
    suitability = _suitability(binding)
    cases = (
        (CanonicalRuntimeReadinessProjectionStatus.READINESS_NOT_PROVISIONED, None),
        (CanonicalRuntimeReadinessProjectionStatus.READINESS_NOT_DECLARED, None),
        (CanonicalRuntimeReadinessProjectionStatus.UNKNOWN, False),
        (CanonicalRuntimeReadinessProjectionStatus.UNAVAILABLE, False),
        (CanonicalRuntimeReadinessProjectionStatus.AVAILABLE, None),
        (CanonicalRuntimeReadinessProjectionStatus.AVAILABLE, False),
    )

    for status, ready in cases:
        result = _assess(
            contract,
            suitability,
            _runtime_observation(binding, runtime_status=status, ready=ready),
        )
        assert result is not None
        assert result.eligible_for_selection is False
        assert result.suitability == suitability


def test_r5_degraded_follows_canonical_ready_without_reinterpreting_metadata() -> None:
    contract = _contract()
    binding = _binding()
    suitability = _suitability(binding)
    ready_observation = _runtime_observation(
        binding,
        runtime_status=CanonicalRuntimeReadinessProjectionStatus.DEGRADED,
        ready=True,
    )
    not_ready_observation = _runtime_observation(
        binding,
        runtime_status=CanonicalRuntimeReadinessProjectionStatus.DEGRADED,
        ready=False,
    )

    eligible = _assess(contract, suitability, ready_observation)
    not_established = _assess(contract, suitability, not_ready_observation)

    assert eligible is not None
    assert eligible.eligible_for_selection is True
    assert not_established is not None
    assert not_established.eligible_for_selection is False


def test_r6_no_positive_eligibility_does_not_create_negative_suitability() -> None:
    contract = _contract()
    binding = _binding()
    suitability = _suitability(binding)
    observation = _runtime_observation(
        binding,
        runtime_status=CanonicalRuntimeReadinessProjectionStatus.UNAVAILABLE,
        ready=False,
    )

    result = _assess(contract, suitability, observation)

    assert result is not None
    assert result.eligible_for_selection is False
    assert result.suitability == suitability
    assert not hasattr(result, "unsuitable")
    assert not hasattr(result, "negative_suitability_score")
    assert not hasattr(result, "permanently_prohibited")


def test_r7_zero_one_many_eligibility_results_remain_independent_and_unranked() -> None:
    contract = _contract()
    bindings = (_binding("fixture.beta"), _binding("fixture.alpha"))
    results = tuple(
        _assess(
            contract,
            _suitability(binding),
            _runtime_observation(binding),
        )
        for binding in bindings
    )

    assert all(result is not None for result in results)
    assert tuple(result.suitability.capability_name for result in results) == (
        "fixture.beta",
        "fixture.alpha",
    )
    assert all(result.eligible_for_selection is True for result in results)
    assert all(not hasattr(result, "rank") for result in results)
    assert all(not hasattr(result, "selected") for result in results)
    assert all(not hasattr(result, "preferred") for result in results)


def test_r8_boundary_is_read_only_derivational_and_non_selective() -> None:
    contract = _contract()
    assessor = contract.GovernedSelectionEligibilityAssessment()

    assert assessor.read_only is True
    assert assessor.derivational is True
    forbidden_true = {
        "mutates_suitability",
        "mutates_resolution_binding",
        "queries_capability_registry",
        "mutates_capability_registry",
        "queries_official_runtime",
        "mutates_official_runtime",
        "creates_runtime_capability_graph",
        "creates_runtime_readiness_evidence",
        "creates_suitability",
        "reconstructs_suitability",
        "infers_suitability",
        "scores_sources",
        "compares_sources",
        "ranks_sources",
        "prefers_sources",
        "filters_sources",
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "acquires_evidence",
        "certifies_truth",
        "grants_authority",
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
        "claims_subjective_experience",
        "claims_consciousness",
    }
    defaults = {field.name: getattr(assessor, field.name) for field in fields(assessor)}
    for field_name in forbidden_true:
        assert field_name in defaults
        assert defaults[field_name] is False
