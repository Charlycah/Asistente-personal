from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimConfidence,
    ClaimEvidenceLink,
    ClaimOrigin,
    ClaimRegistryManager,
    ClaimStatus,
    ClaimType,
    EvidenceKind,
    EvidenceLinkRole,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
    InMemoryClaimRepository,
)

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
HASH_A = "a" * 64
HASH_B = "b" * 64


def test_confidence_validates_range_and_rationale() -> None:
    with pytest.raises(ValueError):
        ClaimConfidence(1.1, "too high")
    with pytest.raises(ValueError):
        ClaimConfidence(0.5, " ")


def test_evidence_link_preserves_versioned_provenance() -> None:
    reference = _evidence("doc-1", HASH_A)
    link = ClaimEvidenceLink.from_reference(reference)
    assert link.evidence_id == reference.evidence_id
    assert link.source_id == "doc-1"
    assert link.evidence_fingerprint == HASH_A
    assert link.normalized_role is EvidenceLinkRole.SUPPORTS


def test_evidence_link_rejects_invalid_hash() -> None:
    with pytest.raises(ValueError):
        ClaimEvidenceLink("e", EvidenceLinkRole.SUPPORTS, "document", "doc", "bad")


def test_fact_requires_supporting_evidence() -> None:
    with pytest.raises(ValueError):
        _claim(evidence_links=())


def test_observation_requires_supporting_evidence() -> None:
    with pytest.raises(ValueError):
        _claim(claim_type=ClaimType.OBSERVATION, evidence_links=())


def test_hypothesis_may_be_proposed_without_evidence() -> None:
    claim = _claim(
        claim_type=ClaimType.HYPOTHESIS,
        origin=ClaimOrigin.HUMAN,
        evidence_links=(),
        status=ClaimStatus.PROPOSED,
    )
    assert claim.normalized_type is ClaimType.HYPOTHESIS


def test_rule_result_requires_rule_origin_and_reference() -> None:
    with pytest.raises(ValueError):
        _claim(claim_type=ClaimType.RULE_RESULT, origin=ClaimOrigin.RULE)
    claim = _claim(
        claim_type=ClaimType.RULE_RESULT,
        origin=ClaimOrigin.RULE,
        rule_reference="rule.task.overdue@1",
        evidence_links=(),
        status=ClaimStatus.PROPOSED,
    )
    assert claim.rule_reference == "rule.task.overdue@1"


def test_non_rule_claim_cannot_declare_rule_reference() -> None:
    with pytest.raises(ValueError):
        _claim(rule_reference="rule-1")


def test_absence_of_evidence_is_not_supported_as_proof() -> None:
    with pytest.raises(ValueError):
        _claim(claim_type=ClaimType.ABSENCE_OF_EVIDENCE)
    claim = _claim(
        claim_type=ClaimType.ABSENCE_OF_EVIDENCE,
        origin=ClaimOrigin.SYSTEM,
        evidence_links=(),
        status=ClaimStatus.PROPOSED,
    )
    assert claim.normalized_type is ClaimType.ABSENCE_OF_EVIDENCE


def test_corroborated_claim_requires_two_supporting_sources() -> None:
    with pytest.raises(ValueError):
        _claim(status=ClaimStatus.CORROBORATED)
    claim = _claim(
        status=ClaimStatus.CORROBORATED,
        evidence_links=(_link("doc-1", HASH_A), _link("doc-2", HASH_B)),
    )
    assert claim.normalized_status is ClaimStatus.CORROBORATED


def test_claim_rejects_duplicate_evidence_links() -> None:
    link = _link("doc-1", HASH_A)
    with pytest.raises(ValueError):
        _claim(evidence_links=(link, link))


def test_claim_is_immutable() -> None:
    claim = _claim()
    with pytest.raises(FrozenInstanceError):
        claim.status = ClaimStatus.REFUTED  # type: ignore[misc]


def test_claim_fingerprint_is_stable_for_same_semantics() -> None:
    first = _claim(claim_id="claim-1")
    second = _claim(claim_id="claim-2")
    assert first.fingerprint == second.fingerprint


def test_repository_rejects_duplicate_semantic_claim() -> None:
    repository = InMemoryClaimRepository()
    repository.save(_claim(claim_id="claim-1"))
    with pytest.raises(ValueError):
        repository.save(_claim(claim_id="claim-2"))


def test_repository_requires_sequential_revisions() -> None:
    repository = InMemoryClaimRepository()
    repository.save(_claim(claim_id="claim-1"))
    with pytest.raises(ValueError):
        repository.save(
            _claim(
                claim_id="claim-1",
                revision=3,
                status=ClaimStatus.DISPUTED,
            )
        )


def test_registry_registers_supported_claim_from_evidence() -> None:
    registry = ClaimRegistryManager()
    claim = registry.register_from_evidence(
        subject="garantía",
        predicate="vence_el",
        object_value="2026-08-15",
        claim_type=ClaimType.FACT,
        evidence=(_evidence("doc-1", HASH_A),),
        created_at=NOW,
    )
    assert claim.normalized_status is ClaimStatus.SUPPORTED
    assert registry.get(claim.claim_id) is claim


