from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import (
    InterestTopic,
    PersonalInterestCenter,
    PersonalInterestProfile,
)


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()


def test_default_center_represents_carlos_and_cristina() -> None:
    center = PersonalInterestCenter()

    assert tuple(profile.person for profile in center.snapshot.profiles) == (
        "Carlos",
        "Cristina",
    )
    assert center.profile_for(" carlos ").is_interested_in(
        InterestTopic.CULTURE_CABA
    )
    assert center.profile_for("CRISTINA").is_interested_in(
        InterestTopic.ARGENTINE_CUISINE
    )
    for topic in (
        InterestTopic.SPACE_EXPLORATION,
        InterestTopic.NASA_MISSIONS,
        InterestTopic.INTERNATIONAL_SPACE_STATION,
        InterestTopic.JAMES_WEBB_SPACE_TELESCOPE,
    ):
        assert center.interested_people(topic) == ("Carlos", "Cristina")


def test_interest_queries_are_household_aware() -> None:
    center = PersonalInterestCenter()

    assert center.interested_people(InterestTopic.FREE_ACTIVITIES) == (
        "Carlos",
        "Cristina",
    )
    assert center.interested_people(InterestTopic.SPORTS) == ("Carlos",)


def test_updates_are_explicit_and_do_not_touch_credentials(tmp_path: Path) -> None:
    credentials = tmp_path / "credentials.json"
    credentials.write_text('{"token": "preserve-me"}', encoding="utf-8")
    center = PersonalInterestCenter(
        (PersonalInterestProfile("Carlos", frozenset({InterestTopic.SPORTS})),)
    )

    center.set_topics("Carlos", {InterestTopic.CULTURE_CABA})

    assert credentials.read_text(encoding="utf-8") == '{"token": "preserve-me"}'
    assert center.profile_for("Carlos").topics == frozenset(
        {InterestTopic.CULTURE_CABA}
    )


def test_official_gateway_is_the_only_production_composition_root() -> None:
    constructors: list[str] = []
    for root in ("app", "application", "core", "domain", "infrastructure"):
        for path in Path(root).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "PersonalInterestCenter"
                ):
                    constructors.append(path.as_posix())

    assert constructors == ["app/official_conversation_gateway.py"]


def test_gateway_exposes_read_only_interest_snapshot() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())

    assert gateway.personal_interest_center.schema_version == "m343.2"
    assert gateway.personal_interest_center.authority.endswith(
        ":OfficialConversationGateway"
    )
    with pytest.raises(AttributeError):
        gateway.personal_interest_center.profiles = ()
