from __future__ import annotations

import ast
import inspect
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.decision_advisory_conversational_realization import (
    DecisionAdvisoryConversationalOutcome,
    DecisionAdvisoryConversationalRealizer,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.governed_decision_advisory import (
    DecisionAdvisoryStatus,
    DecisionOptionDisposition,
    GovernedDecisionAdvisor,
    GovernedDecisionAdvisoryReport,
    GovernedDecisionOptionAssessment,
)

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ExplicitHumanDecisionDeliberationEvidenceProducer()
ADAPTER = ExplicitDeliberationDecisionOptionAdapter()
REALIZER = DecisionAdvisoryConversationalRealizer()


def _evidence_and_adaptation(text: str = "¿A o B?"):
    evidence = PRODUCER.analyze(text)
    adaptation = ADAPTER.adapt(evidence)
    return evidence, adaptation


def _recommendation_report(
    option_ids: tuple[str, ...],
) -> GovernedDecisionAdvisoryReport:
    assessments = tuple(
        GovernedDecisionOptionAssessment(
            option_id=option_id,
            disposition=(
                DecisionOptionDisposition.RECOMMEND
                if index == 0
                else DecisionOptionDisposition.REVIEW
            ),
            priority_score=None,
            explicit_preference=0.0,
            reason_codes=(
                "decision:explicit_test_support"
                if index == 0
                else "decision:human_review_required",
            ),
        )
        for index, option_id in enumerate(option_ids)
    )
    return GovernedDecisionAdvisoryReport(
        report_id="decision-advisory-testrecommend",
        status=DecisionAdvisoryStatus.COMPLETE,
        assessments=assessments,
        recommended_option_id=option_ids[0],
        evidence_codes=(),
        risk_codes=("decision_advisory_not_action_authority",),
        source_fingerprint="report-fingerprint",
    )


def test_realizer_presents_recommendation_as_consultive_not_authoritative() -> None:
    evidence, adaptation = _evidence_and_adaptation()
    report = _recommendation_report(
        tuple(item.option_id for item in adaptation.options)
    )

    realization = REALIZER.realize(report, evidence, adaptation)

    assert realization.outcome is (
        DecisionAdvisoryConversationalOutcome.RECOMMENDATION_PRESENT
    )
    assert "«A»" in realization.response_text
    assert "favorece «A»" in realization.response_text
    assert "recomendación consultiva" in realization.response_text
    assert "decisión sigue siendo tuya" in realization.response_text


def test_realizer_maps_actual_neutral_m391_6_report_to_review_required() -> None:
    evidence, adaptation = _evidence_and_adaptation()
    report = GovernedDecisionAdvisor().assess(adaptation.options)

    realization = REALIZER.realize(report, evidence, adaptation)

    assert report.status is DecisionAdvisoryStatus.REVIEW_REQUIRED
    assert realization.outcome is DecisionAdvisoryConversationalOutcome.REVIEW_REQUIRED
    assert "requiere más revisión" in realization.response_text
    assert "decisión sigue siendo tuya" in realization.response_text


def test_realizer_maps_insufficient_and_degraded_to_insufficient_evidence() -> None:
    evidence, adaptation = _evidence_and_adaptation()
    option_ids = tuple(item.option_id for item in adaptation.options)
    assessments = tuple(
        GovernedDecisionOptionAssessment(
            option_id=option_id,
            disposition=DecisionOptionDisposition.REVIEW,
            priority_score=None,
            explicit_preference=0.0,
            reason_codes=("decision:insufficient_explicit_evidence",),
        )
        for option_id in option_ids
    )
    for status in (
        DecisionAdvisoryStatus.INSUFFICIENT_EVIDENCE,
        DecisionAdvisoryStatus.DEGRADED,
    ):
        report = GovernedDecisionAdvisoryReport(
            report_id=f"decision-advisory-{status.value}",
            status=status,
            assessments=assessments,
            recommended_option_id=None,
            evidence_codes=(),
            risk_codes=("decision_advisory_not_action_authority",),
            source_fingerprint="report-fingerprint",
        )
        realization = REALIZER.realize(report, evidence, adaptation)
        assert realization.outcome is (
            DecisionAdvisoryConversationalOutcome.INSUFFICIENT_EVIDENCE
        )
        assert "no hay evidencia suficiente" in realization.response_text
        assert "decisión queda abierta" in realization.response_text


def test_realizer_preserves_certified_titles_ids_and_evidence_lineage() -> None:
    evidence, adaptation = _evidence_and_adaptation(
        "Tengo tres opciones: auto, tren o avión."
    )
    report = GovernedDecisionAdvisor().assess(adaptation.options)

    realization = REALIZER.realize(report, evidence, adaptation)

    assert realization.source_fingerprint == evidence.source_fingerprint
    assert realization.advisory_report_id == report.report_id
    assert realization.referenced_option_ids == tuple(
        option.option_id for option in adaptation.options
    )
    for option in adaptation.options:
        assert f"«{option.title}»" in realization.response_text


def test_realizer_is_deterministic_and_does_not_mutate_inputs() -> None:
    evidence, adaptation = _evidence_and_adaptation()
    report = GovernedDecisionAdvisor().assess(adaptation.options)

    first = REALIZER.realize(report, evidence, adaptation)
    second = REALIZER.realize(report, evidence, adaptation)

    assert first == second
    assert evidence == PRODUCER.analyze("¿A o B?")
    assert adaptation == ADAPTER.adapt(evidence)


def test_realizer_rejects_mismatched_advisory_lineage() -> None:
    evidence, adaptation = _evidence_and_adaptation()
    other_evidence, other_adaptation = _evidence_and_adaptation("¿A o C?")
    report = GovernedDecisionAdvisor().assess(adaptation.options)

    with pytest.raises(ValueError, match="evidence lineage"):
        REALIZER.realize(report, evidence, other_adaptation)
    with pytest.raises(ValueError, match="must match adaptation"):
        REALIZER.realize(report, other_evidence, other_adaptation)


def test_realization_is_frozen_and_declares_non_authoritative_limits() -> None:
    evidence, adaptation = _evidence_and_adaptation()
    report = GovernedDecisionAdvisor().assess(adaptation.options)
    realization = REALIZER.realize(report, evidence, adaptation)

    assert realization.read_only is True
    assert realization.advisory_only is True
    assert realization.human_decision_preserved is True
    assert realization.executes_actions is False
    assert realization.persists_results is False
    assert realization.grants_authority is False
    assert realization.starts_background_process is False
    with pytest.raises(FrozenInstanceError):
        realization.response_text = "changed"


def test_realizer_source_has_no_reasoning_execution_or_external_side_effects() -> None:
    module_path = Path(inspect.getfile(DecisionAdvisoryConversationalRealizer))
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "core.llm_provider" not in imports
    assert "core.intelligent_personal_organization" not in imports
    assert "core.governed_reasoning.scenario_simulation" not in imports
    assert "core.governed_reasoning.causal_prediction" not in imports
    for forbidden in (
        "OpenAI",
        ".generate(",
        ".advise(",
        ".assess(",
        "requests.",
        "socket.",
        "subprocess.",
        "sqlite3",
        "write_text(",
        "write_bytes(",
    ):
        assert forbidden not in source


def test_realizer_never_uses_authoritative_decision_language() -> None:
    source = (
        Path(inspect.getfile(DecisionAdvisoryConversationalRealizer))
        .read_text(encoding="utf-8")
        .casefold()
    )
    for forbidden in (
        "he decidido",
        "debes hacer",
        "la decisión correcta es",
        "voy a ejecutar",
        "ya elegí",
    ):
        assert forbidden not in source
