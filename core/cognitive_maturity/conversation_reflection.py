from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import TYPE_CHECKING

from .cognitive_turn_dossier import CognitiveTurnDossier
from .epistemic import EpistemicAssessment, EpistemicLevel

if TYPE_CHECKING:
    from .explicit_inner_continuity import ExplicitInnerContinuityReport
    from .simulated_functional_regulation import SimulatedFunctionalRegulationReport
    from .simulated_inner_state import SimulatedInnerStateSnapshot


class ConversationReflectionStatus(str, Enum):
    COMPLETE = "complete"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class ConversationReflectionReport:
    report_id: str
    dossier_id: str
    cycle_id: str
    status: ConversationReflectionStatus
    objective_code: str
    participated_node_ids: tuple[str, ...]
    unresolved_node_ids: tuple[str, ...]
    epistemic_levels: tuple[EpistemicLevel, ...]
    risk_codes: tuple[str, ...]
    open_question_codes: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    inner_state_snapshot_id: str | None = None
    inner_continuity_report_id: str | None = None
    inner_regulation_report_id: str | None = None
    inner_state_observation_codes: tuple[str, ...] = ()
    schema_version: str = "m389.2"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False

    def __post_init__(self) -> None:
        if self.report_id != f"reflection-{self.dossier_id}":
            raise ValueError("conversation reflection lineage is inconsistent")
        if not self.objective_code.strip() or not self.rationale_codes:
            raise ValueError("conversation reflection requires coded rationale")
        if not self.read_only or self.grants_authority:
            raise ValueError("conversation reflection must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("conversation reflection cannot contain private content")
        if self.creates_memory or self.creates_learning_candidate:
            raise ValueError("conversation reflection cannot create persistence")
        if (
            self.inner_state_observation_codes
            and self.inner_state_snapshot_id is None
        ):
            raise ValueError(
                "inner-state reflection requires explicit snapshot lineage"
            )


class ConversationReflectionAuthority:
    """Single read-only authority for post-turn conversational reflection."""

    authority_id = "conversation_reflection"

    def reflect(
        self,
        dossier: CognitiveTurnDossier,
        assessments: tuple[EpistemicAssessment, ...] = (),
        *,
        inner_state: SimulatedInnerStateSnapshot | None = None,
        inner_continuity: ExplicitInnerContinuityReport | None = None,
        inner_regulation: SimulatedFunctionalRegulationReport | None = None,
    ) -> ConversationReflectionReport:
        levels = tuple(item.level for item in assessments)
        unresolved = dossier.nonparticipating_node_ids
        if inner_state is None:
            risks = tuple(
                code
                for code, present in (
                    (
                        "cognitive_route_interrupted",
                        dossier.first_interruption_node_id is not None,
                    ),
                    (
                        "epistemic_unknown_present",
                        EpistemicLevel.UNKNOWN in levels,
                    ),
                    ("degraded_turn_outcome", dossier.outcome.value != "complete"),
                )
                if present
            )
            questions = tuple(
                f"verify_{node_id}" for node_id in unresolved
            )
            objective = (
                "review_interrupted_turn"
                if dossier.first_interruption_node_id is not None
                else "document_completed_turn"
            )
            rationale = (
                "derived_from_certified_turn_dossier",
                "post_turn_read_only_reflection",
            )
            fingerprint = sha256(
                "|".join(
                    (
                        dossier.evidence_fingerprint,
                        objective,
                        ",".join(level.value for level in levels),
                        ",".join(risks),
                        ",".join(questions),
                    )
                ).encode("utf-8")
            ).hexdigest()
            return ConversationReflectionReport(
                report_id=f"reflection-{dossier.dossier_id}",
                dossier_id=dossier.dossier_id,
                cycle_id=dossier.cycle_id,
                status=ConversationReflectionStatus.COMPLETE,
                objective_code=objective,
                participated_node_ids=dossier.participated_node_ids,
                unresolved_node_ids=unresolved,
                epistemic_levels=levels,
                risk_codes=risks,
                open_question_codes=questions,
                rationale_codes=rationale,
                source_fingerprint=fingerprint,
            )

        risks = {
            code
            for code, present in (
                (
                    "cognitive_route_interrupted",
                    dossier.first_interruption_node_id is not None,
                ),
                ("epistemic_unknown_present", EpistemicLevel.UNKNOWN in levels),
                ("degraded_turn_outcome", dossier.outcome.value != "complete"),
            )
            if present
        }
        questions = {f"verify_{node_id}" for node_id in unresolved}
        objective = (
            "review_interrupted_turn"
            if dossier.first_interruption_node_id is not None
            else "document_completed_turn"
        )
        rationale = {
            "derived_from_certified_turn_dossier",
            "post_turn_read_only_reflection",
        }
        inner_codes = set()

        if inner_state is not None:
            inner_codes.add("simulated_inner_state_observed")
            rationale.add("explicit_simulated_inner_state_observed")
            if inner_state.status.value == "degraded":
                risks.add("simulated_inner_state_degraded")
                questions.add("review_simulated_inner_state_degradation")
            if inner_state.dominant_state.value in {"conflicted", "uncertain"}:
                inner_codes.add("simulated_inner_state_uncertainty_observed")
            if inner_state.risk_codes:
                risks.add("simulated_inner_state_risk_present")

        if inner_state is not None and inner_continuity is not None:
            inner_codes.add("explicit_inner_continuity_observed")
            if inner_continuity.status.value == "degraded":
                risks.add("explicit_inner_continuity_degraded")
            elif inner_continuity.continuity.value == "changed":
                inner_codes.add("explicit_inner_state_change_observed")

        if inner_state is not None and inner_regulation is not None:
            inner_codes.add("simulated_functional_regulation_observed")
            if inner_regulation.status.value == "degraded":
                risks.add("simulated_functional_regulation_degraded")
            elif inner_regulation.mode.value in {"stabilize", "cautious"}:
                inner_codes.add("regulated_inner_state_observed")

        fingerprint_parts = [
            dossier.evidence_fingerprint,
            objective,
            ",".join(level.value for level in levels),
            ",".join(sorted(risks)),
            ",".join(sorted(questions)),
        ]
        if inner_state is not None:
            fingerprint_parts.append(inner_state.source_fingerprint)
            if inner_continuity is not None:
                fingerprint_parts.append(inner_continuity.source_fingerprint)
            if inner_regulation is not None:
                fingerprint_parts.append(inner_regulation.source_fingerprint)
            fingerprint_parts.append(",".join(sorted(inner_codes)))
        fingerprint = sha256("|".join(fingerprint_parts).encode("utf-8")).hexdigest()

        return ConversationReflectionReport(
            report_id=f"reflection-{dossier.dossier_id}",
            dossier_id=dossier.dossier_id,
            cycle_id=dossier.cycle_id,
            status=ConversationReflectionStatus.COMPLETE,
            objective_code=objective,
            participated_node_ids=dossier.participated_node_ids,
            unresolved_node_ids=unresolved,
            epistemic_levels=levels,
            risk_codes=tuple(sorted(risks)),
            open_question_codes=tuple(sorted(questions)),
            rationale_codes=tuple(sorted(rationale)),
            source_fingerprint=fingerprint,
            inner_state_snapshot_id=(
                inner_state.snapshot_id if inner_state is not None else None
            ),
            inner_continuity_report_id=(
                inner_continuity.report_id
                if inner_state is not None and inner_continuity is not None
                else None
            ),
            inner_regulation_report_id=(
                inner_regulation.report_id
                if inner_state is not None and inner_regulation is not None
                else None
            ),
            inner_state_observation_codes=tuple(sorted(inner_codes)),
        )

    def reflect_safely(
        self,
        dossier: CognitiveTurnDossier,
        assessments: tuple[EpistemicAssessment, ...] = (),
        *,
        inner_state: SimulatedInnerStateSnapshot | None = None,
        inner_continuity: ExplicitInnerContinuityReport | None = None,
        inner_regulation: SimulatedFunctionalRegulationReport | None = None,
    ) -> ConversationReflectionReport:
        try:
            if (
                inner_state is None
                and inner_continuity is None
                and inner_regulation is None
            ):
                return self.reflect(dossier, assessments)
            return self.reflect(
                dossier,
                assessments,
                inner_state=inner_state,
                inner_continuity=inner_continuity,
                inner_regulation=inner_regulation,
            )
        except Exception:
            return ConversationReflectionReport(
                report_id=f"reflection-{dossier.dossier_id}",
                dossier_id=dossier.dossier_id,
                cycle_id=dossier.cycle_id,
                status=ConversationReflectionStatus.DEGRADED,
                objective_code="reflection_unavailable",
                participated_node_ids=(),
                unresolved_node_ids=(),
                epistemic_levels=(),
                risk_codes=("reflection_engine_failure",),
                open_question_codes=("review_reflection_failure",),
                rationale_codes=("safe_degradation_without_turn_impact",),
                source_fingerprint=dossier.evidence_fingerprint,
            )
