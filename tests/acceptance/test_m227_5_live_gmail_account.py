from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("ROBY_GMAIL_ACCEPTANCE_ENABLED", "").lower()
    not in {"1", "true", "yes", "on"},
    reason="real Gmail acceptance is opt-in",
)


def test_real_gmail_acceptance_requires_deployment_fixture():
    """Deployment replaces this guard with its composed real-account fixture."""
    fixture_ready = os.getenv("ROBY_GMAIL_ACCEPTANCE_FIXTURE_READY", "").lower()
    assert fixture_ready in {"1", "true", "yes", "on"}
