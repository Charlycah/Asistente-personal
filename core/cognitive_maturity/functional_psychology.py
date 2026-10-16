from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .conversation_reflection import ConversationReflectionReport
from .epistemic import EpistemicAssessment, EpistemicLevel
from .historical_analysis import HistoricalAnalysisReport, HistoricalAnalysisStatus


class FunctionalPsychologyStatus(str, Enum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class FunctionalPsychologyIndicator:
    code: str
    evidence_count: int
    confidence: str

    def __post_init__(self) -> None:
        if not self.code.strip() or self.evidence_count < 1:
            raise ValueError("functional psychology indicator must have evidence")
        if self.confidence not in {"limited", "moderate", "strong"}:
            raise ValueError("functional psychology confidence is invalid")


@dataclass(frozen=True)
class FunctionalPsychologyReport:
    report_id: str
    status: FunctionalPsychologyStatus
    source_assessment_count: int
    source_reflection_ids: tuple[str, ...]
    source_history_id: str | None
    cognitive_style_indicators: tuple[FunctionalPsychologyIndicator, ...]
    conversational_function_indicators: tuple[FunctionalPsychologyIndicator, ...]
    stability_indicators: tuple[FunctionalPsychologyIndicator, ...]
    caution_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m389.4"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    performs_clinical_diagnosis: bool = False
    infers_mental_disorder: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    modifies_permissions: bool = False
    prescribes_action: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("functional-psychology-"):
            raise ValueError("functional psychology report identifier is invalid")
        if not self.read_only or self.grants_authority:
            raise ValueError("functional psychology must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("functional psychology cannot contain private content")
        if self.performs_clinical_diagnosis or self.infers_mental_disorder:
            raise ValueError("clinical interpretation is outside this authority")
        if any(
            (
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_planning,
                self.modifies_permissions,
                self.prescribes_action,
            )
        ):
            raise ValueError("functional psychology cannot modify governed domains")


class FunctionalPsychologyAuthority:
    """Single read-only authority for non-clinical functional psychology."""

    authority_id = "functional_psychology"

    def analyze(
        self,
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
    ) -> FunctionalPsychologyReport:
        ordered_assessments = tuple(
            sorted(assessments, key=lambda item: (item.claim_id, item.level.value))
        )
        ordered_reflections = tuple(
            sorted(reflections, key=lambda item: item.report_id)
        )
        reflection_ids = tuple(item.report_id for item in ordered_reflections)
        history_id = history.report_id if history is not None else None

        cognitive = self._cognitive_style(ordered_assessments)
        conversational = self._conversational_function(ordered_reflections)
        stability = self._stability(history)
        caution_codes = self._cautions(
            ordered_assessments,
            ordered_reflections,
            history,
        )
        status = (
            FunctionalPsychologyStatus.COMPLETE
            if ordered_assessments or ordered_reflections or history is not None
            else FunctionalPsychologyStatus.INSUFFICIENT_EVIDENCE
        )
        fingerprint = self._fingerprint(
            ordered_assessments,
            ordered_reflections,
            history,
            cognitive,
            conversational,
            stability,
            caution_codes,
        )
        return FunctionalPsychologyReport(
            report_id=f"functional-psychology-{fingerprint[:16]}",
            status=status,
            source_assessment_count=len(ordered_assessments),
            source_reflection_ids=reflection_ids,
            source_history_id=history_id,
            cognitive_style_indicators=cognitive,
            conversational_function_indicators=conversational,
            stability_indicators=stability,
            caution_codes=caution_codes,
            source_fingerprint=fingerprint,
        )

    def analyze_safely(
        self,
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
    ) -> FunctionalPsychologyReport:
        try:
            return self.analyze(assessments, reflections, history)
        except Exception:
            fingerprint = sha256(b"functional-psychology-failure").hexdigest()
            return FunctionalPsychologyReport(
                report_id=f"functional-psychology-{fingerprint[:16]}",
                status=FunctionalPsychologyStatus.DEGRADED,
                source_assessment_count=0,
                source_reflection_ids=(),
                source_history_id=None,
                cognitive_style_indicators=(),
                conversational_function_indicators=(),
                stability_indicators=(),
                caution_codes=("functional_psychology_failure",),
                source_fingerprint=fingerprint,
            )

    @classmethod
    def _cognitive_style(
        cls,
        assessments: tuple[EpistemicAssessment, ...],
    ) -> tuple[FunctionalPsychologyIndicator, ...]:
        levels = Counter(item.level for item in assessments)
        indicators: list[FunctionalPsychologyIndicator] = []
        mapping = (
            (EpistemicLevel.FACT, "fact_oriented_processing"),
            (EpistemicLevel.INFERENCE, "inferential_processing"),
            (EpistemicLevel.HYPOTHESIS, "exploratory_hypothesis_processing"),
            (EpistemicLevel.UNKNOWN, "explicit_uncertainty_recognition"),
        )
        for level, code in mapping:
            count = levels[level]
            if count:
                indicators.append(cls._indicator(code, count))
        return tuple(indicators)

    @classmethod
    def _conversational_function(
        cls,
        reflections: tuple[ConversationReflectionReport, ...],
    ) -> tuple[FunctionalPsychologyIndicator, ...]:
        objectives = Counter(item.objective_code for item in reflections)
        questions = sum(len(item.open_question_codes) for item in reflections)
        risks = sum(len(item.risk_codes) for item in reflections)
        indicators = [
            cls._indicator(f"objective_pattern:{code}", count)
            for code, count in sorted(objectives.items())
            if code
        ]
        if questions:
            indicators.append(cls._indicator("open_question_engagement", questions))
        if risks:
            indicators.append(cls._indicator("risk_attention", risks))
        return tuple(indicators)

    @classmethod
    def _stability(
        cls,
        history: HistoricalAnalysisReport | None,
    ) -> tuple[FunctionalPsychologyIndicator, ...]:
        if history is None:
            return ()
        indicators = [
            cls._indicator("recurrent_objective_stability", item.count)
            for item in history.recurrent_objectives
        ]
        indicators.extend(
            cls._indicator("recurrent_question_persistence", item.count)
            for item in history.recurrent_questions
        )
        indicators.extend(
            cls._indicator("recurrent_risk_attention", item.count)
            for item in history.recurrent_risks
        )
        return tuple(indicators)

    @staticmethod
    def _cautions(
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
    ) -> tuple[str, ...]:
        codes: set[str] = set()
        if not assessments:
            codes.add("no_cognitive_assessments")
        if not reflections:
            codes.add("no_conversation_reflections")
        if history is None:
            codes.add("no_historical_analysis")
        elif history.status is HistoricalAnalysisStatus.DEGRADED:
            codes.add("degraded_historical_analysis")
        elif history.contradiction_codes:
            codes.add("historical_epistemic_tension")
        return tuple(sorted(codes))

    @staticmethod
    def _indicator(code: str, count: int) -> FunctionalPsychologyIndicator:
        confidence = "limited"
        if count >= 4:
            confidence = "strong"
        elif count >= 2:
            confidence = "moderate"
        return FunctionalPsychologyIndicator(
            code=code,
            evidence_count=count,
            confidence=confidence,
        )

    @staticmethod
    def _fingerprint(
        assessments: tuple[EpistemicAssessment, ...],
        reflections: tuple[ConversationReflectionReport, ...],
        history: HistoricalAnalysisReport | None,
        cognitive: tuple[FunctionalPsychologyIndicator, ...],
        conversational: tuple[FunctionalPsychologyIndicator, ...],
        stability: tuple[FunctionalPsychologyIndicator, ...],
        cautions: tuple[str, ...],
    ) -> str:
        parts = [
            *(f"assessment:{item.claim_id}:{item.level.value}" for item in assessments),
            *(f"reflection:{item.report_id}" for item in reflections),
            f"history:{history.report_id if history is not None else 'none'}",
            *(
                f"cognitive:{item.code}:{item.evidence_count}:{item.confidence}"
                for item in cognitive
            ),
            *(
                f"conversation:{item.code}:{item.evidence_count}:{item.confidence}"
                for item in conversational
            ),
            *(
                f"stability:{item.code}:{item.evidence_count}:{item.confidence}"
                for item in stability
            ),
            *(f"caution:{code}" for code in cautions),
        ]
        return sha256("|".join(parts).encode("utf-8")).hexdigest()
