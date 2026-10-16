from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.location_resolution import (
    LocationCandidate,
    LocationReferenceKind,
    LocationResolutionAction,
    LocationResolutionRequest,
    LocationResolutionStatus,
    ResolvedLocation,
)
from core.maps_foundation import (
    GeoPointSignal,
    MapContext,
    MapFoundationAction,
    MapFoundationStatus,
    MapPrecision,
    MapPurpose,
    MapScope,
    MapsFoundationRequest,
)
from core.places_knowledge import (
    InMemoryPlacesKnowledgeRepository,
    PlaceFact,
    PlaceFactKind,
    PlaceKnowledgeAction,
    PlaceKnowledgeStatus,
    PlacesKnowledgeEngine,
    PlacesKnowledgePolicy,
    PlacesKnowledgeRequest,
)

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)
POINT = GeoPointSignal(-34.6037, -58.3816, 0.95, NOW, "declared")


def resolution(*, owner="Carlos", status=LocationResolutionStatus.RESOLVED):
    map_request = MapsFoundationRequest(
        owner=owner,
        purpose=MapPurpose.PLACE_CONTEXT,
        requested_precision=MapPrecision.NEIGHBORHOOD,
        requested_scope=MapScope.LOCAL,
        location=POINT,
        explicit_user_consent=True,
    )
    context = MapContext(
        request=map_request,
        status=MapFoundationStatus.READY,
        action=MapFoundationAction.ESTABLISH,
        effective_precision=MapPrecision.NEIGHBORHOOD,
        effective_scope=MapScope.LOCAL,
        location_available=True,
        provider_required=True,
        route_computation_allowed=False,
        rationale=("maps_context_ready",),
        created_at=NOW,
    )
    candidate = LocationCandidate(
        label="Obelisco",
        kind=LocationReferenceKind.PLACE,
        confidence=0.95,
        point=POINT,
    )
    request = LocationResolutionRequest(
        owner=owner,
        map_context=context,
        reference="Obelisco",
        reference_kind=LocationReferenceKind.PLACE,
        candidates=(candidate,),
    )
    resolved = status is LocationResolutionStatus.RESOLVED
    return ResolvedLocation(
        request=request,
        status=status,
        action=(
            LocationResolutionAction.ACCEPT
            if resolved
            else LocationResolutionAction.CONFIRM
        ),
        selected_candidate=(candidate if resolved else None),
        resolved_label=("Obelisco" if resolved else None),
        resolved_point=(POINT if resolved else None),
        confidence=(0.95 if resolved else 0.0),
        provider_required=not resolved,
        clarification_required=(status is LocationResolutionStatus.AMBIGUOUS),
        rationale=(
            ("location_resolution_declared_candidate_selected",)
            if resolved
            else ("location_resolution_review",)
        ),
        created_at=NOW,
    )


def fact(
    kind=PlaceFactKind.CATEGORY,
    name="category",
    value="landmark",
    confidence=0.9,
    **changes,
):
    values = dict(
        kind=kind, name=name, value=value, confidence=confidence, source="declared"
    )
    values.update(changes)
    return PlaceFact(**values)


def request(**changes):
    values = dict(
        owner="Carlos",
        resolved_location=resolution(),
        facts=(fact(),),
        knowledge_declared=True,
    )
    values.update(changes)
    return PlacesKnowledgeRequest(**values)


def establish(*, policy=None, now=NOW, **changes):
    return PlacesKnowledgeEngine(policy=policy).establish(request(**changes), now=now)


def test_profile_ready():
    result = establish()
    assert result.status is PlaceKnowledgeStatus.READY
    assert result.action is PlaceKnowledgeAction.ESTABLISH
    assert result.place_label == "Obelisco"


@pytest.mark.parametrize("kind", list(PlaceFactKind))
def test_all_fact_kinds_supported(kind):
    result = establish(facts=(fact(kind=kind),))
    assert result.accepted_facts[0].kind is kind


