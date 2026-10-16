from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationActivityState,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemoryIntellectualContributionRepository,
    IntellectualCompanionLayer,
    IntellectualCompanionPolicy,
    IntellectualCompanionRequest,
    IntellectualContributionKind,
    IntellectualContributionStatus,
    IntellectualDomain,
    LivingConversationContext,
    LivingConversationManager,
    ReflectionGenerator,
)

NOW = datetime(2026, 7, 10, 18, 0, tzinfo=timezone.utc)


def pipeline(
    *,
    kind: str = "reflect",
    sources: tuple[str, ...] = ("book:borges",),
    content_hint: str = (
        "la memoria transforma el modo en que interpretamos el presente"
    ),
    explicit: bool = False,
):
    opportunity = ConversationOpportunity(
        kind=kind,
        reason="La idea conecta con una conversación anterior.",
        value_score=0.91,
        relevance_score=0.92,
        confidence=0.94,
        content_hint=content_hint,
        source_reference_ids=sources,
    )
    context = LivingConversationContext(owner="Carlos", explicit_user_turn=explicit)
    governance = LivingConversationManager().evaluate(context, opportunity, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=context,
            activity=ConversationActivityState.AVAILABLE,
            cognitive_load=0.2,
            local_hour=18,
        ),
        opportunity,
        now=NOW,
    )
    reflection = ReflectionGenerator().generate(governance, timing, now=NOW)
    return governance, timing, reflection


def request(**changes):
    governance, timing, reflection = pipeline(
        kind=changes.pop("kind", "reflect"),
        sources=changes.pop("sources", ("book:borges",)),
        explicit=changes.pop("explicit", False),
    )
    values = {
        "governance": governance,
        "timing": timing,
        "reflection": reflection,
        "domain": IntellectualDomain.LITERATURE,
        "thesis": "La memoria no conserva intacto el pasado: lo vuelve interpretable.",
        "concepts": ("identidad", "tiempo"),
        "requested_at": NOW,
    }
    values.update(changes)
    return IntellectualCompanionRequest(**values)


def test_ready_contribution_is_produced() -> None:
    result = IntellectualCompanionLayer().compose(request(), now=NOW)
    assert result.status is IntellectualContributionStatus.READY
    assert result.kind is IntellectualContributionKind.CONNECTION
    assert result.title == "Una lectura posible"


def test_ready_contribution_preserves_sources() -> None:
    item = request()
    result = IntellectualCompanionLayer().compose(item, now=NOW)
    assert result.source_reference_ids == item.reflection.source_reference_ids


def test_ready_contribution_has_text() -> None:
    result = IntellectualCompanionLayer().compose(request(), now=NOW)
    assert result.text is not None
    assert "memoria" in result.text


def test_concepts_extend_key_points() -> None:
    result = IntellectualCompanionLayer().compose(request(), now=NOW)
    assert "También se relaciona con identidad." in result.key_points
    assert "También se relaciona con tiempo." in result.key_points


@pytest.mark.parametrize(
    ("domain", "title"),
    [
        ("music", "Una escucha posible"),
        ("science", "Una hipótesis para explorar"),
        ("history", "Una perspectiva histórica"),
        ("philosophy", "Una pregunta filosófica"),
        ("culture", "Una conexión cultural"),
        ("personal_project", "Una perspectiva para el proyecto"),
        ("general", "Una reflexión para continuar"),
    ],
)
def test_domain_titles(domain: str, title: str) -> None:
    result = IntellectualCompanionLayer().compose(request(domain=domain), now=NOW)
    assert result.title == title


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("respond", IntellectualContributionKind.RESPONSE),
        ("ask", IntellectualContributionKind.QUESTION),
        ("reflect", IntellectualContributionKind.CONNECTION),
        ("share", IntellectualContributionKind.CONTEXT),
        ("resume", IntellectualContributionKind.CONTINUATION),
    ],
)
def test_reflection_form_maps_to_contribution_kind(kind: str, expected) -> None:
    result = IntellectualCompanionLayer().compose(request(kind=kind), now=NOW)
    assert result.kind is expected


def test_request_rejects_blank_thesis() -> None:
    with pytest.raises(ValueError, match="thesis"):
        request(thesis=" ")


def test_request_rejects_blank_concept() -> None:
    with pytest.raises(ValueError, match="concepts"):
        request(concepts=("identity", " "))


def test_request_rejects_duplicate_concepts_case_insensitive() -> None:
    with pytest.raises(ValueError, match="unique"):
        request(concepts=("Tiempo", "tiempo"))


