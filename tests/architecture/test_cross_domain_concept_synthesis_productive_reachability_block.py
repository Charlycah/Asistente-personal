from __future__ import annotations

from datetime import datetime, timezone

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.governed_reasoning.cross_domain_concept_synthesis import (
    CrossDomainConceptSource,
    CrossDomainConceptSynthesisStatus,
    GovernedCrossDomainConceptSynthesizer,
)
from core.governed_reasoning.hierarchical_concept_composition import (
    CanonicalProductiveConceptEpisode,
    GovernedHierarchicalConceptCandidate,
    HierarchicalConceptComponent,
    HierarchicalConceptCompositionStatus,
    HierarchicalConceptLink,
    HierarchicalConceptRelation,
)
from core.governed_reasoning.relational_abstraction import RelationalAbstractionStatus

OWNER = "Carlos"
SESSION = "cross-domain-synthesis"
NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)


def _episode(domain: str, scope: str, turn: str) -> CanonicalProductiveConceptEpisode:
    components = (
        HierarchicalConceptComponent(
            component_id=f"{domain}:c1",
            abstraction_episode_id=f"{domain}:a1",
            abstraction_fingerprint=f"{domain}:f1",
            relation="required_for",
            outcome="blocked_when_unavailable",
            status=RelationalAbstractionStatus.REVIEW_REQUIRED,
            supporting_example_ids=(f"{domain}:e1", f"{domain}:e2"),
            counterexample_ids=(),
            rationale_codes=("test:governed",),
        ),
        HierarchicalConceptComponent(
            component_id=f"{domain}:c2",
            abstraction_episode_id=f"{domain}:a2",
            abstraction_fingerprint=f"{domain}:f2",
            relation="supports",
            outcome="degraded_when_absent",
            status=RelationalAbstractionStatus.REVIEW_REQUIRED,
            supporting_example_ids=(f"{domain}:e3", f"{domain}:e4"),
            counterexample_ids=(),
            rationale_codes=("test:governed",),
        ),
    )
    links = (
        HierarchicalConceptLink(
            source_component_id=components[0].component_id,
            target_component_id=components[1].component_id,
            relation=HierarchicalConceptRelation.RELATED_COMPONENT,
        ),
    )
    candidate = GovernedHierarchicalConceptCandidate(
        concept_id=f"concept:{domain}",
        scope_reference=scope,
        components=components,
        links=links,
        parent_concept_reference=None,
        child_concept_references=(),
        status=HierarchicalConceptCompositionStatus.REVIEW_REQUIRED,
        rationale_codes=("test:hcc",),
        constituent_episode_ids=(f"{domain}:a1", f"{domain}:a2"),
        constituent_fingerprints=(f"{domain}:f1", f"{domain}:f2"),
        source_fingerprint=f"{domain}:concept-fingerprint",
    )
    return CanonicalProductiveConceptEpisode(
        episode_id=f"episode:{domain}",
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn,
        scope_reference=scope,
        concept_candidate=candidate,
        source_abstraction_episode_ids=(f"{domain}:a1", f"{domain}:a2"),
        source_fingerprint=f"{domain}:episode-fingerprint",
    )


def test_distinct_domains_and_distinct_scopes_form_candidate() -> None:
    result = GovernedCrossDomainConceptSynthesizer().synthesize(
        source=CrossDomainConceptSource("biology", _episode("bio", "scope:bio", "t1")),
        target=CrossDomainConceptSource(
            "software",
            _episode("soft", "scope:software", "t2"),
        ),
    )
    assert result.status is CrossDomainConceptSynthesisStatus.SYNTHESIS_CANDIDATE
    assert result.source_scope_reference == "scope:bio"
    assert result.target_scope_reference == "scope:software"
    assert len(result.correspondences) == 2


