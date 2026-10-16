from __future__ import annotations

import ast
from pathlib import Path

from app.approved_learning_memory_materialization import (
    ApprovedLearningScope,
    StructuralEligibilityEvidence,
)
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
from core.governed_reasoning.contextual_rule_grounding_compilation import (
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    GovernedBoundedSemanticRoleRelationGrounder,
)
from core.learning_foundation import LearningObservation

ROOT = Path(__file__).resolve().parents[2]

_STRUCTURAL_RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
_NON_STRUCTURAL_FACT = "la lectura gobernada fue 42.0"


def _candidate(suffix: str, *, value: str, confidence: float):
    observation = LearningObservation(
        observation_id=f"intel-g8-corrective-observation-{suffix}",
        statement=value,
        source="governed_investigation_evidence",
        source_reference=f"level2-read-only-execution-intel-g8-corrective-{suffix}",
        confidence=confidence,
    )
    return LearningFoundation().structure_candidate(
        subject="conocimiento estructural gobernado",
        proposed_value=value,
        observations=(observation,),
        confidence=confidence,
    )


def _approved_pair(value: str):
    evaluation = GovernedLearningCandidateM369EvaluationV1().evaluate(
        _candidate("a", value=value, confidence=0.90),
        corroborating_candidates=(
            _candidate("b", value=value, confidence=0.80),
        ),
        age_days=0,
    )
    assert (
        evaluation.status
        is GovernedLearningCandidateM369EvaluationStatus.REVIEW_REQUIRED
    )
    assert evaluation.policy_candidate is not None

    approval_foundation = GovernedG6ExplicitHumanLearningApprovalV1()
    response = GovernedExplicitHumanLearningApprovalResponse(
        approval_request_id="intel-g8-corrective-human-approval-request-1",
        source_evaluation_fingerprint=(
            approval_foundation.source_evaluation_fingerprint(evaluation)
        ),
        learning_candidate_id=evaluation.source_candidate.candidate_id,
        policy_candidate_id=evaluation.policy_candidate.candidate_id,
        human_response_reference="conversation:intel-g8-corrective-approval",
        response_text="Sí",
        approver="Carlos",
        scope=ApprovedLearningScope.GENERAL,
        exact_linkage=True,
    )
    result = approval_foundation.evaluate(evaluation, response)
    assert result.approved_evidence is not None
    return evaluation, result.approved_evidence


class _SpyInterpreter:
    def __init__(self) -> None:
        self.delegate = GovernedContextualRuleInterpretationProducer()
        self.calls: list[tuple[str, str, str]] = []

    def produce(self, text: str, *, source_reference: str, scope_reference: str):
        self.calls.append((text, source_reference, scope_reference))
        return self.delegate.produce(
            text,
            source_reference=source_reference,
            scope_reference=scope_reference,
        )


class _SpyGrounder:
    def __init__(self) -> None:
        self.delegate = GovernedBoundedSemanticRoleRelationGrounder()
        self.calls: list[tuple[object, str]] = []

    def ground(self, candidate, *, scope_reference: str):
        self.calls.append((candidate, scope_reference))
        return self.delegate.ground(candidate, scope_reference=scope_reference)


class _SpyCompiler:
    def __init__(self) -> None:
        self.delegate = GovernedContextualRuleGroundingCompiler()
        self.calls: list[tuple[object, object, str]] = []

    def compile(
        self,
        *,
        rule_candidate,
        semantic_grounding,
        scope_reference: str,
    ):
        self.calls.append((rule_candidate, semantic_grounding, scope_reference))
        return self.delegate.compile(
            rule_candidate=rule_candidate,
            semantic_grounding=semantic_grounding,
            scope_reference=scope_reference,
        )


def test_g8_structural_evidence_uses_existing_governed_reasoning_fingerprints() -> None:
    evaluation, approval = _approved_pair(_STRUCTURAL_RULE)
    foundation = GovernedG7ApprovedLearningMemoryMaterializationV1()

    structural = foundation.build_structural_eligibility(evaluation, approval)

    assert isinstance(structural, StructuralEligibilityEvidence)
    interpreter = GovernedContextualRuleInterpretationProducer()
    candidate = interpreter.produce(
        _STRUCTURAL_RULE,
        source_reference=approval.source_evaluation_fingerprint,
        scope_reference=approval.scope.value,
    )
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=approval.scope.value,
    )
    compilation = GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=approval.scope.value,
    )
    assert structural.interpretation_fingerprint == candidate.source_fingerprint
    assert structural.grounding_fingerprint == grounding.source_fingerprint
    assert structural.compilation_fingerprint == compilation.source_fingerprint


def test_g8_invokes_each_existing_structural_reasoning_producer_exactly_once() -> None:
    evaluation, approval = _approved_pair(_STRUCTURAL_RULE)
    foundation = GovernedG7ApprovedLearningMemoryMaterializationV1()
    interpreter = _SpyInterpreter()
    grounder = _SpyGrounder()
    compiler = _SpyCompiler()
    foundation._interpreter = interpreter
    foundation._grounder = grounder
    foundation._compiler = compiler

    structural = foundation.build_structural_eligibility(evaluation, approval)

    assert structural is not None
    assert interpreter.calls == [
        (
            _STRUCTURAL_RULE,
            approval.source_evaluation_fingerprint,
            approval.scope.value,
        )
    ]
    assert len(grounder.calls) == 1
    assert len(compiler.calls) == 1


def test_g8_non_structural_fact_fails_closed_without_fabricated_eligibility() -> None:
    evaluation, approval = _approved_pair(_NON_STRUCTURAL_FACT)

    foundation = GovernedG7ApprovedLearningMemoryMaterializationV1()
    structural = foundation.build_structural_eligibility(
        evaluation,
        approval,
    )

    assert structural is None


def test_g8_non_candidate_stops_before_grounding_and_compilation() -> None:
    evaluation, approval = _approved_pair(_NON_STRUCTURAL_FACT)
    foundation = GovernedG7ApprovedLearningMemoryMaterializationV1()
    interpreter = _SpyInterpreter()
    grounder = _SpyGrounder()
    compiler = _SpyCompiler()
    foundation._interpreter = interpreter
    foundation._grounder = grounder
    foundation._compiler = compiler

    structural = foundation.build_structural_eligibility(evaluation, approval)

    assert structural is None
    assert len(interpreter.calls) == 1
    assert grounder.calls == []
    assert compiler.calls == []


def test_g8_source_contains_no_parallel_structural_fingerprint_fabrication() -> None:
    source_path = ROOT / "app/governed_g7_approved_learning_memory_materialization.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert {"produce", "ground", "compile"}.issubset(calls)
    assert '("governed_reasoning", "interpretation", content)' not in source
    assert '("governed_reasoning", "grounding", content, scope_reference)' not in source
