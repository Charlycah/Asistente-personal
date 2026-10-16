from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class ExplicitComplexDecisionCriteriaStatus(StrEnum):
    NOT_COMPLEX_CRITERIA = "not_complex_criteria"
    EXPLICIT = "explicit"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT_CRITERIA = "insufficient_criteria"


@dataclass(frozen=True)
class ExplicitDecisionCriterionEvidence:
    criterion_id: str
    raw_text: str
    normalized_text: str
    start_offset: int
    end_offset: int
    ordinal: int
    required: bool
    required_source_span: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        if not self.criterion_id.startswith("explicit-decision-criterion-"):
            raise ValueError("explicit decision criterion id is invalid")
        if not self.raw_text or not self.normalized_text:
            raise ValueError("explicit decision criterion text must not be empty")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("explicit decision criterion span is invalid")
        if self.ordinal < 0:
            raise ValueError("explicit decision criterion ordinal must be non-negative")
        if self.required_source_span is not None:
            start, end = self.required_source_span
            if start < 0 or end <= start:
                raise ValueError("required criterion source span is invalid")
            if not self.required:
                raise ValueError("required source span requires required criterion")


@dataclass(frozen=True)
class ExplicitCriterionImportanceRelation:
    more_important_criterion_id: str
    less_important_criterion_id: str
    raw_text: str
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        if self.more_important_criterion_id == self.less_important_criterion_id:
            raise ValueError("criterion importance relation requires distinct criteria")
        if not self.raw_text:
            raise ValueError("criterion importance relation text must not be empty")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("criterion importance relation span is invalid")


