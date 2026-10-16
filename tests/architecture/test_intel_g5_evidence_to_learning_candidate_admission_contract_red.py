from __future__ import annotations

import ast
import importlib
from datetime import datetime, timezone
from pathlib import Path

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryResult,
    GovernedInvestigationExecutionReentryStatus,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureStatus,
    GovernedMultiStepInvestigationReasoningClosureV1,
)
from app.learning_foundation import LearningFoundation
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)
from core.learning_foundation import (
    LearningCandidateDisposition,
    LearningObservation,
)

MODULE = "app.governed_investigation_learning_candidate_admission"
ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 5, 13, 0, tzinfo=timezone.utc)
SOURCE = "conversation:intel-g5"
SNAPSHOT = "world:intel-g5:001"


def _api():
    module = importlib.import_module(MODULE)
    return (
        module.GovernedInvestigationLearningCandidateAdmissionStatus,
        module.GovernedInvestigationLearningCandidateAdmissionResult,
        module.GovernedInvestigationLearningCandidateAdmissionV1,
    )


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-intel-g5-{step:02d}-abcdef",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=f"independence-authorization-intel-g5-{step:02d}-abcdef",
        requirement_id=f"discrimination-requirement-intel-g5-r{step}",
        plan_id=f"evidence-acquisition-plan-intel-g5-{step:02d}-abcdef",
        capability_name="local.sensor",
        evidence_description=f"governed discriminating observation {step}",
        declared_evidence_output=f"intel_g5_evidence_{step}",
        observed_value=40.0 + step,
        observation_source_reference=f"local-reader:intel-g5:e{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=(f"execution:intel-g5:e{step}",),
        source_fingerprint=(str(step) * 64)[:64],
    )


def _reentry(step: int) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(step)
    return GovernedLevel2ReasoningReentryResult(
        reentry_id=f"level2-reasoning-reentry-intel-g5-{step:02d}-abcdef",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id=f"evidence-intel-g5-{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        reasoning_result=None,
        rationale_codes=(f"reentry:intel-g5:r{step}",),
        source_fingerprint=("e" * 63) + str(step),
        automatic_reevaluation_count=1,
    )


def _requirement(step: int) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=f"discrimination-requirement-intel-g5-r{step}",
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared fact",),
        missing_evidence_descriptions=(f"governed discriminating observation {step}",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _execution_step(
    step: int, *, budget: int = 2
) -> GovernedInvestigationExecutionReentryResult:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning:intel-g5:001",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id="discrimination-requirement-intel-g5-r1",
        max_acquisitions=budget,
    ).state
    for completed in range(1, step):
        state = boundary.record_acquisition(state, _envelope(completed)).state
        state = boundary.record_reentry(state, _reentry(completed)).state
        state = boundary.evaluate_continuation(state, _requirement(completed + 1)).state
    state = boundary.record_acquisition(state, _envelope(step)).state

    class _AuthorizationLineage:
        episode_id = state.episode_id
        source_reference = SOURCE
        world_snapshot_id = SNAPSHOT

    envelope = _envelope(step)
    return GovernedInvestigationExecutionReentryResult(
        episode_id=state.episode_id,
        authorization_reentry=_AuthorizationLineage(),
        status=GovernedInvestigationExecutionReentryStatus.ACQUIRED,
        evidence_envelope=envelope,
        resulting_episode_state=state,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        current_step=step,
        remaining_acquisitions=state.remaining_acquisitions,
        execution_status=GovernedLevel2ExecutionStatus.ACQUIRED,
        rationale_codes=(f"execution_reentry:intel-g5:e{step}",),
        source_fingerprint="a" * 64,
        eligible_for_reasoning_reentry=True,
        execution_invocation_count=1,
        episode_record_invocation_count=1,
    )


class _Reasoning:
    def __init__(self, step: int) -> None:
        self._step = step

    def reenter(self, envelope, *, now):
        assert now is NOW
        assert envelope.execution_id == _envelope(self._step).execution_id
        return _reentry(self._step)


def _closure(step: int, *, budget: int = 2):
    return GovernedMultiStepInvestigationReasoningClosureV1(
        _Reasoning(step)
    ).consume(_execution_step(step, budget=budget), now=NOW)


