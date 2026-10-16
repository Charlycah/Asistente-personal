from __future__ import annotations

import ast
import inspect
from dataclasses import replace

import pytest

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessmentFoundationV1,
    GovernedReasoningAssessmentObservation,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityStatus,
)


def _pair(
    suffix: str = "one",
) -> tuple[GovernedReasoningQualityAssessment, GovernedEpistemicSufficiencyAssessment]:
    sufficiency = GovernedEpistemicSufficiencyAssessment(
        assessment_id=f"epistemic-sufficiency-{suffix:0<24}"[:47],
        status=EpistemicSufficiencyStatus.SUFFICIENT,
        source_hypothesis_deepening_report_id=f"deepening-{suffix}",
        source_multi_hypothesis_discrimination_report_id=None,
        source_hypothesis_update_semantics_report_id=None,
        source_reference="scenario-123",
        world_snapshot_id=f"world-{suffix}",
        hypothesis_ids=(f"hypothesis-{suffix}",),
        unresolved_hypothesis_ids=(),
        epistemic_gap_ids=(),
        discrimination_requirement_ids=(),
        rationale_codes=(f"sufficiency:{suffix}",),
        source_fingerprint=f"sufficiency-fingerprint-{suffix}",
    )
    quality = GovernedReasoningQualityAssessment(
        assessment_id=f"reasoning-quality-{suffix:0<24}"[:42],
        status=GovernedReasoningQualityStatus.ADEQUATE,
        source_hypothesis_deepening_report_id=f"deepening-{suffix}",
        source_epistemic_sufficiency_assessment_id=sufficiency.assessment_id,
        source_hypothesis_update_semantics_report_id=None,
        source_multi_hypothesis_discrimination_report_id=None,
        source_reference=sufficiency.source_reference,
        world_snapshot_id=sufficiency.world_snapshot_id,
        rationale_codes=(f"quality:{suffix}",),
        source_fingerprint=f"quality-fingerprint-{suffix}",
    )
    return quality, sufficiency


def test_live_assessments_project_to_exact_neutral_observation() -> None:
    quality, sufficiency = _pair()
    result = GovernedReasoningAssessmentObservation.from_assessments(
        quality,
        sufficiency,
    )

    assert result.quality_assessment_id == quality.assessment_id
    assert result.quality_status is quality.status
    assert result.sufficiency_assessment_id == sufficiency.assessment_id
    assert result.sufficiency_status is sufficiency.status
    assert result.source_reference == quality.source_reference
    assert result.world_snapshot_id == quality.world_snapshot_id
    assert result.quality_source_fingerprint == quality.source_fingerprint
    assert result.sufficiency_source_fingerprint == sufficiency.source_fingerprint


def test_observation_contract_is_neutral_without_full_assessment_fields() -> None:
    names = set(GovernedReasoningAssessmentObservation.__annotations__)
    required = {
        "quality_assessment_id",
        "quality_status",
        "sufficiency_assessment_id",
        "sufficiency_status",
        "source_reference",
        "world_snapshot_id",
        "quality_source_fingerprint",
        "sufficiency_source_fingerprint",
    }
    assert required <= names
    assert "quality" not in names
    assert "sufficiency" not in names


def test_neutral_observation_rejects_non_governed_authority() -> None:
    quality, sufficiency = _pair()
    observation = GovernedReasoningAssessmentObservation.from_assessments(
        quality,
        sufficiency,
    )

    with pytest.raises(ValueError, match="preserve reasoning authority"):
        replace(observation, canonical_authority="other")


def test_neutral_observation_rejects_non_read_only_contract() -> None:
    quality, sufficiency = _pair()
    observation = GovernedReasoningAssessmentObservation.from_assessments(
        quality,
        sufficiency,
    )

    with pytest.raises(ValueError, match="remain read-only"):
        replace(observation, read_only=False)


def test_live_adapter_preserves_governed_read_only_contract() -> None:
    quality, sufficiency = _pair()
    observation = GovernedReasoningAssessmentObservation.from_assessments(
        quality,
        sufficiency,
    )

    assert observation.canonical_authority == "governed_reasoning"
    assert observation.read_only is True
    assert observation.consultative is True


def test_live_adapter_rejects_pair_lineage_mismatch() -> None:
    quality, _sufficiency = _pair("one")
    _other_quality, other = _pair("two")

    with pytest.raises(ValueError, match="quality/sufficiency lineage mismatch"):
        GovernedReasoningAssessmentObservation.from_assessments(quality, other)


def test_live_adapter_rejects_source_or_snapshot_mismatch() -> None:
    quality, sufficiency = _pair()
    other_source = replace(sufficiency, source_reference="scenario-other")
    with pytest.raises(ValueError, match="source lineage mismatch"):
        GovernedReasoningAssessmentObservation.from_assessments(quality, other_source)

    other_snapshot = replace(sufficiency, world_snapshot_id="world-other")
    with pytest.raises(ValueError, match="snapshot lineage mismatch"):
        GovernedReasoningAssessmentObservation.from_assessments(
            quality,
            other_snapshot,
        )


def test_neutral_observation_fails_closed_on_missing_provenance() -> None:
    quality, sufficiency = _pair()
    observation = GovernedReasoningAssessmentObservation.from_assessments(
        quality,
        sufficiency,
    )

    with pytest.raises(ValueError, match="quality fingerprint"):
        replace(observation, quality_source_fingerprint="")
    with pytest.raises(ValueError, match="sufficiency fingerprint"):
        replace(observation, sufficiency_source_fingerprint="")


def test_neutral_observation_rejects_non_enum_statuses() -> None:
    quality, sufficiency = _pair()
    observation = GovernedReasoningAssessmentObservation.from_assessments(
        quality,
        sufficiency,
    )

    with pytest.raises(ValueError, match="quality status"):
        replace(observation, quality_status="adequate")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="sufficiency status"):
        replace(observation, sufficiency_status="sufficient")  # type: ignore[arg-type]


def test_foundation_accepts_direct_neutral_observations_without_full_reports() -> None:
    first_quality, first_sufficiency = _pair("one")
    second_quality, second_sufficiency = _pair("two")
    observations = (
        GovernedReasoningAssessmentObservation.from_assessments(
            first_quality,
            first_sufficiency,
        ),
        GovernedReasoningAssessmentObservation.from_assessments(
            second_quality,
            second_sufficiency,
        ),
    )

    result = GovernedLongitudinalReasoningAssessmentFoundationV1().assess(observations)

    assert result.adequate_count == 2
    assert result.sufficient_count == 2
    assert result.source_reasoning_quality_assessment_ids == (
        first_quality.assessment_id,
        second_quality.assessment_id,
    )


def test_generalized_core_does_not_import_event_bus_memory_or_history_reader() -> None:
    module = inspect.getmodule(GovernedReasoningAssessmentObservation)
    assert module is not None
    source = inspect.getsource(module)
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert "core.cognitive_event_bus" not in imports
    assert all("memory" not in name for name in imports)
    assert "app.governed_reasoning_assessment_event_projection" not in imports
    assert "app.admitted_reasoning_event_history_reader" not in imports
