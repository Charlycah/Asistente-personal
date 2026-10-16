from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.cognitive_authority_map import CognitiveAuthorityMap
from app.cognitive_operational_inventory import CognitiveAuthority
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.causal_prediction import (
    CausalHypothesis,
    GovernedCausalPredictiveReasoner,
)
from core.governed_reasoning.governed_prediction import (
    GovernedPredictionDisposition,
    GovernedPredictionEvaluator,
    GovernedPredictionRequest,
    GovernedPredictionStatus,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 20, 0, tzinfo=timezone.utc)


def _fact(fact_id: str, key: str, value: str) -> PersistentWorldFact:
    return PersistentWorldFact(
        fact_id=fact_id,
        domain=PersistentWorldDomain.ENVIRONMENT,
        fact_key=key,
        value=value,
        source_authority="canonical_memory",
        source_reference=f"ref:{fact_id}",
        epistemic_level=EpistemicLevel.FACT,
        evidence_codes=("explicit_governed_source",),
        persisted_by_source=True,
        source_updated_at=NOW,
    )


def _source(*, weather: str = "rain", patio: str = "wet"):
    world = PersistentWorldModelView().build(
        (
            _fact("weather", "weather.current", weather),
            _fact("patio", "patio.state", patio),
        )
    )
    hypothesis = CausalHypothesis(
        relation_id="rel-rain-wet",
        proposition="Rain could be associated with a wet patio",
        cause_domain="environment",
        cause_key="weather.current",
        cause_value="rain",
        effect_domain="environment",
        effect_key="patio.state",
        effect_value="wet",
        evidence_codes=("explicit_causal_hypothesis",),
    )
    return GovernedCausalPredictiveReasoner().analyze(world, (hypothesis,))


def _request(
    prediction_id: str = "pred-patio",
    relation_id: str = "rel-rain-wet",
) -> GovernedPredictionRequest:
    return GovernedPredictionRequest(
        prediction_id=prediction_id,
        relation_id=relation_id,
        horizon_code="next_observation_window",
        condition_codes=("condition:rain_continues",),
    )


def test_m391_7_preserves_governed_reasoning_as_single_authority() -> None:
    assignment = CognitiveAuthorityMap().snapshot.authority_for(
        CognitiveAuthority.REASONING
    )
    evaluator = GovernedPredictionEvaluator()
    assert assignment.primary == "governed_reasoning"
    assert evaluator.CANONICAL_AUTHORITY == "governed_reasoning"
    assert not hasattr(evaluator, "authority_id")


def test_m391_7_supported_prediction_remains_inference() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    item = report.assessments[0]
    assert item.disposition is GovernedPredictionDisposition.CONDITIONALLY_SUPPORTED
    assert item.epistemic_level is EpistemicLevel.INFERENCE
    assert item.is_future_fact is False
    assert report.creates_facts is False


def test_m391_7_preserves_explicit_horizon_and_conditions() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    item = report.assessments[0]
    assert item.horizon_code == "next_observation_window"
    assert item.condition_codes == ("condition:rain_continues",)
    assert "prediction:horizon_is_explicit_not_inferred" in item.rationale_codes


def test_m391_7_current_contradiction_remains_visible() -> None:
    report = GovernedPredictionEvaluator().evaluate(
        _source(patio="dry"),
        (_request(),),
    )
    assert report.assessments[0].disposition is (
        GovernedPredictionDisposition.CURRENTLY_CONTRADICTED
    )


def test_m391_7_missing_source_relation_requires_review() -> None:
    report = GovernedPredictionEvaluator().evaluate(
        _source(),
        (_request(relation_id="missing-relation"),),
    )
    assert report.status is GovernedPredictionStatus.REVIEW_REQUIRED
    assert report.assessments[0].disposition is GovernedPredictionDisposition.REVIEW
    assert "prediction_review_required" in report.risk_codes


def test_m391_7_empty_requests_are_insufficient_not_invented() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), ())
    assert report.status is GovernedPredictionStatus.INSUFFICIENT_EVIDENCE
    assert report.assessments == ()


def test_m391_7_does_not_calibrate_probability() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    item = report.assessments[0]
    assert item.probability_calibrated is False
    assert report.calibrates_probability is False
    assert "probability_not_calibrated" in report.risk_codes


def test_m391_7_does_not_verify_future_outcomes() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    assert report.assessments[0].outcome_verified is False
    assert report.verifies_outcomes is False


def test_m391_7_cannot_promote_prediction_to_fact() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    with pytest.raises(ValueError, match="future facts"):
        replace(report.assessments[0], is_future_fact=True)


def test_m391_7_cannot_claim_probability_calibration() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    with pytest.raises(ValueError, match="does not calibrate probability"):
        replace(report.assessments[0], probability_calibrated=True)


def test_m391_7_same_inputs_are_deterministic_and_order_independent() -> None:
    source = _source()
    requests = (_request("b"), _request("a"))
    evaluator = GovernedPredictionEvaluator()
    assert evaluator.evaluate(source, requests) == evaluator.evaluate(
        source,
        tuple(reversed(requests)),
    )


def test_m391_7_duplicate_prediction_ids_are_rejected() -> None:
    request = _request()
    with pytest.raises(ValueError, match="ids must be unique"):
        GovernedPredictionEvaluator().evaluate(_source(), (request, request))


def test_m391_7_reports_are_immutable() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    with pytest.raises(FrozenInstanceError):
        report.status = GovernedPredictionStatus.DEGRADED
    with pytest.raises(FrozenInstanceError):
        report.assessments[0].horizon_code = "changed"


def test_m391_7_does_not_persist_learn_plan_decide_or_execute() -> None:
    report = GovernedPredictionEvaluator().evaluate(_source(), (_request(),))
    assert report.read_only is True
    assert report.persists_results is False
    assert report.modifies_world_model is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.modifies_decision is False
    assert report.executes_actions is False
    assert report.grants_authority is False
    assert report.starts_background_process is False


def test_m391_7_safe_failure_degrades_without_authority() -> None:
    class BrokenEvaluator(GovernedPredictionEvaluator):
        @staticmethod
        def _assess(source, request):
            raise RuntimeError("synthetic failure")

    report = BrokenEvaluator().evaluate_safely(_source(), (_request(),))
    assert report.status is GovernedPredictionStatus.DEGRADED
    assert report.assessments == ()
    assert report.risk_codes == ("governed_prediction_failure",)


def test_m391_7_has_no_credentials_storage_or_background_dependency() -> None:
    source = (
        ROOT / "core" / "governed_reasoning" / "governed_prediction.py"
    ).read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "sqlite" not in source.casefold()
    assert "threading" not in source
    assert "asyncio" not in source
    assert "sleep(" not in source


def test_m391_7_does_not_modify_m391_4_predictor_contract() -> None:
    source = (
        ROOT / "core" / "governed_reasoning" / "causal_prediction.py"
    ).read_text(encoding="utf-8")
    assert "m391.7" not in source.casefold()
    assert "GovernedPredictionEvaluator" not in source


def test_m391_7_preserves_canonical_core_constructor_line() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]


def test_m391_7_documentation_records_governed_scope() -> None:
    document = ROOT / "docs" / "M391_7_GOVERNED_PREDICTION.md"
    text = document.read_text(encoding="utf-8")
    assert "governed_reasoning" in text
    assert "M391.4" in text
    assert "INFERENCE" in text
    assert "probabilidad" in text
    assert "M391.7" in (ROOT / "README.md").read_text(encoding="utf-8")
