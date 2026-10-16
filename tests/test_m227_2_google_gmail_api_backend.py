from __future__ import annotations

import base64
from email import message_from_bytes
from types import SimpleNamespace

import pytest

from infrastructure.mail.gmail_provider_transport import (
    GmailProviderAuthenticationError,
    GmailProviderRateLimitError,
    GmailProviderRejectedError,
    GmailTransportOperation,
)
from infrastructure.mail.google_gmail_api_backend import (
    GoogleApiClientFactory,
    GoogleGmailApiBackend,
)


class Request:
    def __init__(self, response=None, error=None):
        self.response = {} if response is None else response
        self.error = error

    def execute(self):
        if self.error is not None:
            raise self.error
        return self.response


class Resource:
    def __init__(self, service, name):
        self.service = service
        self.name = name

    def list(self, **kwargs):
        self.service.calls.append(("list", kwargs))
        return self.service.request

    def get(self, **kwargs):
        self.service.calls.append(("get", kwargs))
        return self.service.request

    def create(self, **kwargs):
        self.service.calls.append(("create", kwargs))
        return self.service.request

    def send(self, **kwargs):
        self.service.calls.append(("send", kwargs))
        return self.service.request


class Users:
    def __init__(self, service):
        self.service = service

    def messages(self):
        return Resource(self.service, "messages")

    def drafts(self):
        return Resource(self.service, "drafts")


class Service:
    def __init__(self, response=None, error=None):
        self.request = Request(response, error)
        self.calls = []

    def users(self):
        return Users(self)


def backend(service):
    timeouts = []

    def factory(*, timeout_seconds):
        timeouts.append(timeout_seconds)
        return service

    return GoogleGmailApiBackend(factory), timeouts


def test_list_recent_maps_to_gmail_messages_list():
    service = Service({"messages": [{"id": "m1", "threadId": "t1"}]})
    item, timeouts = backend(service)
    result = item.execute(
        GmailTransportOperation.LIST_RECENT, {"limit": 5}, timeout_seconds=7.0
    )
    assert service.calls == [("list", {"userId": "me", "maxResults": 5})]
    assert result["messages"] == ({"id": "m1", "thread_id": "t1"},)
    assert timeouts == [7.0]


def test_search_maps_query_and_limit():
    service = Service({"messages": []})
    item, _ = backend(service)
    item.execute(
        GmailTransportOperation.SEARCH,
        {"query": "from:ana", "limit": 3},
        timeout_seconds=4.0,
    )
    assert service.calls[0] == (
        "list",
        {"userId": "me", "q": "from:ana", "maxResults": 3},
    )


def test_read_maps_to_full_message_get():
    service = Service({"id": "m1", "threadId": "t1", "snippet": "hello"})
    item, _ = backend(service)
    result = item.execute(
        GmailTransportOperation.READ, {"message_id": "m1"}, timeout_seconds=4.0
    )
    assert service.calls[0] == (
        "get",
        {"userId": "me", "id": "m1", "format": "full"},
    )
    assert result["snippet"] == "hello"


def test_create_draft_builds_urlsafe_mime_message():
    service = Service({"id": "d1", "message": {"id": "m1"}})
    item, _ = backend(service)
    result = item.execute(
        GmailTransportOperation.CREATE_DRAFT,
        {"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
        timeout_seconds=4.0,
    )
    call, kwargs = service.calls[0]
    raw = kwargs["body"]["message"]["raw"]
    message = message_from_bytes(base64.urlsafe_b64decode(raw))
    assert call == "create"
    assert message["To"] == "ana@example.com"
    assert message["Subject"] == "Hola"
    assert "Texto" in message.get_payload()
    assert result["message_id"] == "m1"


def test_send_builds_message_and_preserves_thread_id():
    service = Service({"id": "m2", "threadId": "t1"})
    item, _ = backend(service)
    result = item.execute(
        GmailTransportOperation.SEND,
        {
            "to": "ana@example.com",
            "subject": "Re: Hola",
            "body": "Respuesta",
            "thread_id": "t1",
        },
        timeout_seconds=4.0,
    )
    assert service.calls[0][0] == "send"
    assert service.calls[0][1]["body"]["threadId"] == "t1"
    assert result["id"] == "m2"


def test_status_never_contains_payload_values():
    service = Service({"id": "private-message"})
    item, _ = backend(service)
    item.execute(
        GmailTransportOperation.READ,
        {"message_id": "private-message"},
        timeout_seconds=4.0,
    )
    assert "private-message" not in repr(item.status())
    assert item.status()["request_count"] == 1


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (401, GmailProviderAuthenticationError),
        (429, GmailProviderRateLimitError),
        (403, GmailProviderRejectedError),
        (503, ConnectionError),
    ],
)
def test_http_failures_are_normalized(status, error_type):
    error = RuntimeError("private provider detail")
    error.resp = SimpleNamespace(status=status)
    item, _ = backend(Service(error=error))
    with pytest.raises(error_type) as captured:
        item.execute(GmailTransportOperation.LIST_RECENT, {}, timeout_seconds=4.0)
    assert "private provider detail" not in str(captured.value)


def test_non_mapping_response_is_rejected():
    item, _ = backend(Service(["invalid"]))
    with pytest.raises(GmailProviderRejectedError):
        item.execute(GmailTransportOperation.LIST_RECENT, {}, timeout_seconds=4.0)


def test_google_client_factory_rejects_absent_credentials_before_build(monkeypatch):
    factory = GoogleApiClientFactory(lambda: None)
    monkeypatch.setattr(
        "infrastructure.mail.google_gmail_api_backend._import_symbol",
        lambda *_: lambda *args, **kwargs: object(),
    )
    with pytest.raises(GmailProviderAuthenticationError):
        factory(timeout_seconds=5.0)