class _LearningFoundationSpy:
    def __init__(self) -> None:
        self.calls = 0
        self.subject = None
        self.proposed_value = None
        self.observations = None
        self.confidence = None
        self._canonical = LearningFoundation()

    def structure_candidate(self, *, subject, proposed_value, observations, confidence):
        self.calls += 1
        self.subject = subject
        self.proposed_value = proposed_value
        self.observations = observations
        self.confidence = confidence
        return self._canonical.structure_candidate(
            subject=subject,
            proposed_value=proposed_value,
            observations=observations,
            confidence=confidence,
        )


def test_intel_g5_terminal_investigation_evidence_enters_existing_m369_once() -> None:
    status_type, result_type, admission_type = _api()
    closure = _closure(2)
    assert closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    spy = _LearningFoundationSpy()

    result = admission_type(learning_foundation=spy).admit(
        closure,
        subject="temperatura del entorno observado",
        proposed_value="la lectura gobernada fue 42.0",
        confidence=0.90,
    )

    assert isinstance(result, result_type)
    assert result.status is status_type.ADMITTED
    assert result.source_closure is closure
    assert result.source_evidence is closure.execution_reentry.evidence_envelope
    assert isinstance(result.learning_observation, LearningObservation)
    assert result.learning_observation.source == "governed_investigation_evidence"
    assert (
        result.learning_observation.source_reference
        == result.source_evidence.execution_id
    )
    assert spy.calls == 1
    assert spy.observations == (result.learning_observation,)
    assert result.learning_candidate is not None
    assert (
        result.learning_candidate.disposition
        is LearningCandidateDisposition.REVIEW_REQUIRED
    )
    assert result.learning_candidate.accepted_as_knowledge is False
    assert result.learning_candidate.persistence_authorized is False
    assert result.read_only is True
    assert result.uses_existing_m369 is True
    assert result.establishes_truth is False
    assert result.accepts_learning is False
    assert result.persists_results is False
    assert result.writes_memory is False
    assert result.writes_knowledge is False


def test_intel_g5_non_terminal_investigation_cannot_create_learning_candidate() -> None:
    status_type, _, admission_type = _api()
    closure = _closure(2, budget=3)
    assert closure.status is GovernedInvestigationReasoningClosureStatus.RECORDED
    spy = _LearningFoundationSpy()

    result = admission_type(learning_foundation=spy).admit(
        closure,
        subject="premature subject",
        proposed_value="premature value",
        confidence=0.90,
    )

    assert result.status is status_type.NOT_ELIGIBLE
    assert spy.calls == 0
    assert result.learning_observation is None
    assert result.learning_candidate is None
    assert result.accepts_learning is False
    assert result.persists_results is False


def test_intel_g5_completion_alone_never_self_admits_learning() -> None:
    _, _, admission_type = _api()
    closure = _closure(2)
    spy = _LearningFoundationSpy()

    boundary = admission_type(learning_foundation=spy)

    assert closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    assert spy.calls == 0
    assert not hasattr(closure, "learning_candidate")
    assert not hasattr(closure, "approved_learning")
    assert boundary is not None


def test_intel_g5_requires_explicit_learning_semantics_before_m369() -> None:
    _, _, admission_type = _api()
    closure = _closure(2)
    spy = _LearningFoundationSpy()
    boundary = admission_type(learning_foundation=spy)

    for subject, value in (("", "value"), ("subject", "")):
        result = boundary.admit(
            closure,
            subject=subject,
            proposed_value=value,
            confidence=0.90,
        )
        assert result.learning_candidate is None

    assert spy.calls == 0


def test_intel_g5_adds_no_parallel_learning_knowledge_or_memory_authority() -> None:
    _api()
    source_path = ROOT / "app/governed_investigation_learning_candidate_admission.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_symbols = (
        "LearningManager",
        "KnowledgeManager",
        "MemoryManager",
        "OfficialMemoryGateway",
        "ApprovedLearningEvidence",
        "PreferenceLearning",
        "SafeLearningPolicies",
        "M369ExplicitHumanLearningApprovalEvidenceFoundation",
        "GovernedMemoryMaterializationProposal",
        "GovernedMemoryWriteRequest",
        "CuriosityM369LearningEvaluationFoundation",
        "GovernedRobyInitiatedLibraryAccessV1",
        "OfficialRuntimeCapabilityRegistry",
    )
    assert not any(symbol in source for symbol in forbidden_symbols)
    assert "LearningFoundation" in source
    assert all(
        not (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name
            in {
                "evaluate",
                "approve",
                "persist",
                "write",
                "plan",
                "execute",
                "research",
                "learn",
            }
        )
        for node in ast.walk(tree)
    )
