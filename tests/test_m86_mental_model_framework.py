from datetime import datetime, timezone

import pytest

from core.adaptive_cognition import (
    Episode,
    EpisodeStatus,
    InMemoryMentalModelRepository,
    MentalModel,
    MentalModelKind,
    MentalModelManager,
    MentalModelPolicy,
    MentalModelQuery,
    MentalModelStatus,
    ModelAssertion,
    ModelAssertionStatus,
    ModelUpdateProposal,
)
from core.scope_guard import ScopeDomain

NOW = datetime(2026, 7, 10, tzinfo=timezone.utc)


def episode(confidence: float = 0.9) -> Episode:
    return Episode(
        title="Project review",
        owner="carlos",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        status=EpisodeStatus.COMPLETED,
        outcome="Delivery completed",
        confidence=confidence,
        started_at=NOW,
        ended_at=NOW,
    )


def test_assertion_has_stable_identity_and_provenance() -> None:
    assertion = ModelAssertion("status", "active", 0.8, asserted_at=NOW)
    assert len(assertion.assertion_id) == 64
    assert assertion.to_dict()["status"] == "tentative"


def test_assertion_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        ModelAssertion("status", "active", 1.1)


def test_model_requires_domains() -> None:
    with pytest.raises(ValueError):
        MentalModel("ROBY", MentalModelKind.SYSTEM, "shared", ())


def test_model_fingerprint_changes_across_revision() -> None:
    model = MentalModel(
        "ROBY",
        MentalModelKind.SYSTEM,
        "shared",
        (ScopeDomain.PERSONAL_OPERATIONS,),
    )
    revised = model.revise(assertions=(ModelAssertion("state", "ready", 0.9),))
    assert revised.revision == 2
    assert revised.fingerprint != model.fingerprint


def test_repository_preserves_history() -> None:
    repository = InMemoryMentalModelRepository()
    model = repository.save(
        MentalModel(
            "ROBY",
            MentalModelKind.SYSTEM,
            "shared",
            (ScopeDomain.PERSONAL_OPERATIONS,),
        )
    )
    repository.save(model.revise())
    assert [item.revision for item in repository.history(model.model_id)] == [1, 2]


def test_repository_rejects_revision_gap() -> None:
    repository = InMemoryMentalModelRepository()
    model = MentalModel(
        "ROBY",
        MentalModelKind.SYSTEM,
        "shared",
        (ScopeDomain.PERSONAL_OPERATIONS,),
    )
    repository.save(model)
    with pytest.raises(ValueError):
        repository.save(model.revise().revise())


def test_manager_creates_empty_model() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT, owner="carlos")
    assert model.subject == "Project ROBY"
    assert model.assertions == ()


def test_episode_produces_proposal_not_automatic_update() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT, owner="carlos")
    proposal = manager.propose_from_episode(
        model.model_id,
        episode(),
        predicate="delivery_status",
        value="completed",
    )
    assert manager.repository.get(model.model_id).assertions == ()
    assert proposal.additions[0].references[0].reference_type == "episode"


def test_high_confidence_proposal_can_be_applied() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT)
    proposal = manager.propose_from_episode(
        model.model_id, episode(), predicate="status", value="completed"
    )
    revised = manager.apply(proposal)
    assert revised.assertions[0].normalized_status is ModelAssertionStatus.ACCEPTED


def test_low_confidence_proposal_requires_review() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT)
    proposal = manager.propose_from_episode(
        model.model_id,
        episode(0.4),
        predicate="risk",
        value="high",
    )
    assert proposal.requires_review
    with pytest.raises(PermissionError):
        manager.apply(proposal)


def test_explicit_approval_applies_reviewed_proposal() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT)
    proposal = manager.propose_from_episode(
        model.model_id, episode(0.4), predicate="risk", value="high"
    )
    revised = manager.apply(proposal, approved=True)
    assert revised.assertions[0].normalized_status is ModelAssertionStatus.TENTATIVE


def test_conflicting_assertions_are_preserved_as_disputed() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT)
    first = manager.propose_from_episode(
        model.model_id, episode(), predicate="status", value="active"
    )
    model = manager.apply(first)
    second = ModelUpdateProposal(
        model_id=model.model_id,
        additions=(ModelAssertion("status", "paused", 0.95),),
        rationale="Conflicting observation",
    )
    revised = manager.apply(second)
    assert revised.normalized_status is MentalModelStatus.REVIEW_REQUIRED
    assert {item.normalized_status for item in revised.assertions} == {
        ModelAssertionStatus.DISPUTED
    }


def test_assertions_can_be_retired_by_explicit_proposal() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT)
    model = manager.apply(
        manager.propose_from_episode(
            model.model_id, episode(), predicate="status", value="active"
        )
    )
    proposal = ModelUpdateProposal(
        model_id=model.model_id,
        retire_assertion_ids=(model.assertions[0].assertion_id,),
        rationale="No longer applicable",
    )
    revised = manager.apply(proposal)
    assert revised.assertions == ()


def test_capacity_is_enforced() -> None:
    manager = MentalModelManager(policy=MentalModelPolicy(max_assertions_per_model=1))
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT)
    proposal = ModelUpdateProposal(
        model_id=model.model_id,
        additions=(
            ModelAssertion("a", "1", 0.9),
            ModelAssertion("b", "2", 0.9),
        ),
        rationale="Too many assertions",
    )
    with pytest.raises(ValueError):
        manager.apply(proposal)


def test_query_filters_owner_kind_and_domain() -> None:
    manager = MentalModelManager()
    manager.create(
        "Carlos",
        kind=MentalModelKind.PERSON,
        owner="carlos",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
    )
    manager.create(
        "ROBY",
        kind=MentalModelKind.SYSTEM,
        owner="shared",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
    )
    result = manager.query(
        MentalModelQuery(
            owner="carlos",
            kinds=(MentalModelKind.PERSON,),
            domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        )
    )
    assert [item.subject for item in result.models] == ["Carlos"]


def test_query_ranks_text_matches() -> None:
    manager = MentalModelManager()
    manager.create("Alpha project", kind=MentalModelKind.PROJECT)
    manager.create("Beta project", kind=MentalModelKind.PROJECT)
    result = manager.query(MentalModelQuery(text="Beta"))
    assert result.models[0].subject == "Beta project"


def test_query_excludes_review_required_by_default() -> None:
    manager = MentalModelManager()
    model = manager.create("Project ROBY", kind=MentalModelKind.PROJECT)
    manager.repository.save(model.revise(status=MentalModelStatus.REVIEW_REQUIRED))
    assert manager.query(MentalModelQuery()).models == ()


def test_unknown_model_is_rejected() -> None:
    manager = MentalModelManager()
    with pytest.raises(KeyError):
        manager.propose_from_episode("missing", episode(), predicate="x", value="y")


def test_prompt_states_epistemic_boundary() -> None:
    lines = MentalModelManager().system_prompt_lines()
    assert any("no hechos" in line for line in lines)
    assert any("contradicciones" in line for line in lines)


def test_models_are_serializable() -> None:
    model = MentalModel(
        "ROBY", MentalModelKind.SYSTEM, "shared", (ScopeDomain.PERSONAL_OPERATIONS,)
    )
    payload = model.to_dict()
    assert payload["kind"] == "system"
    assert payload["revision"] == 1
