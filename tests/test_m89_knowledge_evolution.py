from datetime import datetime, timezone

import pytest

from core.adaptive_cognition import (
    AdaptiveReflectionEngine,
    KnowledgeEvolutionAction,
    KnowledgeEvolutionDecision,
    KnowledgeEvolutionEngine,
    KnowledgeEvolutionManager,
    KnowledgeEvolutionPolicy,
    KnowledgeEvolutionProposal,
    KnowledgeEvolutionRisk,
    KnowledgeEvolutionStatus,
    MetaReasoningAssessment,
    MetaReasoningDimension,
    MetaReasoningFinding,
    MetaReasoningFindingSeverity,
    MetaReasoningJudgement,
)

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def reflection():
    assessment = MetaReasoningAssessment(
        reasoning_result_id="result-1",
        judgement=MetaReasoningJudgement.ACCEPTABLE,
        score=0.8,
        summary="Assessment summary.",
        findings=(
            MetaReasoningFinding(
                MetaReasoningDimension.EVIDENCE_SUFFICIENCY,
                "Evidence is sufficient.",
                MetaReasoningFindingSeverity.INFO,
                0.8,
            ),
        ),
        created_at=NOW,
    )
    return AdaptiveReflectionEngine().reflect((assessment,), now=NOW)


def proposal(**changes):
    values = {
        "action": KnowledgeEvolutionAction.CREATE,
        "title": "Stable preference",
        "content": "The user prefers concise reports.",
        "rationale": "Repeated governed observations support the proposal.",
        "reflection_ids": (reflection().record_id,),
        "confidence": 0.8,
        "risk": KnowledgeEvolutionRisk.LOW,
        "created_at": NOW,
    }
    values.update(changes)
    return KnowledgeEvolutionProposal(**values)


def test_proposal_requires_reflections() -> None:
    with pytest.raises(ValueError):
        proposal(reflection_ids=())


def test_proposal_requires_content() -> None:
    with pytest.raises(ValueError):
        proposal(content="")


def test_confidence_must_be_valid() -> None:
    with pytest.raises(ValueError):
        proposal(confidence=1.5)


def test_references_must_be_unique() -> None:
    with pytest.raises(ValueError):
        proposal(reflection_ids=("a", "a"))


def test_non_create_action_requires_target() -> None:
    with pytest.raises(ValueError):
        proposal(action=KnowledgeEvolutionAction.SUPERSEDE)


def test_identity_is_sha256() -> None:
    assert len(proposal().proposal_id) == 64


def test_low_risk_high_confidence_does_not_require_review() -> None:
    assert not proposal().requires_review


def test_medium_risk_requires_review() -> None:
    assert proposal(risk=KnowledgeEvolutionRisk.MEDIUM).requires_review


def test_proposal_is_serializable() -> None:
    payload = proposal().to_dict()
    assert payload["action"] == "create"
    assert payload["status"] == "proposed"


def test_policy_rejects_auto_approval() -> None:
    with pytest.raises(ValueError):
        KnowledgeEvolutionPolicy(auto_approve_enabled=True)


def test_engine_requires_reflection_evidence() -> None:
    with pytest.raises(ValueError):
        KnowledgeEvolutionEngine().propose_from_reflections(
            "title", "content", (), rationale="reason", now=NOW
        )


def test_low_confidence_escalates_risk() -> None:
    item = KnowledgeEvolutionEngine().propose_from_reflections(
        "title",
        "content",
        (reflection(),),
        rationale="reason",
        confidence=0.4,
        now=NOW,
    )
    assert item.normalized_risk is KnowledgeEvolutionRisk.HIGH


def test_engine_does_not_mutate_reflection() -> None:
    source = reflection()
    before = source.to_dict()
    KnowledgeEvolutionEngine().propose_from_reflections(
        "title", "content", (source,), rationale="reason", now=NOW
    )
    assert source.to_dict() == before


def test_approval_is_explicit() -> None:
    decision = KnowledgeEvolutionEngine().decide(
        proposal(), approve=True, reason="Reviewed", reviewer="carlos", now=NOW
    )
    assert decision.normalized_status is KnowledgeEvolutionStatus.APPROVED


def test_rejection_is_recorded() -> None:
    decision = KnowledgeEvolutionEngine().decide(
        proposal(), approve=False, reason="Weak evidence", reviewer="carlos", now=NOW
    )
    assert decision.normalized_status is KnowledgeEvolutionStatus.REJECTED


def test_high_risk_approval_is_blocked() -> None:
    decision = KnowledgeEvolutionEngine().decide(
        proposal(risk=KnowledgeEvolutionRisk.HIGH),
        approve=True,
        reason="Attempted approval",
        reviewer="carlos",
        now=NOW,
    )
    assert decision.normalized_status is KnowledgeEvolutionStatus.BLOCKED


def test_decision_identity_is_sha256() -> None:
    decision = KnowledgeEvolutionDecision(
        proposal_id=proposal().proposal_id,
        status=KnowledgeEvolutionStatus.APPROVED,
        reason="Reviewed",
        reviewer="carlos",
        decided_at=NOW,
    )
    assert len(decision.decision_id) == 64


def test_manager_persists_proposal() -> None:
    manager = KnowledgeEvolutionManager()
    item = manager.propose_from_reflections(
        "title", "content", (reflection(),), rationale="reason", now=NOW
    )
    assert manager.repository.get_proposal(item.proposal_id) == item


def test_manager_persists_decision() -> None:
    manager = KnowledgeEvolutionManager()
    item = manager.propose_from_reflections(
        "title", "content", (reflection(),), rationale="reason", now=NOW
    )
    decision = manager.decide(
        item, approve=False, reason="Not ready", reviewer="carlos", now=NOW
    )
    assert decision in manager.repository.list_decisions()


def test_prompt_preserves_governance_boundary() -> None:
    lines = KnowledgeEvolutionManager().system_prompt_lines()
    assert any("propuesta" in line for line in lines)
    assert any("no se convierten automáticamente" in line for line in lines)
