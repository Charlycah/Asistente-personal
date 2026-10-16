from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from app.governed_explanatory_model_revision import (
    GovernedEvidenceDrivenExplanatoryModelRevisionV1,
    GovernedExplanatoryModelRevisionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_reasoning_runtime import CanonicalProductiveReasoningSource
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceAssessment,
)
from tests.architecture import (
    test_explanatory_model_discriminating_inquiry_investigation_reentry_block as inquiry,  # noqa: E501
)
from tests.architecture import (
    test_ordinary_multi_hypothesis_reachability_block as ordinary,
)

NOW = datetime(2026, 8, 28, 15, 0, tzinfo=timezone.utc)
EVIDENCE_ID = "evidence-level2-revision-0001"


def _previous():
    gateway, turn_id, model = inquiry._causal_model_with_requirement()
    return gateway, turn_id, model


def _reentry(model, *, evidence_id=EVIDENCE_ID, requirement_id=None):
    requirement = model.discrimination.discrimination_requirements[0]
    return GovernedLevel2ReasoningReentryResult(
        reentry_id="level2-reasoning-reentry-revision0001",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id="level2-execution-revision0001",
        authorization_id="independence-authorization-revision0001",
        requirement_id=requirement_id or requirement.requirement_id,
        plan_id="evidence-acquisition-plan-revision0001",
        capability_name="test_read_only_evidence",
        evidence_id=evidence_id,
        source_reference=model.model.source_reference,
        world_snapshot_id=model.model.world_snapshot_id,
        reasoning_result=None,
        rationale_codes=("test:governed_reentry",),
        source_fingerprint="revision-reentry-fingerprint",
        automatic_reevaluation_count=1,
    )


def _revised_report(model, *, evidence_id=EVIDENCE_ID, apply=True):
    assessments = []
    for index, component in enumerate(model.model.components):
        refs = component.evidence_references
        if apply and index == 0:
            refs = tuple(dict.fromkeys((*refs, evidence_id)))
        assessments.append(
            HypothesisEvidenceAssessment(
                hypothesis_id=component.hypothesis_id,
                proposition=component.proposition,
                relation=component.evidence_relation,
                evidence_references=refs,
                rationale_codes=("revision:reassessed_with_governed_evidence",),
            )
        )
    return GovernedHypothesisDeepeningReport(
        report_id="hypothesis-deepening-revision-0001",
        status=HypothesisDeepeningStatus.COMPLETE,
        source_kind=HypothesisDeepeningSourceKind.CAUSAL_PREDICTION,
        source_reference=model.model.source_reference,
        world_snapshot_id=model.model.world_snapshot_id,
        assessments=tuple(assessments),
        epistemic_gaps=(),
        evidence_codes=("revision:level2_acquired_evidence",),
        risk_codes=("revision:evidence_does_not_establish_truth",),
        source_fingerprint="revision-deepening-fingerprint",
    )


def test_v1_plus_acquired_evidence_produces_materially_distinct_v2():
    _, _, previous = _previous()
    result = GovernedEvidenceDrivenExplanatoryModelRevisionV1().consume(
        previous,
        _reentry(previous),
        _revised_report(previous),
    )
    assert result.status is GovernedExplanatoryModelRevisionStatus.REVISED
    assert result.previous_model_id == previous.model.model_id
    assert result.revised_model_id is not None
    assert result.revised_model_id != previous.model.model_id
    assert result.evidence_id == EVIDENCE_ID
    assert result.changed_hypothesis_ids
    assert result.removed_requirement_ids == (
        previous.discrimination.discrimination_requirements[0].requirement_id,
    )


def test_revision_preserves_same_hypothesis_set_and_exact_evidence_lineage():
    _, _, previous = _previous()
    result = GovernedEvidenceDrivenExplanatoryModelRevisionV1().consume(
        previous,
        _reentry(previous),
        _revised_report(previous),
    )
    assert result.revised_consumption is not None
    before = tuple(sorted(item.hypothesis_id for item in previous.model.components))
    after = tuple(
        sorted(
            item.hypothesis_id for item in result.revised_consumption.model.components
        )
    )
    assert before == after
    assert any(
        EVIDENCE_ID in item.evidence_references
        for item in result.revised_consumption.model.components
    )
    assert result.requirement_id in previous.model.unresolved_requirement_ids


def test_revision_requires_successful_governed_reentry_before_model_revision():
    _, _, previous = _previous()
    reentry = replace(
        _reentry(previous),
        status=GovernedReasoningReentryStatus.REVIEW_REQUIRED,
        evidence_id=None,
        automatic_reevaluation_count=0,
    )
    result = GovernedEvidenceDrivenExplanatoryModelRevisionV1().consume(
        previous,
        reentry,
        _revised_report(previous),
    )
    assert result.status is GovernedExplanatoryModelRevisionStatus.REENTRY_REQUIRED
    assert result.revised_consumption is None


