from __future__ import annotations

from dataclasses import dataclass

from app.positive_same_explanatory_model_continuity_consumer import (
    PositiveSameExplanatoryModelContinuitySelection,
)


@dataclass(frozen=True)
class PositiveSameExplanatoryModelContinuityContext:
    """Consultative projection of an already certified continuity selection."""

    candidate_model_id: str
    assessment_id: str
    projection_status: str = "consultative_continuity_context"
    read_only: bool = True
    consultative: bool = True
    transient: bool = True
    authorizes_revision: bool = False
    persists: bool = False
    creates_learning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    opens_investigation: bool = False
    creates_initiative: bool = False
    authorizes_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def context_lines(self) -> tuple[str, ...]:
        return (
            "Explanatory continuity context: bounded explanatory model "
            f"{self.candidate_model_id} remains the longitudinally identified "
            "continuous prior.",
        )


class PositiveSameExplanatoryModelContinuityContextProjectionV1:
    """Project certified SAME continuity into consultative context only."""

    def project(
        self,
        *,
        selection: PositiveSameExplanatoryModelContinuitySelection,
    ) -> PositiveSameExplanatoryModelContinuityContext | None:
        if selection.selection_status != "selected_continuous_prior":
            return None
        if not selection.candidate_model_id or not selection.assessment_id:
            return None
        if not selection.read_only or not selection.consultative:
            return None
        if not selection.transient or selection.authorizes_revision:
            return None
        if (
            selection.persists
            or selection.creates_learning
            or selection.modifies_memory
            or selection.modifies_world_model
            or selection.opens_investigation
            or selection.creates_initiative
            or selection.executes_actions
            or selection.grants_authority
        ):
            return None

        return PositiveSameExplanatoryModelContinuityContext(
            candidate_model_id=selection.candidate_model_id,
            assessment_id=selection.assessment_id,
        )
