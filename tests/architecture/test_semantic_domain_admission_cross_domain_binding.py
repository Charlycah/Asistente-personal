from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from app.semantic_domain_cross_domain_binding import (
    SemanticDomainAdmissionCrossDomainBinding,
    SemanticDomainAdmissionStatus,
)
from core.governed_reasoning.evidence import (
    EvidenceKind,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
)
from core.governed_reasoning.hierarchical_concept_composition import (
    GovernedHierarchicalConceptCandidate,
    HierarchicalConceptComponent,
    HierarchicalConceptCompositionStatus,
    HierarchicalConceptLink,
    HierarchicalConceptRelation,
)
from core.governed_reasoning.relational_abstraction import RelationalAbstractionStatus

OWNER = "Carlos"
SESSION = "cap19-semantic-domain"
NOW = datetime(2026, 9, 11, 18, 0, tzinfo=timezone.utc)


def _candidate(label: str, scope: str) -> GovernedHierarchicalConceptCandidate:
    components = (
        HierarchicalConceptComponent(
            component_id=f"{label}:c1",
            abstraction_episode_id=f"{label}:a1",
            abstraction_fingerprint=f"{label}:f1",
            relation="required_for",
            outcome="blocked_when_unavailable",
            status=RelationalAbstractionStatus.REVIEW_REQUIRED,
            supporting_example_ids=(f"{label}:e1", f"{label}:e2"),
            counterexample_ids=(),
            rationale_codes=("test:governed",),
        ),
        HierarchicalConceptComponent(
            component_id=f"{label}:c2",
            abstraction_episode_id=f"{label}:a2",
            abstraction_fingerprint=f"{label}:f2",
            relation="supports",
            outcome="degraded_when_absent",
            status=RelationalAbstractionStatus.REVIEW_REQUIRED,
            supporting_example_ids=(f"{label}:e3", f"{label}:e4"),
            counterexample_ids=(),
            rationale_codes=("test:governed",),
        ),
    )
    return GovernedHierarchicalConceptCandidate(
        concept_id=f"concept:{label}",
        scope_reference=scope,
        components=components,
        links=(
            HierarchicalConceptLink(
                source_component_id=components[0].component_id,
                target_component_id=components[1].component_id,
                relation=HierarchicalConceptRelation.RELATED_COMPONENT,
            ),
        ),
        parent_concept_reference=None,
        child_concept_references=(),
        status=HierarchicalConceptCompositionStatus.REVIEW_REQUIRED,
        rationale_codes=("test:hcc",),
        constituent_episode_ids=(f"{label}:a1", f"{label}:a2"),
        constituent_fingerprints=(f"{label}:f1", f"{label}:f2"),
        source_fingerprint=f"{label}:concept-fingerprint",
    )


def _evidence(
    *,
    concept_episode_id: str,
    domain: str | None,
    session_id: str = SESSION,
    owner: str = OWNER,
    extra_metadata: tuple[tuple[str, str], ...] = (),
) -> EvidenceReference:
    metadata = list(extra_metadata)
    if domain is not None:
        metadata.extend(
            (
                ("semantic_domain", domain),
                ("session_id", session_id),
                ("concept_episode_id", concept_episode_id),
            )
        )
    fingerprint = sha256(repr(tuple(metadata)).encode("utf-8")).hexdigest()
    return EvidenceReference(
        source_type=EvidenceSourceType.KNOWLEDGE,
        source_id=f"source:{concept_episode_id}:{domain or 'none'}",
        kind=EvidenceKind.KNOWLEDGE_ITEM,
        owner=owner,
        status=EvidenceStatus.ACTIVE,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=NOW,
        fingerprint=fingerprint,
        summary="Explicit governed semantic-domain evidence.",
        metadata=tuple(metadata),
    )


def _bind_concept(gateway, *, turn: str, label: str, scope: str):
    return gateway.bind_productive_concept_candidate(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn,
        candidate=_candidate(label, scope),
    )


def _adapter(gateway):
    registry = gateway.orchestrator.context_assembler.evidence_registry
    return SemanticDomainAdmissionCrossDomainBinding(
        evidence_registry=registry,
        reasoning_gateway=gateway,
    ), registry


