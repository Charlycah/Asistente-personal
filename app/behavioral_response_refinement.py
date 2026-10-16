from __future__ import annotations

import re
from dataclasses import dataclass

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class BehavioralRefinementSnapshot:
    refinements: int
    concise_responses: int
    technical_labels_removed: int
    redundant_closings_removed: int
    stacked_openers_removed: int
    repeated_sentences_removed: int
    repeated_transitions_varied: int
    excessive_blank_lines_removed: int


class BehavioralResponseRefinement:
    """Adapts operational answers to the user's requested interaction style."""

    _CONCISE_TRIGGERS = (
        "breve",
        "corto",
        "resumido",
        "en una frase",
        "sin detalles",
        "solo decime",
    )
    _TECHNICAL_LABEL = re.compile(
        r"^(?:resultado|respuesta|capacidad|modulo|runtime|interceptor)"
        r"\s+[\w.-]+:\s*",
        re.IGNORECASE,
    )
    _REDUNDANT_CLOSINGS = (
        "Decime si necesitas algo mas.",
        "Decime si queres que siga.",
        "Estoy aca si necesitas algo mas.",
        "Podes preguntarme lo que quieras.",
    )
    _GENERIC_OPENERS = {
        "claro",
        "si",
        "sí",
        "por supuesto",
        "desde luego",
        "perfecto",
    }
    _PROTECTED_CODE = re.compile(r"(```.*?```|`[^`\n]+`)", re.DOTALL)

    def __init__(self) -> None:
        self._refinements = 0
        self._concise_responses = 0
        self._technical_labels_removed = 0
        self._redundant_closings_removed = 0
        self._stacked_openers_removed = 0
        self._repeated_sentences_removed = 0
        self._repeated_transitions_varied = 0
        self._excessive_blank_lines_removed = 0

    @property
    def snapshot(self) -> BehavioralRefinementSnapshot:
        return BehavioralRefinementSnapshot(
            refinements=self._refinements,
            concise_responses=self._concise_responses,
            technical_labels_removed=self._technical_labels_removed,
            redundant_closings_removed=self._redundant_closings_removed,
            stacked_openers_removed=self._stacked_openers_removed,
            repeated_sentences_removed=self._repeated_sentences_removed,
            repeated_transitions_varied=self._repeated_transitions_varied,
            excessive_blank_lines_removed=self._excessive_blank_lines_removed,
        )

    def refine(
        self,
        request: GovernedConversationPipelineRequest | None,
        result: GovernedOperationalInterception,
    ) -> GovernedOperationalInterception:
        text = self._remove_technical_labels(result.response_text.strip())
        text = self._remove_stacked_openers(text)
        text = self._remove_adjacent_repeated_sentences(text)
        text = self._vary_adjacent_repeated_transitions(text)
        text = self._collapse_excessive_blank_lines(text)
        text = self._remove_redundant_closing(text)
        if request is not None and self._asks_for_concise_answer(request.text):
            text = self._make_concise(text)
        if text == result.response_text:
            return result
        self._refinements += 1
        return GovernedOperationalInterception(
            response_text=text,
            rationale=result.rationale,
        )

    def _remove_technical_labels(self, text: str) -> str:
        lines: list[str] = []
        for line in text.splitlines():
            cleaned = self._TECHNICAL_LABEL.sub("", line).strip()
            if cleaned != line.strip():
                self._technical_labels_removed += 1
            lines.append(cleaned)
        return "\n".join(lines).strip()

    def _remove_stacked_openers(self, text: str) -> str:
        parts = self._PROTECTED_CODE.split(text)
        if not parts or not parts[0].strip():
            return text
        prose = parts[0]
        match = re.match(
            r"^(?P<prefix>(?:(?:claro|s[ií]|por supuesto|desde luego|perfecto)"
            r"[.!]\s*)+)(?P<body>.+)$",
            prose,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if match is None:
            return text
        openers = re.findall(
            r"(?:claro|s[ií]|por supuesto|desde luego|perfecto)",
            match.group("prefix"),
            flags=re.IGNORECASE,
        )
        if not openers or not match.group("body").strip():
            return text
        self._stacked_openers_removed += len(openers)
        parts[0] = match.group("body").lstrip()
        return "".join(parts)

    def _remove_adjacent_repeated_sentences(self, text: str) -> str:
        parts = self._PROTECTED_CODE.split(text)
        for index in range(0, len(parts), 2):
            parts[index] = self._deduplicate_prose_sentences(parts[index])
        return "".join(parts)

    def _deduplicate_prose_sentences(self, text: str) -> str:
        paragraphs = re.split(r"(\n\s*\n)", text)
        for index in range(0, len(paragraphs), 2):
            tokens = re.split(r"(?<=[.!?])(?=[ \t]+|$)", paragraphs[index])
            if len(tokens) < 2:
                continue
            kept: list[str] = []
            previous_key: str | None = None
            for token in tokens:
                key = re.sub(r"\s+", " ", token).strip().casefold()
                if key and key == previous_key:
                    self._repeated_sentences_removed += 1
                    continue
                kept.append(token)
                if key:
                    previous_key = key
            paragraphs[index] = "".join(kept)
        return "".join(paragraphs)

    def _vary_adjacent_repeated_transitions(self, text: str) -> str:
        parts = self._PROTECTED_CODE.split(text)
        for index in range(0, len(parts), 2):
            parts[index] = self._vary_prose_transitions(parts[index])
        return "".join(parts)

    def _vary_prose_transitions(self, text: str) -> str:
        alternates = {
            "además": "También",
            "también": "Además",
            "por otro lado": "A la vez",
        }
        pattern = re.compile(
            r"(?P<first>\b(?:además|también|por otro lado),(?P<body>[^.!?]*[.!?]\s*))"
            r"(?P<second>además|también|por otro lado),",
            re.IGNORECASE,
        )

        def replace(match: re.Match[str]) -> str:
            first_key = match.group("first").split(",", 1)[0].casefold()
            second_key = match.group("second").casefold()
            if first_key != second_key:
                return match.group(0)
            self._repeated_transitions_varied += 1
            return match.group("first") + alternates[second_key] + ","

        previous = None
        while previous != text:
            previous = text
            text = pattern.sub(replace, text)
        return text

    def _collapse_excessive_blank_lines(self, text: str) -> str:
        parts = self._PROTECTED_CODE.split(text)
        for index in range(0, len(parts), 2):
            prose = parts[index]
            cleaned, count = re.subn(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", prose)
            if count:
                self._excessive_blank_lines_removed += count
            parts[index] = cleaned
        return "".join(parts)

    def _remove_redundant_closing(self, text: str) -> str:
        normalized = text.rstrip()
        for closing in self._REDUNDANT_CLOSINGS:
            if normalized.casefold().endswith(closing.casefold()):
                self._redundant_closings_removed += 1
                return normalized[: -len(closing)].rstrip()
        return text

    def _make_concise(self, text: str) -> str:
        sentences = self._meaningful_sentences(text)
        if not sentences:
            return text
        concise = " ".join(sentences[:2]).strip()
        if concise != text:
            self._concise_responses += 1
        return concise

    @staticmethod
    def _meaningful_sentences(text: str) -> list[str]:
        flattened = re.sub(r"^[-*]\s*", "", text, flags=re.MULTILINE)
        flattened = re.sub(r"\s+", " ", flattened).strip()
        return [
            item.strip()
            for item in re.split(r"(?<=[.!?])\s+", flattened)
            if item.strip()
        ]

    def _asks_for_concise_answer(self, text: str) -> bool:
        normalized = text.casefold()
        return any(trigger in normalized for trigger in self._CONCISE_TRIGGERS)