def test_request_requires_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        request(requested_at=datetime(2026, 7, 10, 18, 0))


def test_depth_score_is_bounded() -> None:
    result = IntellectualCompanionLayer().compose(request(), now=NOW)
    assert 0.0 <= result.depth_score <= 1.0


def test_low_depth_abstains() -> None:
    governance, timing, reflection = pipeline()
    shallow = replace(
        governance.opportunity,
        value_score=0.1,
        relevance_score=0.1,
        confidence=0.61,
    )
    context = governance.context
    governance = LivingConversationManager().evaluate(context, shallow, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        replace(timing.context, conversation=context), shallow, now=NOW
    )
    reflection = ReflectionGenerator().generate(governance, timing, now=NOW)
    req = IntellectualCompanionRequest(
        governance=governance,
        timing=timing,
        reflection=reflection,
        requested_at=NOW,
    )
    result = IntellectualCompanionLayer().compose(req, now=NOW)
    assert result.status is IntellectualContributionStatus.ABSTAINED


def test_personal_project_can_require_review() -> None:
    layer = IntellectualCompanionLayer(
        policy=IntellectualCompanionPolicy(require_review_for_personal_projects=True)
    )
    result = layer.compose(request(domain="personal_project"), now=NOW)
    assert result.status is IntellectualContributionStatus.REVIEW_REQUIRED
    assert result.text is None


def test_length_limit_abstains() -> None:
    layer = IntellectualCompanionLayer(
        policy=IntellectualCompanionPolicy(maximum_text_length=20)
    )
    result = layer.compose(request(), now=NOW)
    assert result.status is IntellectualContributionStatus.ABSTAINED
    assert result.title is None


def test_key_points_are_bounded() -> None:
    layer = IntellectualCompanionLayer(
        policy=IntellectualCompanionPolicy(maximum_key_points=1)
    )
    result = layer.compose(request(), now=NOW)
    assert len(result.key_points) == 1


def test_repository_stores_and_retrieves() -> None:
    repository = InMemoryIntellectualContributionRepository()
    layer = IntellectualCompanionLayer(repository=repository)
    item = layer.compose(request(), now=NOW)
    assert repository.get(item.contribution_id) == item
    assert repository.list_all() == (item,)
    assert layer.last_contribution == item


def test_repository_rejects_duplicate() -> None:
    repository = InMemoryIntellectualContributionRepository()
    item = IntellectualCompanionLayer().compose(request(), now=NOW)
    repository.add(item)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(item)


def test_contribution_is_immutable() -> None:
    item = IntellectualCompanionLayer().compose(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        item.title = "Otro"  # type: ignore[misc]


def test_contribution_id_is_deterministic() -> None:
    one = IntellectualCompanionLayer().compose(request(), now=NOW)
    two = IntellectualCompanionLayer().compose(request(), now=NOW)
    assert one.contribution_id == two.contribution_id


def test_contribution_rejects_inconsistent_id() -> None:
    item = IntellectualCompanionLayer().compose(request(), now=NOW)
    with pytest.raises(ValueError, match="inconsistent"):
        replace(item, contribution_id="bad")


def test_policy_rejects_invalid_depth() -> None:
    with pytest.raises(ValueError, match="depth"):
        IntellectualCompanionPolicy(minimum_depth_score=1.1)


def test_policy_rejects_negative_source_count() -> None:
    with pytest.raises(ValueError, match="source count"):
        IntellectualCompanionPolicy(minimum_source_count=-1)


def test_policy_rejects_non_positive_key_point_limit() -> None:
    with pytest.raises(ValueError, match="key points"):
        IntellectualCompanionPolicy(maximum_key_points=0)


def test_policy_rejects_non_positive_text_limit() -> None:
    with pytest.raises(ValueError, match="text length"):
        IntellectualCompanionPolicy(maximum_text_length=0)


def test_explicit_response_does_not_require_sources() -> None:
    req = request(kind="respond", sources=(), explicit=True)
    result = IntellectualCompanionLayer().compose(req, now=NOW)
    assert result.status is IntellectualContributionStatus.READY


def test_unaware_compose_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        IntellectualCompanionLayer().compose(
            request(), now=datetime(2026, 7, 10, 18, 0)
        )


def test_non_ready_contribution_cannot_hold_content() -> None:
    ready = IntellectualCompanionLayer().compose(request(), now=NOW)
    with pytest.raises(ValueError, match="non-ready"):
        replace(ready, status="abstained")