def test_registered_explicit_domain_evidence_reaches_existing_binding() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adapter, registry = _adapter(gateway)
    first = _bind_concept(gateway, turn="t1", label="bio", scope="scope:bio")
    second = _bind_concept(gateway, turn="t2", label="soft", scope="scope:soft")
    assert first is not None and second is not None

    first_evidence = registry.register_reference(
        _evidence(concept_episode_id=first.episode_id, domain="biology")
    )
    second_evidence = registry.register_reference(
        _evidence(concept_episode_id=second.episode_id, domain="software")
    )
    first_result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        evidence_id=first_evidence.evidence_id,
    )
    second_result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t2",
        evidence_id=second_evidence.evidence_id,
    )

    assert first_result.status is SemanticDomainAdmissionStatus.ADMITTED
    assert first_result.synthesis_candidate is None
    assert second_result.status is SemanticDomainAdmissionStatus.ADMITTED
    assert second_result.synthesis_candidate is not None
    assert second_result.synthesis_candidate.source_domain_reference == "biology"
    assert second_result.synthesis_candidate.target_domain_reference == "software"


def test_domain_string_without_structured_evidence_fails_closed() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adapter, registry = _adapter(gateway)
    concept = _bind_concept(gateway, turn="t1", label="bio", scope="scope:bio")
    assert concept is not None
    evidence = registry.register_reference(
        _evidence(
            concept_episode_id=concept.episode_id,
            domain=None,
            extra_metadata=(("tag", "biology"),),
        )
    )
    result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        evidence_id=evidence.evidence_id,
    )
    assert result.status is SemanticDomainAdmissionStatus.REJECTED
    assert result.domain_reference is None


def test_source_kind_scope_or_interest_like_metadata_cannot_become_domain() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adapter, registry = _adapter(gateway)
    concept = _bind_concept(gateway, turn="t1", label="x", scope="scope:x")
    assert concept is not None
    evidence = registry.register_reference(
        _evidence(
            concept_episode_id=concept.episode_id,
            domain=None,
            extra_metadata=(
                ("source_kind", "encyclopedia"),
                ("scope_domain", "knowledge"),
                ("interest_topic", "astronomy"),
            ),
        )
    )
    result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        evidence_id=evidence.evidence_id,
    )
    assert result.status is SemanticDomainAdmissionStatus.REJECTED


def test_evidence_must_match_owner_session_and_exact_concept_episode() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adapter, registry = _adapter(gateway)
    concept = _bind_concept(gateway, turn="t1", label="bio", scope="scope:bio")
    assert concept is not None
    wrong_session = registry.register_reference(
        _evidence(
            concept_episode_id=concept.episode_id,
            domain="biology",
            session_id="other-session",
        )
    )
    result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        evidence_id=wrong_session.evidence_id,
    )
    assert result.status is SemanticDomainAdmissionStatus.REJECTED

    wrong_owner = registry.register_reference(
        _evidence(
            concept_episode_id=concept.episode_id,
            domain="biology",
            owner="Cristina",
        )
    )
    result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        evidence_id=wrong_owner.evidence_id,
    )
    assert result.status is SemanticDomainAdmissionStatus.REJECTED


def test_missing_registered_evidence_or_productive_concept_fails_closed() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adapter, registry = _adapter(gateway)
    missing = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        evidence_id="missing-evidence",
    )
    assert missing.status is SemanticDomainAdmissionStatus.REJECTED

    evidence = registry.register_reference(
        _evidence(concept_episode_id="productive-concept:missing", domain="biology")
    )
    result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t2",
        evidence_id=evidence.evidence_id,
    )
    assert result.status is SemanticDomainAdmissionStatus.REJECTED


def test_admission_is_non_persistent_non_learning_and_non_operational() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adapter, registry = _adapter(gateway)
    concept = _bind_concept(gateway, turn="t1", label="bio", scope="scope:bio")
    assert concept is not None
    evidence = registry.register_reference(
        _evidence(concept_episode_id=concept.episode_id, domain="biology")
    )
    result = adapter.admit(
        owner=OWNER,
        session_id=SESSION,
        turn_id="t1",
        evidence_id=evidence.evidence_id,
    )
    assert result.status is SemanticDomainAdmissionStatus.ADMITTED
    assert not result.persists
    assert not result.creates_memory
    assert not result.creates_learning
    assert not result.modifies_world_model
    assert not result.executes_actions
    assert not result.grants_authority