def test_revision_fails_closed_when_acquired_evidence_never_reaches_reassessment():
    _, _, previous = _previous()
    result = GovernedEvidenceDrivenExplanatoryModelRevisionV1().consume(
        previous,
        _reentry(previous),
        _revised_report(previous, apply=False),
    )
    assert result.status is (
        GovernedExplanatoryModelRevisionStatus.EVIDENCE_NOT_APPLIED
    )
    assert result.revised_consumption is None


def test_revision_fails_closed_on_hypothesis_replacement():
    _, _, previous = _previous()
    report = _revised_report(previous)
    replaced = replace(
        report.assessments[0],
        hypothesis_id="causal-hypothesis-replacement",
    )
    report = replace(
        report,
        assessments=(replaced, *report.assessments[1:]),
    )
    result = GovernedEvidenceDrivenExplanatoryModelRevisionV1().consume(
        previous,
        _reentry(previous),
        report,
    )
    assert result.status is (
        GovernedExplanatoryModelRevisionStatus.HYPOTHESIS_SET_MISMATCH
    )


def test_revision_fails_closed_on_requirement_or_snapshot_lineage_mismatch():
    _, _, previous = _previous()
    bad_reentry = _reentry(
        previous,
        requirement_id="discrimination-requirement-unrelated",
    )
    result = GovernedEvidenceDrivenExplanatoryModelRevisionV1().consume(
        previous,
        bad_reentry,
        _revised_report(previous),
    )
    assert result.status is GovernedExplanatoryModelRevisionStatus.LINEAGE_MISMATCH


def test_revision_remains_strictly_consultative_and_non_authoritative():
    _, _, previous = _previous()
    result = GovernedEvidenceDrivenExplanatoryModelRevisionV1().consume(
        previous,
        _reentry(previous),
        _revised_report(previous),
    )
    assert result.read_only and result.consultative
    assert not result.persists_results
    assert not result.creates_facts
    assert not result.establishes_truth
    assert not result.establishes_causality
    assert not result.creates_questions
    assert not result.creates_learning
    assert not result.modifies_memory
    assert not result.modifies_world_model
    assert not result.executes_transfer
    assert not result.registers_rule
    assert not result.executes_actions
    assert not result.grants_authority


def test_gateway_binds_v1_evidence_v2_and_exposes_exact_same_turn_references():
    gateway, source_turn_id, previous = _previous()
    text = "Revisar el modelo explicativo con la nueva evidencia."
    request = GovernedConversationPipelineRequest(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        text=text,
    )
    turn_id = build_governed_conversation_turn_identity(request, NOW).turn_id
    result = gateway.bind_productive_explanatory_model_revision(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
        source_turn_id=source_turn_id,
        reentry=_reentry(previous),
        revised_report=_revised_report(previous),
    )
    assert result.status is GovernedExplanatoryModelRevisionStatus.REVISED
    refs = gateway.productive_explanatory_model_revision_reference_ids(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
    )
    assert result.revision_id in refs
    assert result.previous_model_id in refs
    assert result.revised_model_id in refs
    assert result.reentry_id in refs
    assert result.requirement_id in refs
    assert EVIDENCE_ID in refs
    assert (
        gateway.productive_explanatory_model_revision_reference_ids(
            owner=ordinary.OWNER,
            session_id=ordinary.SESSION,
            turn_id="other-turn",
        )
        == ()
    )


def test_revision_reaches_ordinary_reasoning_as_consultative_context():
    gateway, source_turn_id, previous = _previous()
    text = "Revisar el modelo explicativo con la nueva evidencia."
    request = GovernedConversationPipelineRequest(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        text=text,
    )
    turn_id = build_governed_conversation_turn_identity(request, NOW).turn_id
    gateway.bind_productive_explanatory_model_revision(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        turn_id=turn_id,
        source_turn_id=source_turn_id,
        reentry=_reentry(previous),
        revised_report=_revised_report(previous),
    )
    source = CanonicalProductiveReasoningSource(gateway)
    lines = source.explanatory_model_revision_context_lines(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        text=text,
        now=NOW,
    )
    assert "Modelo explicativo revisado por evidencia gobernada" in lines[0]
    assert "no establece verdad, causalidad" in lines[1]
    refs = source.reference_ids(
        owner=ordinary.OWNER,
        session_id=ordinary.SESSION,
        text=text,
        now=NOW,
    )
    assert EVIDENCE_ID in refs