def test_registry_marks_two_sources_as_corroborated() -> None:
    claim = ClaimRegistryManager().register_from_evidence(
        subject="garantía",
        predicate="vence_el",
        object_value="2026-08-15",
        claim_type=ClaimType.FACT,
        evidence=(_evidence("doc-2", HASH_B), _evidence("doc-1", HASH_A)),
        created_at=NOW,
    )
    assert claim.normalized_status is ClaimStatus.CORROBORATED
    assert [link.source_id for link in claim.evidence_links] == ["doc-1", "doc-2"]


def test_review_required_evidence_prevents_supported_status() -> None:
    claim = ClaimRegistryManager().register_from_evidence(
        subject="dato",
        predicate="es",
        object_value="pendiente",
        claim_type=ClaimType.FACT,
        evidence=(_evidence("doc-1", HASH_A, status=EvidenceStatus.REVIEW_REQUIRED),),
        created_at=NOW,
    )
    assert claim.normalized_status is ClaimStatus.REVIEW_REQUIRED


def test_status_revision_preserves_history() -> None:
    registry = ClaimRegistryManager()
    original = registry.register(_claim(claim_id="claim-1"))
    revised = registry.revise_status(
        original.claim_id,
        ClaimStatus.DISPUTED,
        created_at=NOW + timedelta(minutes=1),
    )
    history = registry.history(original.claim_id)
    assert revised.revision == 2
    assert [item.normalized_status for item in history] == [
        ClaimStatus.SUPPORTED,
        ClaimStatus.DISPUTED,
    ]


def test_revise_missing_claim_fails_explicitly() -> None:
    with pytest.raises(KeyError):
        ClaimRegistryManager().revise_status("missing", ClaimStatus.REFUTED)


def test_supersede_keeps_both_claims_and_links_replacement() -> None:
    registry = ClaimRegistryManager()
    original = registry.register(_claim(claim_id="claim-old"))
    replacement = _claim(
        claim_id="claim-new",
        object_value="2026-09-01",
        evidence_links=(_link("doc-2", HASH_B),),
    )
    superseded, saved_replacement = registry.supersede(
        original.claim_id,
        replacement,
        created_at=NOW + timedelta(minutes=1),
    )
    assert superseded.normalized_status is ClaimStatus.SUPERSEDED
    assert saved_replacement.supersedes == original.claim_id
    assert len(registry.list_all()) == 2


def test_registry_filters_deterministically() -> None:
    registry = ClaimRegistryManager()
    registry.register(_claim(claim_id="b", subject="Beta", owner="carlos"))
    registry.register(
        _claim(
            claim_id="a",
            subject="Alpha",
            owner="shared",
            evidence_links=(_link("doc-2", HASH_B),),
        )
    )
    assert [claim.claim_id for claim in registry.list_all()] == ["b", "a"]
    assert [claim.claim_id for claim in registry.list_all(owner="shared")] == ["a"]


def test_serialization_keeps_claim_evidence_and_distinctions() -> None:
    payload = _claim(confidence=ClaimConfidence(0.8, "single primary source")).to_dict()
    assert payload["type"] == "fact"
    assert payload["origin"] == "evidence"
    assert payload["status"] == "supported"
    assert payload["evidence_links"][0]["source_id"] == "doc-1"
    assert payload["confidence"]["score"] == 0.8


def _claim(
    *,
    subject: str = "garantía",
    predicate: str = "vence_el",
    object_value: str = "2026-08-15",
    claim_type: ClaimType = ClaimType.FACT,
    origin: ClaimOrigin = ClaimOrigin.EVIDENCE,
    status: ClaimStatus = ClaimStatus.SUPPORTED,
    evidence_links: tuple[ClaimEvidenceLink, ...] | None = None,
    confidence: ClaimConfidence | None = None,
    owner: str = "shared",
    rule_reference: str | None = None,
    claim_id: str = "claim-1",
    revision: int = 1,
) -> Claim:
    links = (_link("doc-1", HASH_A),) if evidence_links is None else evidence_links
    return Claim(
        subject=subject,
        predicate=predicate,
        object_value=object_value,
        claim_type=claim_type,
        origin=origin,
        status=status,
        evidence_links=links,
        confidence=confidence,
        owner=owner,
        rule_reference=rule_reference,
        created_at=NOW,
        claim_id=claim_id,
        revision=revision,
    )


def _link(source_id: str, fingerprint: str) -> ClaimEvidenceLink:
    return ClaimEvidenceLink.from_reference(_evidence(source_id, fingerprint))


def _evidence(
    source_id: str,
    fingerprint: str,
    *,
    status: EvidenceStatus = EvidenceStatus.ACTIVE,
) -> EvidenceReference:
    return EvidenceReference(
        source_type=EvidenceSourceType.DOCUMENT,
        source_id=source_id,
        kind=EvidenceKind.DOCUMENT,
        owner="shared",
        status=status,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=NOW,
        fingerprint=fingerprint,
        summary=f"Document {source_id}",
    )
