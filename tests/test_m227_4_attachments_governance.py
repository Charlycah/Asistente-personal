from __future__ import annotations

import base64
from email import message_from_bytes

import pytest

from infrastructure.mail.attachments_governance import (
    AttachmentDisposition,
    AttachmentGovernanceError,
    AttachmentPolicy,
    GmailAttachmentsGovernance,
)
from infrastructure.mail.gmail_provider_transport import GmailTransportOperation
from infrastructure.mail.google_gmail_api_backend import GoogleGmailApiBackend


def attachment(**overrides):
    item = {
        "filename": "report.txt",
        "content_type": "text/plain",
        "content": b"hello",
    }
    item.update(overrides)
    return item


def test_outbound_attachment_is_normalized_and_hashed():
    governed = GmailAttachmentsGovernance().govern_outbound([attachment()])
    assert governed[0]["size_bytes"] == 5
    assert len(governed[0]["sha256"]) == 64


def test_path_components_are_removed_from_filename():
    governed = GmailAttachmentsGovernance().govern_outbound(
        [attachment(filename="../../private/report.txt")]
    )
    assert governed[0]["filename"] == "report.txt"


def test_blocked_extension_is_rejected():
    with pytest.raises(AttachmentGovernanceError, match="extension blocked"):
        GmailAttachmentsGovernance().govern_outbound([attachment(filename="run.exe")])


def test_unknown_outbound_content_type_is_rejected():
    with pytest.raises(AttachmentGovernanceError, match="content type blocked"):
        GmailAttachmentsGovernance().govern_outbound(
            [attachment(content_type="application/x-private")]
        )


def test_unknown_inbound_type_is_quarantined():
    decision = GmailAttachmentsGovernance().inspect_inbound(
        [
            {
                "filename": "sample.bin",
                "content_type": "application/x-private",
                "size_bytes": 3,
                "sha256": "a" * 64,
            }
        ]
    )[0]
    assert decision.disposition is AttachmentDisposition.QUARANTINED


def test_attachment_size_limit_is_enforced():
    policy = AttachmentPolicy(max_attachment_bytes=4, max_total_bytes=8)
    with pytest.raises(AttachmentGovernanceError, match="size limit"):
        GmailAttachmentsGovernance(policy).govern_outbound(
            [attachment(content=b"12345")]
        )


def test_total_size_limit_is_enforced():
    policy = AttachmentPolicy(max_attachment_bytes=5, max_total_bytes=6)
    with pytest.raises(AttachmentGovernanceError, match="total attachment"):
        GmailAttachmentsGovernance(policy).govern_outbound(
            [attachment(content=b"1234"), attachment(filename="b.txt", content=b"5678")]
        )


def test_attachment_count_limit_is_enforced():
    policy = AttachmentPolicy(max_attachment_count=1)
    with pytest.raises(AttachmentGovernanceError, match="count limit"):
        GmailAttachmentsGovernance(policy).govern_outbound(
            [attachment(), attachment(filename="b.txt")]
        )


def test_non_bytes_content_is_rejected():
    with pytest.raises(AttachmentGovernanceError, match="must be bytes"):
        GmailAttachmentsGovernance().govern_outbound([attachment(content="secret")])


def test_status_is_secret_free():
    governance = GmailAttachmentsGovernance()
    governance.govern_outbound([attachment(content=b"private bytes")])
    assert "private" not in repr(governance.status())
    assert governance.status()["evaluated"] == 1


class Request:
    def __init__(self):
        self.kwargs = None

    def execute(self):
        return {"id": "m1"}


class Messages:
    def __init__(self, request):
        self.request = request

    def send(self, **kwargs):
        self.request.kwargs = kwargs
        return self.request


class Users:
    def __init__(self, request):
        self.request = request

    def messages(self):
        return Messages(self.request)


class Service:
    def __init__(self):
        self.request = Request()

    def users(self):
        return Users(self.request)


def test_backend_builds_multipart_message_with_governed_attachment():
    service = Service()
    backend = GoogleGmailApiBackend(lambda **_: service)
    backend.execute(
        GmailTransportOperation.SEND,
        {
            "to": "ana@example.com",
            "subject": "Report",
            "body": "Attached",
            "attachments": [attachment()],
        },
        timeout_seconds=4.0,
    )
    raw = service.request.kwargs["body"]["raw"]
    message = message_from_bytes(base64.urlsafe_b64decode(raw))
    parts = list(message.walk())
    assert any(part.get_filename() == "report.txt" for part in parts)


def test_backend_rejects_attachment_before_api_request():
    service = Service()
    backend = GoogleGmailApiBackend(lambda **_: service)
    with pytest.raises(AttachmentGovernanceError):
        backend.execute(
            GmailTransportOperation.SEND,
            {
                "to": "ana@example.com",
                "subject": "Unsafe",
                "body": "No",
                "attachments": [attachment(filename="run.exe")],
            },
            timeout_seconds=4.0,
        )
    assert service.request.kwargs is None
