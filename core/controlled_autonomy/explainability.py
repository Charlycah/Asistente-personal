from __future__ import annotations

from dataclasses import dataclass

from .contracts import DecisionJournalEntry, DecisionOutcome


@dataclass(frozen=True, slots=True)
class CandidateExplanation:
    candidate_id: str
    action: str
    selected: bool
    risk: str | None
    confidence: float | None
    impact: float | None
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DecisionExplanation:
    decision_id: str
    situation_id: str
    summary: str
    observation: tuple[str, ...]
    candidates: tuple[CandidateExplanation, ...]
    decision: tuple[str, ...]
    outcome: tuple[str, ...]


class DeterministicDecisionExplainer:
    """Reconstructs an auditable explanation without changing system state."""

    def explain(
        self,
        entry: DecisionJournalEntry,
        *,
        outcome: DecisionOutcome | None = None,
    ) -> DecisionExplanation:
        assessments = {
            assessment.candidate_id: assessment
            for assessment in entry.assessments
        }
        candidate_explanations = tuple(
            CandidateExplanation(
                candidate_id=candidate.candidate_id,
                action=candidate.action,
                selected=(
                    candidate.candidate_id == entry.decision.candidate_id
                ),
                risk=(
                    assessments[candidate.candidate_id].risk.value
                    if candidate.candidate_id in assessments
                    else None
                ),
                confidence=(
                    assessments[candidate.candidate_id].confidence
                    if candidate.candidate_id in assessments
                    else None
                ),
                impact=(
                    assessments[candidate.candidate_id].impact
                    if candidate.candidate_id in assessments
                    else None
                ),
                reasons=(
                    candidate.rationale
                    + (
                        assessments[candidate.candidate_id].reasons
                        if candidate.candidate_id in assessments
                        else ()
                    )
                ),
            )
            for candidate in entry.candidates
        )
        resolved_outcome = outcome or entry.outcome
        outcome_lines = (
            ("outcome_not_available",)
            if resolved_outcome is None
            else (
                f"status={resolved_outcome.status.value}",
                f"summary={resolved_outcome.summary}",
                *resolved_outcome.evidence,
            )
        )
        selected_action = next(
            (
                candidate.action
                for candidate in entry.candidates
                if candidate.candidate_id == entry.decision.candidate_id
            ),
            "none",
        )
        return DecisionExplanation(
            decision_id=entry.decision.decision_id,
            situation_id=entry.situation.situation_id,
            summary=(
                f"Roby chose {entry.decision.disposition.value} for "
                f"{selected_action} with {entry.decision.risk.value} risk."
            ),
            observation=(
                f"kind={entry.situation.kind}",
                f"description={entry.situation.description}",
                f"source={entry.situation.source}",
                f"urgency={entry.situation.urgency:.2f}",
                *entry.situation.evidence,
            ),
            candidates=candidate_explanations,
            decision=(
                f"disposition={entry.decision.disposition.value}",
                f"selected_action={selected_action}",
                f"confidence={entry.decision.confidence:.2f}",
                f"risk={entry.decision.risk.value}",
                f"policy_level={entry.decision.policy_level.value}",
                *entry.decision.rationale,
            ),
            outcome=outcome_lines,
        )


__all__ = [
    "CandidateExplanation",
    "DecisionExplanation",
    "DeterministicDecisionExplainer",
]
