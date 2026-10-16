from __future__ import annotations

from infrastructure.mail.gmail_subject_announcement import (
    GmailStartupSubjectAnnouncer,
    GmailSubjectAnnouncementPolicy,
    GoogleGmailUnreadSubjectProvider,
)


class Request:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class Messages:
    def __init__(self, subjects):
        self.subjects = subjects
        self.list_kwargs = None
        self.get_kwargs = []

    def list(self, **kwargs):
        self.list_kwargs = kwargs
        return Request(
            {"messages": [{"id": str(i)} for i in range(len(self.subjects))]}
        )

    def get(self, **kwargs):
        self.get_kwargs.append(kwargs)
        subject = self.subjects[int(kwargs["id"])]
        headers = [] if subject is None else [{"name": "Subject", "value": subject}]
        return Request({"payload": {"headers": headers}, "snippet": "DO NOT READ"})


class Users:
    def __init__(self, messages):
        self._messages = messages

    def messages(self):
        return self._messages


class Service:
    def __init__(self, messages):
        self._users = Users(messages)

    def users(self):
        return self._users


def provider_for(subjects):
    messages = Messages(subjects)
    provider = GoogleGmailUnreadSubjectProvider(
        lambda **_kwargs: Service(messages), timeout_seconds=3
    )
    return provider, messages


def test_disabled_announcement_does_not_touch_provider():
    class FailProvider:
        def list_unread_subjects(self, *, limit):
            raise AssertionError(limit)

    result = GmailStartupSubjectAnnouncer(FailProvider()).announce()
    assert result.text == ""
    assert result.count == 0


def test_empty_inbox_announces_no_new_mail():
    provider, _ = provider_for([])
    result = GmailStartupSubjectAnnouncer(
        provider, GmailSubjectAnnouncementPolicy(enabled=True)
    ).announce()
    assert result.text == "No tenés correos nuevos."


def test_single_subject_is_announced_without_body():
    provider, _ = provider_for(["Factura de julio"])
    result = GmailStartupSubjectAnnouncer(
        provider, GmailSubjectAnnouncementPolicy(enabled=True)
    ).announce()
    assert result.text == "Tenés un correo nuevo. Asuntos: 1. Factura de julio."
    assert result.bodies_requested is False


def test_multiple_subjects_are_enumerated():
    provider, _ = provider_for(["Uno", "Dos"])
    result = GmailStartupSubjectAnnouncer(
        provider, GmailSubjectAnnouncementPolicy(enabled=True)
    ).announce()
    assert result.text == "Tenés 2 correos nuevos. Asuntos: 1. Uno; 2. Dos."


def test_provider_uses_unread_query_and_limit():
    provider, messages = provider_for(["Uno"])
    provider.list_unread_subjects(limit=4)
    assert messages.list_kwargs == {"userId": "me", "q": "is:unread", "maxResults": 4}


def test_provider_requests_only_subject_metadata():
    provider, messages = provider_for(["Uno"])
    provider.list_unread_subjects(limit=1)
    assert messages.get_kwargs == [
        {
            "userId": "me",
            "id": "0",
            "format": "metadata",
            "metadataHeaders": ["Subject"],
        }
    ]


def test_missing_subject_uses_safe_fallback():
    provider, _ = provider_for([None])
    assert provider.list_unread_subjects(limit=1) == ("Sin asunto",)


def test_subject_whitespace_is_normalized():
    provider, _ = provider_for(["  Estado   del\nproyecto "])
    assert provider.list_unread_subjects(limit=1) == ("Estado del proyecto",)


def test_status_confirms_no_bodies_and_no_mutation():
    provider, _ = provider_for([])
    status = provider.status()
    assert status["mode"] == "metadata_only"
    assert status["message_bodies_requested"] is False
    assert status["mailbox_mutated"] is False


def test_announcement_result_is_read_only():
    provider, _ = provider_for(["Uno"])
    result = GmailStartupSubjectAnnouncer(
        provider, GmailSubjectAnnouncementPolicy(enabled=True)
    ).announce()
    assert result.read_only is True
    assert result.to_dict()["subjects"] == ("Uno",)


def test_policy_rejects_invalid_limits():
    try:
        GmailSubjectAnnouncementPolicy(max_subjects=0)
    except ValueError as exc:
        assert "limit" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_provider_rejects_invalid_limit_before_service_creation():
    provider = GoogleGmailUnreadSubjectProvider(
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("service called"))
    )
    try:
        provider.list_unread_subjects(limit=0)
    except ValueError as exc:
        assert "limit" in str(exc)
    else:
        raise AssertionError("expected ValueError")
