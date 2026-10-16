from datetime import datetime, timezone

import pytest

from infrastructure.mail.gmail_production_readiness import (
    GmailProductionCriterion,
    GmailProductionDecision,
    GmailProductionReadinessCertificate,
    GmailProductionReadinessCertifier,
    GmailProductionReadinessPolicy,
)

NOW = datetime(2026, 7, 14, 20, 0, tzinfo=timezone.utc)


class Provider:
    def __init__(self, data):
        self.data = dict(data)

    def status(self, **kwargs):
        del kwargs
        return dict(self.data)


def certifier(**overrides):
    values = {
        "runtime": Provider({"state": "ready"}),
        "oauth": Provider({"state": "ready", "usable": True}),
        "retry": Provider({"max_attempts": 3}),
        "transport": Provider({"timeout_seconds": 30.0}),
        "acceptance": Provider({"write_enabled": False}),
    }
    values.update(overrides)
    return GmailProductionReadinessCertifier(**values)


def test_live_acceptance_produces_go_certificate():
    certificate = certifier().certify(now=NOW, live_acceptance_passed=True)
    assert certificate.decision is GmailProductionDecision.GO
    assert certificate.ready


def test_missing_live_acceptance_is_conditional():
    certificate = certifier().certify(now=NOW)
    assert certificate.decision is GmailProductionDecision.CONDITIONAL


def test_runtime_not_ready_is_no_go():
    certificate = certifier(runtime=Provider({"state": "degraded"})).certify(now=NOW)
    assert certificate.decision is GmailProductionDecision.NO_GO


def test_oauth_must_be_ready_and_usable():
    instance = certifier(oauth=Provider({"state": "ready", "usable": False}))
    certificate = instance.certify(now=NOW, live_acceptance_passed=True)
    assert not next(c for c in certificate.criteria if c.name == "oauth_ready").passed


def test_retry_attempts_must_be_bounded():
    certificate = certifier(retry=Provider({"max_attempts": 99})).certify(
        now=NOW, live_acceptance_passed=True
    )
    assert certificate.decision is GmailProductionDecision.NO_GO


def test_transport_timeout_must_be_bounded():
    certificate = certifier(transport=Provider({"timeout_seconds": 120})).certify(
        now=NOW, live_acceptance_passed=True
    )
    assert certificate.decision is GmailProductionDecision.NO_GO


def test_write_acceptance_requires_explicit_policy():
    certificate = certifier(acceptance=Provider({"write_enabled": True})).certify(
        now=NOW, live_acceptance_passed=True
    )
    assert certificate.decision is GmailProductionDecision.NO_GO


def test_policy_can_approve_write_acceptance():
    instance = certifier(acceptance=Provider({"write_enabled": True}))
    instance.policy = GmailProductionReadinessPolicy(allow_write_acceptance=True)
    assert instance.certify(now=NOW, live_acceptance_passed=True).ready


def test_policy_can_make_live_acceptance_optional():
    instance = certifier()
    instance.policy = GmailProductionReadinessPolicy(require_live_acceptance=False)
    assert instance.certify(now=NOW).ready


def test_certificate_identity_is_deterministic():
    first = certifier().certify(now=NOW, live_acceptance_passed=True)
    second = certifier().certify(now=NOW, live_acceptance_passed=True)
    assert first.certificate_id == second.certificate_id


def test_certificate_rejects_naive_timestamp():
    criterion = GmailProductionCriterion("runtime", True, "ready", "ready")
    with pytest.raises(ValueError, match="timezone-aware"):
        GmailProductionReadinessCertificate(
            GmailProductionDecision.GO, (criterion,), datetime(2026, 1, 1)
        )


def test_status_and_certificate_are_secret_free():
    instance = certifier()
    certificate = instance.certify(now=NOW, live_acceptance_passed=True)
    rendered = repr((certificate.to_dict(), instance.status()))
    assert "token" not in rendered
    assert "recipient" not in rendered
    assert instance.status()["ready"] is True
