from __future__ import annotations

from dataclasses import dataclass

from .first_capability import CapabilityRunResult


@dataclass(frozen=True, slots=True)
class AdvancedCandidateExplanation:
    action: str
    selected: bool
    eligible: bool
    score: float
    risk: str
    confidence: float
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AutonomyExplanation:
    run_id: str
    situation: str
    observation: tuple[str, ...]
    candidates: tuple[AdvancedCandidateExplanation, ...]
    policy_decision: str
    gate_decision: str
    execution_status: str
    outcome_status: str | None
    outcome_summary: str | None
    supervision_directive: str | None
    limits: tuple[str, ...]


class DeterministicAutonomyExplainer:
    """Builds a user-safe explanation from immutable autonomy audit data."""

    def explain(self, result: CapabilityRunResult) -> AutonomyExplanation:
        orchestration = result.orchestration
        situation_result = orchestration.assessment.situation
        situation = (
            situation_result.description
            if situation_result is not None
            else "No actionable situation was identified"
        )
        policy_evaluation = orchestration.policy_evaluation
        scores_by_id = (
            {item.candidate_id: item for item in policy_evaluation.scores}
            if policy_evaluation is not None
            else {}
        )
        assessments_by_id = (
            {
                item.candidate_id: item
                for item in orchestration.risk_evaluation.assessments
            }
            if orchestration.risk_evaluation is not None
            else {}
        )
        selected_id = (
            orchestration.gate_evaluation.gated_decision.candidate_id
            if orchestration.gate_evaluation is not None
            else None
        )
        candidates: list[AdvancedCandidateExplanation] = []
        if orchestration.generation is not None:
            for candidate in orchestration.generation.candidates:
                score = scores_by_id.get(candidate.candidate_id)
                assessment = assessments_by_id.get(candidate.candidate_id)
                candidates.append(
                    AdvancedCandidateExplanation(
                        action=candidate.action,
                        selected=candidate.candidate_id == selected_id,
                        eligible=score.eligible if score is not None else False,
                        score=score.score if score is not None else 0.0,
                        risk=(
                            assessment.risk.value
                            if assessment is not None
                            else "unknown"
                        ),
                        confidence=(
                            assessment.confidence if assessment is not None else 0.0
                        ),
                        reasons=tuple(
                            _safe_text(item)
                            for item in (score.reasons if score is not None else ())
                        ),
                    )
                )
        gate = orchestration.gate_evaluation
        supervision = result.supervision
        return AutonomyExplanation(
            run_id=result.run_id,
            situation=situation,
            observation=tuple(
                _safe_text(item) for item in orchestration.observation.facts
            ),
            candidates=tuple(candidates),
            policy_decision=(
                policy_evaluation.decision.disposition.value
                if policy_evaluation is not None
                else "not_evaluated"
            ),
            gate_decision=(
                gate.gated_decision.disposition.value
                if gate is not None
                else "not_evaluated"
            ),
            execution_status=result.status.value,
            outcome_status=(
                result.outcome.status.value if result.outcome is not None else None
            ),
            outcome_summary=(
                _safe_text(result.outcome.summary)
                if result.outcome is not None
                else None
            ),
            supervision_directive=(
                supervision.directive.value if supervision is not None else None
            ),
            limits=(
                "The explanation is reconstructed from auditable records.",
                "It does not expose hidden reasoning or expand autonomy permissions.",
                "Policy and autonomy-gate limits remain authoritative.",
            ),
        )


def render_autonomy_explanation(explanation: AutonomyExplanation) -> str:
    selected = next(
        (item for item in explanation.candidates if item.selected),
        None,
    )
    if selected is None:
        selection = "No candidate was selected."
    else:
        selection = (
            f"Selected {selected.action} with score {selected.score:.3f}, "
            f"risk {selected.risk}, and confidence {selected.confidence:.3f}."
        )
    outcome = (
        f" Outcome: {explanation.outcome_status}. {explanation.outcome_summary}"
        if explanation.outcome_status is not None
        else " No action outcome was produced."
    )
    return (
        f"Situation: {explanation.situation}. {selection} "
        f"Policy decision: {explanation.policy_decision}; autonomy gate: "
        f"{explanation.gate_decision}; execution: {explanation.execution_status}."
        f"{outcome}"
    )


def _safe_text(value: str) -> str:
    lowered = value.lower()
    sensitive = ("password", "credential", "secret", "token", "api_key")
    if any(item in lowered for item in sensitive):
        key = value.split("=", 1)[0] if "=" in value else "sensitive_data"
        return f"{key}=[redacted]"
    return value


__all__ = [
    "AutonomyExplanation",
    "AdvancedCandidateExplanation",
    "DeterministicAutonomyExplainer",
    "render_autonomy_explanation",
]
