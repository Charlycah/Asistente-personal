from __future__ import annotations

from pathlib import Path

import pytest

from app.epistemic_gap_governed_topic_curiosity_runtime import (
    EpistemicGapGovernedTopicCuriosityRuntime,
    EpistemicGapTopicCuriosityStatus,
)
from app.governed_information_sources import (
    GovernedInformationItem,
    GovernedInformationSources,
)
from app.personal_interest_center import InterestTopic, PersonalInterestCenter
from app.relevance_evaluator import RelevanceEvaluator
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityOutcome,
)
from core.governed_reasoning.hypothesis_deepening import (
    HypothesisDeepeningSourceKind,
    HypothesisEpistemicGap,
)

ROOT = Path(__file__).resolve().parents[2]


class _ConversationGateway:
    def __init__(self) -> None:
        self.sources = GovernedInformationSources()
        self.relevance = RelevanceEvaluator(PersonalInterestCenter())
        self.submissions: list[dict[str, object]] = []

    def accept_information_item(self, item: GovernedInformationItem):
        return self.sources.accept(item)

    def evaluate_relevance(self, candidate):
        return self.relevance.evaluate(candidate)

    def submit(self, text: str, **kwargs):
        record = {"text": text, **kwargs}
        self.submissions.append(record)
        return record


def _gap(reference: str = "nasa:item-1") -> HypothesisEpistemicGap:
    return HypothesisEpistemicGap(
        gap_id="hypothesis-gap-1234567890abcdef",
        hypothesis_id="hypothesis-1",
        subject="propulsion hypothesis",
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-1",
        known_elements=(reference,),
        unknown_element="evidence that discriminates the propulsion hypothesis",
        evidence_codes=("explicit-gap",),
        hypothesis="the propulsion mechanism explains the observation",
        epistemic_level=EpistemicLevel.UNKNOWN,
    )


def _nasa_item() -> GovernedInformationItem:
    return GovernedInformationItem(
        source_id="nasa",
        external_id="item-1",
        title="NASA propulsion evidence",
        topics=frozenset({InterestTopic.SPACE_EXPLORATION}),
        importance=10,
    )


def test_explicit_governed_topic_evidence_reaches_existing_curiosity_submit() -> None:
    conversation = _ConversationGateway()
    runtime = EpistemicGapGovernedTopicCuriosityRuntime(conversation)

    result = runtime.admit(
        text="seguimos con la hipótesis",
        gap=_gap(),
        topic_evidence=_nasa_item(),
        evidence_reference="nasa:item-1",
        session_id="coowners-main",
    )

    assert result.status is EpistemicGapTopicCuriosityStatus.ADMITTED
    assert result.curiosity_report is not None
    assert (
        result.curiosity_report.outcome is EpistemicCuriosityOutcome.QUESTION_CANDIDATE
    )
    assert result.relevance is not None and result.relevance.should_share is True
    assert len(conversation.submissions) == 1
    submitted = conversation.submissions[0]
    question = result.curiosity_report.question_candidate
    assert question is not None
    assert submitted["curiosity_report"] is result.curiosity_report
    assert submitted["curiosity_relevance_candidate"].title == question.question


def test_topic_evidence_must_be_in_exact_gap_lineage() -> None:
    runtime = EpistemicGapGovernedTopicCuriosityRuntime(_ConversationGateway())

    with pytest.raises(ValueError, match="not in the epistemic gap lineage"):
        runtime.admit(
            text="continue",
            gap=_gap("other-evidence"),
            topic_evidence=_nasa_item(),
            evidence_reference="nasa:item-1",
        )


def test_topic_reference_must_identify_exact_governed_item() -> None:
    runtime = EpistemicGapGovernedTopicCuriosityRuntime(_ConversationGateway())

    with pytest.raises(ValueError, match="does not identify the item"):
        runtime.admit(
            text="continue",
            gap=_gap("invented-reference"),
            topic_evidence=_nasa_item(),
            evidence_reference="invented-reference",
        )


def test_undeclared_source_topic_fails_closed_before_curiosity() -> None:
    runtime = EpistemicGapGovernedTopicCuriosityRuntime(_ConversationGateway())
    invalid = GovernedInformationItem(
        source_id="nasa",
        external_id="item-1",
        title="invalid topic",
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
    )

    with pytest.raises(ValueError, match="undeclared source topics"):
        runtime.admit(
            text="continue",
            gap=_gap(),
            topic_evidence=invalid,
            evidence_reference="nasa:item-1",
        )


def test_non_interesting_governed_topic_does_not_materialize_question() -> None:
    conversation = _ConversationGateway()
    runtime = EpistemicGapGovernedTopicCuriosityRuntime(conversation)
    item = GovernedInformationItem(
        source_id="technology_editorial",
        external_id="item-2",
        title="generic technology evidence",
        topics=frozenset({InterestTopic.TECHNOLOGY}),
    )
    # Use a center with a profile that deliberately has no technology interest.
    from app.personal_interest_center import PersonalInterestProfile

    conversation.relevance = RelevanceEvaluator(
        PersonalInterestCenter(
            (
                PersonalInterestProfile(
                    person="Nobody",
                    topics=frozenset({InterestTopic.MUSIC}),
                ),
            )
        )
    )

    result = runtime.admit(
        text="continue",
        gap=_gap("technology_editorial:item-2"),
        topic_evidence=item,
        evidence_reference="technology_editorial:item-2",
    )

    assert result.status is EpistemicGapTopicCuriosityStatus.NOT_RELEVANT
    assert result.curiosity_report is not None
    assert result.curiosity_report.outcome is EpistemicCuriosityOutcome.GAP_NOT_RELEVANT
    assert conversation.submissions == []


def test_runtime_is_wired_into_official_composition_without_gateway_surgery() -> None:
    source = (ROOT / "app" / "official_runtime_composition.py").read_text(
        encoding="utf-8"
    )
    assert "EpistemicGapGovernedTopicCuriosityRuntime(conversation)" in source
    assert "epistemic_gap_curiosity=epistemic_gap_curiosity" in source

    retired = ROOT / "app" / "hypothesis_gap_curiosity_productive_consumption.py"
    assert not retired.exists()


def test_result_preserves_non_persistent_non_operational_limits() -> None:
    result = EpistemicGapGovernedTopicCuriosityRuntime(_ConversationGateway()).admit(
        text="continue",
        gap=_gap(),
        topic_evidence=_nasa_item(),
        evidence_reference="nasa:item-1",
    )

    assert result.read_only is True
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_knowledge is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert result.starts_background_process is False
