from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.governed_level2b_productive_entry import (
    GovernedLevel2BProductiveEntryFoundationV1,
    GovernedLevel2BProductiveEntryResult,
    GovernedLevel2BProductiveEntryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationEpisodeTransition,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


def _requirement() -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-r1",
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("discriminating observation",),
        evidence_codes=("comparison:indistinguishable",),
    )


def test_valid_r1_starts_existing_episode_once_and_is_planning_eligible() -> None:
    result = GovernedLevel2BProductiveEntryFoundationV1().admit(
        _requirement(),
        originating_reasoning_id="reasoning-decision-1",
    )

    assert result.status is GovernedLevel2BProductiveEntryStatus.ADMITTED
    assert result.episode_start_invocation_count == 1
    assert result.episode_state is not None
    assert result.eligible_for_existing_planning
    assert result.episode_state.status is GovernedInvestigationEpisodeStatus.OPEN


def test_admission_preserves_exact_r1_reasoning_source_and_snapshot_lineage() -> None:
    requirement = _requirement()
    result = GovernedLevel2BProductiveEntryFoundationV1().admit(
        requirement,
        originating_reasoning_id="reasoning-decision-1",
    )

    assert result.source_requirement is requirement
    assert result.requirement_id == requirement.requirement_id
    assert result.originating_reasoning_id == "reasoning-decision-1"
    assert result.source_reference == requirement.source_reference
    assert result.world_snapshot_id == requirement.world_snapshot_id
    assert result.episode_state is not None
    assert result.episode_state.requirement_ids == (requirement.requirement_id,)


def test_admitted_episode_has_fixed_clean_budget_and_no_execution_authority() -> None:
    result = GovernedLevel2BProductiveEntryFoundationV1().admit(
        _requirement(),
        originating_reasoning_id="reasoning-decision-1",
    )
    state = result.episode_state

    assert state is not None
    assert state.max_acquisitions == 2
    assert state.consumed_acquisitions == 0
    assert state.remaining_acquisitions == 2
    assert not state.planning_execution_authorized


def test_same_admission_lineage_is_idempotent_and_does_not_restart_episode() -> None:
    entry = GovernedLevel2BProductiveEntryFoundationV1()
    requirement = _requirement()

    first = entry.admit(
        requirement,
        originating_reasoning_id="reasoning-decision-1",
    )
    second = entry.admit(
        requirement,
        originating_reasoning_id="reasoning-decision-1",
    )

    assert first.status is GovernedLevel2BProductiveEntryStatus.ADMITTED
    assert second.status is GovernedLevel2BProductiveEntryStatus.ALREADY_ADMITTED
    assert second.episode_id == first.episode_id
    assert second.episode_start_invocation_count == 0
    assert not second.eligible_for_existing_planning


def test_missing_reasoning_lineage_is_not_eligible_before_episode_start() -> None:
    result = GovernedLevel2BProductiveEntryFoundationV1().admit(
        _requirement(),
        originating_reasoning_id=" ",
    )

    assert result.status is GovernedLevel2BProductiveEntryStatus.NOT_ELIGIBLE
    assert result.episode_start_invocation_count == 0
    assert result.episode_state is None
    assert not result.eligible_for_existing_planning


def test_tampered_non_read_only_requirement_is_not_eligible() -> None:
    requirement = _requirement()
    object.__setattr__(requirement, "read_only", False)

    result = GovernedLevel2BProductiveEntryFoundationV1().admit(
        requirement,
        originating_reasoning_id="reasoning-decision-1",
    )

    assert result.status is GovernedLevel2BProductiveEntryStatus.NOT_ELIGIBLE
    assert result.episode_start_invocation_count == 0


def test_episode_start_failure_enters_review_without_retry() -> None:
    class FailingBoundary:
        calls = 0

        def start(self, **kwargs):
            self.calls += 1
            raise RuntimeError("synthetic episode start failure")

    boundary = FailingBoundary()
    result = GovernedLevel2BProductiveEntryFoundationV1(
        episode_boundary=boundary,
    ).admit(
        _requirement(),
        originating_reasoning_id="reasoning-decision-1",
    )

    assert boundary.calls == 1
    assert result.status is GovernedLevel2BProductiveEntryStatus.REVIEW_REQUIRED
    assert result.episode_start_invocation_count == 1
    assert not result.permits_retry


def test_noncanonical_episode_start_contract_is_rejected() -> None:
    class BadBoundary:
        def start(self, **kwargs):
            state = GovernedInvestigationEpisodeState(
                episode_id="investigation-episode-1234567890abcdef12345678",
                originating_reasoning_id=kwargs["originating_reasoning_id"],
                source_reference=kwargs["source_reference"],
                world_snapshot_id=kwargs["world_snapshot_id"],
                requirement_ids=(kwargs["initial_requirement_id"],),
            )
            object.__setattr__(state, "consumed_acquisitions", 1)
            return GovernedInvestigationEpisodeTransition(
                decision=GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
                state=state,
                rationale_codes=("investigation:synthetic-bad-start",),
            )

    result = GovernedLevel2BProductiveEntryFoundationV1(
        episode_boundary=BadBoundary(),
    ).admit(
        _requirement(),
        originating_reasoning_id="reasoning-decision-1",
    )

    assert result.status is GovernedLevel2BProductiveEntryStatus.REVIEW_REQUIRED
    assert result.episode_state is None
    assert not result.eligible_for_existing_planning


def test_contract_defaults_forbid_downstream_authority_and_side_effects() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedLevel2BProductiveEntryResult)
    }
    for name in (
        "planning_execution_authorized",
        "invokes_planning",
        "invokes_authorization",
        "invokes_execution",
        "invokes_reasoning",
        "invokes_curiosity",
        "creates_questions",
        "modifies_memory",
        "modifies_world_model",
        "permits_retry",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_entry_adapter_has_no_planning_execution_reasoning_or_loop_calls() -> None:
    source = inspect.getsource(GovernedLevel2BProductiveEntryFoundationV1)
    tree = ast.parse(source)

    for forbidden in (
        "GovernedEvidenceAcquisitionProductiveConsumptionV1",
        "GovernedIndependenceAuthorizationBoundaryV1",
        "GovernedLevel2ReadOnlyExecutionGatewayV1",
        "OfficialGovernedReasoningRuntimeGateway",
        "GovernedEpistemicCuriosity",
        "OfficialMemoryGateway",
        "OfficialConversationGateway",
        "subprocess",
        "requests.",
        "socket.",
    ):
        assert forbidden not in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {
                "plan",
                "authorize",
                "execute",
                "reason",
                "retry",
                "run",
                "run_episode",
                "run_next_step",
            }
        )
        for node in ast.walk(tree)
    )