def test_not_declared_is_not_applicable():
    assert (
        establish(knowledge_declared=False).status
        is PlaceKnowledgeStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_blocked():
    assert establish(owner="Other").status is PlaceKnowledgeStatus.BLOCKED


def test_owner_case_insensitive():
    assert establish(owner="carlos").status is PlaceKnowledgeStatus.READY


@pytest.mark.parametrize(
    "status",
    [
        LocationResolutionStatus.AMBIGUOUS,
        LocationResolutionStatus.REVIEW_REQUIRED,
        LocationResolutionStatus.BLOCKED,
        LocationResolutionStatus.NOT_APPLICABLE,
    ],
)
def test_unresolved_location_blocked(status):
    assert (
        establish(resolved_location=resolution(status=status)).status
        is PlaceKnowledgeStatus.BLOCKED
    )


def test_missing_facts_requires_provider():
    result = establish(facts=())
    assert result.status is PlaceKnowledgeStatus.REVIEW_REQUIRED
    assert result.provider_required


def test_low_confidence_fact_rejected():
    result = establish(facts=(fact(confidence=0.2),))
    assert result.status is PlaceKnowledgeStatus.REVIEW_REQUIRED
    assert result.rejected_fact_count == 1


def test_confidence_threshold_configurable():
    result = establish(
        facts=(fact(confidence=0.2),),
        policy=PlacesKnowledgePolicy(minimum_fact_confidence=0.1),
    )
    assert result.status is PlaceKnowledgeStatus.READY


def test_external_fact_allowed_by_default():
    assert (
        establish(facts=(fact(external_id="provider:1"),)).status
        is PlaceKnowledgeStatus.READY
    )


def test_external_fact_can_be_rejected():
    result = establish(
        facts=(fact(external_id="provider:1"),),
        policy=PlacesKnowledgePolicy(allow_external_facts=False),
    )
    assert result.status is PlaceKnowledgeStatus.REVIEW_REQUIRED


def test_fact_limit_requires_review():
    facts = tuple(fact(name=f"n{i}", value=str(i)) for i in range(3))
    result = establish(facts=facts, policy=PlacesKnowledgePolicy(maximum_facts=2))
    assert result.status is PlaceKnowledgeStatus.REVIEW_REQUIRED


def test_duplicate_semantic_fact_keeps_highest_confidence():
    result = establish(
        facts=(fact(value="A", confidence=0.8), fact(value="A", confidence=0.95))
    )
    assert len(result.accepted_facts) == 1
    assert result.accepted_facts[0].confidence == 0.95
    assert result.rejected_fact_count == 1


def test_close_conflicting_values_require_confirmation():
    result = establish(
        facts=(fact(value="A", confidence=0.9), fact(value="B", confidence=0.85))
    )
    assert result.status is PlaceKnowledgeStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_clear_conflict_selects_higher_confidence():
    result = establish(
        facts=(fact(value="A", confidence=0.95), fact(value="B", confidence=0.7)),
        policy=PlacesKnowledgePolicy(conflicting_value_margin=0.1),
    )
    assert result.status is PlaceKnowledgeStatus.READY
    assert result.accepted_facts[0].value == "A"


def test_conflict_margin_configurable():
    result = establish(
        facts=(fact(value="A", confidence=0.9), fact(value="B", confidence=0.85)),
        policy=PlacesKnowledgePolicy(conflicting_value_margin=0.01),
    )
    assert result.status is PlaceKnowledgeStatus.READY


def test_different_names_are_not_conflicts():
    result = establish(
        facts=(fact(name="type", value="A"), fact(name="access", value="B"))
    )
    assert len(result.accepted_facts) == 2


def test_different_kinds_are_not_conflicts():
    result = establish(
        facts=(fact(kind=PlaceFactKind.CATEGORY), fact(kind=PlaceFactKind.ATTRIBUTE))
    )
    assert len(result.accepted_facts) == 2


def test_order_does_not_change_accepted_facts():
    a = fact(name="a", value="1")
    b = fact(name="b", value="2")
    first = establish(facts=(a, b))
    second = establish(facts=(b, a))
    assert first.accepted_facts == second.accepted_facts


def test_repository_round_trip():
    repository = InMemoryPlacesKnowledgeRepository()
    result = PlacesKnowledgeEngine(repository=repository).establish(request(), now=NOW)
    assert repository.get(result.profile_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryPlacesKnowledgeRepository()
    engine = PlacesKnowledgeEngine(repository=repository)
    engine.establish(request(), now=NOW)
    with pytest.raises(ValueError):
        engine.establish(request(), now=NOW)


def test_deterministic_id():
    assert establish().profile_id == establish().profile_id


def test_timestamp_changes_id():
    later = datetime(2026, 7, 11, 12, 1, tzinfo=timezone.utc)
    assert establish().profile_id != establish(now=later).profile_id


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        establish(now=datetime(2026, 7, 11, 12, 0))


def test_profile_is_immutable():
    with pytest.raises(FrozenInstanceError):
        establish().status = PlaceKnowledgeStatus.BLOCKED


def test_request_is_immutable():
    with pytest.raises(FrozenInstanceError):
        request().owner = "Other"


def test_fact_is_immutable():
    with pytest.raises(FrozenInstanceError):
        fact().value = "Other"


@pytest.mark.parametrize(
    "field,value", [("name", " "), ("value", " "), ("source", " ")]
)
def test_fact_blank_fields_rejected(field, value):
    kwargs = {field: value}
    with pytest.raises(ValueError):
        fact(**kwargs)


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_fact_invalid_confidence_rejected(confidence):
    with pytest.raises(ValueError):
        fact(confidence=confidence)


def test_fact_normalizes_text():
    item = fact(
        name="  opening   hours ", value="  Always   open ", source=" DECLARED "
    )
    assert item.name == "opening hours"
    assert item.value == "Always open"
    assert item.source == "declared"


def test_blank_external_id_rejected():
    with pytest.raises(ValueError):
        fact(external_id=" ")


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner=" ")


@pytest.mark.parametrize("minimum", [-0.1, 1.1])
def test_invalid_minimum_confidence_rejected(minimum):
    with pytest.raises(ValueError):
        PlacesKnowledgePolicy(minimum_fact_confidence=minimum)


def test_invalid_maximum_facts_rejected():
    with pytest.raises(ValueError):
        PlacesKnowledgePolicy(maximum_facts=0)


@pytest.mark.parametrize("margin", [-0.1, 1.1])
def test_invalid_conflict_margin_rejected(margin):
    with pytest.raises(ValueError):
        PlacesKnowledgePolicy(conflicting_value_margin=margin)


def test_tampered_profile_id_rejected():
    with pytest.raises(ValueError):
        replace(establish(), profile_id="bad")


def test_ready_profile_requires_facts():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, accepted_facts=())


