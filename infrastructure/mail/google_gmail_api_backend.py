from __future__ import annotations

import base64
import importlib
from collections.abc import Callable, Mapping
from email.message import EmailMessage
from types import MappingProxyType
from typing import Any, Protocol

from infrastructure.mail.attachments_governance import (
    AttachmentGovernanceError,
    GmailAttachmentsGovernance,
)
from infrastructure.mail.gmail_provider_transport import (
    GmailProviderAuthenticationError,
    GmailProviderRateLimitError,
    GmailProviderRejectedError,
    GmailTransportOperation,
)


class GmailApiRequest(Protocol):
    def execute(self) -> Mapping[str, Any]: ...


class GmailApiServiceFactory(Protocol):
    def __call__(self, *, timeout_seconds: float) -> Any: ...


class GoogleApiClientFactory:
    """Lazily builds a Gmail API client from deployment-owned credentials."""

    def __init__(self, credentials_loader: Callable[[], object]) -> None:
        self._credentials_loader = credentials_loader

    def __call__(self, *, timeout_seconds: float) -> Any:
        if timeout_seconds <= 0:
            raise ValueError("gmail api timeout must be positive")
        build = _import_symbol("googleapiclient.discovery", "build")
        credentials = self._credentials_loader()
        if credentials is None:
            raise GmailProviderAuthenticationError("credentials unavailable")
        return build(
            "gmail",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )


class GoogleGmailApiBackend:
    """M227.2 concrete Gmail API backend behind GmailProviderBackend."""

    USER_ID = "me"

    def __init__(
        self,
        service_factory: GmailApiServiceFactory,
        attachments_governance: GmailAttachmentsGovernance | None = None,
    ) -> None:
        self._service_factory = service_factory
        self._attachments_governance = (
            attachments_governance or GmailAttachmentsGovernance()
        )
        self._request_count = 0
        self._failure_count = 0
        self._last_operation: GmailTransportOperation | None = None

    def execute(
        self,
        operation: GmailTransportOperation,
        payload: Mapping[str, Any],
        *,
        timeout_seconds: float,
    ) -> Mapping[str, Any]:
        self._request_count += 1
        self._last_operation = operation
        try:
            service = self._service_factory(timeout_seconds=timeout_seconds)
            request = self._build_request(service, operation, payload)
            response = request.execute()
        except (
            AttachmentGovernanceError,
            GmailProviderAuthenticationError,
            GmailProviderRateLimitError,
            GmailProviderRejectedError,
            TimeoutError,
            ConnectionError,
            OSError,
        ):
            self._failure_count += 1
            raise
        except Exception as exc:
            self._failure_count += 1
            self._raise_normalized(exc)
        if not isinstance(response, Mapping):
            self._failure_count += 1
            raise GmailProviderRejectedError("gmail api response must be an object")
        return MappingProxyType(self._normalize_response(operation, response))

    def status(self) -> dict[str, object]:
        return {
            "provider": "gmail",
            "backend": "google_api",
            "request_count": self._request_count,
            "failure_count": self._failure_count,
            "last_operation": (
                self._last_operation.value if self._last_operation is not None else None
            ),
        }

    def _build_request(
        self,
        service: Any,
        operation: GmailTransportOperation,
        payload: Mapping[str, Any],
    ) -> GmailApiRequest:
        users = service.users()
        if operation is GmailTransportOperation.LIST_RECENT:
            return users.messages().list(
                userId=self.USER_ID,
                maxResults=int(payload.get("limit", 10)),
            )
        if operation is GmailTransportOperation.SEARCH:
            return users.messages().list(
                userId=self.USER_ID,
                q=str(payload["query"]),
                maxResults=int(payload.get("limit", 10)),
            )
        if operation is GmailTransportOperation.READ:
            return users.messages().get(
                userId=self.USER_ID,
                id=str(payload["message_id"]),
                format="full",
            )
        message_body = self._message_body(payload)
        if operation is GmailTransportOperation.CREATE_DRAFT:
            return users.drafts().create(
                userId=self.USER_ID,
                body={"message": message_body},
            )
        if operation is GmailTransportOperation.SEND:
            return users.messages().send(
                userId=self.USER_ID,
                body=message_body,
            )
        raise ValueError("unsupported gmail api operation")

    def _message_body(self, payload: Mapping[str, Any]) -> dict[str, str]:
        message = EmailMessage()
        recipients = payload["to"]
        if isinstance(recipients, str):
            recipients = (recipients,)
        message["To"] = ", ".join(str(item) for item in recipients)
        message["Subject"] = str(payload["subject"])
        message.set_content(str(payload["body"]))
        attachments = payload.get("attachments", ())
        governed = self._attachments_governance.govern_outbound(attachments)
        for attachment in governed:
            maintype, subtype = str(attachment["content_type"]).split("/", 1)
            message.add_attachment(
                attachment["content"],
                maintype=maintype,
                subtype=subtype,
                filename=str(attachment["filename"]),
            )
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        body = {"raw": raw}
        thread_id = payload.get("thread_id")
        if thread_id:
            body["threadId"] = str(thread_id)
        return body

    @staticmethod
    def _normalize_response(
        operation: GmailTransportOperation,
        response: Mapping[str, Any],
    ) -> dict[str, Any]:
        if operation in {
            GmailTransportOperation.LIST_RECENT,
            GmailTransportOperation.SEARCH,
        }:
            messages = response.get("messages", ())
            if not isinstance(messages, (list, tuple)):
                messages = ()
            normalized: dict[str, Any] = {
                "messages": tuple(
                    {
                        "id": str(item.get("id", "")),
                        "thread_id": str(item.get("threadId", "")),
                    }
                    for item in messages
                    if isinstance(item, Mapping) and item.get("id")
                )
            }
            if response.get("nextPageToken"):
                normalized["next_page_token"] = str(response["nextPageToken"])
            if isinstance(response.get("resultSizeEstimate"), int):
                normalized["result_size_estimate"] = response["resultSizeEstimate"]
            return normalized
        if operation is GmailTransportOperation.READ:
            return {
                "id": str(response.get("id", "")),
                "thread_id": str(response.get("threadId", "")),
                "label_ids": tuple(str(item) for item in response.get("labelIds", ())),
                "snippet": str(response.get("snippet", "")),
                "payload": response.get("payload", {}),
            }
        return {
            "id": str(response.get("id", "")),
            "thread_id": str(response.get("threadId", "")),
            "message_id": str(
                response.get("message", {}).get("id", "")
                if isinstance(response.get("message"), Mapping)
                else ""
            ),
        }

    @staticmethod
    def _raise_normalized(exc: Exception) -> None:
        status = _http_status(exc)
        if status == 401:
            raise GmailProviderAuthenticationError(
                "gmail api authentication failed"
            ) from exc
        if status == 429:
            raise GmailProviderRateLimitError("gmail api rate limited") from exc
        if status in {408, 504}:
            raise TimeoutError("gmail api request timed out") from exc
        if status is not None and status >= 500:
            raise ConnectionError("gmail api unavailable") from exc
        if status in {400, 403, 404, 409, 412}:
            raise GmailProviderRejectedError("gmail api request rejected") from exc
        raise ConnectionError("gmail api request failed") from exc


def _http_status(exc: Exception) -> int | None:
    response = getattr(exc, "resp", None)
    status = getattr(response, "status", None)
    return status if isinstance(status, int) else None


def _import_symbol(module_name: str, symbol_name: str) -> Any:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError("gmail api deployment dependency unavailable") from exc
    try:
        return getattr(module, symbol_name)
    except AttributeError as exc:
        raise ImportError("gmail api deployment dependency incomplete") from exc
