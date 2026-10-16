from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .conversation_reflection import ConversationReflectionReport
from .epistemic import EpistemicLevel


class HistoricalAnalysisStatus(str, Enum):
    COMPLETE = "complete"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class HistoricalTopicFrequency:
    code: str
    count: int

    def __post_init__(self) -> None:
        if not self.code.strip() or self.count < 1:
            raise ValueError("historical topic frequency must be positive")


@dataclass(frozen=True)
class HistoricalAnalysisReport:
    report_id: str
    status: HistoricalAnalysisStatus
    evaluated_report_ids: tuple[str, ...]
    recurrent_objectives: tuple[HistoricalTopicFrequency, ...]
    recurrent_risks: tuple[HistoricalTopicFrequency, ...]
    recurrent_questions: tuple[HistoricalTopicFrequency, ...]
    unresolved_question_codes: tuple[str, ...]
    epistemic_distribution: tuple[HistoricalTopicFrequency, ...]
    contradiction_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m389.3"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    resolves_contradictions: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("history-"):
            raise ValueError("historical report identifier is invalid")
        if not self.read_only or self.grants_authority:
            raise ValueError("historical analysis must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("historical analysis cannot contain private content")
        if self.creates_memory or self.creates_learning_candidate:
            raise ValueError("historical analysis cannot create persistence")
        if self.resolves_contradictions:
            raise ValueError("historical analysis cannot resolve contradictions")


class HistoricalAnalysisAuthority:
    """Single read-only authority for coded historical analysis."""

    authority_id = "historical_analysis"

    def analyze(
        self,
        reflections: tuple[ConversationReflectionReport, ...],
    ) -> HistoricalAnalysisReport:
        ordered = tuple(sorted(reflections, key=lambda item: item.report_id))
        report_ids = tuple(item.report_id for item in ordered)
        objectives = self._frequencies(
            item.objective_code for item in ordered
        )
        risks = self._frequencies(
            code for item in ordered for code in item.risk_codes
        )
        questions = self._frequencies(
            code for item in ordered for code in item.open_question_codes
        )
        epistemic = self._frequencies(
            level.value
            for item in ordered
            for level in item.epistemic_levels
        )
        unresolved = tuple(sorted({item.code for item in questions}))
        contradictions = self._contradictions(ordered)
        fingerprint = sha256(
            "|".join(
                (
                    *report_ids,
                    *(f"objective:{item.code}:{item.count}" for item in objectives),
                    *(f"risk:{item.code}:{item.count}" for item in risks),
                    *(f"question:{item.code}:{item.count}" for item in questions),
                    *(f"epistemic:{item.code}:{item.count}" for item in epistemic),
                    *contradictions,
                )
            ).encode("utf-8")
        ).hexdigest()
        return HistoricalAnalysisReport(
            report_id=f"history-{fingerprint[:16]}",
            status=HistoricalAnalysisStatus.COMPLETE,
            evaluated_report_ids=report_ids,
            recurrent_objectives=self._recurrent(objectives),
            recurrent_risks=self._recurrent(risks),
            recurrent_questions=self._recurrent(questions),
            unresolved_question_codes=unresolved,
            epistemic_distribution=epistemic,
            contradiction_codes=contradictions,
            source_fingerprint=fingerprint,
        )

    def analyze_safely(
        self,
        reflections: tuple[ConversationReflectionReport, ...],
    ) -> HistoricalAnalysisReport:
        try:
            return self.analyze(reflections)
        except Exception:
            fingerprint = sha256(b"historical-analysis-failure").hexdigest()
            return HistoricalAnalysisReport(
                report_id=f"history-{fingerprint[:16]}",
                status=HistoricalAnalysisStatus.DEGRADED,
                evaluated_report_ids=(),
                recurrent_objectives=(),
                recurrent_risks=(
                    HistoricalTopicFrequency(
                        code="historical_analysis_failure",
                        count=1,
                    ),
                ),
                recurrent_questions=(),
                unresolved_question_codes=(
                    "review_historical_analysis_failure",
                ),
                epistemic_distribution=(),
                contradiction_codes=(),
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _frequencies(values) -> tuple[HistoricalTopicFrequency, ...]:
        counter = Counter(value for value in values if value)
        return tuple(
            HistoricalTopicFrequency(code=code, count=count)
            for code, count in sorted(counter.items())
        )

    @staticmethod
    def _recurrent(
        values: tuple[HistoricalTopicFrequency, ...],
    ) -> tuple[HistoricalTopicFrequency, ...]:
        return tuple(item for item in values if item.count > 1)

    @staticmethod
    def _contradictions(
        reflections: tuple[ConversationReflectionReport, ...],
    ) -> tuple[str, ...]:
        levels = {
            level
            for item in reflections
            for level in item.epistemic_levels
        }
        if EpistemicLevel.FACT in levels and EpistemicLevel.HYPOTHESIS in levels:
            return ("fact_and_hypothesis_coexist",)
        return ()
