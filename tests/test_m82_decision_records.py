from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimConfidence,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ConfidenceAssessment,
    ConflictAnalysis,
    ContextAssemblyStatus,
    DecisionClaimLink,
    DecisionEvidenceLink,
    DecisionOutcome,
    DecisionRecord,
    DecisionRecordManager,
    DecisionRuleLink,
    DecisionStatus,
    InferenceResult,
    InferenceRun,
    InferenceStatus,
    InMemoryDecisionRecordRepository,
    ReasoningContextBundle,
    ReasoningQuery,
    ReviewEvent,
    ReviewStatus,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def _claim(cid: str = "claim-a") -> Claim:
    return Claim(
        "task",
        "status",
        "pending",
        ClaimType.ASSUMPTION,
        ClaimOrigin.HUMAN,
        ClaimStatus.PROPOSED,
        confidence=ClaimConfidence(0.8, "human confirmation"),
        created_at=NOW,
        claim_id=cid,
    )


def _context(
    status: ContextAssemblyStatus = ContextAssemblyStatus.READY,
    claims: tuple[Claim, ...] | None = None,
) -> ReasoningContextBundle:
    query = ReasoningQuery(
        "Is the task pending?",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        as_of=NOW,
    )
    decision = (
        ScopeGuardManager()
        .observe_turn(
            query.text,
            proposed_domains=query.normalized_domains,
            now=NOW,
        )
        .decision
    )
    return ReasoningContextBundle(
        query,
        status,
        decision,
        claims if claims is not None else (_claim(),),
        (),
        (),
        NOW,
    )


def _analysis(*, review: bool = False) -> ConflictAnalysis:
    if review:
        from core.governed_reasoning import (
            Conflict,
            ConflictSeverity,
            ConflictType,
            ResolutionDecision,
            ResolutionStatus,
        )

        conflict = Conflict(
            ConflictType.VALUE_MISMATCH,
            ("a", "b"),
            "task",
            "status",
            ConflictSeverity.HIGH,
            "incompatible values",
        )
        resolution = ResolutionDecision(
            conflict.conflict_id,
            ResolutionStatus.REVIEW_REQUIRED,
            None,
            "human review required",
        )
        return ConflictAnalysis(
            (conflict,),
            (resolution,),
            ConfidenceAssessment(0.4, (), "conflict limited confidence"),
            NOW,
        )
    return ConflictAnalysis(
        (), (), ConfidenceAssessment(0.8, (), "consistent inputs"), NOW
    )


def _inference(applied: bool = True) -> InferenceRun:
    output = Claim(
        "task",
        "is_pending",
        "true",
        ClaimType.RULE_RESULT,
        ClaimOrigin.RULE,
        ClaimStatus.PROPOSED,
        confidence=ClaimConfidence(0.7, "rule confidence"),
        rule_reference="task.pending@1.0.0",
        created_at=NOW,
        claim_id="derived-a",
    )
    result = InferenceResult(
        "task.pending",
        "1.0.0",
        InferenceStatus.APPLIED if applied else InferenceStatus.NOT_APPLICABLE,
        "evaluated",
        ("claim-a",),
        output if applied else None,
        NOW,
    )
    return InferenceRun(_context().context_id, (result,), NOW)


def test_link_validation() -> None:
    with pytest.raises(ValueError):
        DecisionEvidenceLink("", "a" * 64)
    with pytest.raises(ValueError):
        DecisionEvidenceLink("e", "bad")
    with pytest.raises(ValueError):
        DecisionClaimLink("c", 0)
    with pytest.raises(ValueError):
        DecisionRuleLink("r", "")


def test_review_event_requires_final_status_and_aware_time() -> None:
    with pytest.raises(ValueError):
        ReviewEvent("human", ReviewStatus.PENDING, "later", NOW)
    with pytest.raises(ValueError):
        ReviewEvent("human", ReviewStatus.APPROVED, "ok", datetime(2026, 1, 1))


def test_record_is_immutable() -> None:
    record = _manager().record(
        _context(), _analysis(), conclusion="yes", created_at=NOW
    )
    with pytest.raises(FrozenInstanceError):
        record.conclusion = "no"  # type: ignore[misc]


def test_record_requires_valid_confidence() -> None:
    with pytest.raises(ValueError):
        _direct_record(confidence_score=2)


def test_blocked_status_requires_blocked_outcome() -> None:
    with pytest.raises(ValueError):
        _direct_record(status=DecisionStatus.BLOCKED)


def test_review_required_requires_pending_review() -> None:
    with pytest.raises(ValueError):
        _direct_record(
            status=DecisionStatus.REVIEW_REQUIRED,
            outcome=DecisionOutcome.HUMAN_REVIEW,
        )


def test_manager_records_completed_decision() -> None:
    record = _manager().record(
        _context(), _analysis(), conclusion="The task is pending.", created_at=NOW
    )
    assert record.normalized_status is DecisionStatus.COMPLETED
    assert record.normalized_outcome is DecisionOutcome.CONCLUSION
    assert record.claim_links == (DecisionClaimLink("claim-a", 1),)
    assert len(record.decision_id) == 64


def test_manager_records_blocked_context() -> None:
    record = _manager().record(
        _context(ContextAssemblyStatus.BLOCKED, ()),
        _analysis(),
        conclusion="The query is outside scope.",
        created_at=NOW,
    )
    assert record.normalized_status is DecisionStatus.BLOCKED
    assert record.normalized_outcome is DecisionOutcome.BLOCKED