@dataclass(frozen=True)
class ExplicitComplexDecisionCriteriaEvidence:
    status: ExplicitComplexDecisionCriteriaStatus
    source_text: str
    criteria: tuple[ExplicitDecisionCriterionEvidence, ...]
    importance_relations: tuple[ExplicitCriterionImportanceRelation, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-explicit-complex-decision-criteria-v1"
    read_only: bool = True
    generates_criteria: bool = False
    infers_importance: bool = False
    evaluates_options: bool = False
    resolves_context: bool = False
    uses_llm: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.source_fingerprint.strip():
            raise ValueError("complex criteria evidence fingerprint must not be blank")
        if self.status is ExplicitComplexDecisionCriteriaStatus.EXPLICIT:
            if len(self.criteria) < 2:
                raise ValueError(
                    "explicit complex criteria requires at least two criteria"
                )
        elif self.criteria or self.importance_relations:
            raise ValueError("non-explicit complex criteria cannot expose evidence")
        if len(self.criteria) > 5:
            raise ValueError("explicit complex criteria supports at most five criteria")
        if any(
            (
                not self.read_only,
                self.generates_criteria,
                self.infers_importance,
                self.evaluates_options,
                self.resolves_context,
                self.uses_llm,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("complex criteria evidence violates governed limits")
        criterion_ids = tuple(item.criterion_id for item in self.criteria)
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("explicit complex criterion ids must be unique")
        normalized = tuple(item.normalized_text.casefold() for item in self.criteria)
        if len(normalized) != len(set(normalized)):
            raise ValueError("explicit complex criteria must be textually unique")
        known_ids = set(criterion_ids)
        for expected_ordinal, criterion in enumerate(self.criteria):
            if criterion.ordinal != expected_ordinal:
                raise ValueError(
                    "explicit complex criterion ordinals must be contiguous"
                )
            if criterion.end_offset > len(self.source_text):
                raise ValueError("explicit complex criterion exceeds source text")
            source_slice = self.source_text[
                criterion.start_offset : criterion.end_offset
            ]
            if source_slice != criterion.raw_text:
                raise ValueError(
                    "explicit complex criterion span must match source text"
                )
            if criterion.required_source_span is not None:
                start, end = criterion.required_source_span
                if end > len(self.source_text):
                    raise ValueError("required criterion span exceeds source text")
        seen_relations: set[tuple[str, str]] = set()
        for relation in self.importance_relations:
            pair = (
                relation.more_important_criterion_id,
                relation.less_important_criterion_id,
            )
            if pair[0] not in known_ids or pair[1] not in known_ids:
                raise ValueError("importance relation references unknown criterion")
            if pair in seen_relations or (pair[1], pair[0]) in seen_relations:
                raise ValueError("importance relation is duplicate or contradictory")
            seen_relations.add(pair)
            if relation.end_offset > len(self.source_text):
                raise ValueError("importance relation exceeds source text")
            source_slice = self.source_text[relation.start_offset : relation.end_offset]
            if source_slice != relation.raw_text:
                raise ValueError("importance relation span must match source text")


class ExplicitComplexDecisionCriteriaEvidenceProducerV1:
    """Extract only bounded, explicit current-turn decision criteria evidence."""

    _MAX_CRITERIA = 5
    _CRITERIA_RE = re.compile(
        r"(?:^|[.!?]\s*)los\s+criterios\s+son\s+(?P<body>[^.!?]+)",
        re.IGNORECASE,
    )
    _AMBIGUOUS_NAMES = {"eso", "esto", "aquello", "el otro", "la otra", "lo anterior"}

    def analyze(self, text: str) -> ExplicitComplexDecisionCriteriaEvidence:
        source = text if isinstance(text, str) else str(text)
        match = self._CRITERIA_RE.search(source)
        if match is None:
            return self._result(
                ExplicitComplexDecisionCriteriaStatus.NOT_COMPLEX_CRITERIA, source
            )

        criterion_spans = self._criterion_spans(source, match)
        if criterion_spans is None:
            return self._result(
                ExplicitComplexDecisionCriteriaStatus.INSUFFICIENT_CRITERIA, source
            )
        if len(criterion_spans) > self._MAX_CRITERIA:
            return self._result(ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS, source)

        normalized_names = tuple(
            self._normalize(source[start:end]) for start, end in criterion_spans
        )
        if any(name.casefold() in self._AMBIGUOUS_NAMES for name in normalized_names):
            return self._result(ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS, source)
        if len({name.casefold() for name in normalized_names}) != len(normalized_names):
            return self._result(ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS, source)

        ids = tuple(self._criterion_id(name) for name in normalized_names)

        required_spans: dict[int, tuple[int, int]] = {}
        tail_start = match.end("body")
        tail = source[tail_start:]
        for index, name in enumerate(normalized_names):
            required_re = re.compile(
                rf"(?<![\w]){re.escape(name)}\s+es\s+obligatori[oa](?![\w])",
                re.IGNORECASE,
            )
            matches = tuple(required_re.finditer(tail))
            if len(matches) > 1:
                return self._result(
                    ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS, source
                )
            if matches:
                item = matches[0]
                required_spans[index] = (
                    tail_start + item.start(),
                    tail_start + item.end(),
                )

        relations: list[ExplicitCriterionImportanceRelation] = []
        relation_pairs: set[tuple[int, int]] = set()
        for more_index, more_name in enumerate(normalized_names):
            for less_index, less_name in enumerate(normalized_names):
                if more_index == less_index:
                    continue
                importance_re = re.compile(
                    rf"(?<![\w]){re.escape(more_name)}\s+es\s+"
                    rf"(?:m[aá]s\s+importante|prioritari[oa])\s+que\s+"
                    rf"{re.escape(less_name)}(?![\w])",
                    re.IGNORECASE,
                )
                for item in importance_re.finditer(tail):
                    pair = (more_index, less_index)
                    if (
                        pair in relation_pairs
                        or (less_index, more_index) in relation_pairs
                    ):
                        return self._result(
                            ExplicitComplexDecisionCriteriaStatus.AMBIGUOUS, source
                        )
                    relation_pairs.add(pair)
                    start_offset = tail_start + item.start()
                    end_offset = tail_start + item.end()
                    relations.append(
                        ExplicitCriterionImportanceRelation(
                            more_important_criterion_id=ids[more_index],
                            less_important_criterion_id=ids[less_index],
                            raw_text=source[start_offset:end_offset],
                            start_offset=start_offset,
                            end_offset=end_offset,
                        )
                    )

        criteria = tuple(
            ExplicitDecisionCriterionEvidence(
                criterion_id=ids[index],
                raw_text=source[start:end],
                normalized_text=normalized_names[index],
                start_offset=start,
                end_offset=end,
                ordinal=index,
                required=index in required_spans,
                required_source_span=required_spans.get(index),
            )
            for index, (start, end) in enumerate(criterion_spans)
        )
        return self._result(
            ExplicitComplexDecisionCriteriaStatus.EXPLICIT,
            source,
            criteria=criteria,
            importance_relations=tuple(relations),
        )

    @classmethod
    def _criterion_spans(
        cls,
        source: str,
        match: re.Match[str],
    ) -> tuple[tuple[int, int], ...] | None:
        body_start, body_end = match.span("body")
        body = source[body_start:body_end]
        parts = re.split(r"\s*,\s*|\s+y\s+", body, flags=re.IGNORECASE)
        if len(parts) < 2:
            return None
        spans: list[tuple[int, int]] = []
        cursor = 0
        for part in parts:
            located = body.find(part, cursor)
            if located < 0:
                return None
            start = body_start + located
            end = start + len(part)
            start, end = cls._trim_span(source, start, end)
            if start >= end:
                return None
            spans.append((start, end))
            cursor = located + len(part)
        return tuple(spans)

    @staticmethod
    def _trim_span(source: str, start: int, end: int) -> tuple[int, int]:
        while start < end and source[start].isspace():
            start += 1
        while end > start and source[end - 1].isspace():
            end -= 1
        return start, end

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().split())

    @staticmethod
    def _criterion_id(normalized_text: str) -> str:
        digest = sha256(
            (
                "explicit-complex-decision-criterion-v1\n" + normalized_text.casefold()
            ).encode("utf-8")
        ).hexdigest()
        return f"explicit-decision-criterion-{digest[:20]}"

    @staticmethod
    def _result(
        status: ExplicitComplexDecisionCriteriaStatus,
        source: str,
        *,
        criteria: tuple[ExplicitDecisionCriterionEvidence, ...] = (),
        importance_relations: tuple[ExplicitCriterionImportanceRelation, ...] = (),
    ) -> ExplicitComplexDecisionCriteriaEvidence:
        payload = repr(
            (
                "post-m409.1-explicit-complex-decision-criteria-v1",
                status.value,
                source,
                criteria,
                importance_relations,
            )
        )
        return ExplicitComplexDecisionCriteriaEvidence(
            status=status,
            source_text=source,
            criteria=criteria,
            importance_relations=importance_relations,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
