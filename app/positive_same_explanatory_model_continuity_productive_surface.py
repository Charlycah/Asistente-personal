from __future__ import annotations

from app.positive_same_explanatory_model_continuity_consumer import (
    PositiveSameExplanatoryModelContinuitySelection,
)
from app.positive_same_explanatory_model_continuity_context_projection import (
    PositiveSameExplanatoryModelContinuityContext,
    PositiveSameExplanatoryModelContinuityContextProjectionV1,
)


class PositiveSameExplanatoryModelContinuityProductiveSurfaceV1:
    """Expose certified DI.19 continuity context without owning its semantics."""

    def __init__(self) -> None:
        self._projection = PositiveSameExplanatoryModelContinuityContextProjectionV1()

    def project(
        self,
        *,
        selection: PositiveSameExplanatoryModelContinuitySelection,
    ) -> PositiveSameExplanatoryModelContinuityContext | None:
        return self._projection.project(selection=selection)

    def context_lines(
        self,
        *,
        selection: PositiveSameExplanatoryModelContinuitySelection,
    ) -> tuple[str, ...]:
        context = self.project(selection=selection)
        if context is None:
            return ()
        return context.context_lines()
