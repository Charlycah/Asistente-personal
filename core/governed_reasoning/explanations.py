from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from core.governed_reasoning.decisions import (
    DecisionOutcome,
    DecisionRecord,
    DecisionStatus,
)


class ExplanationLevel(str, Enum):
    """Amount of public audit detail included in an explanation."""

    CONCISE = "concise"
    STANDARD = "standard"
    AUDIT = "audit"


class ExplanationSectionType(str, Enum):
    """Stable public sections used by every explainable answer."""

    CONCLUSION = "conclusion"
    FACTUAL_BASIS = "factual_basis"
    INFERENCES = "inferences"
    SOURCES = "sources"
    UNCERTAINTY = "uncertainty"
    LIMITS = "limits"
    REVIEW = "review"
    AUDIT = "audit"


class CitationKind(str, Enum):
    """Traceable public references available from a Decision Record."""

    EVIDENCE = "evidence"
    CLAIM = "claim"
    RULE = "rule"
    CONFLICT = "conflict"
    DECISION = "decision"


@dataclass(frozen=True)
class SourceCitation:
    kind: CitationKind | str
    reference_id: str
    qualifier: str = ""

    def __post_init__(self) -> None:
        CitationKind(self.kind)
        if not self.reference_id.strip():
            raise ValueError("citation reference id must not be empty")

    @property
    def normalized_kind(self) -> CitationKind:
        return CitationKind(self.kind)

    @property
    def label(self) -> str:
        suffix = f" ({self.qualifier})" if self.qualifier else ""
        return f"{self.normalized_kind.value}:{self.reference_id}{suffix}"


@dataclass(frozen=True)
class ExplanationSection:
    section_type: ExplanationSectionType | str
    title: str
    content: tuple[str, ...]
    citations: tuple[SourceCitation, ...] = ()

    def __post_init__(self) -> None:
        ExplanationSectionType(self.section_type)
        if not self.title.strip():
            raise ValueError("explanation section title must not be empty")
        if not self.content or any(not item.strip() for item in self.content):
            raise ValueError("explanation section content must not be empty")
        object.__setattr__(
            self,
            "citations",
            tuple(
                sorted(
                    self.citations,
                    key=lambda item: (
                        item.normalized_kind.value,
                        item.reference_id,
                        item.qualifier,
                    ),
                )
            ),
        )

    @property
    def normalized_type(self) -> ExplanationSectionType:
        return ExplanationSectionType(self.section_type)


@dataclass(frozen=True)
class ExplainableAnswer:
    decision_id: str
    level: ExplanationLevel | str
    status: DecisionStatus | str
    outcome: DecisionOutcome | str
    title: str
    summary: str
    confidence_label: str
    sections: tuple[ExplanationSection, ...]
    requires_human_review: bool
    answer_id: str = ""

    def __post_init__(self) -> None:
        ExplanationLevel(self.level)
        DecisionStatus(self.status)
        DecisionOutcome(self.outcome)
        for value, label in (
            (self.decision_id, "decision id"),
            (self.title, "title"),
            (self.summary, "summary"),
            (self.confidence_label, "confidence label"),
        ):
            if not value.strip():
                raise ValueError(f"explainable answer {label} must not be empty")
        if not self.sections:
            raise ValueError("explainable answer requires at least one section")
        section_types = [item.normalized_type for item in self.sections]
        if len(section_types) != len(set(section_types)):
            raise ValueError("explanation section types must be unique")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.answer_id and self.answer_id != expected:
            raise ValueError("explainable answer id is inconsistent")
        object.__setattr__(self, "answer_id", expected)

    @property
    def normalized_level(self) -> ExplanationLevel:
        return ExplanationLevel(self.level)

    @property
    def normalized_status(self) -> DecisionStatus:
        return DecisionStatus(self.status)

    @property
    def normalized_outcome(self) -> DecisionOutcome:
        return DecisionOutcome(self.outcome)

    @property
    def citations(self) -> tuple[SourceCitation, ...]:
        unique: dict[tuple[str, str, str], SourceCitation] = {}
        for section in self.sections:
            for citation in section.citations:
                key = (
                    citation.normalized_kind.value,
                    citation.reference_id,
                    citation.qualifier,
                )
                unique[key] = citation
        return tuple(unique[key] for key in sorted(unique))

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.decision_id,
                self.normalized_level.value,
                self.normalized_status.value,
                self.normalized_outcome.value,
                self.title,
                self.summary,
                self.confidence_label,
                ";".join(
                    ":".join(
                        (
                            section.normalized_type.value,
                            section.title,
                            ",".join(section.content),
                            ",".join(item.label for item in section.citations),
                        )
                    )
                    for section in self.sections
                ),
                str(self.requires_human_review),
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.answer_id,
            "decision_id": self.decision_id,
            "level": self.normalized_level.value,
            "status": self.normalized_status.value,
            "outcome": self.normalized_outcome.value,
            "title": self.title,
            "summary": self.summary,
            "confidence": self.confidence_label,
            "requires_human_review": self.requires_human_review,
            "sections": [
                {
                    "type": item.normalized_type.value,
                    "title": item.title,
                    "content": list(item.content),
                    "citations": [citation.label for citation in item.citations],
                }
                for item in self.sections
            ],
        }

    def render_text(self) -> str:
        lines = [self.title, self.summary, f"Confidence: {self.confidence_label}"]
        for section in self.sections:
            lines.append("")
            lines.append(section.title)
            lines.extend(f"- {item}" for item in section.content)
            if section.citations:
                lines.append(
                    "- References: "
                    + ", ".join(item.label for item in section.citations)
                )
        return "\n".join(lines)


