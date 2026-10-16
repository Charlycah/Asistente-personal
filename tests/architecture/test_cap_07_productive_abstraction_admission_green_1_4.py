from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    GovernedBoundedSemanticRoleRelationGrounder,
)
from core.governed_reasoning.productive_abstraction_admission import (
    GovernedProductiveAbstractionAdmission,
    ProductiveAbstractionAdmissionStatus,
)
from core.governed_reasoning.relational_abstraction import RelationalAbstractionStatus

SCOPE = "session:cap-07-green"
SESSION = "session:cap-07-green"
PRODUCER = GovernedContextualRuleInterpretationProducer()
GROUNDER = GovernedBoundedSemanticRoleRelationGrounder()


def _ground(source: str, text: str, *, scope: str = SCOPE):
    candidate = PRODUCER.produce(
        text,
        source_reference=source,
        scope_reference=scope,
    )
    return GROUNDER.ground(candidate, scope_reference=scope)


def _dependency_rule(subject: str, resource: str, capability: str) -> str:
    return (
        f"Regla temporal: si el sistema {subject} depende exclusivamente de un recurso "
        f"{resource} para una función {capability} y ese recurso queda "
        "indisponible y no hay alternativa, "
        "entonces ese sistema pierde esa capacidad."
    )


def test_green_1_contracts_are_frozen_and_preserve_governed_limits() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    first = admission.observe(
        _ground("conversation:cap07/1", _dependency_rule("A", "B", "C")),
        session_id=SESSION,
        turn_id="turn-1",
        scope_reference=SCOPE,
    )

    assert first.status is ProductiveAbstractionAdmissionStatus.INSUFFICIENT_EVIDENCE
    assert first.canonical_authority == "governed_reasoning"
    assert first.read_only is True
    assert first.session_local is True
    assert first.persists is False
    assert first.creates_memory is False
    assert first.creates_learning is False
    assert first.executes_transfer is False
    assert first.grants_authority is False
    with pytest.raises(FrozenInstanceError):
        first.status = (  # type: ignore[misc]
            ProductiveAbstractionAdmissionStatus.ADMITTED
        )


def test_green_2_certified_grounding_normalizes_without_reinterpreting_text() -> None:
    grounding = _ground(
        "conversation:cap07/2",
        _dependency_rule("una app", "un servicio", "una función"),
    )
    evidence = GovernedProductiveAbstractionAdmission.normalize_grounding(
        grounding,
        scope_reference=SCOPE,
    )

    assert evidence is not None
    assert evidence.example.relation == "required_for"
    assert evidence.example.outcome == "blocked_when_unavailable"
    assert evidence.example.source_fingerprint == grounding.source_fingerprint
    assert evidence.grounding_fingerprint == grounding.source_fingerprint


def test_green_2_non_grounded_or_scope_mismatch_fails_closed() -> None:
    unsupported = _ground("conversation:cap07/3", "Si llueve, entonces Juan sale.")
    assert (
        GovernedProductiveAbstractionAdmission.normalize_grounding(
            unsupported,
            scope_reference=SCOPE,
        )
        is None
    )

    grounding = _ground(
        "conversation:cap07/4",
        _dependency_rule("A", "B", "C"),
    )
    with pytest.raises(ValueError, match="scope mismatch"):
        GovernedProductiveAbstractionAdmission.normalize_grounding(
            grounding,
            scope_reference="session:other",
        )


def test_green_3_duplicate_evidence_does_not_inflate_support() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    grounding = _ground(
        "conversation:cap07/5",
        _dependency_rule("A", "B", "C"),
    )
    one = admission.observe(
        grounding,
        session_id=SESSION,
        turn_id="turn-1",
        scope_reference=SCOPE,
    )
    duplicate = admission.observe(
        grounding,
        session_id=SESSION,
        turn_id="turn-2",
        scope_reference=SCOPE,
    )

    assert one.admitted_support == 1
    assert duplicate.status is ProductiveAbstractionAdmissionStatus.DUPLICATE
    assert duplicate.admitted_support == 1


