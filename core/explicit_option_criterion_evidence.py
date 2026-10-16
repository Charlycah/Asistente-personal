from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class ExplicitOptionCriterionEvidenceStatus(StrEnum):
    NOT_OPTION_CRITERION_EVIDENCE = "not_option_criterion_evidence"
    EXPLICIT = "explicit"
    AMBIGUOUS = "ambiguous"


class ExplicitOptionCriterionOutcome(StrEnum):
    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class ExplicitOptionCriterionRelationEvidence:
    option_reference: str
    criterion_reference: str
    outcome: ExplicitOptionCriterionOutcome
    raw_text: str
    start_offset: int
    end_offset: int
    ordinal: int
    evidence_id: str

    def __post_init__(self) -> None:
        if not self.option_reference.strip() or not self.criterion_reference.strip():
            raise ValueError("option criterion evidence requires explicit references")
        if not isinstance(self.outcome, ExplicitOptionCriterionOutcome):
            raise ValueError("option criterion evidence outcome is invalid")
        if not self.raw_text:
            raise ValueError("option criterion evidence text must not be empty")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("option criterion evidence span is invalid")
        if self.ordinal < 0:
            raise ValueError("option criterion evidence ordinal must be non-negative")
        if not self.evidence_id.startswith("explicit-option-criterion-evidence-"):
            raise ValueError("option criterion evidence id is invalid")