@dataclass(frozen=True)
class ExplanationRequest:
    decision: DecisionRecord
    level: ExplanationLevel | str = ExplanationLevel.STANDARD
    max_citations: int = 20

    def __post_init__(self) -> None:
        ExplanationLevel(self.level)
        if self.max_citations < 1:
            raise ValueError("maximum citations must be positive")

    @property
    def normalized_level(self) -> ExplanationLevel:
        return ExplanationLevel(self.level)


class ExplainableAnswerRenderer:
    """Render deterministic public explanations from immutable decisions."""

    def render(
        self,
        decision: DecisionRecord,
        *,
        level: ExplanationLevel | str = ExplanationLevel.STANDARD,
        max_citations: int = 20,
    ) -> ExplainableAnswer:
        return self.render_request(ExplanationRequest(decision, level, max_citations))

    def render_request(self, request: ExplanationRequest) -> ExplainableAnswer:
        decision = request.decision
        level = request.normalized_level
        sections = self._sections(decision, level, request.max_citations)
        return ExplainableAnswer(
            decision_id=decision.decision_id,
            level=level,
            status=decision.normalized_status,
            outcome=decision.normalized_outcome,
            title=self._title(decision),
            summary=self._summary(decision),
            confidence_label=self._confidence_label(decision.confidence_score),
            sections=sections,
            requires_human_review=decision.requires_human_review,
        )

    def _sections(
        self,
        decision: DecisionRecord,
        level: ExplanationLevel,
        max_citations: int,
    ) -> tuple[ExplanationSection, ...]:
        sections = [self._conclusion_section(decision)]
        if level is ExplanationLevel.CONCISE:
            sections.extend(self._concise_sections(decision, max_citations))
            return tuple(sections)

        sections.append(self._basis_section(decision, max_citations))
        if decision.rule_links:
            sections.append(self._inference_section(decision, max_citations))
        sections.append(self._uncertainty_section(decision))
        if decision.limitations or decision.assumptions:
            sections.append(self._limits_section(decision))
        if decision.requires_human_review or decision.review_events:
            sections.append(self._review_section(decision))
        if level is ExplanationLevel.AUDIT:
            sections.append(self._audit_section(decision, max_citations))
        return tuple(sections)

    def _concise_sections(
        self,
        decision: DecisionRecord,
        max_citations: int,
    ) -> tuple[ExplanationSection, ...]:
        result: list[ExplanationSection] = []
        citations = self._evidence_citations(decision)[: min(3, max_citations)]
        if citations:
            result.append(
                ExplanationSection(
                    ExplanationSectionType.SOURCES,
                    "Main sources",
                    (f"{len(citations)} traceable source reference(s) used.",),
                    citations,
                )
            )
        if decision.conflict_ids or decision.requires_human_review:
            result.append(self._uncertainty_section(decision))
        return tuple(result)

    @staticmethod
    def _conclusion_section(decision: DecisionRecord) -> ExplanationSection:
        return ExplanationSection(
            ExplanationSectionType.CONCLUSION,
            "Conclusion",
            (decision.conclusion,),
            (SourceCitation(CitationKind.DECISION, decision.decision_id),),
        )

    def _basis_section(
        self,
        decision: DecisionRecord,
        max_citations: int,
    ) -> ExplanationSection:
        evidence = self._evidence_citations(decision)
        claims = self._claim_citations(decision)
        citations = (evidence + claims)[:max_citations]
        content = (
            f"The decision references {len(decision.evidence_links)} evidence item(s).",
            f"It considers {len(decision.claim_links)} versioned claim(s).",
        )
        if not citations:
            content += ("No factual source reference was available.",)
        return ExplanationSection(
            ExplanationSectionType.FACTUAL_BASIS,
            "Factual basis",
            content,
            citations,
        )

    def _inference_section(
        self,
        decision: DecisionRecord,
        max_citations: int,
    ) -> ExplanationSection:
        citations = self._rule_citations(decision)[:max_citations]
        return ExplanationSection(
            ExplanationSectionType.INFERENCES,
            "Inferences",
            (
                f"{len(decision.rule_links)} explicit versioned rule(s) were used.",
                "Rule-derived results remain distinct from confirmed facts.",
            ),
            citations,
        )

    def _uncertainty_section(self, decision: DecisionRecord) -> ExplanationSection:
        content = [decision.confidence_rationale]
        if decision.conflict_ids:
            content.append(
                f"{len(decision.conflict_ids)} conflict(s) affected this decision."
            )
        if decision.normalized_outcome is DecisionOutcome.ABSTENTION:
            content.append(
                "ROBY abstained instead of presenting an unsupported conclusion."
            )
        if decision.normalized_outcome is DecisionOutcome.BLOCKED:
            content.append("The request was blocked by governance boundaries.")
        if decision.requires_human_review:
            content.append("Human review is required before treating this as resolved.")
        citations = tuple(
            SourceCitation(CitationKind.CONFLICT, item)
            for item in decision.conflict_ids
        )
        return ExplanationSection(
            ExplanationSectionType.UNCERTAINTY,
            "Uncertainty and conflicts",
            tuple(content),
            citations,
        )

    @staticmethod
    def _limits_section(decision: DecisionRecord) -> ExplanationSection:
        content = tuple(
            [f"Limitation: {item}" for item in decision.limitations]
            + [f"Assumption: {item}" for item in decision.assumptions]
        )
        return ExplanationSection(
            ExplanationSectionType.LIMITS,
            "Limits and assumptions",
            content,
        )

    @staticmethod
    def _review_section(decision: DecisionRecord) -> ExplanationSection:
        content = [f"Review status: {decision.normalized_review_status.value}."]
        content.extend(
            f"{item.reviewer}: {item.normalized_status.value} — {item.comment}"
            for item in decision.review_events
        )
        return ExplanationSection(
            ExplanationSectionType.REVIEW,
            "Human review",
            tuple(content),
        )

    def _audit_section(
        self,
        decision: DecisionRecord,
        max_citations: int,
    ) -> ExplanationSection:
        citations = (
            self._evidence_citations(decision)
            + self._claim_citations(decision)
            + self._rule_citations(decision)
            + tuple(
                SourceCitation(CitationKind.CONFLICT, item)
                for item in decision.conflict_ids
            )
        )[:max_citations]
        content = (
            f"Decision id: {decision.decision_id}",
            f"Query id: {decision.query_id}",
            f"Context id: {decision.context_id}",
            f"Scope status: {decision.scope_status}",
            f"Decision status: {decision.normalized_status.value}",
            f"Created at: {decision.created_at.isoformat()}",
        )
        return ExplanationSection(
            ExplanationSectionType.AUDIT,
            "Audit details",
            content,
            citations,
        )

    @staticmethod
    def _title(decision: DecisionRecord) -> str:
        titles = {
            DecisionOutcome.CONCLUSION: "Governed conclusion",
            DecisionOutcome.ABSTENTION: "Governed abstention",
            DecisionOutcome.BLOCKED: "Governed block",
            DecisionOutcome.HUMAN_REVIEW: "Human review required",
        }
        return titles[decision.normalized_outcome]

    @staticmethod
    def _summary(decision: DecisionRecord) -> str:
        if decision.normalized_outcome is DecisionOutcome.CONCLUSION:
            return "ROBY reached a traceable conclusion from the recorded context."
        if decision.normalized_outcome is DecisionOutcome.ABSTENTION:
            return "ROBY did not have enough governed support for a conclusion."
        if decision.normalized_outcome is DecisionOutcome.BLOCKED:
            return (
                "ROBY did not proceed because the request crossed "
                "a governance boundary."
            )
        return "ROBY requires human review before this reasoning can be resolved."

    @staticmethod
    def _confidence_label(score: float) -> str:
        if score < 0.25:
            band = "insufficient"
        elif score < 0.50:
            band = "low"
        elif score < 0.70:
            band = "moderate"
        elif score < 0.90:
            band = "high"
        else:
            band = "very high"
        return f"{band} ({score:.0%})"

    @staticmethod
    def _evidence_citations(
        decision: DecisionRecord,
    ) -> tuple[SourceCitation, ...]:
        return tuple(
            SourceCitation(
                CitationKind.EVIDENCE,
                item.evidence_id,
                f"sha256:{item.fingerprint}",
            )
            for item in decision.evidence_links
        )

    @staticmethod
    def _claim_citations(decision: DecisionRecord) -> tuple[SourceCitation, ...]:
        return tuple(
            SourceCitation(
                CitationKind.CLAIM,
                item.claim_id,
                f"revision:{item.revision}",
            )
            for item in decision.claim_links
        )

    @staticmethod
    def _rule_citations(decision: DecisionRecord) -> tuple[SourceCitation, ...]:
        return tuple(
            SourceCitation(
                CitationKind.RULE,
                item.rule_id,
                f"version:{item.version}",
            )
            for item in decision.rule_links
        )
