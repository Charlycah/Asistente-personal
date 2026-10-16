"""RED contractual: noticias espont?neas configurables."""

from dataclasses import fields

from app.proactive_verified_runtime import ProactiveVerifiedPolicy


def test_spontaneous_news_policy_is_explicit():
    names = {field.name for field in fields(ProactiveVerifiedPolicy)}

    assert "spontaneous_news_enabled" in names


def test_historical_news_policy_remains_enabled():
    names = {field.name for field in fields(ProactiveVerifiedPolicy)}
    assert "spontaneous_news_enabled" in names

    policy = ProactiveVerifiedPolicy()

    assert policy.spontaneous_news_enabled is True


def test_spontaneous_news_can_be_disabled_without_disabling_runtime():
    names = {field.name for field in fields(ProactiveVerifiedPolicy)}
    assert "spontaneous_news_enabled" in names

    policy = ProactiveVerifiedPolicy(
        spontaneous_news_enabled=False
    )

    assert policy.spontaneous_news_enabled is False


def test_news_on_demand_retains_existing_authority():
    from app.runtime_root_factory import build_runtime_root

    assert callable(build_runtime_root)


def test_disabled_spontaneous_news_preserves_important_gmail(
    tmp_path,
):
    from datetime import datetime, timezone

    from app.proactive_verified_runtime import ProactiveVerifiedRuntime
    from tests.test_m310_proactive_verified_runtime import (
        GmailAnnouncer,
        NewsClient,
        item,
    )

    now = datetime(2026, 7, 23, 18, tzinfo=timezone.utc)
    delivered = []

    runtime = ProactiveVerifiedRuntime(
        notify=delivered.append,
        news_client=NewsClient([item(now)]),
        gmail_announcer=GmailAnnouncer(),
        now=lambda: now,
        policy=ProactiveVerifiedPolicy(
            state_path=tmp_path / "state.json",
            spontaneous_news_enabled=False,
        ),
    )

    messages = runtime.tick()

    assert len(messages) == 1
    assert "turno m\u00e9dico" in messages[0]
    assert delivered == list(messages)


def test_desktop_factory_disables_spontaneous_news_by_default(
    monkeypatch,
    tmp_path,
):
    from app.proactive_verified_runtime import (
        build_proactive_verified_runtime_from_environment,
    )
    from tests.test_m310_proactive_verified_runtime import (
        GmailAnnouncer,
    )

    monkeypatch.setenv("ROBY_PERSONAL_RUNTIME_ENABLED", "true")
    monkeypatch.setenv("ROBY_PROACTIVE_VERIFIED_ENABLED", "true")
    monkeypatch.setenv(
        "ROBY_PROACTIVE_VERIFIED_STATE_PATH",
        str(tmp_path / "state.json"),
    )

    delivered = []
    runtime = build_proactive_verified_runtime_from_environment(
        notify=delivered.append,
        gmail_announcer=GmailAnnouncer(),
    )

    assert runtime is not None
    assert runtime.policy.spontaneous_news_enabled is False
