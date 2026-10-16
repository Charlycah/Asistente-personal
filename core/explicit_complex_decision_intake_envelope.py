from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.explicit_complex_decision_criteria_evidence import (
    ExplicitComplexDecisionCriteriaEvidence,
    ExplicitComplexDecisionCriteriaEvidenceProducerV1,
    ExplicitComplexDecisionCriteriaStatus,
)
from core.explicit_human_decision_deliberation import (
    ExplicitDecisionDeliberationEvidence,
    ExplicitDecisionDeliberationStatus,
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_option_criterion_evidence import (
    ExplicitOptionCriterionEvidence,
    ExplicitOptionCriterionEvidenceProducerV1,
    ExplicitOptionCriterionEvidenceStatus,
)


class ExplicitComplexDecisionIntakeEnvelopeStatus(StrEnum):
    NOT_ENVELOPE = "not_envelope"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    AMBIGUOUS = "ambiguous"


class ExplicitComplexDecisionIntakeSectionKind(StrEnum):
    DECISION = "decision"
    CRITERIA = "criteria"
    EVIDENCE = "evidence"


@dataclass(frozen=True)
class ExplicitComplexDecisionIntakeSection:
    kind: ExplicitComplexDecisionIntakeSectionKind
    raw_payload: str
    start_offset: int
    end_offset: int
    payload_fingerprint: str

    def __post_init__(self) -> None:
        if not self.raw_payload:
            raise ValueError(
                "complex decision intake section payload must not be empty"
            )
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("complex decision intake section span is invalid")
        if len(self.payload_fingerprint) != 64:
            raise ValueError(
                "complex decision intake section fingerprint must be SHA-256"
            )


@dataclass(frozen=True)
class ExplicitComplexDecisionIntakeEnvelopeResult:
    status: ExplicitComplexDecisionIntakeEnvelopeStatus
    source_text: str
    source_fingerprint: str
    decision_section: ExplicitComplexDecisionIntakeSection | None
    criteria_section: ExplicitComplexDecisionIntakeSection | None
    evidence_section: ExplicitComplexDecisionIntakeSection | None
    deliberation_evidence: ExplicitDecisionDeliberationEvidence | None
    criteria_evidence: ExplicitComplexDecisionCriteriaEvidence | None
    option_criterion_evidence: ExplicitOptionCriterionEvidence | None
    schema_version: str = "post-m409.1-explicit-complex-decision-intake-envelope-v1"
    read_only: bool = True
    framing_only: bool = True
    parses_decision_semantics: bool = False
    parses_criteria_semantics: bool = False
    parses_option_criterion_semantics: bool = False
    generates_options: bool = False
    generates_criteria: bool = False
    infers_outcomes: bool = False
    resolves_context: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    uses_memory: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    performs_linkage: bool = False
    builds_assessments: bool = False
    assembles_gcdr_input: bool = False
    calls_gcdr: bool = False
    evaluates_decision: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if len(self.source_fingerprint) != 64:
            raise ValueError("complex decision intake fingerprint must be SHA-256")
        sections = (
            self.decision_section,
            self.criteria_section,
            self.evidence_section,
        )
        evidence = (
            self.deliberation_evidence,
            self.criteria_evidence,
            self.option_criterion_evidence,
        )
        if self.status is ExplicitComplexDecisionIntakeEnvelopeStatus.COMPLETE:
            if any(item is None for item in sections + evidence):
                raise ValueError(
                    "complete complex decision intake requires all artifacts"
                )
        if self.status is ExplicitComplexDecisionIntakeEnvelopeStatus.NOT_ENVELOPE:
            if any(item is not None for item in sections + evidence):
                raise ValueError("non-envelope intake cannot expose parsed artifacts")
        if any(
            (
                not self.read_only,
                not self.framing_only,
                self.parses_decision_semantics,
                self.parses_criteria_semantics,
                self.parses_option_criterion_semantics,
                self.generates_options,
                self.generates_criteria,
                self.infers_outcomes,
                self.resolves_context,
                self.uses_llm,
                self.uses_retrieval,
                self.uses_memory,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.performs_linkage,
                self.builds_assessments,
                self.assembles_gcdr_input,
                self.calls_gcdr,
                self.evaluates_decision,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("complex decision intake violates governed limits")


class ExplicitComplexDecisionIntakeEnvelopeFoundationV1:
    """Frame one explicit turn and delegate semantics to frozen evidence producers."""

    _HEADER_RE = re.compile(
        r"(?im)^(?P<header>Decisión|Criterios|Evidencia):[ \t]*$"
    )
    _EXPECTED_HEADERS = ("decisión", "criterios", "evidencia")

    def __init__(self) -> None:
        self._deliberation = ExplicitHumanDecisionDeliberationEvidenceProducer()
        self._criteria = ExplicitComplexDecisionCriteriaEvidenceProducerV1()
        self._relations = ExplicitOptionCriterionEvidenceProducerV1()

    def analyze(self, text: str) -> ExplicitComplexDecisionIntakeEnvelopeResult:
        source = text if isinstance(text, str) else str(text)
        headers = tuple(self._HEADER_RE.finditer(source))
        if not headers:
            return self._result(
                ExplicitComplexDecisionIntakeEnvelopeStatus.NOT_ENVELOPE,
                source,
            )

        header_names = tuple(match.group("header").casefold() for match in headers)
        if len(headers) != 3 or header_names != self._EXPECTED_HEADERS:
            return self._result(
                ExplicitComplexDecisionIntakeEnvelopeStatus.AMBIGUOUS,
                source,
            )
        if source[: headers[0].start()].strip():
            return self._result(
                ExplicitComplexDecisionIntakeEnvelopeStatus.AMBIGUOUS,
                source,
            )

        spans = []
        for index, match in enumerate(headers):
            raw_start = match.end()
            raw_end = headers[index + 1].start() if index < 2 else len(source)
            start, end = self._trim_span(source, raw_start, raw_end)
            if start >= end:
                return self._result(
                    ExplicitComplexDecisionIntakeEnvelopeStatus.INCOMPLETE,
                    source,
                )
            spans.append((start, end))

        decision = self._section(
            ExplicitComplexDecisionIntakeSectionKind.DECISION,
            source,
            *spans[0],
        )
        criteria = self._section(
            ExplicitComplexDecisionIntakeSectionKind.CRITERIA,
            source,
            *spans[1],
        )
        evidence = self._section(
            ExplicitComplexDecisionIntakeSectionKind.EVIDENCE,
            source,
            *spans[2],
        )

        deliberation_evidence = self._deliberation.analyze(decision.raw_payload)
        criteria_evidence = self._criteria.analyze(criteria.raw_payload)
        relation_evidence = self._relations.analyze(evidence.raw_payload)

        complete = (
            deliberation_evidence.status is ExplicitDecisionDeliberationStatus.EXPLICIT
            and criteria_evidence.status
            is ExplicitComplexDecisionCriteriaStatus.EXPLICIT
            and relation_evidence.status
            is ExplicitOptionCriterionEvidenceStatus.EXPLICIT
        )
        status = (
            ExplicitComplexDecisionIntakeEnvelopeStatus.COMPLETE
            if complete
            else ExplicitComplexDecisionIntakeEnvelopeStatus.INCOMPLETE
        )
        return self._result(
            status,
            source,
            decision_section=decision,
            criteria_section=criteria,
            evidence_section=evidence,
            deliberation_evidence=deliberation_evidence,
            criteria_evidence=criteria_evidence,
            option_criterion_evidence=relation_evidence,
        )

    @staticmethod
    def _trim_span(source: str, start: int, end: int) -> tuple[int, int]:
        while start < end and source[start].isspace():
            start += 1
        while end > start and source[end - 1].isspace():
            end -= 1
        return start, end

    @staticmethod
    def _section(
        kind: ExplicitComplexDecisionIntakeSectionKind,
        source: str,
        start: int,
        end: int,
    ) -> ExplicitComplexDecisionIntakeSection:
        payload = source[start:end]
        return ExplicitComplexDecisionIntakeSection(
            kind=kind,
            raw_payload=payload,
            start_offset=start,
            end_offset=end,
            payload_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )

    @staticmethod
    def _result(
        status: ExplicitComplexDecisionIntakeEnvelopeStatus,
        source: str,
        *,
        decision_section: ExplicitComplexDecisionIntakeSection | None = None,
        criteria_section: ExplicitComplexDecisionIntakeSection | None = None,
        evidence_section: ExplicitComplexDecisionIntakeSection | None = None,
        deliberation_evidence: ExplicitDecisionDeliberationEvidence | None = None,
        criteria_evidence: ExplicitComplexDecisionCriteriaEvidence | None = None,
        option_criterion_evidence: ExplicitOptionCriterionEvidence | None = None,
    ) -> ExplicitComplexDecisionIntakeEnvelopeResult:
        payload = repr(
            (
                "post-m409.1-explicit-complex-decision-intake-envelope-v1",
                status.value,
                source,
                decision_section,
                criteria_section,
                evidence_section,
                getattr(deliberation_evidence, "source_fingerprint", None),
                getattr(criteria_evidence, "source_fingerprint", None),
                getattr(option_criterion_evidence, "source_fingerprint", None),
            )
        )
        return ExplicitComplexDecisionIntakeEnvelopeResult(
            status=status,
            source_text=source,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
            decision_section=decision_section,
            criteria_section=criteria_section,
            evidence_section=evidence_section,
            deliberation_evidence=deliberation_evidence,
            criteria_evidence=criteria_evidence,
            option_criterion_evidence=option_criterion_evidence,
        )
