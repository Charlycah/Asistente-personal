from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping

from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)


class IsolationBoundaryViolation(ValueError):
    """Raised when material crosses the frozen H7 evaluation boundary."""


class RetryNotAuthorized(RuntimeError):
    """Raised when more than one attempt is requested for one H7 case."""


class RawCaptureAlreadySealed(RuntimeError):
    """Raised when a sealed raw H7 capture would be replaced."""


class PrimaryExecutionNotAuthorized(RuntimeError):
    """Raised while the H7 primary execution gate remains closed."""


_ALLOWED_CASE_FIELDS = frozenset(
    {"case_id", "difficulty", "domain", "scenario", "requirement"}
)
_ALLOWED_REQUIREMENT_FIELDS = frozenset(
    {"requirement_id", "source_reference", "world_snapshot_reference"}
)
_FORBIDDEN_FIELDS = frozenset(
    {
        "expected_class",
        "decisive_condition",
        "expected_planning_invocation_count",
        "required_authority",
        "ground_truth",
        "score",
        "scoring_mode",
    }
)


@dataclass
class IsolatedH7Case:
    case_id: str
    difficulty: str
    domain: str
    scenario: str
    requirement_id: str
    source_reference: str
    world_snapshot_reference: str
    attempt_count: int = 0
    raw_capture_sha256: str | None = None


@dataclass(frozen=True)
class RawH7Capture:
    case_id: str
    raw_result: str
    raw_result_sha256: str


class HCPDQV2H7IsolationAdapter:
    """Corpus-only H7 evaluation boundary with zero planning authority."""

    def __init__(self) -> None:
        self._active_case: IsolatedH7Case | None = None

    def build_roby_payload(
        self,
        case: Mapping[str, object],
    ) -> dict[str, object]:
        self.validate_corpus_case(case)
        requirement = case["requirement"]
        if not isinstance(requirement, Mapping):
            raise IsolationBoundaryViolation(
                "requirement must be a mapping"
            )
        return {
            "case_id": str(case["case_id"]),
            "difficulty": str(case["difficulty"]),
            "domain": str(case["domain"]),
            "scenario": str(case["scenario"]),
            "requirement": {
                "requirement_id": str(requirement["requirement_id"]),
                "source_reference": str(requirement["source_reference"]),
                "world_snapshot_reference": str(
                    requirement["world_snapshot_reference"]
                ),
            },
        }

    def validate_corpus_case(
        self,
        case: Mapping[str, object],
    ) -> None:
        fields = set(case)
        forbidden = fields & _FORBIDDEN_FIELDS
        if forbidden:
            raise IsolationBoundaryViolation(
                "ground-truth/scoring fields are forbidden: "
                + ", ".join(sorted(forbidden))
            )
        if fields != _ALLOWED_CASE_FIELDS:
            raise IsolationBoundaryViolation(
                "case must contain only frozen H7 corpus fields"
            )
        requirement = case["requirement"]
        if not isinstance(requirement, Mapping):
            raise IsolationBoundaryViolation(
                "requirement must be a mapping"
            )
        requirement_fields = set(requirement)
        forbidden_requirement = requirement_fields & _FORBIDDEN_FIELDS
        if forbidden_requirement:
            raise IsolationBoundaryViolation(
                "ground-truth/scoring requirement fields are forbidden"
            )
        if requirement_fields != _ALLOWED_REQUIREMENT_FIELDS:
            raise IsolationBoundaryViolation(
                "requirement contains non-corpus fields"
            )

    def open_case(
        self,
        case: Mapping[str, object],
    ) -> IsolatedH7Case:
        payload = self.build_roby_payload(case)
        requirement = payload["requirement"]
        if not isinstance(requirement, dict):
            raise IsolationBoundaryViolation(
                "validated requirement payload is invalid"
            )
        handle = IsolatedH7Case(
            case_id=str(payload["case_id"]),
            difficulty=str(payload["difficulty"]),
            domain=str(payload["domain"]),
            scenario=str(payload["scenario"]),
            requirement_id=str(requirement["requirement_id"]),
            source_reference=str(requirement["source_reference"]),
            world_snapshot_reference=str(
                requirement["world_snapshot_reference"]
            ),
        )
        self._active_case = handle
        return handle

    def mark_attempt(self, handle: IsolatedH7Case) -> None:
        self._require_active(handle)
        if handle.attempt_count >= 1:
            raise RetryNotAuthorized(
                "exactly one HCPDQ-v2 H7 attempt is authorized per case"
            )
        handle.attempt_count += 1

    def capture_raw(
        self,
        handle: IsolatedH7Case,
        raw_result: str,
    ) -> RawH7Capture:
        self._require_active(handle)
        if handle.attempt_count != 1:
            raise IsolationBoundaryViolation(
                "raw capture requires exactly one recorded attempt"
            )
        if handle.raw_capture_sha256 is not None:
            raise RawCaptureAlreadySealed(
                "sealed H7 raw capture cannot be replaced"
            )
        raw = str(raw_result)
        fingerprint = sha256(raw.encode("utf-8")).hexdigest()
        handle.raw_capture_sha256 = fingerprint
        return RawH7Capture(
            case_id=handle.case_id,
            raw_result=raw,
            raw_result_sha256=fingerprint,
        )

    def visible_prior_results(
        self,
        handle: IsolatedH7Case,
    ) -> tuple[()]:
        self._require_active(handle)
        return ()

    @staticmethod
    def build_productive_entry_path(
        registry: object,
    ) -> GovernedMultiStepInvestigationPlanningReentryV1:
        return GovernedMultiStepInvestigationPlanningReentryV1(registry)

    @staticmethod
    def authorized_capabilities() -> dict[str, bool]:
        return {
            "ground_truth_read": False,
            "scoring": False,
            "learning_write": False,
            "memory_write": False,
            "world_model_write": False,
            "benchmark_feedback": False,
            "action_execution": False,
        }

    def execute_primary_run(self) -> None:
        raise PrimaryExecutionNotAuthorized(
            "primary HCPDQ-v2 H7 execution is not authorized"
        )

    def _require_active(self, handle: IsolatedH7Case) -> None:
        if self._active_case is not handle:
            raise IsolationBoundaryViolation(
                "case handle is not the active isolated H7 case"
            )
