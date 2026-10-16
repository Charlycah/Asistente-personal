from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.cognitive_memory import LearningCategory
from core.cognitive_memory_recall import (
    CognitiveMemoryRecallItem,
    CognitiveMemoryRecallResult,
)
from core.cognitive_memory_store import CognitiveMemoryRecord
from core.governed_reasoning import (
    Claim,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    ContextAssemblyStatus,
    GovernedInferenceEngine,
    GovernedRecalledKnowledgeStructuralProjector,
    GovernedStructuralKnowledgeTransferMatcher,
    GovernedTargetProblemStructuralProjector,
    GovernedTransferAdmissionGuard,
    GovernedTransferInstantiator,
    InferenceStatus,
    InMemoryInferenceRuleRegistry,
    ReasoningContextBundle,
    ReasoningQuery,
    TransferAdmissionGuardStatus,
    TransferInstantiationStatus,
)
from core.scope_guard import ScopeDomain, ScopeGuardManager

NOW = datetime(2026, 8, 19, 16, 30, tzinfo=timezone.utc)
SCOPE = "rc-1-4-transfer-admission"
RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
TARGET = (
    "La misión orbital depende exclusivamente de la ventana de lanzamiento para "
    "ejecutar una maniobra. La ventana de lanzamiento queda indisponible y no "
    "existe alternativa."
)


def _memory() -> CognitiveMemoryRecord:
    return CognitiveMemoryRecord(
        id=1,
        content=RULE,
        category=LearningCategory.STABLE_KNOWLEDGE,
        confidence=0.91,
        reason="stable structural rule",
        tags=("deep_reasoning",),
        metadata={"source": "rc-1.4-test"},
        created_at="2026-08-19T16:00:00+00:00",
    )


def _package():
    recall = CognitiveMemoryRecallResult(
        should_use_memory=True,
        items=(
            CognitiveMemoryRecallItem(
                memory=_memory(),
                score=0.84,
                matched_signals=("deep_reasoning",),
            ),
        ),
        reason="relevant_memory_found",
    )
    source_projection = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=recall,
        scope_reference=SCOPE,
    )
    source = source_projection.items[0]
    target = GovernedTargetProblemStructuralProjector().project(
        text=TARGET,
        source_reference="conversation:rc-1.4/target",
        scope_reference=SCOPE,
    )
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(source.grounding,),
        scope_reference=SCOPE,
    )
    return GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference=SCOPE,
    )


def _admit(registry: InMemoryInferenceRuleRegistry):
    return GovernedTransferAdmissionGuard().admit(
        package=_package(),
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.KNOWLEDGE,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )


def test_valid_transfer_delegates_to_canonical_admission_boundary() -> None:
    registry = InMemoryInferenceRuleRegistry()
    result = _admit(registry)

    assert (
        result.normalized_status
        is TransferAdmissionGuardStatus.ADMITTED_FOR_REVIEW
    )
    assert result.canonical_admission is not None
    assert len(registry.list()) == 1
    assert registry.list()[0] == result.canonical_admission.rule


def test_admitted_transfer_is_temporary_and_review_required() -> None:
    result = _admit(InMemoryInferenceRuleRegistry())
    assert result.canonical_admission is not None

    rule = result.canonical_admission.rule
    assert rule.temporary is True
    assert rule.requires_review is True
    assert rule.scope_reference == SCOPE
    assert rule.valid_from == NOW
    assert rule.valid_until == NOW + timedelta(minutes=30)


def test_admission_result_preserves_complete_transfer_lineage() -> None:
    package = _package()
    registry = InMemoryInferenceRuleRegistry()
    result = GovernedTransferAdmissionGuard().admit(
        package=package,
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.KNOWLEDGE,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )

    assert result.transfer_package_fingerprint == package.source_fingerprint
    assert result.source_memory_id == package.source_memory_id
    assert (
        result.source_memory_content_fingerprint
        == package.source_memory_content_fingerprint
    )
    assert result.source_grounding_fingerprint == package.source_grounding_fingerprint
    assert (
        result.source_compilation_fingerprint
        == package.source_compilation_fingerprint
    )
    assert (
        result.transfer_candidate_fingerprint
        == package.transfer_candidate_fingerprint
    )
    assert (
        result.target_projection_fingerprint
        == package.target_projection_fingerprint
    )
    assert package.instantiated_candidate is not None
    assert (
        result.instantiated_candidate_fingerprint
        == package.instantiated_candidate.source_fingerprint
    )


def test_non_instantiated_transfer_is_rejected_without_registry_mutation() -> None:
    package = _package()
    invalid = replace(
        package,
        status=TransferInstantiationStatus.NO_TRANSFER,
        bindings=(),
        instantiated_candidate=None,
    )
    registry = InMemoryInferenceRuleRegistry()

    result = GovernedTransferAdmissionGuard().admit(
        package=invalid,
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.KNOWLEDGE,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )

    assert (
        result.normalized_status
        is TransferAdmissionGuardStatus.NOT_TRANSFER_INSTANTIATED
    )
    assert result.canonical_admission is None
    assert registry.list() == ()


