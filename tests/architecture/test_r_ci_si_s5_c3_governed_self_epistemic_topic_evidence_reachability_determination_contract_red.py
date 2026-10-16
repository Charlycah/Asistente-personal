from __future__ import annotations

from dataclasses import fields
from importlib import import_module

import pytest

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
)

MODULE = "app.governed_self_epistemic_topic_evidence_reachability_determination"
C2_MODULE = "app.governed_self_epistemic_need_curiosity_evidence_projection"
C2_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_c2_governed_self_epistemic_need_curiosity_"
    "evidence_projection_contract_red"
)


def _contract():
    return import_module(MODULE)


def _c2_projection():
    c2 = import_module(C2_MODULE)
    fixtures = import_module(C2_TEST_MODULE)
    need = fixtures._c1_determination()
    return c2.GovernedSelfEpistemicNeedCuriosityEvidenceProjectionV1().project(need)


def _determine(contract, projection):
    owner = contract.GovernedSelfEpistemicTopicEvidenceReachabilityDeterminationV1()
    return owner.determine(projection)


def test_r1_requires_actual_c2_and_preserves_exact_upstream_anchors() -> None:
    contract = _contract()
    projection = _c2_projection()

    result = _determine(contract, projection)

    assert result.curiosity_evidence_projection is projection
    assert result.need_to_ask_determination is projection.need_to_ask_determination
    assert result.route_determination is projection.route_determination
    assert result.evidence is projection.evidence
    assert result.selection is projection.selection
    assert result.authorization_report is projection.authorization_report
    with pytest.raises(TypeError):
        _determine(contract, projection.need_to_ask_determination)
    with pytest.raises(TypeError):
        _determine(contract, object())


def test_r2_preserves_self_epistemic_lineage_and_unknown_relevance() -> None:
    contract = _contract()
    projection = _c2_projection()

    result = _determine(contract, projection)

    assert result.capability_name == projection.capability_name
    assert result.source_reference == projection.source_reference
    assert result.world_snapshot_id == projection.world_snapshot_id
    assert result.requirement_identity == projection.requirement_identity
    assert result.need_status is projection.need_status
    assert result.route_status is projection.route_status
    assert result.evidence.relevance is EpistemicCuriosityRelevance.UNKNOWN
    assert result.relevance_determined is False


def test_r3_reports_only_no_compatible_governed_topic_evidence_route() -> None:
    contract = _contract()
    result = _determine(contract, _c2_projection())

    assert result.status is (
        contract.GovernedSelfEpistemicTopicEvidenceReachabilityStatus
        .NO_COMPATIBLE_GOVERNED_TOPIC_EVIDENCE_ROUTE
    )
    assert result.compatible_topic_evidence is None
    assert result.topic_evidence_reference is None
    assert result.interest_topics == frozenset()
    assert result.topic_evidence_reachable is False
    assert "topic_evidence:no_compatible_governed_route_proven" in (
        result.rationale_codes
    )


def test_r4_does_not_infer_topic_correspondence_from_c2_content() -> None:
    contract = _contract()
    owner = contract.GovernedSelfEpistemicTopicEvidenceReachabilityDeterminationV1()

    prohibited_flags = (
        "infers_topics_from_capability_name",
        "infers_topics_from_source_reference",
        "infers_topics_from_requirement_identity",
        "infers_topics_from_subject",
        "infers_topics_from_unknown_element",
        "infers_topics_from_evidence_codes",
        "uses_tags_as_topic_evidence",
        "uses_fuzzy_matching",
        "uses_semantic_matching",
        "uses_llm",
        "uses_retrieval",
    )
    for flag in prohibited_flags:
        assert getattr(owner, flag) is False


def test_r5_does_not_discover_or_fabricate_governed_topic_evidence() -> None:
    contract = _contract()
    owner = contract.GovernedSelfEpistemicTopicEvidenceReachabilityDeterminationV1()
    result = owner.determine(_c2_projection())

    assert result.compatible_topic_evidence is None
    inert_flags = (
        "queries_information_source_registry",
        "queries_capability_registry",
        "uses_dynamic_route_discovery",
        "creates_governed_information_item",
        "creates_interest_topics",
        "acquires_topic_evidence",
        "selects_information_source",
        "maintains_topic_route_table",
        "fabricates_fallback_route",
    )
    for flag in inert_flags:
        assert getattr(owner, flag) is False


def test_r6_does_not_cross_into_existing_relevance_or_curiosity_owners() -> None:
    contract = _contract()
    owner = contract.GovernedSelfEpistemicTopicEvidenceReachabilityDeterminationV1()
    result = owner.determine(_c2_projection())

    assert result.relevance_determined is False
    assert result.question_worthiness_determined is False
    assert result.question_candidate is None
    assert result.ask_now is False
    for flag in (
        "creates_relevance_candidate",
        "invokes_relevance",
        "assigns_relevance",
        "invokes_curiosity",
        "creates_questions",
        "invokes_initiative",
        "invokes_conversation",
        "asks_human",
    ):
        assert getattr(owner, flag) is False


def test_r7_determination_is_deterministic_explicit_and_read_only() -> None:
    contract = _contract()
    projection = _c2_projection()
    owner = contract.GovernedSelfEpistemicTopicEvidenceReachabilityDeterminationV1()

    first = owner.determine(projection)
    second = owner.determine(projection)

    assert first.status is second.status
    assert first.rationale_codes == second.rationale_codes
    assert first.read_only is True
    assert first.derivational is True
    result_fields = {
        item.name
        for item in fields(
            contract.GovernedSelfEpistemicTopicEvidenceReachabilityDetermination
        )
    }
    assert "question" not in result_fields


def test_r8_stops_before_relevance_curiosity_initiative_and_conversation() -> None:
    contract = _contract()
    owner = contract.GovernedSelfEpistemicTopicEvidenceReachabilityDeterminationV1()

    inert_flags = (
        "selects_capability",
        "reselects_epistemic_path",
        "reruns_authorization",
        "plans_acquisition",
        "acquires_evidence",
        "executes_actions",
        "persists_results",
        "creates_learning_candidate",
        "modifies_memory",
        "modifies_world_model",
        "creates_cognitive_authority",
        "creates_relevance_authority",
        "creates_curiosity_authority",
        "creates_initiative_authority",
        "creates_conversation_authority",
    )
    for flag in inert_flags:
        assert getattr(owner, flag) is False
