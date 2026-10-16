from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from infrastructure.calendar.calendar_runtime_composition import (
    CALENDAR_EVENT_SCOPE,
    CALENDAR_FREEBUSY_SCOPE,
    CalendarRuntimeComposition,
    CalendarRuntimeConfig,
    CalendarRuntimeState,
    build_calendar_runtime_from_environment,
)
from infrastructure.calendar.google_calendar_adapter import GoogleCalendarAdapter


class Credentials:
    def __init__(self, *, scopes=(), valid=True, expired=False) -> None:
        self.expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        self.scopes = list(scopes)
        self.valid = valid
        self.expired = expired
        self.refresh_token = "refresh"
        self.token = "secret"

    def refresh(self, request) -> None:
        self.valid = True
        self.expired = False

    def to_json(self) -> str:
        return "{}"


class Material:
    def __init__(self, credentials: Credentials) -> None:
        self._credentials = credentials
        self.deployment_credentials = credentials
        self.revoked = False

    @property
    def scopes(self):
        return tuple(self._credentials.scopes)

    @property
    def expires_at(self):
        return self._credentials.expiry


class OAuth:
    def __init__(self, material=None, *, interactive=False) -> None:
        self.material = material
        self.config = type(
            "Config",
            (),
            {"allow_interactive_authorization": interactive},
        )()
        self.activations = []

    def load(self, account_fingerprint):
        return self.material

    def activate(self, account_fingerprint, scopes):
        self.activations.append((account_fingerprint, scopes))
        return "activated"


def _provider() -> GoogleCalendarAdapter:
    return GoogleCalendarAdapter(lambda: object())


def test_runtime_is_disabled_by_default() -> None:
    runtime = CalendarRuntimeComposition()

    snapshot = runtime.snapshot()

    assert snapshot.state is CalendarRuntimeState.DISABLED
    assert snapshot.enabled is False


def test_enabled_runtime_without_configuration_degrades_cleanly() -> None:
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True)
    )

    assert runtime.snapshot().reason == "configuration_missing"


def test_enabled_runtime_without_credentials_degrades_cleanly() -> None:
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True),
        oauth=OAuth(),
        provider=_provider(),
    )

    assert runtime.snapshot().reason == "credentials_absent"


def test_runtime_requires_all_calendar_scopes() -> None:
    material = Material(Credentials(scopes=(CALENDAR_EVENT_SCOPE,)))
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True),
        oauth=OAuth(material),
        provider=_provider(),
    )

    snapshot = runtime.snapshot()

    assert snapshot.state is CalendarRuntimeState.DEGRADED
    assert snapshot.reason == "insufficient_scope"


def test_ready_runtime_exposes_provider() -> None:
    material = Material(
        Credentials(scopes=(CALENDAR_EVENT_SCOPE, CALENDAR_FREEBUSY_SCOPE))
    )
    provider = _provider()
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True),
        oauth=OAuth(material),
        provider=provider,
    )

    assert runtime.snapshot().state is CalendarRuntimeState.READY
    assert runtime.require_provider() is provider


def test_explicit_activation_is_blocked_when_runtime_disabled() -> None:
    runtime = CalendarRuntimeComposition(
        oauth=OAuth(interactive=True),
        provider=_provider(),
    )

    with pytest.raises(RuntimeError, match="disabled"):
        runtime.activate()


def test_explicit_activation_uses_governed_scopes() -> None:
    oauth = OAuth(interactive=True)
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True, account_fingerprint="carlos"),
        oauth=oauth,
        provider=_provider(),
    )

    assert runtime.activate() == "activated"
    assert oauth.activations == [
        ("carlos", (CALENDAR_EVENT_SCOPE, CALENDAR_FREEBUSY_SCOPE))
    ]


class Secrets:
    def __init__(self, values):
        self.values = values

    def get(self, key, default=None):
        return self.values.get(key, default)


def test_environment_builder_does_not_require_credentials_when_disabled() -> None:
    runtime = build_calendar_runtime_from_environment(
        secrets_loader=Secrets({}),
        environment=lambda name: None,
    )

    assert runtime.snapshot().state is CalendarRuntimeState.DISABLED


def test_environment_builder_uses_canonical_google_paths_without_writing_them(
    tmp_path: Path,
) -> None:
    token_path = tmp_path / "calendar-token.json"
    client_path = tmp_path / "client.json"
    secrets = Secrets(
        {
            "GOOGLE_TOKEN_FILE": str(token_path),
            "GOOGLE_CLIENT_SECRET_FILE": str(client_path),
        }
    )
    env = {
        "ROBY_CALENDAR_ENABLED": "true",
        "ROBY_CALENDAR_ALLOW_INTERACTIVE_OAUTH": "false",
    }

    runtime = build_calendar_runtime_from_environment(
        secrets_loader=secrets,
        environment=env.get,
    )

    assert runtime.config.enabled is True
    assert runtime.configured is True
    assert runtime.oauth.config.token_path == token_path
    assert runtime.oauth.config.client_secrets_path == client_path
    assert token_path.exists() is False
    assert client_path.exists() is False
