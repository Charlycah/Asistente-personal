from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.cognitive_maturity.governed_epistemic_curiosity import (
    GovernedEpistemicCuriosityReport,
)

from .productive_conversational_curiosity_wiring import (
    ProductiveConversationalCuriosityAssembly,
)


@dataclass(frozen=True)
class GovernedIntellectualGoalProposal:
    """Read-only projection of admitted curiosity into a proposed study goal."""

    proposal_id: str
    owner: str
    subject: str
    unknown_element: str
    question: str
    curiosity_report_id: str
    question_id: str
    source_reference: str
    curiosity_source_fingerprint: str
    assembly_source_fingerprint: str
    relevance_recipient: str
    initiative_disposition: str
    schema_version: str = "intel-g3-governed-intellectual-goal-proposal-v1"
    read_only: bool = True
    non_executive: bool = True
    authorization_required: bool = True
    authorized: bool = False
    planning_invoked: bool = False
    investigation_started: bool = False
    executes_capabilities: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.proposal_id.startswith("intellectual-goal-proposal-"):
            raise ValueError("intellectual goal proposal identifier is invalid")
        required = (
            self.owner,
            self.subject,
            self.unknown_element,
            self.question,
            self.curiosity_report_id,
            self.question_id,
            self.source_reference,
            self.curiosity_source_fingerprint,
            self.assembly_source_fingerprint,
            self.relevance_recipient,
            self.initiative_disposition,
        )
        if any(not value.strip() for value in required):
            raise ValueError("intellectual goal proposal lineage cannot be blank")
        if not self.read_only or not self.non_executive:
            raise ValueError("intellectual goal proposal must remain non-executive")
        if not self.authorization_required or self.authorized:
            raise ValueError("intellectual goal proposal requires later authorization")
        if any(
            (
                self.planning_invoked,
                self.investigation_started,
                self.executes_capabilities,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_knowledge,
                self.starts_background_process,
            )
        ):
            raise ValueError("intellectual goal proposal crossed its governed stop")


class GovernedIntellectualGoalProposalProjectorV1:
    """Project certified curiosity lineage without crossing its governed stop."""

    def project(
        self,
        *,
        owner: str,
        report: GovernedEpistemicCuriosityReport,
        assembly: ProductiveConversationalCuriosityAssembly,
    ) -> GovernedIntellectualGoalProposal:
        question = report.question_candidate
        if question is None:
            raise ValueError("intellectual goal proposal requires a curiosity question")
        if report.report_id != assembly.curiosity_report_id:
            raise ValueError("intellectual goal proposal lineage does not match")
        if question.question_id != assembly.question_id:
            raise ValueError("intellectual goal proposal lineage does not match")
        if question.question != assembly.question:
            raise ValueError("intellectual goal proposal lineage does not match")
        if not report.read_only or report.grants_authority:
            raise ValueError("intellectual goal proposal requires governed curiosity")
        if not assembly.read_only or assembly.grants_authority:
            raise ValueError("intellectual goal proposal requires governed assembly")

        clean_owner = owner.strip()
        if not clean_owner:
            raise ValueError("intellectual goal proposal owner cannot be blank")
        proposal_id = self._proposal_id(clean_owner, report, assembly)
        return GovernedIntellectualGoalProposal(
            proposal_id=proposal_id,
            owner=clean_owner,
            subject=question.subject,
            unknown_element=question.unknown_element,
            question=assembly.question,
            curiosity_report_id=report.report_id,
            question_id=question.question_id,
            source_reference=question.source_reference,
            curiosity_source_fingerprint=report.source_fingerprint,
            assembly_source_fingerprint=assembly.source_fingerprint,
            relevance_recipient=assembly.consumption.relevance.recipient.value,
            initiative_disposition=assembly.consumption.initiative.disposition.value,
        )

    @staticmethod
    def _proposal_id(
        owner: str,
        report: GovernedEpistemicCuriosityReport,
        assembly: ProductiveConversationalCuriosityAssembly,
    ) -> str:
        fingerprint = sha256(
            repr(
                (
                    owner,
                    report.report_id,
                    report.source_fingerprint,
                    assembly.question_id,
                    assembly.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return f"intellectual-goal-proposal-{fingerprint[:24]}"
