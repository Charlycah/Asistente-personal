from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .contextual_initiative import ContextualInitiative
from .next_step_proposal import NextStepProposal


@dataclass(frozen=True, slots=True)
class ContextualProposalPresentation:
    initiative_id: str
    proposal_id: str
    title: str
    message: str
    authorization_required: bool
    executable: bool = False

    def __post_init__(self) -> None:
        if not self.initiative_id.strip() or not self.proposal_id.strip():
            raise ValueError("presentation identifiers must not be blank")
        if not self.title.strip() or not self.message.strip():
            raise ValueError("presentation text must not be blank")
        if self.executable:
            raise ValueError("contextual presentations must never be executable")


@runtime_checkable
class ContextualProposalPresenter(Protocol):
    def present(
        self,
        *,
        initiative: ContextualInitiative,
        proposal: NextStepProposal,
    ) -> ContextualProposalPresentation: ...


class DeterministicContextualProposalPresenter:
    """Renders an evaluated initiative without authorizing or executing it."""

    def present(
        self,
        *,
        initiative: ContextualInitiative,
        proposal: NextStepProposal,
    ) -> ContextualProposalPresentation:
        if initiative.proposal_id != proposal.proposal_id:
            raise ValueError("initiative and proposal identifiers do not match")
        if not initiative.should_propose:
            raise ValueError("contextual initiative is not eligible for presentation")

        authorization = (
            " Necesito tu autorización antes de realizar cualquier acción."
            if proposal.authorization_required
            else " No voy a ejecutar nada automáticamente."
        )
        capability = (
            f" Capacidad requerida: {proposal.required_capability}."
            if proposal.required_capability is not None
            else ""
        )
        message = (
            f"{proposal.summary} Próximo paso sugerido: {proposal.description}. "
            f"Motivo: {proposal.rationale}.{capability}{authorization}"
        )
        return ContextualProposalPresentation(
            initiative_id=initiative.initiative_id,
            proposal_id=proposal.proposal_id,
            title="Propuesta de próximo paso",
            message=message,
            authorization_required=proposal.authorization_required,
        )
