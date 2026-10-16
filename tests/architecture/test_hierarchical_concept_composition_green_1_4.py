from __future__ import annotations

from core.governed_reasoning.hierarchical_concept_composition import (
    GovernedHierarchicalConceptComposer,
    HierarchicalConceptCompositionStatus,
    HierarchicalConceptLink,
    HierarchicalConceptRelation,
)
from core.governed_reasoning.productive_abstraction_admission import (
    CanonicalProductiveAbstractionEpisode,
)
from core.governed_reasoning.relational_abstraction import (
    GovernedRelationalAbstractionCandidate,
    RelationalAbstractionStatus,
)


def _abstraction(
    *,
    fingerprint: str,
    relation: str,
    outcome: str,
    contested: bool = False,
) -> GovernedRelationalAbstractionCandidate:
    return GovernedRelationalAbstractionCandidate(
        status=(
            RelationalAbstractionStatus.CONTESTED
            if contested
            else RelationalAbstractionStatus.REVIEW_REQUIRED
        ),
        scope_reference="scope:hcc",
        invariant_relation=relation,
        invariant_outcome=outcome,
        supporting_example_ids=(
            f"{fingerprint}:support:1",
            f"{fingerprint}:support:2",
        ),
        counterexample_ids=(
            (f"{fingerprint}:counter:1",) if contested else ()
        ),
        confidence=0.666667 if contested else 1.0,
        rationale_codes=(
            (
                "abstraction:shared_relational_invariant",
                "abstraction:counterexample_present",
            )
            if contested
            else ("abstraction:shared_relational_invariant",)
        ),
        source_fingerprint=fingerprint,
    )


def _episode(
    *,
    episode_id: str,
    fingerprint: str,
    relation: str,
    outcome: str,
    contested: bool = False,
    scope: str = "scope:hcc",
) -> CanonicalProductiveAbstractionEpisode:
    candidate = _abstraction(
        fingerprint=fingerprint,
        relation=relation,
        outcome=outcome,
        contested=contested,
    )
    if scope != candidate.scope_reference:
        candidate = GovernedRelationalAbstractionCandidate(
            status=candidate.status,
            scope_reference=scope,
            invariant_relation=candidate.invariant_relation,
            invariant_outcome=candidate.invariant_outcome,
            supporting_example_ids=candidate.supporting_example_ids,
            counterexample_ids=candidate.counterexample_ids,
            confidence=candidate.confidence,
            rationale_codes=candidate.rationale_codes,
            source_fingerprint=candidate.source_fingerprint,
        )
    return CanonicalProductiveAbstractionEpisode(
        episode_id=episode_id,
        session_id="session:hcc",
        turn_id=f"turn:{episode_id}",
        scope_reference=scope,
        admitted_evidence_fingerprints=(
            f"{fingerprint}:evidence:1",
            f"{fingerprint}:evidence:2",
        ),
        abstraction_candidate=candidate,
        source_fingerprint=f"episode-source:{fingerprint}",
    )


def _episodes() -> tuple[
    CanonicalProductiveAbstractionEpisode,
    CanonicalProductiveAbstractionEpisode,
]:
    return (
        _episode(
            episode_id="episode:a",
            fingerprint="fp:a",
            relation="required_for",
            outcome="blocked_when_unavailable",
        ),
        _episode(
            episode_id="episode:b",
            fingerprint="fp:b",
            relation="depends_on",
            outcome="degraded_when_missing",
        ),
    )


def test_green_1_contracts_are_read_only_and_non_persistent() -> None:
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=_episodes(),
        scope_reference="scope:hcc",
    )
    assert result.status is HierarchicalConceptCompositionStatus.REVIEW_REQUIRED
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.session_local is True
    assert result.persists is False
    assert result.creates_memory is False
    assert result.creates_learning is False
    assert result.modifies_world_model is False
    assert result.modifies_personal_knowledge is False
    assert result.executes_transfer is False
    assert result.registers_rule is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_green_2_requires_multiple_canonical_abstraction_episodes() -> None:
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=(_episodes()[0],),
        scope_reference="scope:hcc",
    )
    assert (
        result.status
        is HierarchicalConceptCompositionStatus.INSUFFICIENT_COMPONENTS
    )
    assert result.components == ()