def test_tampered_package_fingerprint_is_rejected_without_registry_mutation() -> None:
    package = replace(_package(), source_fingerprint="a" * 64)
    registry = InMemoryInferenceRuleRegistry()

    result = GovernedTransferAdmissionGuard().admit(
        package=package,
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.KNOWLEDGE,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )

    assert (
        result.normalized_status
        is TransferAdmissionGuardStatus.PROVENANCE_MISMATCH
    )
    assert result.canonical_admission is None
    assert registry.list() == ()


def test_tampered_target_fingerprint_is_rejected_without_registry_mutation() -> None:
    package = replace(_package(), target_projection_fingerprint="b" * 64)
    registry = InMemoryInferenceRuleRegistry()

    result = GovernedTransferAdmissionGuard().admit(
        package=package,
        registry=registry,
        scope_reference=SCOPE,
        allowed_domains=(ScopeDomain.KNOWLEDGE,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )

    assert (
        result.normalized_status
        is TransferAdmissionGuardStatus.PROVENANCE_MISMATCH
    )
    assert registry.list() == ()


def test_scope_mismatch_is_rejected_without_registry_mutation() -> None:
    registry = InMemoryInferenceRuleRegistry()
    result = GovernedTransferAdmissionGuard().admit(
        package=_package(),
        registry=registry,
        scope_reference="rc-1-4-other",
        allowed_domains=(ScopeDomain.KNOWLEDGE,),
        admitted_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )

    assert result.normalized_status is TransferAdmissionGuardStatus.SCOPE_MISMATCH
    assert result.canonical_admission is None
    assert registry.list() == ()


def test_invalid_temporality_is_still_rejected_by_canonical_boundary() -> None:
    registry = InMemoryInferenceRuleRegistry()

    with pytest.raises(ValueError, match="expire after admission"):
        GovernedTransferAdmissionGuard().admit(
            package=_package(),
            registry=registry,
            scope_reference=SCOPE,
            allowed_domains=(ScopeDomain.KNOWLEDGE,),
            admitted_at=NOW,
            expires_at=NOW,
        )
    assert registry.list() == ()


def test_admitted_transfer_inference_remains_review_required() -> None:
    registry = InMemoryInferenceRuleRegistry()
    admission = _admit(registry)
    assert admission.canonical_admission is not None
    rule = admission.canonical_admission.rule

    claims = tuple(
        _claim(
            f"condition-{index}",
            condition.subject or "",
            condition.predicate,
            condition.values[0],
        )
        for index, condition in enumerate(rule.conditions, start=1)
    )
    query = ReasoningQuery(
        "apply transferred knowledge under review",
        domains=(ScopeDomain.KNOWLEDGE,),
        as_of=NOW + timedelta(minutes=1),
    )
    scope = (
        ScopeGuardManager()
        .observe_turn(
            "apply transferred knowledge under review",
            proposed_domains=(ScopeDomain.KNOWLEDGE,),
            now=NOW,
        )
        .decision
    )
    context = ReasoningContextBundle(
        query=query,
        status=ContextAssemblyStatus.READY,
        scope_decision=scope,
        claims=claims,
        evidence=(),
        decisions=(),
        created_at=NOW,
    )

    result = GovernedInferenceEngine(registry).infer(
        context,
        now=NOW + timedelta(minutes=1),
        scope_reference=SCOPE,
    ).results[0]

    assert result.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert result.output_claim is not None
    assert result.output_claim.normalized_status is ClaimStatus.REVIEW_REQUIRED
    assert result.output_claim.normalized_type is ClaimType.RULE_RESULT


def test_transfer_admission_does_not_gain_memory_learning_or_action_authority() -> None:
    result = _admit(InMemoryInferenceRuleRegistry())

    assert result.canonical_authority == "governed_reasoning"
    assert result.session_local is True
    for name in (
        "persistent",
        "creates_memory",
        "modifies_memory",
        "creates_learning_candidate",
        "modifies_learning",
        "modifies_world_model",
        "establishes_truth",
        "authorizes_inference",
        "executes_actions",
        "grants_authority",
        "uses_provider",
        "uses_retrieval",
    ):
        assert getattr(result, name) is False


def test_transfer_admission_result_is_immutable() -> None:
    result = _admit(InMemoryInferenceRuleRegistry())
    with pytest.raises(FrozenInstanceError):
        result.scope_reference = "changed"  # type: ignore[misc]


def _claim(claim_id: str, subject: str, predicate: str, value: str) -> Claim:
    return Claim(
        subject=subject,
        predicate=predicate,
        object_value=value,
        claim_type=ClaimType.HYPOTHESIS,
        origin=ClaimOrigin.HUMAN,
        status=ClaimStatus.PROPOSED,
        owner="shared",
        created_at=NOW,
        claim_id=claim_id,
    )
