from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from scripts.hcpdq_v2_h6_h7_exposure_isolation_protocol import (
    ExposureIsolationPolicy,
    SubjectEnvelope,
)


class IsolationBoundaryViolation(ValueError):
    """Raised when evaluation material crosses the frozen subject boundary."""


class PrimaryExecutionNotAuthorized(RuntimeError):
    """Raised while the primary held-out execution gate remains closed."""


_FORBIDDEN_SUBJECT_FIELDS = frozenset(
    {
        "expected",
        "expected_answer",
        "expected_outcome",
        "ground_truth",
        "ground_truth_reference",
        "held_out_solution",
        "human_answer",
        "previous_score",
        "rationale",
        "required_structure",
        "rubric",
        "score",
        "scoring_mode",
    }
)

_REQUIRED_SUBJECT_FIELDS = frozenset(
    {"case_id", "family", "difficulty", "prompt"}
)


@dataclass
class IsolatedCaseHandle:
    case_id: str
    family: str
    difficulty: str
    prompt: str
    raw_capture: str | None = None


class HCPDQV2H6H7IsolationAdapter:
    """Ephemeral H6/H7 evaluation boundary with zero cognitive authority."""

    def __init__(self, *, policy: ExposureIsolationPolicy) -> None:
        self._policy = policy
        self._active_case: IsolatedCaseHandle | None = None

    def build_subject_request(
        self,
        envelope: SubjectEnvelope,
    ) -> dict[str, str]:
        request = {
            "case_id": envelope.case_id,
            "family": envelope.family,
            "difficulty": envelope.difficulty,
            "prompt": envelope.prompt,
        }
        self.validate_subject_request(request)
        return request

    def validate_subject_request(
        self,
        request: Mapping[str, object],
    ) -> None:
        fields = set(request)
        forbidden = fields & _FORBIDDEN_SUBJECT_FIELDS
        if forbidden:
            raise IsolationBoundaryViolation(
                "ground-truth/scoring material is forbidden: "
                + ", ".join(sorted(forbidden))
            )
        if fields != _REQUIRED_SUBJECT_FIELDS:
            raise IsolationBoundaryViolation(
                "subject request must contain only the frozen envelope fields"
            )
        family = str(request["family"]).strip().upper()
        if family not in self._policy.allowed_families:
            raise IsolationBoundaryViolation(
                "case family is outside the frozen HCPDQ-v2 scope"
            )

    def authorized_capabilities(self) -> dict[str, bool]:
        return {
            "memory_write": self._policy.allow_memory_writes,
            "learning_write": self._policy.allow_learning_writes,
            "persistent_state_write": self._policy.allow_persistent_state_writes,
            "adaptation": (
                self._policy.allow_threshold_adaptation
                or self._policy.allow_self_improvement
            ),
        }

    def open_case(
        self,
        envelope: SubjectEnvelope,
    ) -> IsolatedCaseHandle:
        self.validate_subject_request(self.build_subject_request(envelope))
        handle = IsolatedCaseHandle(
            case_id=envelope.case_id,
            family=envelope.family,
            difficulty=envelope.difficulty,
            prompt=envelope.prompt,
        )
        self._active_case = handle
        return handle

    def capture_raw(
        self,
        handle: IsolatedCaseHandle,
        raw_result: str,
    ) -> None:
        self._require_active(handle)
        handle.raw_capture = str(raw_result)

    def visible_prior_results(
        self,
        handle: IsolatedCaseHandle,
    ) -> tuple[()]:
        self._require_active(handle)
        return ()

    def scoring_allowed(self, handle: IsolatedCaseHandle) -> bool:
        self._require_active(handle)
        return handle.raw_capture is not None

    def execute_primary_run(
        self,
        envelopes: Iterable[SubjectEnvelope],
    ) -> None:
        del envelopes
        raise PrimaryExecutionNotAuthorized(
            "primary HCPDQ-v2 held-out execution is not authorized"
        )

    def _require_active(self, handle: IsolatedCaseHandle) -> None:
        if self._active_case is not handle:
            raise IsolationBoundaryViolation(
                "case handle is not the active isolated case"
            )
