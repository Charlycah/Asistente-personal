from __future__ import annotations

from datetime import datetime, timezone

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)
from core.governed_reasoning.hierarchical_concept_composition import (
    GovernedHierarchicalConceptComposer,
    HierarchicalConceptCompositionStatus,
)
from core.governed_reasoning.productive_abstraction_admission import (
    CanonicalProductiveAbstractionEpisode,
)
from core.governed_reasoning.relational_abstraction import (
    GovernedRelationalAbstractionCandidate,
    RelationalAbstractionStatus,
)


def _abstraction_episode(
    episode_id: str,
    relation: str,
    outcome: str,
) -> CanonicalProductiveAbstractionEpisode:
    fingerprint = f"fp:{episode_id}"
    candidate = GovernedRelationalAbstractionCandidate(
        status=RelationalAbstractionStatus.REVIEW_REQUIRED,
        scope_reference="scope:hcc-green5",
        invariant_relation=relation,
        invariant_outcome=outcome,
        supporting_example_ids=(
            f"{episode_id}:support:1",
            f"{episode_id}:support:2",
        ),
        counterexample_ids=(),
        confidence=1.0,
        rationale_codes=("abstraction:shared_relational_invariant",),
        source_fingerprint=fingerprint,
    )
    return CanonicalProductiveAbstractionEpisode(
        episode_id=episode_id,
        session_id="session:hcc-green5",
        turn_id=f"turn:{episode_id}",
        scope_reference="scope:hcc-green5",
        admitted_evidence_fingerprints=(
            f"{episode_id}:evidence:1",
            f"{episode_id}:evidence:2",
        ),
        abstraction_candidate=candidate,
        source_fingerprint=f"episode:{fingerprint}",
    )


def _candidate():
    return GovernedHierarchicalConceptComposer().compose(
        episodes=(
            _abstraction_episode(
                "abstraction:a",
                "required_for",
                "blocked_when_unavailable",
            ),
            _abstraction_episode(
                "abstraction:b",
                "depends_on",
                "degraded_when_missing",
            ),
        ),
        scope_reference="scope:hcc-green5",
    )


def test_green_5_binds_canonical_productive_concept_episode() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    candidate = _candidate()
    episode = gateway.bind_productive_concept_candidate(
        owner="Carlos",
        session_id="session:hcc-green5",
        turn_id="turn:concept",
        candidate=candidate,
    )
    assert episode is not None
    assert episode.concept_candidate is candidate
    assert episode.source_abstraction_episode_ids == (
        "abstraction:a",
        "abstraction:b",
    )
    assert episode.canonical_authority == "governed_reasoning"
    assert episode.read_only is True
    assert episode.persists is False
    assert episode.creates_memory is False
    assert episode.creates_learning is False
    assert episode.executes_transfer is False


def test_green_5_binding_is_idempotent_for_same_turn_and_candidate() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    candidate = _candidate()
    first = gateway.bind_productive_concept_candidate(
        owner="Carlos",
        session_id="session:hcc-green5",
        turn_id="turn:concept",
        candidate=candidate,
    )
    second = gateway.bind_productive_concept_candidate(
        owner="Carlos",
        session_id="session:hcc-green5",
        turn_id="turn:concept",
        candidate=candidate,
    )
    assert first == second


def test_green_5_fail_closed_candidate_is_not_bound() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    candidate = GovernedHierarchicalConceptComposer().compose(
        episodes=(
            _abstraction_episode(
                "abstraction:a",
                "required_for",
                "blocked_when_unavailable",
            ),
        ),
        scope_reference="scope:hcc-green5",
    )
    assert (
        candidate.status
        is HierarchicalConceptCompositionStatus.INSUFFICIENT_COMPONENTS
    )
    assert gateway.bind_productive_concept_candidate(
        owner="Carlos",
        session_id="session:hcc-green5",
        turn_id="turn:insufficient",
        candidate=candidate,
    ) is None


def test_green_5_source_exposes_concept_references_and_context() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    now = datetime(2026, 8, 27, 18, 0, tzinfo=timezone.utc)
    text = "consulta conceptual"
    identity = build_governed_conversation_turn_identity(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="session:hcc-green5",
            text=text,
        ),
        now,
    )
    episode = gateway.bind_productive_concept_candidate(
        owner="Carlos",
        session_id="session:hcc-green5",
        turn_id=identity.turn_id,
        candidate=_candidate(),
    )
    assert episode is not None

    refs = source.reference_ids(
        owner="Carlos",
        session_id="session:hcc-green5",
        text=text,
        now=now,
    )
    lines = source.concept_context_lines(
        owner="Carlos",
        session_id="session:hcc-green5",
        text=text,
        now=now,
    )
    assert episode.episode_id in refs
    assert episode.concept_candidate.concept_id in refs
    assert "Concepto jerárquico gobernado disponible" in lines[0]
    assert "no establece verdad" in lines[1]


def test_green_5_context_is_exact_turn_scoped() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    gateway.bind_productive_concept_candidate(
        owner="Carlos",
        session_id="session:hcc-green5",
        turn_id="turn:other",
        candidate=_candidate(),
    )
    lines = source.concept_context_lines(
        owner="Carlos",
        session_id="session:hcc-green5",
        text="different turn",
        now=datetime(2026, 8, 27, 18, 1, tzinfo=timezone.utc),
    )
    assert lines == ()


def test_green_5_no_automatic_transfer_or_persistence_path_is_added() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    episode = gateway.bind_productive_concept_candidate(
        owner="Carlos",
        session_id="session:hcc-green5",
        turn_id="turn:concept",
        candidate=_candidate(),
    )
    assert episode is not None
    assert episode.modifies_world_model is False
    assert episode.modifies_personal_knowledge is False
    assert episode.executes_transfer is False
    assert episode.registers_rule is False
    assert episode.executes_actions is False
    assert episode.grants_authority is False
