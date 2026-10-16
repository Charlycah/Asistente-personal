from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Callable, Mapping

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.high_load_cognitive_scheduling import CognitiveAdmissionDisposition
from core.llm_provider import LLMRequest
from core.long_running_stability import (
    LongRunningStabilityAssessment,
    LongRunningStabilityMonitor,
    LongRunningStabilityState,
)
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class ConcurrentExecutionStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    IDLE = "idle"


class ConcurrentTaskStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ConcurrentCognitiveTask:
    sequence: int
    action: str
    priority: int

    def __post_init__(self) -> None:
        action = self.action.strip()
        if self.sequence < 1:
            raise ValueError("concurrent task sequence must be positive")
        if not action:
            raise ValueError("concurrent task action must not be blank")
        if not 0 <= self.priority <= 100:
            raise ValueError("concurrent task priority must be bounded")
        object.__setattr__(self, "action", action)


@dataclass(frozen=True)
class ConcurrentTaskResult:
    sequence: int
    action: str
    status: ConcurrentTaskStatus | str
    value: str = ""
    error: str = ""

    def __post_init__(self) -> None:
        action = self.action.strip()
        status = ConcurrentTaskStatus(self.status)
        if self.sequence < 1 or not action:
            raise ValueError("concurrent result identity is invalid")
        if status is ConcurrentTaskStatus.FAILED and not self.error.strip():
            raise ValueError("failed concurrent result requires an error")
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "value", self.value.strip())
        object.__setattr__(self, "error", self.error.strip())


@dataclass(frozen=True)
class ConcurrentCognitiveExecution:
    owner: str
    session_id: str
    status: ConcurrentExecutionStatus | str
    worker_limit: int
    tasks: tuple[ConcurrentCognitiveTask, ...]
    results: tuple[ConcurrentTaskResult, ...]
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_id: str = ""

    def __post_init__(self) -> None:
        owner, session_id = self.owner.strip(), self.session_id.strip()
        status = ConcurrentExecutionStatus(self.status)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("concurrent execution identity must be complete")
        if self.worker_limit < 1:
            raise ValueError("concurrent execution worker limit must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("concurrent execution time must be timezone-aware")
        sequences = tuple(item.sequence for item in self.tasks)
        if sequences != tuple(range(1, len(self.tasks) + 1)):
            raise ValueError("concurrent tasks must be contiguous")
        if tuple(item.sequence for item in self.results) != sequences:
            raise ValueError("concurrent results must preserve task order")
        if len(set(references)) != len(references):
            raise ValueError("concurrent execution references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    str(self.worker_limit),
                    *(
                        f"{item.sequence}:{item.action}:{item.priority}"
                        for item in self.tasks
                    ),
                    *(
                        f"{item.sequence}:{item.action}:{item.status.value}:{item.value}:{item.error}"
                        for item in self.results
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.execution_id and self.execution_id != expected:
            raise ValueError("concurrent execution id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "execution_id", expected)


class ConcurrentCognitiveExecutor:
    """Execute admitted cognitive work concurrently with deterministic joining."""

    def __init__(
        self, stability: LongRunningStabilityMonitor, *, max_workers: int = 4
    ) -> None:
        if max_workers < 1:
            raise ValueError("concurrent executor max workers must be positive")
        self.stability = stability
        self.max_workers = max_workers
        self.last_execution: ConcurrentCognitiveExecution | None = None

    def execute(
        self,
        *,
        owner: str,
        session_id: str,
        handlers: Mapping[str, Callable[[], object]],
        demand_units: int | None = None,
        now: datetime | None = None,
    ) -> ConcurrentCognitiveExecution:
        timestamp = now or datetime.now(timezone.utc)
        assessment = self.stability.assess(
            owner=owner, session_id=session_id, demand_units=demand_units, now=timestamp
        )
        result = self.execute_assessment(assessment, handlers)
        self.last_execution = result
        return result

    def execute_assessment(
        self,
        assessment: LongRunningStabilityAssessment,
        handlers: Mapping[str, Callable[[], object]],
    ) -> ConcurrentCognitiveExecution:
        schedule = self.stability.scheduler.last_schedule
        if schedule is None:
            raise ValueError("concurrent execution requires a high-load schedule")
        admitted = tuple(
            item
            for item in schedule.items
            if item.disposition is CognitiveAdmissionDisposition.ADMIT
        )
        tasks = tuple(
            ConcurrentCognitiveTask(index, item.action, item.priority)
            for index, item in enumerate(admitted, 1)
            if item.action in handlers
        )
        blocked = assessment.state is LongRunningStabilityState.GUARDED
        worker_limit = (
            1
            if assessment.state is LongRunningStabilityState.CHECKPOINT_REQUIRED
            else self.max_workers
        )
        worker_limit = max(1, min(worker_limit, len(tasks) or 1))
        if blocked:
            results = tuple(
                ConcurrentTaskResult(item.sequence, item.action, "skipped")
                for item in tasks
            )
            status = ConcurrentExecutionStatus.BLOCKED
        elif not tasks:
            results = ()
            status = ConcurrentExecutionStatus.IDLE
        else:
            completed: dict[int, ConcurrentTaskResult] = {}
            with ThreadPoolExecutor(
                max_workers=worker_limit, thread_name_prefix="roby-cognitive"
            ) as pool:
                futures = {pool.submit(handlers[item.action]): item for item in tasks}
                for future in as_completed(futures):
                    item = futures[future]
                    try:
                        value = str(future.result())
                        completed[item.sequence] = ConcurrentTaskResult(
                            item.sequence, item.action, "completed", value=value
                        )
                    except Exception as exc:  # noqa: BLE001 - failure is captured as data
                        completed[item.sequence] = ConcurrentTaskResult(
                            item.sequence,
                            item.action,
                            "failed",
                            error=f"{type(exc).__name__}: {exc}",
                        )
            results = tuple(completed[index] for index in range(1, len(tasks) + 1))
            status = (
                ConcurrentExecutionStatus.COMPLETED
                if all(
                    item.status is ConcurrentTaskStatus.COMPLETED for item in results
                )
                else ConcurrentExecutionStatus.PARTIAL
            )
        return ConcurrentCognitiveExecution(
            assessment.owner,
            assessment.session_id,
            status,
            worker_limit,
            tasks,
            results,
            tuple(
                dict.fromkeys(
                    (assessment.assessment_id, *assessment.source_reference_ids)
                )
            ),
            assessment.created_at,
        )


@dataclass
class ConcurrentCognitiveExecutionRuntimeContributor:
    executor: ConcurrentCognitiveExecutor
    blackboard: UnifiedCognitiveBlackboard
    name: str = "concurrent_cognitive_execution"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del text, request
        execution = self.executor.execute(
            owner=owner, session_id=session_id, handlers={}, now=now
        )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key="concurrent_cognitive_execution",
                value=execution.status.value,
                confidence=1.0,
                source_reference_ids=(
                    execution.execution_id,
                    *execution.source_reference_ids,
                ),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Ejecución cognitiva concurrente: "
                f"{execution.status.value}; workers={execution.worker_limit}.",
            ),
            reference_ids=(
                entry.entry_id,
                execution.execution_id,
                *execution.source_reference_ids,
            ),
            rationale=(
                "bounded_parallelism_applied",
                "deterministic_result_join_preserved",
                "task_failures_isolated",
            ),
        )
