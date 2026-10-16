from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from core.governed_reasoning import (
    Claim,
    ClaimEvidenceLink,
    ClaimOrigin,
    ClaimRegistryManager,
    ClaimStatus,
    ClaimType,
    ContextAssemblyStatus,
    ContextDecisionOutcome,
    ContextItemType,
    ContextSelectionPolicy,
    EvidenceKind,
    EvidenceReference,
    EvidenceRegistry,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
    GovernedContextAssembler,
    ReasoningContextBundle,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def test_query_requires_text_owner_domains_and_aware_time() -> None:
    with pytest.raises(ValueError):
        ReasoningQuery(" ", as_of=NOW)
    with pytest.raises(ValueError):
        ReasoningQuery("garantía", owner=" ", as_of=NOW)
    with pytest.raises(ValueError):
        ReasoningQuery("garantía", domains=(), as_of=NOW)
    with pytest.raises(ValueError):
        ReasoningQuery("garantía", as_of=NOW.replace(tzinfo=None))


def test_query_id_and_terms_are_stable_and_accent_insensitive() -> None:
    first = ReasoningQuery(
        "¿Cuándo vence la garantía?",
        topics=("Documento",),
        as_of=NOW,
    )
    second = ReasoningQuery(
        "¿Cuándo vence la garantía?",
        topics=("Documento",),
        as_of=NOW,
    )
    assert first.query_id == second.query_id
    assert "garantia" in first.search_terms
    assert "documento" in first.search_terms


def test_policy_validates_limits_and_status_sets() -> None:
    with pytest.raises(ValueError):
        ContextSelectionPolicy(max_claims=0)
    with pytest.raises(ValueError):
        ContextSelectionPolicy(allowed_claim_statuses=())


def test_selection_decision_is_typed_and_immutable() -> None:
    decision = _decision("claim-1")
    assert decision.normalized_item_type is ContextItemType.CLAIM
    assert decision.normalized_outcome is ContextDecisionOutcome.INCLUDED
    with pytest.raises(FrozenInstanceError):
        decision.reason = "changed"  # type: ignore[misc]


def test_context_bundle_rejects_duplicate_claims_and_naive_time() -> None:
    query = ReasoningQuery("garantía", as_of=NOW)
    assembler, claim, evidence = _assembler()
    scope = assembler.scope_guard.observe_turn("garantía").decision
    with pytest.raises(ValueError):
        ReasoningContextBundle(
            query,
            ContextAssemblyStatus.READY,
            scope,
            (claim, claim),
            (evidence,),
            (),
            NOW,
        )
    with pytest.raises(ValueError):
        ReasoningContextBundle(
            query,
            ContextAssemblyStatus.READY,
            scope,
            (claim,),
            (evidence,),
            (),
            NOW.replace(tzinfo=None),
        )


def test_assembler_selects_relevant_claim_and_linked_evidence() -> None:
    assembler, claim, evidence = _assembler()
    bundle = assembler.assemble(
        ReasoningQuery("¿Cuándo vence la garantía?", as_of=NOW),
        now=NOW,
    )
    assert bundle.normalized_status is ContextAssemblyStatus.READY
    assert bundle.claims == (claim,)
    assert bundle.evidence == (evidence,)
    assert _outcome(bundle, ContextItemType.CLAIM, claim.claim_id) == "included"


def test_explicit_claim_is_selected_without_keyword_match() -> None:
    assembler, claim, evidence = _assembler()
    bundle = assembler.assemble(
        ReasoningQuery("consulta general", claim_ids=(claim.claim_id,), as_of=NOW),
        now=NOW,
    )
    assert bundle.claims == (claim,)
    assert bundle.evidence == (evidence,)


def test_explicit_evidence_is_selected_without_claim_or_keyword_match() -> None:
    assembler, _, evidence = _assembler(include_claim=False)
    bundle = assembler.assemble(
        ReasoningQuery(
            "consulta general",
            evidence_ids=(evidence.evidence_id,),
            as_of=NOW,
        ),
        now=NOW,
    )
    assert bundle.evidence == (evidence,)


def test_missing_referenced_evidence_is_audited() -> None:
    assembler, _, _ = _assembler(include_evidence=False)
    bundle = assembler.assemble(
        ReasoningQuery("garantía", as_of=NOW),
        now=NOW,
    )
    missing = [
        item for item in bundle.decisions if item.item_type == ContextItemType.EVIDENCE
    ]
    assert any(item.reason == "referenced evidence is unavailable" for item in missing)


def test_owner_filter_allows_shared_but_blocks_other_private_owner() -> None:
    assembler, _, _ = _assembler(owner="ana")
    bundle = assembler.assemble(
        ReasoningQuery("garantía", owner="carlos", as_of=NOW),
        now=NOW,
    )
    assert not bundle.claims
    assert any(item.reason == "owner outside query scope" for item in bundle.decisions)


def test_owner_filter_can_exclude_shared_items_by_policy() -> None:
    assembler, _, _ = _assembler(
        owner="shared",
        policy=ContextSelectionPolicy(include_shared_owner=False),
    )
    bundle = assembler.assemble(
        ReasoningQuery("garantía", owner="carlos", as_of=NOW),
        now=NOW,
    )
    assert not bundle.claims


def test_stale_superseded_and_refuted_claims_are_excluded() -> None:
    for status in (ClaimStatus.STALE, ClaimStatus.SUPERSEDED, ClaimStatus.REFUTED):
        assembler, claim, _ = _assembler(claim_status=status)
        bundle = assembler.assemble(ReasoningQuery("garantía", as_of=NOW), now=NOW)
        assert claim not in bundle.claims
        assert any(
            item.item_id == claim.claim_id and "claim status excluded" in item.reason
            for item in bundle.decisions
        )


def test_archived_superseded_and_cancelled_evidence_are_excluded() -> None:
    for status in (
        EvidenceStatus.ARCHIVED,
        EvidenceStatus.SUPERSEDED,
        EvidenceStatus.CANCELLED,
    ):
        assembler, _, evidence = _assembler(evidence_status=status)
        bundle = assembler.assemble(ReasoningQuery("garantía", as_of=NOW), now=NOW)
        assert evidence not in bundle.evidence


def test_future_and_expired_claims_are_excluded_at_query_time() -> None:
    future = _claim(valid_from=NOW + timedelta(days=1))
    expired = _claim(
        claim_id="expired",
        subject="garantía expirada",
        valid_until=NOW - timedelta(seconds=1),
    )
    registry = ClaimRegistryManager()
    registry.register(future)
    registry.register(expired)
    assembler = GovernedContextAssembler(
        claim_registry=registry,
        evidence_registry=_evidence_registry(_evidence()),
    )
    bundle = assembler.assemble(ReasoningQuery("garantía", as_of=NOW), now=NOW)
    assert not bundle.claims
    reasons = {item.reason for item in bundle.decisions}
    assert "claim is not yet valid" in reasons
    assert "claim is no longer valid" in reasons


def test_future_and_expired_evidence_are_excluded_at_query_time() -> None:
    future = _evidence(source_id="future", valid_from=NOW + timedelta(days=1))
    expired = _evidence(source_id="expired", valid_until=NOW - timedelta(seconds=1))
    assembler = GovernedContextAssembler(
        claim_registry=ClaimRegistryManager(),
        evidence_registry=_evidence_registry(future, expired),
    )
    bundle = assembler.assemble(ReasoningQuery("garantía", as_of=NOW), now=NOW)
    assert not bundle.evidence
    reasons = {item.reason for item in bundle.decisions}
    assert "evidence is not yet valid" in reasons
    assert "evidence is no longer valid" in reasons


def test_daily_briefing_is_excluded_by_default() -> None:
    briefing = _evidence(
        source_id="briefing-1",
        source_type=EvidenceSourceType.DAILY_BRIEFING,
        kind=EvidenceKind.SUMMARY,
    )
    assembler = GovernedContextAssembler(
        claim_registry=ClaimRegistryManager(),
        evidence_registry=_evidence_registry(briefing),
    )
    bundle = assembler.assemble(ReasoningQuery("briefing diario", as_of=NOW), now=NOW)
    assert not bundle.evidence
    assert any("derived briefing" in item.reason for item in bundle.decisions)


def test_daily_briefing_can_be_included_only_by_explicit_policy() -> None:
    briefing = _evidence(
        source_id="briefing-1",
        source_type=EvidenceSourceType.DAILY_BRIEFING,
        kind=EvidenceKind.SUMMARY,
        summary="briefing diario de tareas",
    )
    assembler = GovernedContextAssembler(
        claim_registry=ClaimRegistryManager(),
        evidence_registry=_evidence_registry(briefing),
        policy=ContextSelectionPolicy(include_derived_summaries=True),
    )
    bundle = assembler.assemble(ReasoningQuery("briefing diario", as_of=NOW), now=NOW)
    assert bundle.evidence == (briefing,)


def test_scope_guard_blocks_forbidden_query_before_selection() -> None:
    assembler, _, _ = _assembler()
    bundle = assembler.assemble(
        ReasoningQuery(
            "transferencia bancaria",
            domains=(ScopeDomain.BANKING,),
            as_of=NOW,
        ),
        now=NOW,
    )
    assert bundle.normalized_status is ContextAssemblyStatus.BLOCKED
    assert not bundle.claims and not bundle.evidence and not bundle.decisions


def test_review_scope_propagates_review_required_status() -> None:
    assembler, _, _ = _assembler()
    bundle = assembler.assemble(
        ReasoningQuery(
            "revisar diagnóstico y garantía",
            domains=(ScopeDomain.MEDICAL_DECISION,),
            as_of=NOW,
        ),
        now=NOW,
    )
    assert bundle.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED
    assert bundle.requires_human_review


def test_disputed_claim_propagates_review_required_status() -> None:
    assembler, _, _ = _assembler(claim_status=ClaimStatus.DISPUTED)
    bundle = assembler.assemble(ReasoningQuery("garantía", as_of=NOW), now=NOW)
    assert bundle.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED


def test_review_required_evidence_propagates_review_status() -> None:
    assembler, _, _ = _assembler(evidence_status=EvidenceStatus.REVIEW_REQUIRED)
    bundle = assembler.assemble(ReasoningQuery("garantía", as_of=NOW), now=NOW)
    assert bundle.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED


def test_empty_relevant_selection_is_insufficient_not_failure() -> None:
    assembler, _, _ = _assembler()
    bundle = assembler.assemble(ReasoningQuery("tema inexistente", as_of=NOW), now=NOW)
    assert bundle.normalized_status is ContextAssemblyStatus.INSUFFICIENT


def test_limits_keep_highest_relevance_and_audit_exclusions() -> None:
    registry = ClaimRegistryManager()
    evidence = _evidence()
    registry.register(_claim(claim_id="high", subject="garantía documento"))
    registry.register(_claim(claim_id="low", subject="garantía"))
    assembler = GovernedContextAssembler(
        claim_registry=registry,
        evidence_registry=_evidence_registry(evidence),
        policy=ContextSelectionPolicy(max_claims=1),
    )
    bundle = assembler.assemble(
        ReasoningQuery("garantía documento", as_of=NOW),
        now=NOW,
    )
    assert [claim.claim_id for claim in bundle.claims] == ["high"]
    assert any(item.reason == "claim limit reached" for item in bundle.decisions)


def test_input_order_does_not_change_context_fingerprint() -> None:
    evidence_a = _evidence(source_id="a", fingerprint=HASH_A)
    evidence_b = _evidence(source_id="b", fingerprint=HASH_B)
    claim_a = _claim(claim_id="a", evidence=evidence_a)
    claim_b = _claim(claim_id="b", evidence=evidence_b)
    first = _custom_assembler((claim_a, claim_b), (evidence_a, evidence_b))
    second = _custom_assembler((claim_b, claim_a), (evidence_b, evidence_a))
    query = ReasoningQuery("garantía", as_of=NOW)
    first_context = first.assemble(query, now=NOW)
    second_context = second.assemble(query, now=NOW)
    assert first_context.context_id == second_context.context_id


def test_created_at_does_not_change_semantic_context_fingerprint() -> None:
    assembler, _, _ = _assembler()
    query = ReasoningQuery("garantía", as_of=NOW)
    first = assembler.assemble(query, now=NOW)
    second = assembler.assemble(query, now=NOW + timedelta(minutes=1))
    assert first.context_id == second.context_id


def test_serialization_exposes_scope_selection_and_sources() -> None:
    assembler, claim, evidence = _assembler()
    bundle = assembler.assemble(ReasoningQuery("garantía", as_of=NOW), now=NOW)
    payload = bundle.to_dict()
    assert payload["status"] == "ready"
    assert payload["claims"][0]["id"] == claim.claim_id
    assert payload["evidence"][0]["id"] == evidence.evidence_id
    assert payload["scope_decision"]["status"] == "in_scope"
    assert payload["decisions"]


def _outcome(bundle, item_type: ContextItemType, item_id: str) -> str:
    for item in bundle.decisions:
        if item.normalized_item_type is item_type and item.item_id == item_id:
            return item.normalized_outcome.value
    raise AssertionError("selection decision not found")


def _decision(item_id: str):
    from core.governed_reasoning import ContextSelectionDecision

    return ContextSelectionDecision(
        ContextItemType.CLAIM,
        item_id,
        ContextDecisionOutcome.INCLUDED,
        "relevant",
        1,
    )


def _assembler(
    *,
    owner: str = "shared",
    claim_status: ClaimStatus = ClaimStatus.SUPPORTED,
    evidence_status: EvidenceStatus = EvidenceStatus.ACTIVE,
    include_claim: bool = True,
    include_evidence: bool = True,
    policy: ContextSelectionPolicy | None = None,
):
    evidence = _evidence(status=evidence_status, owner=owner)
    claim = _claim(status=claim_status, owner=owner, evidence=evidence)
    registry = ClaimRegistryManager()
    if include_claim:
        registry.register(claim)
    evidence_registry = _evidence_registry(*(evidence,) if include_evidence else ())
    assembler = GovernedContextAssembler(
        claim_registry=registry,
        evidence_registry=evidence_registry,
        policy=policy,
    )
    return assembler, claim, evidence


def _custom_assembler(claims, evidence):
    registry = ClaimRegistryManager()
    for claim in claims:
        registry.register(claim)
    return GovernedContextAssembler(
        claim_registry=registry,
        evidence_registry=_evidence_registry(*evidence),
    )


def _claim(
    *,
    claim_id: str = "claim-1",
    subject: str = "garantía",
    status: ClaimStatus = ClaimStatus.SUPPORTED,
    owner: str = "shared",
    evidence: EvidenceReference | None = None,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
) -> Claim:
    reference = evidence or _evidence(owner=owner)
    return Claim(
        subject=subject,
        predicate="vence_el",
        object_value="2026-08-15",
        claim_type=ClaimType.FACT,
        origin=ClaimOrigin.EVIDENCE,
        status=status,
        evidence_links=(ClaimEvidenceLink.from_reference(reference),),
        owner=owner,
        valid_from=valid_from,
        valid_until=valid_until,
        created_at=NOW,
        claim_id=claim_id,
    )


def _evidence(
    *,
    source_id: str = "doc-1",
    fingerprint: str = HASH_A,
    source_type: EvidenceSourceType = EvidenceSourceType.DOCUMENT,
    kind: EvidenceKind = EvidenceKind.DOCUMENT,
    status: EvidenceStatus = EvidenceStatus.ACTIVE,
    owner: str = "shared",
    summary: str = "Documento de garantía con vencimiento",
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
) -> EvidenceReference:
    return EvidenceReference(
        source_type=source_type,
        source_id=source_id,
        kind=kind,
        owner=owner,
        status=status,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=NOW,
        valid_from=valid_from,
        valid_until=valid_until,
        fingerprint=fingerprint,
        summary=summary,
    )


def _evidence_registry(*references: EvidenceReference) -> EvidenceRegistry:
    registry = EvidenceRegistry()
    registry._references = {item.evidence_id: item for item in references}
    return registry
