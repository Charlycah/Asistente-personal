from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Protocol
from uuid import uuid4

from infrastructure.mail.gmail_oauth_governance import (
    GmailOAuthGovernance,
    GmailOAuthState,
)


class GmailTransportOperation(str, Enum):
    """Canonical provider operations accepted by the Gmail transport boundary."""

    LIST_RECENT = "list_recent"
    SEARCH = "search"
    READ = "read"
    CREATE_DRAFT = "create_draft"
    SEND = "send"


class GmailTransportErrorCode(str, Enum):
    """Secret-free error taxonomy published outside the provider boundary."""

    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"
    REJECTED = "rejected"
    INVALID_RESPONSE = "invalid_response"


class GmailProviderAuthenticationError(RuntimeError):
    """Backend signal indicating that provider credentials were rejected."""


class GmailProviderRateLimitError(RuntimeError):
    """Backend signal indicating that the provider rejected request volume."""


class GmailProviderRejectedError(RuntimeError):
    """Backend signal indicating a valid request was rejected by Gmail."""


class GmailProviderTransportError(RuntimeError):
    """Normalized provider failure that never includes backend exception text."""

    def __init__(
        self,
        code: GmailTransportErrorCode,
        operation: GmailTransportOperation,
        *,
        retryable: bool,
    ) -> None:
        self.code = code
        self.operation = operation
        self.retryable = retryable
        super().__init__(f"gmail provider transport failed: {code.value}")

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "operation": self.operation.value,
            "retryable": self.retryable,
        }


class GmailProviderBackend(Protocol):
    """Provider-specific implementation hidden behind the governed transport."""

    def execute(
        self,
        operation: GmailTransportOperation,
        payload: Mapping[str, Any],
        *,
        timeout_seconds: float,
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class GmailProviderTransportPolicy:
    """Local transport limits independent from provider SDK configuration."""

    timeout_seconds: float = 30.0
    max_result_items: int = 25

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("gmail transport timeout must be positive")
        if self.max_result_items <= 0:
            raise ValueError("gmail transport result limit must be positive")


@dataclass(frozen=True)
class GmailTransportResult:
    """Immutable transport result with payload kept behind the transport boundary."""

    operation: GmailTransportOperation
    payload: Mapping[str, Any]
    transport_id: str = field(default_factory=lambda: uuid4().hex)
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.transport_id.strip():
            raise ValueError("gmail transport id must not be empty")
        if self.completed_at.tzinfo is None:
            raise ValueError("gmail transport timestamp must be timezone-aware")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))

    def status(self) -> dict[str, object]:
        return {
            "transport_id": self.transport_id,
            "operation": self.operation.value,
            "completed_at": self.completed_at.isoformat(),
            "payload_field_count": len(self.payload),
        }


