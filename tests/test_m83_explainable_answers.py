from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.governed_reasoning import (
    CitationKind,
    DecisionClaimLink,
    DecisionEvidenceLink,
    DecisionOutcome,
    DecisionRecord,
    DecisionRuleLink,
    DecisionStatus,
    ExplainableAnswer,
    ExplainableAnswerRenderer,
    ExplanationLevel,
    ExplanationRequest,
    ExplanationSection,
    ExplanationSectionType,
    ReviewEvent,
    ReviewStatus,
    SourceCitation,
)

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def _record(
    *,
    status: DecisionStatus = DecisionStatus.COMPLETED,
    outcome: DecisionOutcome = DecisionOutcome.CONCLUSION,
    confidence: float = 0.82,
    conflicts: tuple[str, ...] = (),
    review_status: ReviewStatus = ReviewStatus.NOT_REQUIRED,
    review_events: tuple[ReviewEvent, ...] = (),
    evidence: bool = True,
    claims: bool = True,
    rules: bool = True,
    limitations: tuple[str, ...] = ("source may become stale",),
    assumptions: tuple[str, ...] = ("same owner",),
) -> DecisionRecord:
    return DecisionRecord(
        query_id="query-1",
        query_text="Is the task overdue?",
        context_id="context-1",
        scope_status="allowed",
        status=status,
        outcome=outcome,
        conclusion="The task is overdue.",
        confidence_score=confidence,
        confidence_rationale="consistent evidence with limited uncertainty",
        evidence_links=(DecisionEvidenceLink("evidence-1", "a" * 64),)
        if evidence
        else (),
        claim_links=(DecisionClaimLink("claim-1", 2),) if claims else (),
        rule_links=(DecisionRuleLink("task.overdue", "1.0.0"),) if rules else (),
        conflict_ids=conflicts,
        limitations=limitations,
        assumptions=assumptions,
        review_status=review_status,
        review_events=review_events,
        created_at=NOW,
    )


def test_source_citation_validation_and_label() -> None:
    with pytest.raises(ValueError):
        SourceCitation(CitationKind.EVIDENCE, "")
    citation = SourceCitation("claim", "claim-1", "revision:2")
    assert citation.normalized_kind is CitationKind.CLAIM
    assert citation.label == "claim:claim-1 (revision:2)"


def test_section_requires_content() -> None:
    with pytest.raises(ValueError):
        ExplanationSection(ExplanationSectionType.CONCLUSION, "Conclusion", ())


def test_section_sorts_citations_deterministically() -> None:
    section = ExplanationSection(
        ExplanationSectionType.SOURCES,
        "Sources",
        ("Used sources.",),
        (
            SourceCitation(CitationKind.RULE, "z"),
            SourceCitation(CitationKind.EVIDENCE, "a"),
        ),
    )
    assert [item.normalized_kind for item in section.citations] == [
        CitationKind.EVIDENCE,
        CitationKind.RULE,
    ]


def test_answer_is_immutable_and_has_stable_id() -> None:
    answer = ExplainableAnswerRenderer().render(_record())
    duplicate = ExplainableAnswerRenderer().render(_record())
    assert answer.answer_id == duplicate.answer_id
    with pytest.raises(FrozenInstanceError):
        answer.summary = "changed"  # type: ignore[misc]


def test_answer_rejects_duplicate_section_types() -> None:
    section = ExplanationSection(
        ExplanationSectionType.CONCLUSION,
        "Conclusion",
        ("A",),
    )
    with pytest.raises(ValueError):
        ExplainableAnswer(
            "decision",
            ExplanationLevel.STANDARD,
            DecisionStatus.COMPLETED,
            DecisionOutcome.CONCLUSION,
            "Title",
            "Summary",
            "high",
            (section, section),
            False,
        )


def test_request_validates_citation_limit() -> None:
    with pytest.raises(ValueError):
        ExplanationRequest(_record(), max_citations=0)


def test_concise_answer_contains_conclusion_and_main_sources() -> None:
    answer = ExplainableAnswerRenderer().render(
        _record(), level=ExplanationLevel.CONCISE
    )
    assert answer.normalized_level is ExplanationLevel.CONCISE
    assert [section.normalized_type for section in answer.sections] == [
        ExplanationSectionType.CONCLUSION,
        ExplanationSectionType.SOURCES,
    ]


def test_standard_answer_separates_facts_inferences_and_limits() -> None:
    answer = ExplainableAnswerRenderer().render(_record())
    types = {section.normalized_type for section in answer.sections}
    assert ExplanationSectionType.FACTUAL_BASIS in types
    assert ExplanationSectionType.INFERENCES in types
    assert ExplanationSectionType.UNCERTAINTY in types
    assert ExplanationSectionType.LIMITS in types


def test_standard_answer_does_not_include_audit_section() -> None:
    answer = ExplainableAnswerRenderer().render(_record())
    assert ExplanationSectionType.AUDIT not in {
        item.normalized_type for item in answer.sections
    }


def test_audit_answer_includes_record_identifiers() -> None:
    answer = ExplainableAnswerRenderer().render(_record(), level=ExplanationLevel.AUDIT)
    audit = next(
        item
        for item in answer.sections
        if item.normalized_type is ExplanationSectionType.AUDIT
    )
    assert any("Decision id:" in item for item in audit.content)
    assert any("Context id: context-1" == item for item in audit.content)


def test_rule_based_result_is_explicitly_marked_as_inference() -> None:
    answer = ExplainableAnswerRenderer().render(_record())
    inference = next(
        item
        for item in answer.sections
        if item.normalized_type is ExplanationSectionType.INFERENCES
    )
    assert "remain distinct from confirmed facts" in inference.content[1]
    assert inference.citations[0].normalized_kind is CitationKind.RULE


