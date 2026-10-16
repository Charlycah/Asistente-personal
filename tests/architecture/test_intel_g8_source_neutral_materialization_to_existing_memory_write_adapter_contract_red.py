from __future__ import annotations

import ast
from pathlib import Path

from app.approved_learning_memory_materialization import (
    ApprovedLearningScope,
    GovernedMemoryMaterializationProposal,
)
from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.curiosity_m369_learning_evaluation import CuriosityLearningKind
from app.governed_g6_explicit_human_learning_approval import (
    GovernedExplicitHumanLearningApprovalResponse,
    GovernedG6ExplicitHumanLearningApprovalV1,
)
from app.governed_g7_approved_learning_memory_materialization import (
    GovernedG7ApprovedLearningMemoryMaterializationV1,
)
from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationStatus,
    GovernedLearningCandidateM369EvaluationV1,
)
from app.learning_foundation import LearningFoundation
from core.cognitive_memory import LearningCategory
from core.learning_foundation import LearningObservation
from core.memory_consolidation_foundation import (
    ConsolidationAssessment,
    ConsolidationDisposition,
    ConsolidationReason,
    ConsolidationTarget,
)

ROOT = Path(__file__).resolve().parents[2]

_STRUCTURAL_RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


def _candidate(suffix: str, *, confidence: float):
    observation = LearningObservation(
        observation_id=f"intel-g8-write-adapter-observation-{suffix}",
        statement=_STRUCTURAL_RULE,
        source="governed_investigation_evidence",
        source_reference=f"intel-g8-write-adapter-{suffix}",
        confidence=confidence,
    )
    return LearningFoundation().structure_candidate(
        subject="conocimiento estructural gobernado",
        proposed_value=_STRUCTURAL_RULE,
        observations=(observation,),
        confidence=confidence,
    )


def _g8_proposal() -> GovernedMemoryMaterializationProposal:
    evaluation = GovernedLearningCandidateM369EvaluationV1().evaluate(
        _candidate("a", confidence=0.90),
        corroborating_candidates=(_candidate("b", confidence=0.80),),
        age_days=0,
    )
    assert (
        evaluation.status
        is GovernedLearningCandidateM369EvaluationStatus.REVIEW_REQUIRED
    )
    assert evaluation.policy_candidate is not None

    approval_foundation = GovernedG6ExplicitHumanLearningApprovalV1()
    response = GovernedExplicitHumanLearningApprovalResponse(
        approval_request_id="intel-g8-write-adapter-human-approval-request-1",
        source_evaluation_fingerprint=(
            approval_foundation.source_evaluation_fingerprint(evaluation)
        ),
        learning_candidate_id=evaluation.source_candidate.candidate_id,
        policy_candidate_id=evaluation.policy_candidate.candidate_id,
        human_response_reference="conversation:intel-g8-write-adapter-approval",
        response_text="Sí",
        approver="Carlos",
        scope=ApprovedLearningScope.GENERAL,
        exact_linkage=True,
    )
    approval_result = approval_foundation.evaluate(evaluation, response)
    assert approval_result.approved_evidence is not None
    approval = approval_result.approved_evidence

    materialization = GovernedG7ApprovedLearningMemoryMaterializationV1()
    structural = materialization.build_structural_eligibility(
        evaluation,
        approval,
    )
    assert structural is not None
    report = materialization.propose(
        evaluation,
        approval,
        structural_eligibility=structural,
    )
    assert report.proposal is not None
    return report.proposal


def _historical_preference_proposal() -> GovernedMemoryMaterializationProposal:
    return GovernedMemoryMaterializationProposal(
        proposal_id="approved-learning-memory-proposal-historical1",
        learning_candidate_id="learning-candidate-historical-1",
        preference_candidate_id="preference-candidate-historical-1",
        subject="Carlos",
        value="ejecutar Ruff antes de pytest",
        approval_id="approval-historical-1",
        approver="Carlos",
        approval_scope=ApprovedLearningScope.PROJECT,
        human_response_reference="conversation:historical-approval",
        m369_evaluation_fingerprint="a" * 64,
        human_approval_fingerprint="b" * 64,
        confidence=0.82,
        evidence_ids=("evidence-historical-1",),
        consolidation=ConsolidationAssessment(
            candidate_id="approved-learning-preference-historical-1",
            disposition=ConsolidationDisposition.PROPOSE_LONG_TERM,
            proposed_target=ConsolidationTarget.LONG_TERM,
            reasons=(ConsolidationReason.EXPLICIT_USER_INTENT,),
            requires_human_confirmation=False,
        ),
        source_fingerprint="c" * 64,
        learning_kind=CuriosityLearningKind.PREFERENCE,
    )


def test_g8_source_neutral_proposal_uses_existing_write_adapter() -> None:
    proposal = _g8_proposal()

    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)

    assert request.materialization_proposal_id == proposal.proposal_id
    assert request.memory_item.content == proposal.value


def test_g8_source_neutral_metadata_preserves_policy_without_fake_preference() -> None:
    proposal = _g8_proposal()

    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)
    metadata = request.memory_item.metadata

    assert metadata["policy_candidate_id"] == proposal.policy_candidate_id
    assert "preference_candidate_id" not in metadata
    assert "learning_kind" not in metadata
    assert metadata["learning_category"] == "stable_knowledge"


def test_g8_source_neutral_write_request_remains_inert_stable_knowledge() -> None:
    proposal = _g8_proposal()

    request = GovernedMemoryWriteAdapterFoundation().adapt(proposal)

    assert request.learning_category is LearningCategory.STABLE_KNOWLEDGE
    assert request.structural_evidence_fingerprint
    assert request.writer_authority == "memory_gateway"
    assert request.writer_component == "OfficialMemoryGateway"
    assert request.writer_method == "remember_governed_learning"
    assert request.read_only is True
    assert request.write_performed is False
    assert request.persists_results is False
    assert request.creates_memory is False


def test_existing_adapter_preserves_historical_and_source_neutral_lineage() -> None:
    adapter = GovernedMemoryWriteAdapterFoundation()
    historical = _historical_preference_proposal()

    historical_request = adapter.adapt(historical)
    historical_metadata = historical_request.memory_item.metadata
    assert historical_metadata["preference_candidate_id"] == (
        historical.preference_candidate_id
    )
    assert historical_metadata["learning_kind"] == "preference"

    source_neutral = _g8_proposal()
    source_neutral_request = adapter.adapt(source_neutral)
    source_neutral_metadata = source_neutral_request.memory_item.metadata
    assert source_neutral_metadata["policy_candidate_id"] == (
        source_neutral.policy_candidate_id
    )
    assert "preference_candidate_id" not in source_neutral_metadata
    assert "learning_kind" not in source_neutral_metadata


def test_existing_adapter_source_has_no_fake_source_neutral_provenance_or_writer(
) -> None:
    source_path = ROOT / "app" / "approved_learning_memory_write_adapter.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "proposal.policy_candidate_id" in source
    assert '"learning_kind": proposal.learning_kind.value,' not in source
    assert (
        '"preference_candidate_id": proposal.preference_candidate_id,'
        not in source
    )
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "app.memory_consolidation" not in imports
    assert "OfficialMemoryGateway(" not in source
    assert ".remember_governed_learning(" not in source
    assert "class SourceNeutralMemoryWriter" not in source
    assert "class G8MemoryWriteAdapter" not in source
