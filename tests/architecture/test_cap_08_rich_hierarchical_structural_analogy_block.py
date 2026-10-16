from __future__ import annotations

from hashlib import sha256

from core.governed_reasoning import (
    GovernedHierarchicalStructuralAnalogyMatcher,
    HierarchicalStructuralAnalogyStatus,
)
from core.governed_reasoning.hierarchical_concept_composition import (
    CanonicalProductiveConceptEpisode,
    GovernedHierarchicalConceptComposer,
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

SCOPE = "cap-08-rich-hierarchical-analogy"


def _abstraction(
    episode_id: str,
    relation: str,
    outcome: str,
    marker: str,
    *,
    scope: str = SCOPE,
) -> CanonicalProductiveAbstractionEpisode:
    candidate_fp = sha256(f"candidate:{marker}".encode()).hexdigest()
    candidate = GovernedRelationalAbstractionCandidate(
        status=RelationalAbstractionStatus.REVIEW_REQUIRED,
        scope_reference=scope,
        invariant_relation=relation,
        invariant_outcome=outcome,
        supporting_example_ids=(f"{marker}:1", f"{marker}:2"),
        counterexample_ids=(),
        confidence=1.0,
        rationale_codes=("test:reviewable",),
        source_fingerprint=candidate_fp,
    )
    episode_fp = sha256(f"episode:{marker}".encode()).hexdigest()
    return CanonicalProductiveAbstractionEpisode(
        episode_id=episode_id,
        session_id="cap08-session",
        turn_id=f"turn:{marker}",
        scope_reference=scope,
        admitted_evidence_fingerprints=(
            sha256(f"{marker}:e1".encode()).hexdigest(),
            sha256(f"{marker}:e2".encode()).hexdigest(),
        ),
        abstraction_candidate=candidate,
        source_fingerprint=episode_fp,
    )


def _concept(
    marker: str,
    *,
    second_outcome: str = "blocked_when_prerequisite_unavailable",
    scope: str = SCOPE,
    linked: bool = False,
) -> CanonicalProductiveConceptEpisode:
    episodes = (
        _abstraction(
            f"abs:{marker}:r1",
            "required_for",
            "blocked_when_unavailable",
            f"{marker}:r1",
            scope=scope,
        ),
        _abstraction(
            f"abs:{marker}:r2",
            "required_for",
            second_outcome,
            f"{marker}:r2",
            scope=scope,
        ),
    )
    composer = GovernedHierarchicalConceptComposer()
    base = composer.compose(episodes=episodes, scope_reference=scope)
    links = ()
    if linked:
        links = (
            HierarchicalConceptLink(
                source_component_id=base.components[0].component_id,
                target_component_id=base.components[1].component_id,
                relation=HierarchicalConceptRelation.RELATED_COMPONENT,
            ),
        )
    candidate = composer.compose(
        episodes=episodes,
        scope_reference=scope,
        links=links,
    )
    fp = sha256(f"concept-episode:{marker}:{linked}".encode()).hexdigest()
    return CanonicalProductiveConceptEpisode(
        episode_id=f"concept:{marker}",
        owner="Carlos",
        session_id="cap08-session",
        turn_id=f"concept-turn:{marker}",
        scope_reference=scope,
        concept_candidate=candidate,
        source_abstraction_episode_ids=candidate.constituent_episode_ids,
        source_fingerprint=fp,
    )


def _match(source, target):
    return GovernedHierarchicalStructuralAnalogyMatcher().match(
        source=source,
        target=target,
        scope_reference=SCOPE,
    )


def test_hcc_concepts_match_by_multi_component_structure_not_episode_identity() -> None:
    result = _match(_concept("source"), _concept("target"))
    assert result.status is HierarchicalStructuralAnalogyStatus.ANALOGY_CANDIDATE
    assert len(result.component_correspondences) == 2
    assert result.source_concept_episode_id == "concept:source"
    assert result.target_concept_episode_id == "concept:target"


def test_component_semantic_difference_rejects_rich_analogy() -> None:
    result = _match(
        _concept("source"),
        _concept("target", second_outcome="different_outcome"),
    )
    assert result.status is HierarchicalStructuralAnalogyStatus.NO_ANALOGY
    assert result.component_correspondences == ()


def test_hierarchical_link_topology_is_part_of_analogy_structure() -> None:
    result = _match(_concept("source", linked=True), _concept("target", linked=True))
    assert result.status is HierarchicalStructuralAnalogyStatus.ANALOGY_CANDIDATE
    assert result.matched_link_relations == (
        HierarchicalConceptRelation.RELATED_COMPONENT,
    )


def test_link_topology_mismatch_rejects_analogy() -> None:
    result = _match(_concept("source", linked=True), _concept("target"))
    assert result.status is HierarchicalStructuralAnalogyStatus.NO_ANALOGY
    assert "hierarchical_analogy:link_topology_mismatch" in result.rationale_codes


def test_same_concept_episode_is_not_an_analogy() -> None:
    concept = _concept("same")
    result = _match(concept, concept)
    assert result.status is HierarchicalStructuralAnalogyStatus.NO_ANALOGY


def test_cross_scope_concepts_fail_closed() -> None:
    source = _concept("source")
    target = _concept("target", scope="other-scope")
    result = GovernedHierarchicalStructuralAnalogyMatcher().match(
        source=source,
        target=target,
        scope_reference=SCOPE,
    )
    assert result.status is HierarchicalStructuralAnalogyStatus.SCOPE_MISMATCH


def test_rich_analogy_is_read_only_and_cannot_execute_existing_transfer() -> None:
    result = _match(_concept("source"), _concept("target"))
    assert result.status is HierarchicalStructuralAnalogyStatus.ANALOGY_CANDIDATE
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.session_local is True
    assert result.persists is False
    assert result.creates_memory is False
    assert result.creates_learning is False
    assert result.modifies_world_model is False
    assert result.establishes_truth is False
    assert result.authorizes_inference is False
    assert result.executes_transfer is False
    assert result.registers_rule is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_rich_analogy_is_deterministic() -> None:
    source = _concept("source", linked=True)
    target = _concept("target", linked=True)
    first = _match(source, target)
    second = _match(source, target)
    assert first == second
    assert first.source_fingerprint == second.source_fingerprint
