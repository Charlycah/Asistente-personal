from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class ExplicitDecisionDeliberationStatus(StrEnum):
    NOT_DELIBERATION = "not_deliberation"
    EXPLICIT = "explicit"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT_OPTIONS = "insufficient_options"


@dataclass(frozen=True)
class ExplicitDecisionAlternative:
    raw_text: str
    normalized_text: str
    start_offset: int
    end_offset: int
    ordinal: int

    def __post_init__(self) -> None:
        if not self.raw_text:
            raise ValueError("explicit decision alternative raw text must not be empty")
        if not self.normalized_text:
            raise ValueError(
                "explicit decision alternative normalized text must not be empty"
            )
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("explicit decision alternative span is invalid")
        if self.ordinal < 0:
            raise ValueError(
                "explicit decision alternative ordinal must be non-negative"
            )


@dataclass(frozen=True)
class ExplicitDecisionDeliberationEvidence:
    status: ExplicitDecisionDeliberationStatus
    source_text: str
    alternatives: tuple[ExplicitDecisionAlternative, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-explicit-deliberation-v1"
    read_only: bool = True
    advisory_only: bool = False
    generates_alternatives: bool = False
    resolves_context: bool = False
    uses_llm: bool = False
    persists_results: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.source_fingerprint.strip():
            raise ValueError("explicit deliberation fingerprint must not be blank")
        if self.status is ExplicitDecisionDeliberationStatus.EXPLICIT:
            if len(self.alternatives) < 2:
                raise ValueError(
                    "explicit deliberation requires at least two alternatives"
                )
        elif self.alternatives:
            raise ValueError("non-explicit deliberation cannot expose alternatives")
        if len(self.alternatives) > 5:
            raise ValueError("explicit deliberation supports at most five alternatives")
        if any(
            (
                not self.read_only,
                self.advisory_only,
                self.generates_alternatives,
                self.resolves_context,
                self.uses_llm,
                self.persists_results,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("explicit deliberation evidence violates governed limits")
        previous_end = -1
        for expected_ordinal, alternative in enumerate(self.alternatives):
            if alternative.ordinal != expected_ordinal:
                raise ValueError(
                    "explicit decision alternative ordinals must be contiguous"
                )
            if alternative.end_offset > len(self.source_text):
                raise ValueError("explicit decision alternative exceeds source text")
            if alternative.start_offset < previous_end:
                raise ValueError("explicit decision alternative spans must not overlap")
            if (
                self.source_text[alternative.start_offset : alternative.end_offset]
                != alternative.raw_text
            ):
                raise ValueError(
                    "explicit decision alternative span must match source text"
                )
            previous_end = alternative.end_offset


class ExplicitHumanDecisionDeliberationEvidenceProducer:
    """Extract only explicit current-turn decision alternatives.

    This producer is a deterministic evidence parser. It does not generate alternatives,
    resolve conversational references, consult memory, rank options, call M391.6,
    or grant decision authority.
    """

    _MAX_ALTERNATIVES = 5
    _COORDINATOR_RE = re.compile(r"\s+o\s+", re.IGNORECASE)
    _AMBIGUOUS_ALTERNATIVES = {
        "el otro",
        "la otra",
        "los otros",
        "las otras",
        "el anterior",
        "la anterior",
        "ese",
        "esa",
        "esos",
        "esas",
        "eso",
        "esto",
        "aquello",
        "la de antes",
        "el de antes",
    }
    _INCOMPLETE_ALTERNATIVES = {
        "qué otra cosa",
        "que otra cosa",
        "otra cosa",
        "qué más",
        "que más",
        "algo más",
        "algo mas",
    }

    _BETWEEN_RE = re.compile(
        r"^\s*¿?\s*entre\s+"
        r"(?P<a>.+?)\s+y\s+(?P<b>.+?)\s*,\s*¿?\s*"
        r"(?:cu[aá]l|que|qué)\s+(?:me\s+)?conviene\s*\?\s*$",
        re.IGNORECASE,
    )
    _WHAT_CONVENIENT_RE = re.compile(
        r"^\s*¿?\s*(?:que|qué)\s+me\s+conviene\s*:\s*"
        r"(?P<a>.+?)\s+o\s+(?P<b>.+?)\s*\?\s*$",
        re.IGNORECASE,
    )
    _CONVENIENT_RE = re.compile(
        r"^\s*¿?\s*conviene\s+"
        r"(?P<a>.+?)\s+o\s+(?P<b>.+?)\s*\?\s*$",
        re.IGNORECASE,
    )
    _SIMPLE_BINARY_RE = re.compile(
        r"^\s*¿?\s*(?P<a>.+?)\s+o\s+(?P<b>.+?)\s*\?\s*$",
        re.IGNORECASE,
    )
    _MARKED_OPTIONS_RE = re.compile(
        r"^\s*tengo\s+(?P<count>dos|tres|cuatro|cinco|[2-5])\s+"
        r"opciones?\s*:\s*(?P<body>.+?)\s*[.]?\s*$",
        re.IGNORECASE,
    )
    _INSUFFICIENT_RE = re.compile(
        r"^\s*¿?\s*(?:(?:que|qué)\s+me\s+conviene|"
        r"(?:que|qué)\s+opciones\s+tengo|(?:cu[aá]les)\s+son\s+mis\s+opciones)"
        r"\s*\?\s*$",
        re.IGNORECASE,
    )

    _COUNT_WORDS = {
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
    }

    def analyze(self, text: str) -> ExplicitDecisionDeliberationEvidence:
        source = text if isinstance(text, str) else str(text)
        if not source.strip():
            return self._result(
                ExplicitDecisionDeliberationStatus.NOT_DELIBERATION,
                source,
            )

        marked = self._marked_options(source)
        if marked is not None:
            return self._from_spans(source, marked)

        for pattern in (
            self._BETWEEN_RE,
            self._WHAT_CONVENIENT_RE,
            self._CONVENIENT_RE,
            self._SIMPLE_BINARY_RE,
        ):
            match = pattern.match(source)
            if match is None:
                continue
            spans = self._binary_spans(source, match)
            if spans is None:
                return self._result(
                    ExplicitDecisionDeliberationStatus.INSUFFICIENT_OPTIONS,
                    source,
                )
            if (
                pattern is self._SIMPLE_BINARY_RE
                and self._has_internal_sentence_boundary(source, spans)
            ):
                return self._result(
                    ExplicitDecisionDeliberationStatus.NOT_DELIBERATION,
                    source,
                )
            return self._from_spans(source, spans)

        if self._INSUFFICIENT_RE.match(source):
            return self._result(
                ExplicitDecisionDeliberationStatus.INSUFFICIENT_OPTIONS,
                source,
            )
        return self._result(
            ExplicitDecisionDeliberationStatus.NOT_DELIBERATION,
            source,
        )

    def _marked_options(self, source: str) -> tuple[tuple[int, int], ...] | None:
        match = self._MARKED_OPTIONS_RE.match(source)
        if match is None:
            return None
        expected = self._count(match.group("count"))
        body_start, body_end = match.span("body")
        body = source[body_start:body_end]
        coordinator_matches = tuple(self._COORDINATOR_RE.finditer(body))
        if len(coordinator_matches) != 1:
            return ()
        coordinator = coordinator_matches[0]
        left = body[: coordinator.start()]
        left_parts = list(re.finditer(r"[^,]+", left))
        if len(left_parts) + 1 != expected:
            return ()
        spans = [
            self._trim_span(
                source,
                body_start + part.start(),
                body_start + part.end(),
            )
            for part in left_parts
        ]
        spans.append(
            self._trim_span(
                source,
                body_start + coordinator.end(),
                body_start + len(body),
            )
        )
        if any(start >= end for start, end in spans):
            return ()
        return tuple(spans)

    def _binary_spans(
        self,
        source: str,
        match: re.Match[str],
    ) -> tuple[tuple[int, int], tuple[int, int]] | None:
        a_start, a_end = self._trim_span(source, *match.span("a"))
        b_start, b_end = self._trim_span(source, *match.span("b"))
        a = source[a_start:a_end]
        b = source[b_start:b_end]
        if not a or not b:
            return None
        if "," in a or "," in b:
            return None
        if self._COORDINATOR_RE.search(a) or self._COORDINATOR_RE.search(b):
            return None
        return ((a_start, a_end), (b_start, b_end))

    @staticmethod
    def _has_internal_sentence_boundary(
        source: str,
        spans: tuple[tuple[int, int], tuple[int, int]],
    ) -> bool:
        for start, end in spans:
            candidate = source[start:end]
            if "¿" in candidate or re.search(r"[.!?]\s", candidate):
                return True
        return False

    def _from_spans(
        self,
        source: str,
        spans: tuple[tuple[int, int], ...],
    ) -> ExplicitDecisionDeliberationEvidence:
        if not 2 <= len(spans) <= self._MAX_ALTERNATIVES:
            return self._result(
                ExplicitDecisionDeliberationStatus.INSUFFICIENT_OPTIONS,
                source,
            )
        alternatives = tuple(
            self._alternative(source, start, end, ordinal)
            for ordinal, (start, end) in enumerate(spans)
        )
        normalized = tuple(item.normalized_text.casefold() for item in alternatives)
        if any(self._is_ambiguous(value) for value in normalized):
            return self._result(ExplicitDecisionDeliberationStatus.AMBIGUOUS, source)
        if any(value in self._INCOMPLETE_ALTERNATIVES for value in normalized):
            return self._result(
                ExplicitDecisionDeliberationStatus.INSUFFICIENT_OPTIONS,
                source,
            )
        if len(set(normalized)) != len(normalized):
            return self._result(
                ExplicitDecisionDeliberationStatus.INSUFFICIENT_OPTIONS,
                source,
            )
        return self._result(
            ExplicitDecisionDeliberationStatus.EXPLICIT,
            source,
            alternatives,
        )

    @staticmethod
    def _alternative(
        source: str,
        start: int,
        end: int,
        ordinal: int,
    ) -> ExplicitDecisionAlternative:
        raw = source[start:end]
        normalized = re.sub(r"\s+", " ", raw.strip())
        return ExplicitDecisionAlternative(
            raw_text=raw,
            normalized_text=normalized,
            start_offset=start,
            end_offset=end,
            ordinal=ordinal,
        )

    @classmethod
    def _is_ambiguous(cls, value: str) -> bool:
        return value in cls._AMBIGUOUS_ALTERNATIVES

    @classmethod
    def _count(cls, raw: str) -> int:
        folded = raw.casefold()
        return cls._COUNT_WORDS.get(folded, int(folded) if folded.isdigit() else 0)

    @staticmethod
    def _trim_span(source: str, start: int, end: int) -> tuple[int, int]:
        while start < end and source[start].isspace():
            start += 1
        while end > start and source[end - 1].isspace():
            end -= 1
        return start, end

    @classmethod
    def _result(
        cls,
        status: ExplicitDecisionDeliberationStatus,
        source: str,
        alternatives: tuple[ExplicitDecisionAlternative, ...] = (),
    ) -> ExplicitDecisionDeliberationEvidence:
        fingerprint_payload = (
            status.value,
            source,
            tuple(
                (
                    item.raw_text,
                    item.normalized_text,
                    item.start_offset,
                    item.end_offset,
                    item.ordinal,
                )
                for item in alternatives
            ),
        )
        fingerprint = sha256(repr(fingerprint_payload).encode("utf-8")).hexdigest()
        return ExplicitDecisionDeliberationEvidence(
            status=status,
            source_text=source,
            alternatives=alternatives,
            source_fingerprint=fingerprint,
        )