def test_green_3_scope_and_session_accumulators_are_isolated() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    scope_a = "scope:a"
    scope_b = "scope:b"
    one = admission.observe(
        _ground("conversation:cap07/6", _dependency_rule("A", "B", "C"), scope=scope_a),
        session_id="session:a",
        turn_id="turn-1",
        scope_reference=scope_a,
    )
    two = admission.observe(
        _ground("conversation:cap07/7", _dependency_rule("D", "E", "F"), scope=scope_b),
        session_id="session:a",
        turn_id="turn-2",
        scope_reference=scope_b,
    )
    three = admission.observe(
        _ground("conversation:cap07/8", _dependency_rule("G", "H", "I"), scope=scope_a),
        session_id="session:b",
        turn_id="turn-3",
        scope_reference=scope_a,
    )

    assert one.admitted_support == 1
    assert two.admitted_support == 1
    assert three.admitted_support == 1
    assert all(
        result.status is ProductiveAbstractionAdmissionStatus.INSUFFICIENT_EVIDENCE
        for result in (one, two, three)
    )


def test_green_3_accumulator_is_bounded_and_fails_closed() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    admission.MAX_ITEMS_PER_SCOPE = 2
    one = admission.observe(
        _ground("conversation:cap07/9", _dependency_rule("A", "B", "C")),
        session_id=SESSION,
        turn_id="turn-1",
        scope_reference=SCOPE,
        counterexample=True,
    )
    two = admission.observe(
        _ground("conversation:cap07/10", _dependency_rule("D", "E", "F")),
        session_id=SESSION,
        turn_id="turn-2",
        scope_reference=SCOPE,
        counterexample=True,
    )
    three = admission.observe(
        _ground("conversation:cap07/11", _dependency_rule("G", "H", "I")),
        session_id=SESSION,
        turn_id="turn-3",
        scope_reference=SCOPE,
        counterexample=True,
    )

    assert one.admitted_counterexamples == 1
    assert two.admitted_counterexamples == 2
    assert three.status is ProductiveAbstractionAdmissionStatus.ABSTAIN
    assert three.admitted_counterexamples == 2


def test_green_4_two_unique_supports_selectively_reuse_existing_inducer() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    first = admission.observe(
        _ground("conversation:cap07/12", _dependency_rule("A", "B", "C")),
        session_id=SESSION,
        turn_id="turn-1",
        scope_reference=SCOPE,
    )
    second = admission.observe(
        _ground("conversation:cap07/13", _dependency_rule("D", "E", "F")),
        session_id=SESSION,
        turn_id="turn-2",
        scope_reference=SCOPE,
    )

    assert first.status is ProductiveAbstractionAdmissionStatus.INSUFFICIENT_EVIDENCE
    assert second.status is ProductiveAbstractionAdmissionStatus.ABSTRACTION_AVAILABLE
    assert second.episode is not None
    candidate = second.episode.abstraction_candidate
    assert candidate.status is RelationalAbstractionStatus.REVIEW_REQUIRED
    assert candidate.invariant_relation == "required_for"
    assert candidate.invariant_outcome == "blocked_when_unavailable"
    assert len(candidate.supporting_example_ids) == 2
    assert second.episode.creates_memory is False
    assert second.episode.creates_learning is False
    assert second.episode.executes_transfer is False


def test_green_4_episode_identity_is_stable_for_same_evidence_set() -> None:
    groundings = (
        _ground("conversation:cap07/14", _dependency_rule("A", "B", "C")),
        _ground("conversation:cap07/15", _dependency_rule("D", "E", "F")),
    )
    forward = GovernedProductiveAbstractionAdmission()
    forward.observe(
        groundings[0],
        session_id=SESSION,
        turn_id="turn-a",
        scope_reference=SCOPE,
    )
    forward_result = forward.observe(
        groundings[1],
        session_id=SESSION,
        turn_id="turn-final",
        scope_reference=SCOPE,
    )

    reverse = GovernedProductiveAbstractionAdmission()
    reverse.observe(
        groundings[1],
        session_id=SESSION,
        turn_id="turn-b",
        scope_reference=SCOPE,
    )
    reverse_result = reverse.observe(
        groundings[0],
        session_id=SESSION,
        turn_id="turn-final",
        scope_reference=SCOPE,
    )

    assert forward_result.episode is not None
    assert reverse_result.episode is not None
    assert (
        forward_result.episode.abstraction_candidate.source_fingerprint
        == reverse_result.episode.abstraction_candidate.source_fingerprint
    )
    assert forward_result.episode.episode_id == reverse_result.episode.episode_id