def test_non_ready_profile_cannot_expose_facts():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, status=PlaceKnowledgeStatus.BLOCKED)


def test_negative_rejected_count_rejected():
    with pytest.raises(ValueError):
        replace(establish(), rejected_fact_count=-1)


def test_empty_rationale_rejected():
    with pytest.raises(ValueError):
        replace(establish(), rationale=())


def test_no_route_or_navigation_capability_exposed():
    result = establish()
    assert not hasattr(result, "route")
    assert not hasattr(result, "navigation")
    assert not hasattr(result, "recommendation")


def test_engine_has_no_provider_or_io_method():
    engine = PlacesKnowledgeEngine()
    assert not hasattr(engine, "search")
    assert not hasattr(engine, "geocode")
    assert not hasattr(engine, "fetch")


def test_m123_lineage_preserved():
    result = establish()
    assert (
        result.request.resolved_location.resolution_id
        == request().resolved_location.resolution_id
    )


def test_multiple_valid_facts_preserved():
    facts = (
        fact(PlaceFactKind.CATEGORY, "category", "landmark"),
        fact(PlaceFactKind.ADDRESS, "street", "Avenida 9 de Julio"),
        fact(PlaceFactKind.DESCRIPTION, "summary", "Historic monument"),
    )
    result = establish(facts=facts)
    assert len(result.accepted_facts) == 3


def test_rejected_count_includes_duplicate_and_low_confidence():
    result = establish(
        facts=(
            fact(value="A", confidence=0.95),
            fact(value="A", confidence=0.8),
            fact(name="low", confidence=0.1),
        )
    )
    assert result.rejected_fact_count == 2


def test_provider_not_required_when_declared_facts_suffice():
    assert not establish().provider_required


def test_confirmation_not_required_when_ready():
    assert not establish().confirmation_required


def test_profile_label_comes_from_resolution():
    assert establish().place_label == resolution().resolved_label
