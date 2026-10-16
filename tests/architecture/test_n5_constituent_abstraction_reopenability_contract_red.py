"""N5 contract: reopen exact constituent abstractions without runtime mutation."""

from dataclasses import replace

from core.governed_reasoning.hierarchical_concept_composition import (
    CanonicalProductiveConceptEpisode,
    GovernedConstituentAbstractionReopener,
    GovernedHierarchicalConceptComposer,
)
from core.governed_reasoning.productive_abstraction_admission import (
    CanonicalProductiveAbstractionEpisode,
)
from core.governed_reasoning.relational_abstraction import (
    GovernedRelationalAbstractionCandidate,
    RelationalAbstractionStatus,
)


def _abstraction(
    episode_id: str,
    relation: str,
    outcome: str,
) -> CanonicalProductiveAbstractionEpisode:
    fingerprint = f"fp:{episode_id}"
    candidate = GovernedRelationalAbstractionCandidate(
        status=RelationalAbstractionStatus.REVIEW_REQUIRED,
        scope_reference="scope:n5-reopen",
        invariant_relation=relation,
        invariant_outcome=outcome,
        supporting_example_ids=(
            f"{episode_id}:support:1",
            f"{episode_id}:support:2",
        ),
        counterexample_ids=(f"{episode_id}:counter:1",),
        confidence=0.666667,
        rationale_codes=(
            "abstraction:shared_relational_invariant",
            "abstraction:counterexample_present",
        ),
        source_fingerprint=fingerprint,
    )
    return CanonicalProductiveAbstractionEpisode(
        episode_id=episode_id,
        session_id="session:n5-reopen",
        turn_id=f"turn:{episode_id}",
        scope_reference="scope:n5-reopen",
        admitted_evidence_fingerprints=(
            f"{episode_id}:evidence:1",
            f"{episode_id}:evidence:2",
        ),
        abstraction_candidate=candidate,
        source_fingerprint=f"episode:{fingerprint}",
    )


def _concept():
    episodes = (
        _abstraction("abstraction:a", "required_for", "blocked_when_absent"),
        _abstraction("abstraction:b", "supports", "degraded_when_absent"),
    )
    candidate = GovernedHierarchicalConceptComposer().compose(
        episodes=episodes,
        scope_reference="scope:n5-reopen",
    )
    concept = CanonicalProductiveConceptEpisode(
        episode_id="productive-concept:n5-reopen",
        owner="Carlos",
        session_id="session:n5-reopen",
        turn_id="turn:concept",
        scope_reference="scope:n5-reopen",
        concept_candidate=candidate,
        source_abstraction_episode_ids=candidate.constituent_episode_ids,
        source_fingerprint=candidate.source_fingerprint,
    )
    return episodes, concept


def test_n5_reopens_exact_constituent_abstraction_episodes() -> None:
    episodes, concept = _concept()

    reopened = GovernedConstituentAbstractionReopener.reopen(
        concept_episode=concept,
        available_episodes=episodes,
    )

    assert reopened == episodes
    assert tuple(item.episode_id for item in reopened) == (
        concept.source_abstraction_episode_ids
    )


def test_n5_reopening_preserves_support_counterevidence_and_fingerprints() -> None:
    episodes, concept = _concept()

    reopened = GovernedConstituentAbstractionReopener.reopen(
        concept_episode=concept,
        available_episodes=episodes,
    )

    assert tuple(item.source_fingerprint for item in reopened) == tuple(
        item.source_fingerprint for item in episodes
    )
    assert reopened[0].abstraction_candidate.supporting_example_ids
    assert reopened[0].abstraction_candidate.counterexample_ids
    assert reopened[0].admitted_evidence_fingerprints


def test_n5_reopening_fails_closed_for_missing_constituent() -> None:
    episodes, concept = _concept()

    assert GovernedConstituentAbstractionReopener.reopen(
        concept_episode=concept,
        available_episodes=episodes[:1],
    ) == ()


def test_n5_reopening_fails_closed_for_foreign_lineage() -> None:
    episodes, concept = _concept()
    foreign = replace(episodes[0], session_id="session:foreign")

    assert GovernedConstituentAbstractionReopener.reopen(
        concept_episode=concept,
        available_episodes=(foreign, episodes[1]),
    ) == ()


def test_n5_reopening_rejects_fingerprint_mismatch() -> None:
    episodes, concept = _concept()
    tampered = replace(episodes[0], source_fingerprint="episode:tampered")

    assert GovernedConstituentAbstractionReopener.reopen(
        concept_episode=concept,
        available_episodes=(tampered, episodes[1]),
    ) == ()


def test_n5_reopening_remains_read_only_and_non_operational() -> None:
    episodes, concept = _concept()

    reopened = GovernedConstituentAbstractionReopener.reopen(
        concept_episode=concept,
        available_episodes=episodes,
    )

    assert reopened
    for episode in reopened:
        assert episode.canonical_authority == "governed_reasoning"
        assert episode.read_only
        assert episode.session_local
        assert not episode.persists
        assert not episode.creates_memory
        assert not episode.creates_learning
        assert not episode.executes_transfer
        assert not episode.grants_authority