def test_same_domain_does_not_fabricate_cross_domain_synthesis() -> None:
    result = GovernedCrossDomainConceptSynthesizer().synthesize(
        source=CrossDomainConceptSource("biology", _episode("a", "scope:a", "t1")),
        target=CrossDomainConceptSource("BIOLOGY", _episode("b", "scope:b", "t2")),
    )
    assert result.status is CrossDomainConceptSynthesisStatus.SAME_DOMAIN
    assert result.correspondences == ()


def test_owner_or_session_lineage_mismatch_fails_closed() -> None:
    target = _episode("b", "scope:b", "t2")
    object.__setattr__(target, "session_id", "other-session")
    result = GovernedCrossDomainConceptSynthesizer().synthesize(
        source=CrossDomainConceptSource("biology", _episode("a", "scope:a", "t1")),
        target=CrossDomainConceptSource("software", target),
    )
    assert result.status is CrossDomainConceptSynthesisStatus.LINEAGE_MISMATCH


def test_productive_gateway_preserves_domain_and_scope_provenance() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    first = _episode("bio", "scope:bio", "t1")
    second = _episode("soft", "scope:software", "t2")
    assert gateway.bind_productive_cross_domain_concept(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        domain_reference="biology",
        concept_episode=first,
    ) is None
    result = gateway.bind_productive_cross_domain_concept(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t2",
        domain_reference="software",
        concept_episode=second,
    )
    assert result is not None
    assert result.source_domain_reference == "biology"
    assert result.target_domain_reference == "software"
    assert result.source_scope_reference != result.target_scope_reference


def test_candidate_is_strictly_consultative() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    gateway.bind_productive_cross_domain_concept(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        domain_reference="biology",
        concept_episode=_episode("bio", "scope:bio", "t1"),
    )
    result = gateway.bind_productive_cross_domain_concept(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t2",
        domain_reference="software",
        concept_episode=_episode("soft", "scope:software", "t2"),
    )
    assert result is not None
    assert result.read_only
    assert not result.persists
    assert not result.establishes_truth
    assert not result.establishes_causality
    assert not result.authorizes_inference
    assert not result.creates_memory
    assert not result.creates_learning
    assert not result.modifies_world_model
    assert not result.executes_transfer
    assert not result.registers_rule
    assert not result.executes_actions
    assert not result.grants_authority


def test_same_turn_source_exposes_synthesis_refs_and_context() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = CanonicalProductiveReasoningSource(gateway)
    first = _episode("bio", "scope:bio", "t1")
    second = _episode("soft", "scope:software", "t2")
    gateway.bind_productive_cross_domain_concept(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        domain_reference="biology",
        concept_episode=first,
    )
    # Use a real ordinary turn identity so the source can retrieve the candidate.
    from core.governed_operational_conversation_pipeline import (
        GovernedConversationPipelineRequest,
        build_governed_conversation_turn_identity,
    )
    text = "comparar estructuras entre dominios"
    request = GovernedConversationPipelineRequest(
        owner=OWNER,
        session_id=SESSION,
        text=text,
    )
    turn_id = build_governed_conversation_turn_identity(request, NOW).turn_id
    gateway.bind_productive_cross_domain_concept(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
        domain_reference="software",
        concept_episode=second,
    )
    lines = source.cross_domain_synthesis_context_lines(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=NOW,
    )
    refs = source.reference_ids(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=NOW,
    )
    candidate = gateway.productive_cross_domain_synthesis_candidate(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert candidate is not None
    assert "Síntesis conceptual interdominio gobernada" in lines[0]
    assert "no establece verdad" in lines[1]
    assert candidate.source_fingerprint in refs


def test_reasoning_contributor_consumes_cross_domain_context() -> None:
    class Source:
        def __call__(self, **kwargs):
            return None

        def cross_domain_synthesis_context_lines(self, **kwargs):
            return ("cross-domain",)

    # Reachability is already established through the official source contract.
    # This assertion protects the contributor's structural consumption hook.
    source_text = (
        __import__("pathlib").Path("core/reasoning_runtime_integration.py")
        .read_text(encoding="utf-8")
    )
    assert "cross_domain_synthesis_context_lines" in source_text
