from __future__ import annotations

from dataclasses import fields
from importlib import import_module

import pytest

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)

MODULE = "app.governed_self_epistemic_need_curiosity_evidence_projection"
C1_MODULE = "app.governed_self_epistemic_need_to_ask"
B1_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c3_b1_governed_authorized_epistemic_"
    "acquisition_route_determination_contract_red"
)


def _contract():
    return import_module(MODULE)


def _c1_determination():
    c1 = import_module(C1_MODULE)
    fixtures = import_module(B1_TEST_MODULE)
    b1 = import_module(
        "app.governed_authorized_epistemic_acquisition_route_determination"
    )
    route = b1.GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1().determine(
        fixtures._a3_binding()
    )
    return c1.GovernedSelfEpistemicNeedToAskDeterminationV1().determine(route)


def _project(contract, need):
    owner = contract.GovernedSelfEpistemicNeedCuriosityEvidenceProjectionV1()
    return owner.project(need)


def test_r1_requires_actual_c1_and_preserves_upstream_anchor() -> None:
    contract = _contract()
    need = _c1_determination()

    result = _project(contract, need)

    assert result.need_to_ask_determination is need
    assert result.route_determination is need.route_determination
    assert result.selection is need.selection
    assert result.authorization_report is need.authorization_report
    with pytest.raises(TypeError):
        _project(contract, need.route_determination)
    with pytest.raises(TypeError):
        _project(contract, object())


def test_r2_projects_exact_existing_curiosity_evidence_contract() -> None:
    contract = _contract()
    need = _c1_determination()

    result = _project(contract, need)

    assert isinstance(result.evidence, MultisourceKnowledgeGapEvidence)
    assert result.evidence.source_kind is EpistemicCuriositySourceKind.REASONING
    assert result.evidence.source_reference == need.requirement_identity
    assert result.evidence.relevance is EpistemicCuriosityRelevance.UNKNOWN
    assert result.evidence.target_person is None
    assert result.evidence.hypothesis is None
    assert result.evidence.prior_question_reference is None


def test_r3_projection_preserves_explicit_self_epistemic_lineage() -> None:
    contract = _contract()
    need = _c1_determination()

    result = _project(contract, need)
    evidence = result.evidence

    assert result.capability_name == need.capability_name
    assert result.source_reference == need.source_reference
    assert result.world_snapshot_id == need.world_snapshot_id
    assert result.requirement_identity == need.requirement_identity
    assert result.need_status is need.status
    assert result.route_status is need.route_status
    requirement_code = f"requirement_identity:{need.requirement_identity}"
    assert requirement_code in evidence.evidence_codes
    assert f"world_snapshot:{need.world_snapshot_id}" in evidence.evidence_codes
    assert f"selected_capability:{need.capability_name}" in evidence.evidence_codes


def test_r4_need_to_ask_projects_gap_without_question_or_self_claim() -> None:
    contract = _contract()
    need = _c1_determination()

    result = _project(contract, need)
    evidence = result.evidence

    assert evidence.unknown_element is not None
    assert need.requirement_identity in evidence.known_elements
    assert need.world_snapshot_id in evidence.known_elements
    projected = " ".join(
        (evidence.subject, *evidence.known_elements, evidence.unknown_element)
    ).lower()
    for prohibited in ("i am conscious", "subjective experience", "real emotion"):
        assert prohibited not in projected
    result_fields = {
        item.name
        for item in fields(
            contract.GovernedSelfEpistemicNeedCuriosityEvidenceProjection
        )
    }
    assert "question" not in result_fields


def test_r5_unknown_relevance_fails_closed_before_question_candidate() -> None:
    contract = _contract()
    result = _project(contract, _c1_determination())

    curiosity = GovernedEpistemicCuriosityFoundation().evaluate(result.evidence)

    assert result.evidence.relevance is EpistemicCuriosityRelevance.UNKNOWN
    assert curiosity.question_candidate is None
    assert "relevance_not_yet_governed" in curiosity.rationale_codes
    assert result.relevance_determined is False
    assert result.question_worthiness_determined is False
    assert result.question_candidate is None


def test_r6_reuses_existing_contract_without_invoking_downstream_owners() -> None:
    contract = _contract()
    owner = contract.GovernedSelfEpistemicNeedCuriosityEvidenceProjectionV1()

    assert owner.target_contract == "MultisourceKnowledgeGapEvidence"
    inert_flags = (
        "invokes_relevance",
        "assigns_relevance",
        "invokes_curiosity",
        "creates_questions",
        "invokes_initiative",
        "invokes_conversation",
        "asks_human",
    )
    for flag in inert_flags:
        assert getattr(owner, flag) is False


def test_r7_projection_is_deterministic_explicit_and_heuristic_free() -> None:
    contract = _contract()
    need = _c1_determination()
    owner = contract.GovernedSelfEpistemicNeedCuriosityEvidenceProjectionV1()

    first = owner.project(need)
    second = owner.project(need)

    assert first.evidence == second.evidence
    assert first.rationale_codes == second.rationale_codes
    assert "projection:explicit_need_to_ask" in first.rationale_codes
    assert "projection:relevance_unknown" in first.rationale_codes
    assert owner.infers_from_text is False
    assert owner.uses_semantic_matching is False
    assert owner.uses_llm is False
    assert owner.uses_retrieval is False


def test_r8_stops_before_relevance_curiosity_initiative_and_conversation() -> None:
    contract = _contract()
    owner = contract.GovernedSelfEpistemicNeedCuriosityEvidenceProjectionV1()
    result = owner.project(_c1_determination())

    assert result.read_only is True
    assert result.derivational is True
    assert result.relevance_determined is False
    assert result.question_worthiness_determined is False
    assert result.question_candidate is None
    assert result.ask_now is False
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