class GmailProviderTransport:
    """M226.6 OAuth-aware and error-normalizing Gmail provider transport."""

    PROVIDER = "gmail"
    TRANSPORT = "provider_api"

    _REQUIRED_FIELDS = {
        GmailTransportOperation.LIST_RECENT: (),
        GmailTransportOperation.SEARCH: ("query",),
        GmailTransportOperation.READ: ("message_id",),
        GmailTransportOperation.CREATE_DRAFT: ("to", "subject", "body"),
        GmailTransportOperation.SEND: ("to", "subject", "body"),
    }

    def __init__(
        self,
        backend: GmailProviderBackend,
        oauth: GmailOAuthGovernance,
        policy: GmailProviderTransportPolicy | None = None,
    ) -> None:
        self.backend = backend
        self.oauth = oauth
        self.policy = policy or GmailProviderTransportPolicy()
        self._request_count = 0
        self._failure_count = 0
        self._last_operation: GmailTransportOperation | None = None

    def execute(
        self,
        operation: GmailTransportOperation | str,
        payload: Mapping[str, Any] | None = None,
        *,
        now: datetime | None = None,
    ) -> GmailTransportResult:
        resolved = self._resolve_operation(operation)
        request_payload = dict(payload or {})
        self._validate_payload(resolved, request_payload)
        self._require_ready_oauth(resolved, now=now)
        self._request_count += 1
        self._last_operation = resolved
        try:
            response = self.backend.execute(
                resolved,
                MappingProxyType(request_payload),
                timeout_seconds=self.policy.timeout_seconds,
            )
        except GmailProviderTransportError:
            self._failure_count += 1
            raise
        except GmailProviderAuthenticationError as exc:
            self._failure_count += 1
            raise self._error(
                GmailTransportErrorCode.AUTHENTICATION, resolved, retryable=False
            ) from exc
        except TimeoutError as exc:
            self._failure_count += 1
            raise self._error(
                GmailTransportErrorCode.TIMEOUT, resolved, retryable=True
            ) from exc
        except GmailProviderRateLimitError as exc:
            self._failure_count += 1
            raise self._error(
                GmailTransportErrorCode.RATE_LIMITED, resolved, retryable=True
            ) from exc
        except GmailProviderRejectedError as exc:
            self._failure_count += 1
            raise self._error(
                GmailTransportErrorCode.REJECTED, resolved, retryable=False
            ) from exc
        except (ConnectionError, OSError) as exc:
            self._failure_count += 1
            raise self._error(
                GmailTransportErrorCode.UNAVAILABLE, resolved, retryable=True
            ) from exc
        except Exception as exc:  # pragma: no cover - defensive provider boundary
            self._failure_count += 1
            raise self._error(
                GmailTransportErrorCode.UNAVAILABLE, resolved, retryable=True
            ) from exc
        if not isinstance(response, Mapping):
            self._failure_count += 1
            raise self._error(
                GmailTransportErrorCode.INVALID_RESPONSE,
                resolved,
                retryable=False,
            )
        return GmailTransportResult(operation=resolved, payload=response)

    def status(self) -> dict[str, object]:
        """Returns transport health metadata without credentials or payload values."""

        return {
            "provider": self.PROVIDER,
            "transport": self.TRANSPORT,
            "timeout_seconds": self.policy.timeout_seconds,
            "max_result_items": self.policy.max_result_items,
            "request_count": self._request_count,
            "failure_count": self._failure_count,
            "last_operation": (
                self._last_operation.value if self._last_operation is not None else None
            ),
            "oauth_state": self.oauth.inspect().state.value,
        }

    @staticmethod
    def _resolve_operation(
        operation: GmailTransportOperation | str,
    ) -> GmailTransportOperation:
        if isinstance(operation, GmailTransportOperation):
            return operation
        normalized = operation.strip().casefold()
        try:
            return GmailTransportOperation(normalized)
        except ValueError as exc:
            raise ValueError("unsupported gmail transport operation") from exc

    def _validate_payload(
        self,
        operation: GmailTransportOperation,
        payload: Mapping[str, Any],
    ) -> None:
        missing = tuple(
            field
            for field in self._REQUIRED_FIELDS[operation]
            if not self._is_present(payload.get(field))
        )
        if missing:
            raise ValueError(
                "gmail transport payload missing required fields: " + ", ".join(missing)
            )
        limit = payload.get("limit")
        if limit is not None:
            if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
                raise ValueError("gmail transport limit must be a positive integer")
            if limit > self.policy.max_result_items:
                raise ValueError("gmail transport limit exceeds local policy")

    def _require_ready_oauth(
        self,
        operation: GmailTransportOperation,
        *,
        now: datetime | None,
    ) -> None:
        if self.oauth.inspect(now=now).state is GmailOAuthState.READY:
            return
        self._failure_count += 1
        raise self._error(
            GmailTransportErrorCode.AUTHENTICATION,
            operation,
            retryable=False,
        )

    @staticmethod
    def _is_present(value: Any) -> bool:
        return value is not None and value != "" and value != () and value != []

    @staticmethod
    def _error(
        code: GmailTransportErrorCode,
        operation: GmailTransportOperation,
        *,
        retryable: bool,
    ) -> GmailProviderTransportError:
        return GmailProviderTransportError(
            code,
            operation,
            retryable=retryable,
        )
