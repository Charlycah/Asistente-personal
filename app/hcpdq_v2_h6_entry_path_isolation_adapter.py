from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from app.official_conversation_gateway import OfficialConversationGateway


class IsolationBoundaryViolation(ValueError):
    """Raised when material crosses the frozen H6 evaluation boundary."""


class RetryNotAuthorized(RuntimeError):
    """Raised when a second attempt is requested for the same case."""


class PrimaryExecutionNotAuthorized(RuntimeError):
    """Raised while the H6 primary execution gate remains closed."""


_REQUIRED_SUBJECT_FIELDS = frozenset({"case_id", "prompt"})
_FORBIDDEN_SUBJECT_FIELDS = frozenset(
    {
        "expected",
        "expected_answer",
        "expected_outcome",
        "ground_truth",
        "ground_truth_reference",
        "human_answer",
        "previous_score",
        "rationale",
        "rubric",
        "score",
        "scoring_mode",
    }
)


@dataclass
class IsolatedH6Case:
    case_id: str
    prompt: str
    attempt_count: int = 0


@dataclass(frozen=True)
class RawH6Capture:
    case_id: str
    raw_response: str


class HCPDQV2H6EntryPathIsolationAdapter:
    """Ephemeral H6 evaluation boundary with no cognitive authority."""

    def __init__(self) -> None:
        self._active_case: IsolatedH6Case | None = None

    def build_subject_request(
        self,
        case_id: str,
        prompt: str,
    ) -> dict[str, str]:
        request = {
            "case_id": str(case_id),
            "prompt": str(prompt),
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
                "subject request must contain only case_id and prompt"
            )

    def open_case(
        self,
        case_id: str,
        prompt: str,
    ) -> IsolatedH6Case:
        self.validate_subject_request(
            self.build_subject_request(case_id, prompt)
        )
        handle = IsolatedH6Case(
            case_id=str(case_id),
            prompt=str(prompt),
        )
        self._active_case = handle
        return handle

    def mark_attempt(self, handle: IsolatedH6Case) -> None:
        self._require_active(handle)
        if handle.attempt_count >= 1:
            raise RetryNotAuthorized(
                "exactly one HCPDQ-v2 H6 attempt is authorized per case"
            )
        handle.attempt_count += 1

    def capture_raw(
        self,
        handle: IsolatedH6Case,
        raw_response: str,
    ) -> RawH6Capture:
        self._require_active(handle)
        return RawH6Capture(
            case_id=handle.case_id,
            raw_response=str(raw_response),
        )

    def visible_prior_results(
        self,
        handle: IsolatedH6Case,
    ) -> tuple[()]:
        self._require_active(handle)
        return ()

    @staticmethod
    def authorized_capabilities() -> dict[str, bool]:
        return {
            "learning_write": False,
            "memory_write": False,
            "benchmark_feedback": False,
            "persistent_state_write": False,
        }

    def build_official_gateway(self, runtime: object) -> OfficialConversationGateway:
        return OfficialConversationGateway(runtime)

    def execute_primary_run(self) -> None:
        raise PrimaryExecutionNotAuthorized(
            "primary HCPDQ-v2 H6 execution is not authorized"
        )

    def _require_active(self, handle: IsolatedH6Case) -> None:
        if self._active_case is not handle:
            raise IsolationBoundaryViolation(
                "case handle is not the active isolated case"
            )
