from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveObservabilityProfile,
    CognitivePlanner,
)


def test_summary_export_is_versioned_and_metrics_only():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    export = kernel.export_observability(decision)

    assert export.schema_version == "rp22.05"
    assert export.profile is CognitiveObservabilityProfile.SUMMARY
    assert export.metrics["total_decisions"] == 1
    assert export.calibration is not None
    assert export.explanation is None
    assert "explanation_omitted_by_profile" in export.redaction_codes


def test_diagnostic_export_redacts_free_text_narrative():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    payload = kernel.export_observability(
        decision,
        profile=CognitiveObservabilityProfile.DIAGNOSTIC,
    ).as_dict()

    assert payload["explanation"]["narrative"] == "[redacted]"
    assert "explanation_narrative_redacted" in payload["redaction_codes"]


def test_metrics_only_export_does_not_require_a_decision():
    kernel = CognitiveDecisionKernel()

    payload = kernel.export_observability().as_dict()

    assert payload["metrics"]["total_decisions"] == 0
    assert payload["calibration"] is None
    assert payload["explanation"] is None


def test_export_is_deterministic_and_has_no_persistence_side_effects(tmp_path):
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    first = kernel.export_observability(decision).as_dict()
    second = kernel.export_observability(decision).as_dict()

    assert first == second
    assert list(tmp_path.iterdir()) == []


def test_shadow_runtime_export_is_explicit_and_fail_open():
    class LegacyKernel:
        pass

    runtime = CognitivePlannerShadowRuntime(decision_kernel=LegacyKernel())

    assert runtime.export_kernel_observability() is None
