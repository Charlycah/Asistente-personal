from __future__ import annotations

import ast
import importlib
from pathlib import Path

from app.learning_foundation import LearningFoundation
from app.safe_learning_policies import SafeLearningPolicies
from core.learning_foundation import (
    LearningCandidate,
    LearningCandidateDisposition,
    LearningObservation,
)
from core.safe_learning_policies import SafeLearningDisposition

MODULE = "app.governed_learning_candidate_m369_evaluation"
ROOT = Path(__file__).resolve().parents[2]


def _api():
    module = importlib.import_module(MODULE)
    return (
        module.GovernedLearningCandidateM369EvaluationStatus,
        module.GovernedLearningCandidateM369EvaluationResult,
        module.GovernedLearningCandidateM369EvaluationV1,
    )


def _candidate(
    suffix: str,
    *,
    subject: str = "temperatura del entorno observado",
    value: str = "la lectura gobernada fue 42.0",
    confidence: float = 0.90,
) -> LearningCandidate:
    observation = LearningObservation(
        observation_id=f"intel-g6-investigation-observation-{suffix}",
        statement=value,
        source="governed_investigation_evidence",
        source_reference=f"level2-read-only-execution-intel-g6-{suffix}",
        confidence=confidence,
    )
    return LearningFoundation().structure_candidate(
        subject=subject,
        proposed_value=value,
        observations=(observation,),
        confidence=confidence,
    )


class _SafeLearningSpy:
    def __init__(self) -> None:
        self.calls = 0
        self.policy_candidate = None
        self._canonical = SafeLearningPolicies()

    def evaluate(self, candidate):
        self.calls += 1
        self.policy_candidate = candidate
        return self._canonical.evaluate(candidate)


def test_intel_g6_single_g5_candidate_remains_insufficient_evidence() -> None:
    status_type, result_type, evaluation_type = _api()
    candidate = _candidate("a")
    spy = _SafeLearningSpy()

    result = evaluation_type(safe_learning_policies=spy).evaluate(
        candidate,
        age_days=0,
    )

    assert isinstance(result, result_type)
    assert result.status is status_type.INSUFFICIENT_EVIDENCE
    assert result.source_candidate is candidate
    assert result.corroborating_candidates == ()
    assert result.policy_candidate is spy.policy_candidate
    assert result.safe_learning_decision is not None
    assert (
        result.safe_learning_decision.disposition
        is SafeLearningDisposition.INSUFFICIENT_EVIDENCE
    )
    assert spy.calls == 1
    assert result.policy_candidate.evidence_ids == (candidate.candidate_id,)
    assert result.read_only is True
    assert result.uses_existing_m369 is True
    assert result.accepts_learning is False
    assert result.persists_results is False
    assert result.writes_memory is False
    assert result.writes_knowledge is False


def test_intel_g6_corroborated_candidate_reaches_review_required_only() -> None:
    status_type, _, evaluation_type = _api()
    source = _candidate("a", confidence=0.90)
    corroborating = _candidate("b", confidence=0.80)
    spy = _SafeLearningSpy()

    result = evaluation_type(safe_learning_policies=spy).evaluate(
        source,
        corroborating_candidates=(corroborating,),
        age_days=0,
    )

    assert result.status is status_type.REVIEW_REQUIRED
    assert result.source_candidate is source
    assert result.corroborating_candidates == (corroborating,)
    assert spy.calls == 1
    assert result.policy_candidate.evidence_ids == (
        source.candidate_id,
        corroborating.candidate_id,
    )
    assert result.policy_candidate.confidence == 0.85
    assert result.safe_learning_decision.review_authorized is True
    assert result.safe_learning_decision.acceptance_authorized is False
    assert result.safe_learning_decision.persistence_authorized is False
    assert result.safe_learning_decision.adaptation_authorized is False
    assert result.accepts_learning is False
    assert result.persists_results is False


def test_intel_g6_semantic_disagreement_fails_before_safe_learning() -> None:
    status_type, _, evaluation_type = _api()
    source = _candidate("a")
    disagreeing = _candidate("b", value="la lectura gobernada fue 99.0")
    spy = _SafeLearningSpy()

    result = evaluation_type(safe_learning_policies=spy).evaluate(
        source,
        corroborating_candidates=(disagreeing,),
        age_days=0,
    )

    assert result.status is status_type.NOT_ELIGIBLE
    assert spy.calls == 0
    assert result.policy_candidate is None
    assert result.safe_learning_decision is None
    assert result.accepts_learning is False
    assert result.persists_results is False


def test_intel_g6_requires_canonical_review_only_learning_candidates() -> None:
    status_type, _, evaluation_type = _api()
    source = _candidate("a")
    assert source.disposition is LearningCandidateDisposition.REVIEW_REQUIRED
    assert source.accepted_as_knowledge is False
    assert source.persistence_authorized is False
    spy = _SafeLearningSpy()

    result = evaluation_type(safe_learning_policies=spy).evaluate(
        source,
        corroborating_candidates=(source,),
        age_days=0,
    )

    assert result.status is status_type.NOT_ELIGIBLE
    assert spy.calls == 0
    assert result.policy_candidate is None
    assert result.safe_learning_decision is None


def test_intel_g6_adds_no_parallel_learning_knowledge_or_memory_authority() -> None:
    _api()
    source_path = ROOT / "app/governed_learning_candidate_m369_evaluation.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_symbols = (
        "LearningManager",
        "KnowledgeManager",
        "MemoryManager",
        "OfficialMemoryGateway",
        "ApprovedLearningEvidence",
        "M369ExplicitHumanLearningApprovalEvidenceFoundation",
        "GovernedMemoryMaterializationProposal",
        "GovernedMemoryWriteRequest",
        "CuriosityM369LearningEvaluationFoundation",
        "CuriosityKnowledgeCandidate",
        "PreferenceLearning",
        "GovernedRobyInitiatedLibraryAccessV1",
        "OfficialRuntimeCapabilityRegistry",
    )
    assert not any(symbol in source for symbol in forbidden_symbols)
    assert "SafeLearningPolicies" in source
    assert all(
        not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name
            in {
                "approve",
                "persist",
                "write",
                "plan",
                "execute",
                "research",
                "learn",
                "materialize",
            }
        )
        for node in ast.walk(tree)
    )
