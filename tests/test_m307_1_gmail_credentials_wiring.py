from app.runtime_environment_wiring import (
    build_mail_reader_conversation_from_environment,
)
from app.unified_runtime_integration import MailReaderConversationInterceptionPort


def test_m307_1_mail_reader_uses_canonical_credentials_without_base_config(
    monkeypatch,
):
    monkeypatch.delenv("ROBY_MAIL_READER_ENABLED", raising=False)
    monkeypatch.delenv("ROBY_MAIL_ENABLED", raising=False)
    monkeypatch.setenv("GMAIL_ADDRESS", "roby@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "app-password")

    interception = build_mail_reader_conversation_from_environment()

    assert isinstance(interception, MailReaderConversationInterceptionPort)
    provider = interception.adapter.provider
    assert provider.username == "roby@example.com"
