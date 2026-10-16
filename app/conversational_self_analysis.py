from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SelfAnalysisPolicy:
    minimum_turns: int = 3
    cooldown_turns: int = 3
    trigger_score: int = 3
    recent_window: int = 4


@dataclass(frozen=True)
class SelfAnalysisFinding:
    dimension: str
    severity: str
    evidence: str
    recommendation: str


@dataclass(frozen=True)
class ConversationalSelfAnalysisReport:
    turn: int
    trigger_reason: str
    score: int
    findings: tuple[SelfAnalysisFinding, ...]
    advisory_only: bool = True


@dataclass(frozen=True)
class ConversationalSelfAnalysisSnapshot:
    observed_turns: int
    analyses_run: int
    skipped_by_cooldown: int
    last_score: int
    last_report: ConversationalSelfAnalysisReport | None


class AutonomousConversationalSelfAnalysis:
    """Advisory self-analysis selected by ROBY, never by a public command."""

    _CORRECTION_MARKERS = (
        "te dije",
        "ya te dije",
        "eso no",
        "no era",
        "incorrecto",
        "otra vez",
        "de nuevo no",
        "no entendiste",
    )
    _CONTEXT_MARKERS = (
        "como te dije",
        "ya habiamos",
        "ya habíamos",
        "lo hablamos",
        "lo charlamos",
    )
    _OPENING = re.compile(r"^\s*([\wáéíóúüñ]+(?:\s+[\wáéíóúüñ]+)?)", re.IGNORECASE)

    def __init__(self, policy: SelfAnalysisPolicy | None = None) -> None:
        self.policy = policy or SelfAnalysisPolicy()
        self._turn = 0
        self._analyses_run = 0
        self._skipped_by_cooldown = 0
        self._last_analysis_turn = -self.policy.cooldown_turns
        self._last_score = 0
        self._last_report: ConversationalSelfAnalysisReport | None = None
        self._recent_openings: list[str] = []
        self._recent_lengths: list[int] = []

    @property
    def snapshot(self) -> ConversationalSelfAnalysisSnapshot:
        return ConversationalSelfAnalysisSnapshot(
            observed_turns=self._turn,
            analyses_run=self._analyses_run,
            skipped_by_cooldown=self._skipped_by_cooldown,
            last_score=self._last_score,
            last_report=self._last_report,
        )

    def observe(self, request_text: str | None, response_text: str) -> None:
        self._turn += 1
        opening = self._extract_opening(response_text)
        if opening:
            self._recent_openings.append(opening)
            self._recent_openings = self._recent_openings[-self.policy.recent_window :]
        self._recent_lengths.append(len(response_text.split()))
        self._recent_lengths = self._recent_lengths[-self.policy.recent_window :]
        self.analyze_if_needed(request_text, response_text)

    def analyze_if_needed(
        self,
        request_text: str | None,
        response_text: str,
    ) -> ConversationalSelfAnalysisReport | None:
        score, findings, reasons = self._assess(request_text, response_text)
        self._last_score = score
        if self._turn < self.policy.minimum_turns or score < self.policy.trigger_score:
            return None
        if self._turn - self._last_analysis_turn < self.policy.cooldown_turns:
            self._skipped_by_cooldown += 1
            return None
        return self.self_analyze(score, findings, reasons)

    def self_analyze(
        self,
        score: int,
        findings: tuple[SelfAnalysisFinding, ...],
        reasons: tuple[str, ...],
    ) -> ConversationalSelfAnalysisReport:
        report = ConversationalSelfAnalysisReport(
            turn=self._turn,
            trigger_reason=", ".join(reasons),
            score=score,
            findings=findings,
        )
        self._analyses_run += 1
        self._last_analysis_turn = self._turn
        self._last_report = report
        return report

    def _assess(
        self,
        request_text: str | None,
        response_text: str,
    ) -> tuple[int, tuple[SelfAnalysisFinding, ...], tuple[str, ...]]:
        normalized_request = (request_text or "").casefold()
        findings: list[SelfAnalysisFinding] = []
        reasons: list[str] = []
        score = 0

        context_signal = any(
            marker in normalized_request for marker in self._CONTEXT_MARKERS
        )
        correction_signal = (
            any(marker in normalized_request for marker in self._CORRECTION_MARKERS)
            and not context_signal
        )

        if correction_signal:
            score += 3
            reasons.append("user_correction")
            findings.append(
                SelfAnalysisFinding(
                    dimension="repair",
                    severity="high",
                    evidence="The user signaled that a prior answer missed the target.",
                    recommendation=(
                        "Re-check the active goal and avoid repeating the "
                        "failed framing."
                    ),
                )
            )

        if context_signal:
            score += 2
            reasons.append("context_reuse_risk")
            findings.append(
                SelfAnalysisFinding(
                    dimension="context",
                    severity="medium",
                    evidence="The user referenced information already shared.",
                    recommendation=(
                        "Prefer available conversation context over asking again."
                    ),
                )
            )

        if self._has_repeated_opening():
            score += 2
            reasons.append("repeated_opening")
            findings.append(
                SelfAnalysisFinding(
                    dimension="expression_variation",
                    severity="medium",
                    evidence="Recent answers began with the same expression pattern.",
                    recommendation=(
                        "Use a direct opening or a different natural transition."
                    ),
                )
            )

        if self._length_mismatch(normalized_request, response_text):
            score += 1
            reasons.append("length_mismatch")
            findings.append(
                SelfAnalysisFinding(
                    dimension="response_length",
                    severity="low",
                    evidence=(
                        "Response length did not match the user's explicit request."
                    ),
                    recommendation=(
                        "Adapt the next answer length to the stated preference."
                    ),
                )
            )

        return score, tuple(findings), tuple(reasons)

    def _has_repeated_opening(self) -> bool:
        if len(self._recent_openings) < 3:
            return False
        return len(set(self._recent_openings[-3:])) == 1

    @staticmethod
    def _length_mismatch(request: str, response: str) -> bool:
        words = len(response.split())
        asks_short = any(
            marker in request
            for marker in ("breve", "corto", "en una frase", "sin detalles")
        )
        asks_detail = any(
            marker in request
            for marker in ("detalle", "explica", "desarrolla", "completo")
        )
        return (asks_short and words > 45) or (asks_detail and words < 12)

    def _extract_opening(self, response: str) -> str:
        prose = re.sub(r"```.*?```|`[^`\n]+`", "", response, flags=re.DOTALL)
        match = self._OPENING.search(prose)
        if match is None:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).casefold()
