from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Callable, Mapping

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.concurrent_cognitive_execution import (
    ConcurrentCognitiveExecutor,
    ConcurrentExecutionStatus,
    ConcurrentTaskStatus,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class StressValidationStatus(str, Enum):
    PASSED = "passed"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True)
class StressScenario:
    name: str
    demand_pattern: tuple[int, ...]
    injected_failures: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        name = self.name.strip()
        failures = tuple(
            item.strip() for item in self.injected_failures if item.strip()
        )
        if not name:
            raise ValueError("stress scenario name must not be blank")
        if not self.demand_pattern or any(item < 0 for item in self.demand_pattern):
            raise ValueError("stress scenario demand pattern must be non-negative")
        if len(set(failures)) != len(failures):
            raise ValueError("stress scenario failures must be unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "injected_failures", failures)


@dataclass(frozen=True)
class StressScenarioResult:
    name: str
    cycles: int
    completed: int
    partial: int
    blocked: int
    idle: int
    task_failures: int
    peak_workers: int
    source_reference_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        name = self.name.strip()
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        counts = (self.completed, self.partial, self.blocked, self.idle)
        if not name or self.cycles < 1 or min(*counts, self.task_failures) < 0:
            raise ValueError("stress scenario result is invalid")
        if sum(counts) != self.cycles:
            raise ValueError("stress scenario cycle accounting must be complete")
        if self.peak_workers < 1:
            raise ValueError("stress scenario peak workers must be positive")
        if len(set(references)) != len(references):
            raise ValueError("stress scenario references must be unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "source_reference_ids", references)


@dataclass(frozen=True)
class EndToEndStressReport:
    owner: str
    session_id: str
    status: StressValidationStatus | str
    scenarios: tuple[StressScenarioResult, ...]
    total_cycles: int
    total_task_failures: int
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    report_id: str = ""

    def __post_init__(self) -> None:
        owner, session_id = self.owner.strip(), self.session_id.strip()
        status = StressValidationStatus(self.status)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id or not self.scenarios:
            raise ValueError("stress report identity and scenarios are required")
        if self.total_cycles != sum(item.cycles for item in self.scenarios):
            raise ValueError("stress report cycle total is inconsistent")
        if self.total_task_failures != sum(
            item.task_failures for item in self.scenarios
        ):
            raise ValueError("stress report failure total is inconsistent")
        if self.created_at.tzinfo is None:
            raise ValueError("stress report time must be timezone-aware")
        if len(set(references)) != len(references):
            raise ValueError("stress report references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    str(self.total_cycles),
                    str(self.total_task_failures),
                    *(
                        f"{item.name}:{item.cycles}:{item.completed}:{item.partial}:"
                        f"{item.blocked}:{item.idle}:{item.task_failures}:{item.peak_workers}"
                        for item in self.scenarios
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.report_id and self.report_id != expected:
            raise ValueError("stress report id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "report_id", expected)


class EndToEndStressValidator:
    """Run bounded synthetic probes through the governed M211-M216 chain."""

    def __init__(
        self, executor: ConcurrentCognitiveExecutor, *, max_cycles: int = 64
    ) -> None:
        if max_cycles < 1:
            raise ValueError("stress validator max cycles must be positive")
        self.executor = executor
        self.max_cycles = max_cycles
        self.last_report: EndToEndStressReport | None = None

    def validate(
        self,
        *,
        owner: str,
        session_id: str,
        scenarios: tuple[StressScenario, ...] | None = None,
        handlers: Mapping[str, Callable[[], object]] | None = None,
        now: datetime | None = None,
    ) -> EndToEndStressReport:
        timestamp = now or datetime.now(timezone.utc)
        selected = scenarios or (
            StressScenario("nominal", (1, 1, 2)),
            StressScenario("load_sweep", (2, 4, 6, 10)),
            StressScenario("recovery_probe", (10, 2, 1)),
        )
        total = sum(len(item.demand_pattern) for item in selected)
        if total > self.max_cycles:
            raise ValueError("stress validation exceeds bounded cycle limit")
        results = tuple(
            self._run_scenario(
                owner,
                session_id,
                scenario,
                handlers or {},
                timestamp + timedelta(seconds=index * 100),
            )
            for index, scenario in enumerate(selected)
        )
        failures = sum(item.task_failures for item in results)
        blocked = sum(item.blocked for item in results)
        partial = sum(item.partial for item in results)
        status = (
            StressValidationStatus.FAILED
            if blocked == total
            else StressValidationStatus.DEGRADED
            if failures or partial or blocked
            else StressValidationStatus.PASSED
        )
        references = tuple(
            dict.fromkeys(ref for item in results for ref in item.source_reference_ids)
        )
        report = EndToEndStressReport(
            owner, session_id, status, results, total, failures, references, timestamp
        )
        self.last_report = report
        return report

    def _run_scenario(
        self,
        owner: str,
        session_id: str,
        scenario: StressScenario,
        handlers: Mapping[str, Callable[[], object]],
        start: datetime,
    ) -> StressScenarioResult:
        executions = []
        for offset, demand in enumerate(scenario.demand_pattern):
            assessment = self.executor.stability.assess(
                owner=owner,
                session_id=session_id,
                demand_units=demand,
                now=start + timedelta(seconds=offset),
            )
            schedule = self.executor.stability.scheduler.last_schedule
            assert schedule is not None
            action_handlers: dict[str, Callable[[], object]] = {}
            for item in schedule.items:
                if item.action in handlers:
                    action_handlers[item.action] = handlers[item.action]
                elif item.action in scenario.injected_failures:
                    action_handlers[item.action] = self._failure_handler(item.action)
                else:
                    action_handlers[item.action] = lambda action=item.action: (
                        f"probe:{action}"
                    )
            executions.append(
                self.executor.execute_assessment(assessment, action_handlers)
            )
        return StressScenarioResult(
            scenario.name,
            len(executions),
            sum(
                item.status is ConcurrentExecutionStatus.COMPLETED
                for item in executions
            ),
            sum(
                item.status is ConcurrentExecutionStatus.PARTIAL for item in executions
            ),
            sum(
                item.status is ConcurrentExecutionStatus.BLOCKED for item in executions
            ),
            sum(item.status is ConcurrentExecutionStatus.IDLE for item in executions),
            sum(
                result.status is ConcurrentTaskStatus.FAILED
                for execution in executions
                for result in execution.results
            ),
            max(item.worker_limit for item in executions),
            tuple(
                dict.fromkeys(
                    ref
                    for execution in executions
                    for ref in (execution.execution_id, *execution.source_reference_ids)
                )
            ),
        )

    @staticmethod
    def _failure_handler(action: str) -> Callable[[], object]:
        def fail() -> object:
            raise RuntimeError(f"injected stress failure: {action}")

        return fail


@dataclass
class EndToEndStressValidationRuntimeContributor:
    validator: EndToEndStressValidator
    blackboard: UnifiedCognitiveBlackboard
    name: str = "end_to_end_stress_validation"

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
        report = self.validator.validate(
            owner=owner,
            session_id=session_id,
            scenarios=(StressScenario("runtime_probe", (1,)),),
            now=now,
        )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key="end_to_end_stress_validation",
                value=report.status.value,
                confidence=1.0,
                source_reference_ids=(report.report_id, *report.source_reference_ids),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Validación de estrés E2E: "
                f"{report.status.value}; ciclos={report.total_cycles}.",
            ),
            reference_ids=(
                entry.entry_id,
                report.report_id,
                *report.source_reference_ids,
            ),
            rationale=(
                "bounded_end_to_end_probe_completed",
                "m211_m216_lineage_preserved",
                "infrastructure_mutation_absent",
            ),
        )
