from datetime import datetime, timezone

import pytest

from core.adaptive_cognition import (
    InMemoryMetaReasoningRepository,
    MentalModel,
    MentalModelKind,
    MetaReasoningDimension,
    MetaReasoningEngine,
    MetaReasoningFinding,
    MetaReasoningFindingSeverity,
    MetaReasoningJudgement,
    MetaReasoningManager,
    MetaReasoningPolicy,
    ReasoningReference,
)
from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimConfidence,
    ClaimOrigin,
    ClaimRegistryManager,
    ClaimStatus,
    ClaimType,
    ConflictResolutionManager,
    DecisionRecordManager,
    EvidenceRegistry,
    GovernedContextAssembler,
    GovernedInferenceEngine,
    GovernedReasoningOrchestrator,
    InferenceRule,
    InMemoryDecisionRecordRepository,
    InMemoryInferenceRuleRegistry,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def result(*, claim: bool = True, review: bool = False):
    claims = ClaimRegistryManager()
    if claim:
        claims.register(
            Claim(
                "task",
                "status",
                "pending",
                ClaimType.ASSUMPTION,
                ClaimOrigin.HUMAN,
                ClaimStatus.REVIEW_REQUIRED if review else ClaimStatus.PROPOSED,
                confidence=ClaimConfidence(0.8, "confirmed"),
                owner="shared",
                created_at=NOW,
                claim_id="claim-task-status",
            )
        )
    assembler = GovernedContextAssembler(
        claim_registry=claims,
        evidence_registry=EvidenceRegistry(),
    )
    registry = InMemoryInferenceRuleRegistry()
    registry.register(
        InferenceRule(
            "task.pending",
            "1.0.0",
            "identify pending task",
            (ClaimCondition("status", values=("pending",)),),
            "task",
            "is_pending",
            "true",
            base_confidence=0.7,
        )
    )
    orchestrator = GovernedReasoningOrchestrator(
        context_assembler=assembler,
        inference_engine=GovernedInferenceEngine(registry),
        conflict_manager=ConflictResolutionManager(),
        decision_manager=DecisionRecordManager(InMemoryDecisionRecordRepository()),
    )
    query = ReasoningQuery(
        "task status",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        as_of=NOW,
    )
    return orchestrator.reason(query, now=NOW)


def test_reference_requires_non_empty_fields() -> None:
    with pytest.raises(ValueError):
        ReasoningReference("", "id")


def test_finding_identity_is_stable() -> None:
    finding = MetaReasoningFinding(
        MetaReasoningDimension.INFERENCE_QUALITY,
        "Inference was inspected.",
        MetaReasoningFindingSeverity.INFO,
        0.8,
    )
    assert len(finding.finding_id) == 64


def test_finding_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        MetaReasoningFinding(
            MetaReasoningDimension.INFERENCE_QUALITY,
            "bad",
            MetaReasoningFindingSeverity.INFO,
            2.0,
        )


def test_policy_requires_descending_thresholds() -> None:
    with pytest.raises(ValueError):
        MetaReasoningPolicy(sound_threshold=0.5, acceptable_threshold=0.8)


def test_engine_creates_traceable_assessment() -> None:
    assessment = MetaReasoningEngine().assess(result(), now=NOW)
    assert assessment.reasoning_result_id == result().result_id
    assert len(assessment.assessment_id) == 64
    assert assessment.findings


def test_assessment_does_not_change_source_result() -> None:
    source = result()
    before = source.snapshot()
    MetaReasoningEngine().assess(source, now=NOW)
    assert source.snapshot() == before


def test_missing_evidence_is_reported() -> None:
    assessment = MetaReasoningEngine().assess(result(), now=NOW)
    evidence = next(
        item
        for item in assessment.findings
        if item.normalized_dimension is MetaReasoningDimension.EVIDENCE_SUFFICIENCY
    )
    assert evidence.normalized_severity is MetaReasoningFindingSeverity.HIGH


def test_abstained_reasoning_is_not_judged_sound() -> None:
    assessment = MetaReasoningEngine().assess(result(claim=False), now=NOW)
    assert assessment.normalized_judgement in {
        MetaReasoningJudgement.UNCERTAIN,
        MetaReasoningJudgement.DEFICIENT,
    }


def test_review_required_produces_reviewable_assessment() -> None:
    assessment = MetaReasoningEngine().assess(result(review=True), now=NOW)
    assert assessment.requires_review


def test_mental_models_are_references_not_mutated_inputs() -> None:
    model = MentalModel(
        "ROBY",
        MentalModelKind.SELF,
        "shared",
        (ScopeDomain.PERSONAL_OPERATIONS,),
    )
    assessment = MetaReasoningEngine().assess(result(), mental_models=(model,), now=NOW)
    assert assessment.mental_model_ids == (model.model_id,)
    assert model.revision == 1


def test_repository_stores_assessments() -> None:
    repository = InMemoryMetaReasoningRepository()
    assessment = MetaReasoningEngine().assess(result(), now=NOW)
    repository.add(assessment)
    assert repository.get(assessment.assessment_id) == assessment


def test_repository_rejects_duplicates() -> None:
    repository = InMemoryMetaReasoningRepository()
    assessment = MetaReasoningEngine().assess(result(), now=NOW)
    repository.add(assessment)
    with pytest.raises(ValueError):
        repository.add(assessment)


def test_repository_filters_by_reasoning_result() -> None:
    repository = InMemoryMetaReasoningRepository()
    assessment = MetaReasoningEngine().assess(result(), now=NOW)
    repository.add(assessment)
    assert repository.for_result(assessment.reasoning_result_id) == (assessment,)


def test_manager_persists_last_assessment() -> None:
    manager = MetaReasoningManager()
    assessment = manager.assess(result(), now=NOW)
    assert manager.last_assessment == assessment
    assert manager.repository.get(assessment.assessment_id) == assessment


def test_manager_prompt_preserves_governance_boundary() -> None:
    lines = MetaReasoningManager().system_prompt_lines()
    assert any("no reemplaza" in line for line in lines)
    assert any("automáticamente" in line for line in lines)


def test_assessment_is_serializable() -> None:
    payload = MetaReasoningEngine().assess(result(), now=NOW).to_dict()
    assert payload["reasoning_result_id"]
    assert len(payload["findings"]) == 5


def test_findings_reference_decision_and_result() -> None:
    assessment = MetaReasoningEngine().assess(result(), now=NOW)
    reference_types = {
        reference.reference_type
        for finding in assessment.findings
        for reference in finding.references
    }
    assert reference_types == {"decision", "reasoning_result"}


def test_recommendations_are_advisory() -> None:
    assessment = MetaReasoningEngine().assess(result(), now=NOW)
    assert "Acquire additional governed evidence." in assessment.recommendations


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError):
        MetaReasoningEngine().assess(result(), now=datetime(2026, 7, 10, 12, 0))


def test_custom_policy_changes_judgement_threshold() -> None:
    engine = MetaReasoningEngine(
        MetaReasoningPolicy(
            sound_threshold=0.95,
            acceptable_threshold=0.2,
            uncertain_threshold=0.1,
        )
    )
    assessment = engine.assess(result(), now=NOW)
    assert assessment.normalized_judgement is MetaReasoningJudgement.ACCEPTABLE
