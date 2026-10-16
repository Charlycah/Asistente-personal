from __future__ import annotations

from importlib import import_module
from pathlib import Path

cert = import_module(
    "scripts.whole_system_cross_capability_cognitive_integration_transfer_certification"
)

ROOT = Path(__file__).resolve().parents[2]
HARNESS = (
    ROOT
    / "scripts"
    / "whole_system_cross_capability_cognitive_integration_transfer_certification.py"
)


def _cci08():
    return next(item for item in cert._scenarios() if item.scenario_id == "CCI-08")


def test_cci08_uses_current_source_owned_explainability_evidence():
    scenario = _cci08()
    by_stage = {item.stage: item for item in scenario.evidence}
    assert "source_owned_explanation_boundary" in by_stage
    requirement = by_stage["source_owned_explanation_boundary"]
    assert requirement.path == "core/governed_reasoning/explanations.py"
    assert "ExplainableAnswerRenderer" in requirement.tokens
    assert "DecisionRecord" in requirement.tokens
    assert "immutable decisions" in requirement.tokens


def test_cci08_does_not_claim_productive_personality_to_explainability_wiring():
    scenario = _cci08()
    assert "bounded adaptive delivery" in scenario.cognitive_flow
    assert "source-owned explanation boundary" in scenario.cognitive_flow
    assert "explanation presentation only" not in scenario.cognitive_flow
    assert "explanation_profile" not in {item.stage for item in scenario.evidence}


def test_retired_global_m378_evidence_cannot_return_to_cross_capability_harness():
    source = HARNESS.read_text(encoding="utf-8")
    assert "core/intelligent_explanations.py" not in source
    assert "AdaptivePersonalityProfile" not in source


def test_cci08_passes_by_design_with_current_boundaries():
    result = next(
        item for item in cert.run_certification(ROOT).scenarios
        if item.scenario_id == "CCI-08"
    )
    assert result.status is cert.CertificationStatus.PASS_BY_DESIGN
    assert result.missing_stages == ()
