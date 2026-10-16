from __future__ import annotations

from hashlib import sha256

from app.canonical_decision_facade import CanonicalDecisionFacade
from core.adaptive_cognition.episodic_memory import EpisodeReference
from core.adaptive_cognition.mental_models import (
    MentalModel,
    MentalModelKind,
    ModelAssertion,
    ModelAssertionStatus,
)
from core.governed_decision_advisory import GovernedDecisionOption
from core.mental_model_decision_evidence import (
    GovernedMentalModelDecisionEvidenceProjector,
)
from core.scope_guard import ScopeDomain


def _model(
    *,
    owner: str = "carlos",
    domains: tuple[ScopeDomain, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
    status: ModelAssertionStatus = ModelAssertionStatus.ACCEPTED,
    confidence: float = 0.95,
    references: bool = True,
) -> MentalModel:
    refs = ()
    if references:
        refs = (EpisodeReference("episode", "episode-1", sha256(b"x").hexdigest()),)
    assertion = ModelAssertion(
        predicate="prefers",
        value="quiet_hotel",
        confidence=confidence,
        status=status,
        references=refs,
    )
    return MentalModel(
        subject="Carlos",
        kind=MentalModelKind.PERSON,
        owner=owner,
        domains=domains,
        assertions=(assertion,),
    )


def _project(model: MentalModel, *, owner: str = "carlos"):
    return GovernedMentalModelDecisionEvidenceProjector().project(
        (model,),
        owner=owner,
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        option_matches={"quiet": (("prefers", "quiet_hotel"),)},
    )


def _options() -> tuple[GovernedDecisionOption, ...]:
    return (
        GovernedDecisionOption("nightlife", "Nightlife hotel"),
        GovernedDecisionOption("quiet", "Quiet hotel"),
    )


def test_relevant_accepted_model_materially_constrains_later_decision() -> None:
    facade = CanonicalDecisionFacade()
    baseline = facade.advise(_options())
    evidence = _project(_model())
    influenced = facade.advise(_options(), mental_model_evidence=evidence)
    assert baseline.recommended_option_id is None
    assert influenced.recommended_option_id == "quiet"
    assert any(
        code.startswith("mental_model_evidence:")
        for code in influenced.evidence_codes
    )


def test_projection_preserves_owner_scope_and_provenance() -> None:
    evidence = _project(_model())
    assert len(evidence) == 1
    item = evidence[0]
    assert item.owner == "carlos"
    assert ScopeDomain.PERSONAL_OPERATIONS.value in item.domains
    assert item.provenance[0].startswith("episode:episode-1:")
    assert item.canonical_authority == "unified_cognitive_coordination"


def test_tentative_assertion_does_not_influence_decision() -> None:
    assert _project(_model(status=ModelAssertionStatus.TENTATIVE)) == ()


def test_disputed_assertion_does_not_influence_decision() -> None:
    assert _project(_model(status=ModelAssertionStatus.DISPUTED)) == ()


def test_wrong_owner_does_not_cross_decision_boundary() -> None:
    assert _project(_model(owner="cristina")) == ()


def test_incompatible_scope_is_ignored() -> None:
    model = _model(domains=(ScopeDomain.KNOWLEDGE,))
    assert _project(model) == ()


def test_low_confidence_or_missing_provenance_is_ignored() -> None:
    assert _project(_model(confidence=0.5)) == ()
    assert _project(_model(references=False)) == ()


def test_irrelevant_accepted_model_does_not_change_decision() -> None:
    projector = GovernedMentalModelDecisionEvidenceProjector()
    evidence = projector.project(
        (_model(),),
        owner="carlos",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        option_matches={"quiet": (("prefers", "mountain_hiking"),)},
    )
    assert evidence == ()
    report = CanonicalDecisionFacade().advise(
        _options(), mental_model_evidence=evidence
    )
    assert report.recommended_option_id is None


def test_mental_model_evidence_remains_advisory_only() -> None:
    evidence = _project(_model())
    report = CanonicalDecisionFacade().advise(
        _options(), mental_model_evidence=evidence
    )
    assert report.read_only is True
    assert report.advisory_only is True
    assert report.human_decision_preserved is True
    assert report.executes_actions is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
    assert report.grants_authority is False
