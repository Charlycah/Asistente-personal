from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from core.device_capabilities import CapabilityMatchStatus
from core.device_continuity import SessionContinuityStatus

from .models import (
    ContextSensitivity,
    ContextTransferAction,
    ContextTransferManifest,
    ContextTransferPolicy,
    ContextTransferRepository,
    ContextTransferRequest,
    ContextTransferStatus,
    InMemoryContextTransferRepository,
)


class CrossDeviceContextTransfer:
    """Prepares an auditable transfer manifest without transporting context."""

    def __init__(
        self,
        *,
        repository: ContextTransferRepository | None = None,
        policy: ContextTransferPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryContextTransferRepository()
        self.policy = policy or ContextTransferPolicy()

    def prepare(
        self,
        request: ContextTransferRequest,
        *,
        now: datetime | None = None,
    ) -> ContextTransferManifest:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("context transfer evaluation timestamp must be aware")
        self._validate_chain(request)
        status, action, included, excluded, review, rationale = self._evaluate(
            request, timestamp
        )
        digest = None
        cursor = None
        if status is ContextTransferStatus.READY:
            cursor = request.continuity.resume_cursor
            digest = sha256(
                "|".join(
                    (
                        cursor or "",
                        *(
                            f"{item.fragment_id}:{item.revision}:{item.content_digest}"
                            for item in request.fragments
                            if item.fragment_id in included
                        ),
                    )
                ).encode("utf-8")
            ).hexdigest()
        manifest = ContextTransferManifest(
            request,
            status,
            action,
            included,
            excluded,
            review,
            cursor,
            digest,
            rationale,
            timestamp,
        )
        self.repository.add(manifest)
        return manifest

    def _validate_chain(self, request: ContextTransferRequest) -> None:
        session = request.continuity.request.session
        target = request.continuity.request.target.device
        match = request.capability_match
        if request.owner != session.owner or request.owner != target.owner:
            raise ValueError("context transfer ownership is inconsistent")
        if match.device != target:
            raise ValueError("capability match must describe continuity target")
        for fragment in request.fragments:
            if (
                fragment.owner != request.owner
                or fragment.session_id != session.session_id
            ):
                raise ValueError(
                    "context fragment ownership or session is inconsistent"
                )

    def _evaluate(self, request: ContextTransferRequest, now: datetime):
        continuity = request.continuity
        match = request.capability_match
        if continuity.status is not SessionContinuityStatus.READY:
            return self._blocked("continuity_not_ready")
        if self.policy.require_satisfied_capabilities:
            if match.status is CapabilityMatchStatus.REVIEW_REQUIRED:
                return self._review("capabilities_require_review")
            if match.status is not CapabilityMatchStatus.SATISFIED:
                return self._blocked("capabilities_not_satisfied")
        if not request.fragments:
            return (
                ContextTransferStatus.NOT_APPLICABLE,
                ContextTransferAction.NONE,
                (),
                (),
                (),
                ("no_context_fragments",),
            )
        if len(request.fragments) > self.policy.max_fragments:
            return self._review("fragment_limit_exceeded")
        required = {item.name for item in match.requirements}
        included: list[str] = []
        excluded: list[str] = []
        review: list[str] = []
        rationale: list[str] = []
        for fragment in request.fragments:
            if fragment.expires_at is not None and fragment.expires_at <= now:
                excluded.append(fragment.fragment_id)
                rationale.append(f"expired:{fragment.fragment_id}")
                continue
            if not set(fragment.required_capabilities).issubset(required):
                excluded.append(fragment.fragment_id)
                rationale.append(f"capability_gap:{fragment.fragment_id}")
                continue
            if fragment.sensitivity is ContextSensitivity.RESTRICTED:
                if not self.policy.allow_restricted:
                    excluded.append(fragment.fragment_id)
                    rationale.append(f"restricted:{fragment.fragment_id}")
                    continue
            if fragment.sensitivity is ContextSensitivity.SENSITIVE:
                if not self.policy.allow_sensitive:
                    excluded.append(fragment.fragment_id)
                    rationale.append(f"sensitive_blocked:{fragment.fragment_id}")
                    continue
                if self.policy.review_sensitive:
                    review.append(fragment.fragment_id)
                    rationale.append(f"sensitive_review:{fragment.fragment_id}")
                    continue
            included.append(fragment.fragment_id)
        if review:
            return (
                ContextTransferStatus.REVIEW_REQUIRED,
                ContextTransferAction.CONFIRM,
                tuple(included),
                tuple(excluded),
                tuple(review),
                tuple(rationale) or ("context_requires_review",),
            )
        if not included:
            return self._blocked(*(rationale or ["no_transferable_context"]))
        return (
            ContextTransferStatus.READY,
            ContextTransferAction.PREPARE,
            tuple(included),
            tuple(excluded),
            (),
            tuple(rationale) or ("context_manifest_ready",),
        )

    @staticmethod
    def _blocked(*rationale: str):
        return (
            ContextTransferStatus.BLOCKED,
            ContextTransferAction.STAY,
            (),
            (),
            (),
            tuple(rationale),
        )

    @staticmethod
    def _review(*rationale: str):
        return (
            ContextTransferStatus.REVIEW_REQUIRED,
            ContextTransferAction.CONFIRM,
            (),
            (),
            (),
            tuple(rationale),
        )