def test_green_2_rejects_duplicate_episode_identity() -> None:
    episode = _episodes()[0]
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=(episode, episode),
        scope_reference="scope:hcc",
    )
    assert result.status is HierarchicalConceptCompositionStatus.NOT_COMPOSABLE
    assert "hcc:duplicate_episode" in result.rationale_codes


def test_green_2_exact_scope_is_required() -> None:
    one, _ = _episodes()
    other = _episode(
        episode_id="episode:other",
        fingerprint="fp:other",
        relation="related_to",
        outcome="supports",
        scope="scope:other",
    )
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=(one, other),
        scope_reference="scope:hcc",
    )
    assert result.status is HierarchicalConceptCompositionStatus.SCOPE_MISMATCH


def test_green_2_identity_is_independent_of_input_order() -> None:
    one, two = _episodes()
    composer = GovernedHierarchicalConceptComposer()
    first = composer.compose(
        episodes=(one, two),
        scope_reference="scope:hcc",
    )
    second = composer.compose(
        episodes=(two, one),
        scope_reference="scope:hcc",
    )
    assert first.concept_id == second.concept_id
    assert first.source_fingerprint == second.source_fingerprint
    assert first.components == second.components


def test_green_3_component_local_counterevidence_is_preserved() -> None:
    one, _ = _episodes()
    contested = _episode(
        episode_id="episode:contested",
        fingerprint="fp:contested",
        relation="related_to",
        outcome="supports",
        contested=True,
    )
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=(one, contested),
        scope_reference="scope:hcc",
    )
    assert result.status is HierarchicalConceptCompositionStatus.CONTESTED
    by_episode = {
        item.abstraction_episode_id: item for item in result.components
    }
    assert by_episode["episode:a"].counterexample_ids == ()
    assert by_episode["episode:contested"].counterexample_ids == (
        "fp:contested:counter:1",
    )


def test_green_3_bounded_component_links_are_validated() -> None:
    composer = GovernedHierarchicalConceptComposer()
    base = composer.compose(
        episodes=_episodes(),
        scope_reference="scope:hcc",
    )
    first, second = base.components
    link = HierarchicalConceptLink(
        source_component_id=first.component_id,
        target_component_id=second.component_id,
        relation=HierarchicalConceptRelation.CONTAINS_COMPONENT,
    )
    result = composer.compose(
        episodes=_episodes(),
        scope_reference="scope:hcc",
        links=(link,),
        parent_concept_reference="concept:parent",
        child_concept_references=("concept:child:b", "concept:child:a"),
    )
    assert result.links == (link,)
    assert result.parent_concept_reference == "concept:parent"
    assert result.child_concept_references == (
        "concept:child:a",
        "concept:child:b",
    )


def test_green_3_link_to_unknown_component_fails_closed() -> None:
    base = GovernedHierarchicalConceptComposer().compose(
        episodes=_episodes(),
        scope_reference="scope:hcc",
    )
    link = HierarchicalConceptLink(
        source_component_id=base.components[0].component_id,
        target_component_id="hcc-component:missing",
        relation=HierarchicalConceptRelation.RELATED_COMPONENT,
    )
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=_episodes(),
        scope_reference="scope:hcc",
        links=(link,),
    )
    assert result.status is HierarchicalConceptCompositionStatus.NOT_COMPOSABLE
    assert result.links == ()


def test_green_4_candidate_preserves_exact_constituent_lineage() -> None:
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=_episodes(),
        scope_reference="scope:hcc",
    )
    assert result.constituent_episode_ids == ("episode:a", "episode:b")
    assert result.constituent_fingerprints == (
        "episode-source:fp:a",
        "episode-source:fp:b",
    )
    assert tuple(
        item.abstraction_episode_id for item in result.components
    ) == result.constituent_episode_ids


def test_green_4_no_structural_transfer_or_persistence_is_invoked() -> None:
    result = GovernedHierarchicalConceptComposer().compose(
        episodes=_episodes(),
        scope_reference="scope:hcc",
    )
    assert result.executes_transfer is False
    assert result.creates_learning is False
    assert result.creates_memory is False
    assert result.modifies_personal_knowledge is False
    assert result.modifies_world_model is False