def test_manager_records_insufficient_context_as_abstention() -> None:
    record = _manager().record(
        _context(ContextAssemblyStatus.INSUFFICIENT, ()),
        _analysis(),
        conclusion="There is not enough evidence.",
        created_at=NOW,
    )
    assert record.normalized_status is DecisionStatus.INCONCLUSIVE
    assert record.normalized_outcome is DecisionOutcome.ABSTENTION


def test_conflict_review_creates_pending_record() -> None:
    record = _manager().record(
        _context(),
        _analysis(review=True),
        conclusion="Review required.",
        created_at=NOW,
    )
    assert record.normalized_status is DecisionStatus.REVIEW_REQUIRED
    assert record.requires_human_review


def test_non_applied_inference_is_inconclusive() -> None:
    record = _manager().record(
        _context(),
        _analysis(),
        conclusion="No rule applied.",
        inference_run=_inference(False),
        created_at=NOW,
    )
    assert record.normalized_status is DecisionStatus.INCONCLUSIVE


def test_applied_inference_records_rule_and_derived_claim() -> None:
    record = _manager().record(
        _context(),
        _analysis(),
        conclusion="The task is pending.",
        inference_run=_inference(),
        created_at=NOW,
    )
    assert DecisionRuleLink("task.pending", "1.0.0") in record.rule_links
    assert {item.claim_id for item in record.claim_links} == {"claim-a", "derived-a"}


def test_record_preserves_limitations_and_assumptions() -> None:
    record = _manager().record(
        _context(),
        _analysis(),
        conclusion="yes",
        limitations=("source is old",),
        assumptions=("same owner",),
        created_at=NOW,
    )
    assert record.limitations == ("source is old",)
    assert record.assumptions == ("same owner",)


def test_repository_rejects_duplicate_record() -> None:
    repository = InMemoryDecisionRecordRepository()
    manager = DecisionRecordManager(repository)
    record = manager.record(_context(), _analysis(), conclusion="yes", created_at=NOW)
    with pytest.raises(ValueError):
        repository.add(record)


def test_repository_lists_deterministically() -> None:
    repository = InMemoryDecisionRecordRepository()
    repository.add(_direct_record(created_at=NOW, query_id="q1"))
    later = datetime(2026, 7, 10, 13, 0, tzinfo=timezone.utc)
    repository.add(_direct_record(created_at=later, query_id="q2"))
    assert [item.query_id for item in repository.list_all()] == ["q1", "q2"]


def test_review_approval_creates_new_record_without_mutating_original() -> None:
    manager = _manager()
    original = manager.record(
        _context(), _analysis(review=True), conclusion="review", created_at=NOW
    )
    later = datetime(2026, 7, 11, tzinfo=timezone.utc)
    revised = manager.review(
        original.decision_id,
        reviewer="Carlos",
        approved=True,
        comment="verified",
        reviewed_at=later,
    )
    assert original.requires_human_review
    assert revised.normalized_status is DecisionStatus.COMPLETED
    assert revised.normalized_review_status is ReviewStatus.APPROVED
    assert revised.supersedes == original.decision_id
    assert revised.decision_id != original.decision_id


def test_review_rejection_creates_rejected_abstention() -> None:
    manager = _manager()
    original = manager.record(
        _context(), _analysis(review=True), conclusion="review", created_at=NOW
    )
    revised = manager.review(
        original.decision_id,
        reviewer="Carlos",
        approved=False,
        comment="not verified",
        reviewed_at=datetime(2026, 7, 11, tzinfo=timezone.utc),
    )
    assert revised.normalized_status is DecisionStatus.REJECTED
    assert revised.normalized_outcome is DecisionOutcome.ABSTENTION


def test_cannot_review_non_pending_decision() -> None:
    manager = _manager()
    record = manager.record(_context(), _analysis(), conclusion="yes", created_at=NOW)
    with pytest.raises(ValueError):
        manager.review(
            record.decision_id,
            reviewer="Carlos",
            approved=True,
            comment="ok",
            reviewed_at=NOW,
        )


def test_unknown_review_target_raises_key_error() -> None:
    with pytest.raises(KeyError):
        _manager().review(
            "missing", reviewer="Carlos", approved=True, comment="ok", reviewed_at=NOW
        )


def test_record_id_is_stable_for_same_payload() -> None:
    first = _direct_record()
    second = _direct_record()
    assert first.decision_id == second.decision_id


def test_to_dict_exposes_public_audit_fields() -> None:
    record = _manager().record(
        _context(), _analysis(), conclusion="yes", created_at=NOW
    )
    payload = record.to_dict()
    assert payload["id"] == record.decision_id
    assert payload["status"] == "completed"
    assert payload["claims"] == [{"id": "claim-a", "revision": 1}]


def test_naive_decision_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError):
        _manager().record(
            _context(), _analysis(), conclusion="yes", created_at=datetime(2026, 1, 1)
        )


def test_exports_are_available() -> None:
    from core.governed_reasoning import DecisionRecordRepository

    assert DecisionRecordRepository is not None


def _manager() -> DecisionRecordManager:
    return DecisionRecordManager(InMemoryDecisionRecordRepository())


def _direct_record(**overrides) -> DecisionRecord:
    values = {
        "query_id": "query-a",
        "query_text": "question",
        "context_id": "context-a",
        "scope_status": "in_scope",
        "status": DecisionStatus.COMPLETED,
        "outcome": DecisionOutcome.CONCLUSION,
        "conclusion": "answer",
        "confidence_score": 0.8,
        "confidence_rationale": "consistent inputs",
        "created_at": NOW,
    }
    values.update(overrides)
    return DecisionRecord(**values)