def test_answer_without_rules_omits_inference_section() -> None:
    answer = ExplainableAnswerRenderer().render(_record(rules=False))
    assert ExplanationSectionType.INFERENCES not in {
        item.normalized_type for item in answer.sections
    }


def test_answer_without_sources_states_absence() -> None:
    answer = ExplainableAnswerRenderer().render(
        _record(evidence=False, claims=False, rules=False)
    )
    basis = next(
        item
        for item in answer.sections
        if item.normalized_type is ExplanationSectionType.FACTUAL_BASIS
    )
    assert "No factual source reference was available." in basis.content


def test_conflicts_are_visible_and_cited() -> None:
    answer = ExplainableAnswerRenderer().render(_record(conflicts=("conflict-1",)))
    uncertainty = next(
        item
        for item in answer.sections
        if item.normalized_type is ExplanationSectionType.UNCERTAINTY
    )
    assert any("1 conflict" in item for item in uncertainty.content)
    assert uncertainty.citations == (
        SourceCitation(CitationKind.CONFLICT, "conflict-1"),
    )


def test_abstention_is_not_rendered_as_conclusion() -> None:
    answer = ExplainableAnswerRenderer().render(
        _record(
            status=DecisionStatus.INCONCLUSIVE,
            outcome=DecisionOutcome.ABSTENTION,
            rules=False,
        )
    )
    assert answer.title == "Governed abstention"
    assert "did not have enough" in answer.summary


def test_blocked_decision_explains_governance_boundary() -> None:
    answer = ExplainableAnswerRenderer().render(
        _record(
            status=DecisionStatus.BLOCKED,
            outcome=DecisionOutcome.BLOCKED,
            rules=False,
        )
    )
    assert answer.title == "Governed block"
    assert any(
        "governance boundaries" in line
        for section in answer.sections
        for line in section.content
    )


def test_pending_review_is_explicit() -> None:
    answer = ExplainableAnswerRenderer().render(
        _record(
            status=DecisionStatus.REVIEW_REQUIRED,
            outcome=DecisionOutcome.HUMAN_REVIEW,
            review_status=ReviewStatus.PENDING,
        )
    )
    assert answer.requires_human_review
    assert answer.title == "Human review required"
    assert ExplanationSectionType.REVIEW in {
        item.normalized_type for item in answer.sections
    }


def test_completed_review_event_is_rendered() -> None:
    event = ReviewEvent("human", ReviewStatus.APPROVED, "verified", NOW)
    answer = ExplainableAnswerRenderer().render(
        _record(
            review_status=ReviewStatus.APPROVED,
            review_events=(event,),
        )
    )
    review = next(
        item
        for item in answer.sections
        if item.normalized_type is ExplanationSectionType.REVIEW
    )
    assert any("human: approved" in item for item in review.content)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.10, "insufficient"),
        (0.30, "low"),
        (0.60, "moderate"),
        (0.80, "high"),
        (0.95, "very high"),
    ],
)
def test_confidence_bands(score: float, expected: str) -> None:
    answer = ExplainableAnswerRenderer().render(_record(confidence=score))
    assert answer.confidence_label.startswith(expected)


def test_citation_limit_is_respected() -> None:
    answer = ExplainableAnswerRenderer().render(
        _record(),
        level=ExplanationLevel.AUDIT,
        max_citations=1,
    )
    audit = next(
        item
        for item in answer.sections
        if item.normalized_type is ExplanationSectionType.AUDIT
    )
    assert len(audit.citations) == 1


def test_answer_citations_are_deduplicated() -> None:
    answer = ExplainableAnswerRenderer().render(_record(), level=ExplanationLevel.AUDIT)
    keys = [
        (item.normalized_kind, item.reference_id, item.qualifier)
        for item in answer.citations
    ]
    assert len(keys) == len(set(keys))


def test_to_dict_is_public_and_structured() -> None:
    payload = ExplainableAnswerRenderer().render(_record()).to_dict()
    assert payload["decision_id"] == _record().decision_id
    assert payload["outcome"] == "conclusion"
    assert isinstance(payload["sections"], list)


def test_render_text_contains_public_sections_and_references() -> None:
    text = ExplainableAnswerRenderer().render(_record()).render_text()
    assert "Governed conclusion" in text
    assert "Factual basis" in text
    assert "References:" in text


def test_renderer_supports_concise_explanations() -> None:
    answer = ExplainableAnswerRenderer().render(
        _record(), level=ExplanationLevel.CONCISE
    )
    assert answer.normalized_level is ExplanationLevel.CONCISE


def test_rendering_is_independent_of_input_link_order() -> None:
    first = _record()
    second = DecisionRecord(
        query_id=first.query_id,
        query_text=first.query_text,
        context_id=first.context_id,
        scope_status=first.scope_status,
        status=first.status,
        outcome=first.outcome,
        conclusion=first.conclusion,
        confidence_score=first.confidence_score,
        confidence_rationale=first.confidence_rationale,
        evidence_links=tuple(reversed(first.evidence_links)),
        claim_links=tuple(reversed(first.claim_links)),
        rule_links=tuple(reversed(first.rule_links)),
        conflict_ids=tuple(reversed(first.conflict_ids)),
        limitations=tuple(reversed(first.limitations)),
        assumptions=tuple(reversed(first.assumptions)),
        review_status=first.review_status,
        created_at=first.created_at,
    )
    renderer = ExplainableAnswerRenderer()
    assert renderer.render(first).answer_id == renderer.render(second).answer_id