@dataclass(frozen=True)
class ExplicitOptionCriterionEvidence:
    status: ExplicitOptionCriterionEvidenceStatus
    source_text: str
    relations: tuple[ExplicitOptionCriterionRelationEvidence, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-explicit-option-criterion-evidence-v1"
    read_only: bool = True
    generates_options: bool = False
    generates_criteria: bool = False
    infers_outcome: bool = False
    resolves_context: bool = False
    uses_llm: bool = False
    uses_retrieval: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    evaluates_decision: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.source_fingerprint.strip():
            raise ValueError("option criterion evidence fingerprint must not be blank")
        if self.status is ExplicitOptionCriterionEvidenceStatus.EXPLICIT:
            if not self.relations:
                raise ValueError(
                    "explicit option criterion evidence requires relations"
                )
        elif self.relations:
            raise ValueError(
                "non-explicit option criterion result cannot expose relations"
            )
        if any(
            (
                not self.read_only,
                self.generates_options,
                self.generates_criteria,
                self.infers_outcome,
                self.resolves_context,
                self.uses_llm,
                self.uses_retrieval,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.evaluates_decision,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("option criterion evidence violates governed limits")
        seen_pairs: dict[tuple[str, str], ExplicitOptionCriterionOutcome] = {}
        previous_end = -1
        for expected_ordinal, relation in enumerate(self.relations):
            if relation.ordinal != expected_ordinal:
                raise ValueError(
                    "option criterion evidence ordinals must be contiguous"
                )
            if relation.end_offset > len(self.source_text):
                raise ValueError("option criterion evidence exceeds source text")
            if relation.start_offset < previous_end:
                raise ValueError("option criterion evidence spans must not overlap")
            if (
                self.source_text[relation.start_offset : relation.end_offset]
                != relation.raw_text
            ):
                raise ValueError(
                    "option criterion evidence span must match source text"
                )
            pair = (
                relation.option_reference.casefold(),
                relation.criterion_reference.casefold(),
            )
            prior = seen_pairs.get(pair)
            if prior is not None and prior is not relation.outcome:
                raise ValueError("option criterion evidence cannot contradict one pair")
            if prior is not None:
                raise ValueError("option criterion evidence pair must be unique")
            seen_pairs[pair] = relation.outcome
            previous_end = relation.end_offset


class ExplicitOptionCriterionEvidenceProducerV1:
    """Extract only bounded explicit current-turn option×criterion relations."""

    _MAX_RELATIONS = 10
    _REF = (
        r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9][\wÁÉÍÓÚÜÑáéíóúüñ-]*(?:\s+[\wÁÉÍÓÚÜÑáéíóúüñ-]+){0,3}"
    )
    _AMBIGUOUS_REFERENCES = {
        "eso",
        "esto",
        "aquello",
        "esa",
        "ese",
        "esta",
        "este",
        "la primera",
        "la segunda",
        "el primero",
        "el segundo",
        "la otra",
        "el otro",
    }

    _PATTERNS = (
        (
            ExplicitOptionCriterionOutcome.INSUFFICIENT,
            re.compile(
                rf"(?P<raw>(?:no\s+s[eé]|no\s+est[aá]\s+claro)\s+si\s+"
                rf"(?P<option>{_REF})\s+(?:cumple|satisface)\s+"
                rf"(?P<criterion>{_REF}))",
                re.IGNORECASE,
            ),
        ),
        (
            ExplicitOptionCriterionOutcome.UNFAVORABLE,
            re.compile(
                rf"(?P<raw>(?P<option>{_REF})\s+no\s+(?:cumple|satisface)\s+"
                rf"(?P<criterion>{_REF}))",
                re.IGNORECASE,
            ),
        ),
        (
            ExplicitOptionCriterionOutcome.FAVORABLE,
            re.compile(
                rf"(?P<raw>(?P<option>{_REF})\s+(?:cumple|satisface)\s+"
                rf"(?P<criterion>{_REF}))",
                re.IGNORECASE,
            ),
        ),
        (
            ExplicitOptionCriterionOutcome.UNFAVORABLE,
            re.compile(
                rf"(?P<raw>(?P<option>{_REF})\s+es\s+desfavorable\s+"
                rf"respecto\s+de\s+(?P<criterion>{_REF}))",
                re.IGNORECASE,
            ),
        ),
        (
            ExplicitOptionCriterionOutcome.FAVORABLE,
            re.compile(
                rf"(?P<raw>(?P<option>{_REF})\s+es\s+favorable\s+"
                rf"respecto\s+de\s+(?P<criterion>{_REF}))",
                re.IGNORECASE,
            ),
        ),
    )

    def analyze(self, text: str) -> ExplicitOptionCriterionEvidence:
        source = text if isinstance(text, str) else str(text)
        candidates: list[tuple[int, int, ExplicitOptionCriterionOutcome, str, str]] = []
        for outcome, pattern in self._PATTERNS:
            for match in pattern.finditer(source):
                start, end = match.span("raw")
                candidates.append(
                    (
                        start,
                        end,
                        outcome,
                        self._normalize_reference(match.group("option")),
                        self._normalize_reference(match.group("criterion")),
                    )
                )

        if not candidates:
            return self._result(
                ExplicitOptionCriterionEvidenceStatus.NOT_OPTION_CRITERION_EVIDENCE,
                source,
            )

        candidates.sort(key=lambda item: (item[0], -(item[1] - item[0])))
        selected: list[tuple[int, int, ExplicitOptionCriterionOutcome, str, str]] = []
        for candidate in candidates:
            start, end, *_ = candidate
            if any(
                start < other_end and end > other_start
                for other_start, other_end, *_ in selected
            ):
                continue
            selected.append(candidate)
        selected.sort(key=lambda item: item[0])

        if len(selected) > self._MAX_RELATIONS:
            return self._result(ExplicitOptionCriterionEvidenceStatus.AMBIGUOUS, source)

        if any(
            option.casefold() in self._AMBIGUOUS_REFERENCES
            or criterion.casefold() in self._AMBIGUOUS_REFERENCES
            for _, _, _, option, criterion in selected
        ):
            return self._result(ExplicitOptionCriterionEvidenceStatus.AMBIGUOUS, source)

        pair_outcomes: dict[tuple[str, str], ExplicitOptionCriterionOutcome] = {}
        for _, _, outcome, option, criterion in selected:
            pair = (option.casefold(), criterion.casefold())
            previous = pair_outcomes.get(pair)
            if previous is not None:
                return self._result(
                    ExplicitOptionCriterionEvidenceStatus.AMBIGUOUS, source
                )
            pair_outcomes[pair] = outcome

        relations = tuple(
            ExplicitOptionCriterionRelationEvidence(
                option_reference=option,
                criterion_reference=criterion,
                outcome=outcome,
                raw_text=source[start:end],
                start_offset=start,
                end_offset=end,
                ordinal=index,
                evidence_id=self._evidence_id(option, criterion, outcome),
            )
            for index, (start, end, outcome, option, criterion) in enumerate(selected)
        )
        return self._result(
            ExplicitOptionCriterionEvidenceStatus.EXPLICIT,
            source,
            relations,
        )

    @staticmethod
    def _normalize_reference(value: str) -> str:
        return " ".join(value.strip().split())

    @staticmethod
    def _evidence_id(
        option: str,
        criterion: str,
        outcome: ExplicitOptionCriterionOutcome,
    ) -> str:
        payload = f"{option.casefold()}|{criterion.casefold()}|{outcome.value}"
        digest = sha256(payload.encode("utf-8")).hexdigest()[:20]
        return f"explicit-option-criterion-evidence-{digest}"

    @staticmethod
    def _fingerprint(
        source: str,
        relations: tuple[ExplicitOptionCriterionRelationEvidence, ...],
    ) -> str:
        payload = "|".join(
            (
                source,
                *(
                    f"{item.option_reference}|{item.criterion_reference}|"
                    f"{item.outcome.value}|{item.start_offset}|{item.end_offset}"
                    for item in relations
                ),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def _result(
        self,
        status: ExplicitOptionCriterionEvidenceStatus,
        source: str,
        relations: tuple[ExplicitOptionCriterionRelationEvidence, ...] = (),
    ) -> ExplicitOptionCriterionEvidence:
        return ExplicitOptionCriterionEvidence(
            status=status,
            source_text=source,
            relations=relations,
            source_fingerprint=self._fingerprint(source, relations),
        )
