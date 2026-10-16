from __future__ import annotations

from typing import Any

from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstructionFoundationV1,
    GovernedRecalledAntecedentAdmission,
    LongitudinalIntellectualCurrentEpistemicView,
)


class LongitudinalIntellectualReconstructionProductiveAdapterV1:
    """Expose bounded antecedent admission without extending protected runtimes."""

    def __init__(self) -> None:
        self._foundation = GovernedLongitudinalIntellectualReconstructionFoundationV1()

    def admit_recalled_antecedent(
        self, *, candidates: tuple[Any, ...]
    ) -> GovernedRecalledAntecedentAdmission | None:
        """Delegate exact single-candidate admission to governed_reasoning."""
        return self._foundation.admit_recalled_antecedent(candidates=candidates)

    @staticmethod
    def project_current_epistemic_view(
        epistemic_episode: Any,
    ) -> LongitudinalIntellectualCurrentEpistemicView | None:
        """Project one already-governed assessed episode into the existing view."""
        if epistemic_episode is None:
            return None
        status = getattr(epistemic_episode, "status", None)
        status_value = getattr(status, "value", status)
        if str(status_value).lower() != "assessed":
            return None
        sufficiency = getattr(epistemic_episode, "sufficiency", None)
        if sufficiency is None:
            return None
        sufficiency_status = getattr(sufficiency, "status", None)
        sufficiency_status_value = getattr(
            sufficiency_status, "value", sufficiency_status
        )
        assessment_id = getattr(epistemic_episode, "assessment_episode_id", "")
        source_reference = getattr(sufficiency, "source_reference", "")
        source_fingerprint = getattr(epistemic_episode, "source_fingerprint", "")
        productive_reference = getattr(
            epistemic_episode, "productive_reference_id", None
        )
        if not all(
            (
                isinstance(assessment_id, str) and assessment_id.strip(),
                isinstance(sufficiency_status_value, str)
                and sufficiency_status_value.strip(),
                isinstance(source_reference, str) and source_reference.strip(),
                isinstance(source_fingerprint, str)
                and len(source_fingerprint) == 64,
            )
        ):
            return None
        evidence_references = (
            (productive_reference,)
            if isinstance(productive_reference, str) and productive_reference.strip()
            else ()
        )
        return LongitudinalIntellectualCurrentEpistemicView(
            assessment_id=assessment_id,
            status=sufficiency_status_value,
            evidence_references=evidence_references,
            open_state_references=(),
            source_reference=source_reference,
            source_fingerprint=source_fingerprint,
        )
