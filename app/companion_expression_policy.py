from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CompanionExpressionSnapshot:
    evaluations: int
    personality_adjustments: int
    structural_fusions: int


class CompanionExpressionPolicy:
    """Keeps every visible answer inside ROBY's stable companion identity."""

    _REPLACEMENTS = (
        (r"(?im)^(\s*[-*]\s*)?temp\.?\s*:\s*", r"\1Temperatura: "),
        (r"(?im)^(\s*[-*]\s*)?sens\.?\s*:\s*", r"\1Sensación térmica: "),
        (r"(?im)^(\s*[-*]\s*)?hum\.?\s*:\s*", r"\1Humedad: "),
        (r"\bpuede\s+usted\b", "podes"),
        (r"\busted\b", "vos"),
        (r"\btu\s+puedes\b", "vos podes"),
        (r"\bpara\s+ti\b", "para vos"),
        (r"\ba\s+ti\b", "a vos"),
        (r"\bcontigo\b", "con vos"),
        (r"\btú\b", "vos"),
        (r"\beres\b", "sos"),
        (r"\bpuedes\b", "podes"),
        (r"\bquieres\b", "queres"),
        (r"\bquiere\s+que\b", "queres que"),
        (r"\bte\s+gustaria\b", "te gustaria"),
        (r"\bsi\s+deseas\b", "si queres"),
        (r"\bdebes\b", "tenes que"),
        (r"\bpuedo\s+ayudarte\b", "te puedo ayudar"),
        (r"\btienes\b", "tenes"),
        (r"\bvienes\b", "venis"),
        (r"\bdices\b", "decis"),
        (r"\bprefieres\b", "preferis"),
        (r"\bdime\b", "decime"),
        (r"\bcu[eé]ntame\b", "contame"),
        (r"\bmu[eé]strame\b", "mostrame"),
        (r"\brecu[eé]rdame\b", "acordame"),
        (r"\brecu[eé]rda\b", "acordate"),
        (r"\belige\b", "elegi"),
        (r"\bven\b", "veni"),
        (r"\bhaz\b", "hace"),
        (r"\bpon\b", "pone"),
        (r"\bsal\b", "sali"),
        (r"\bten\b", "tene"),
    )
    _PROTECTED_CODE = re.compile(r"(```.*?```|`[^`\n]+`)", re.DOTALL)
    _MODULE_HEADINGS = re.compile(
        r"^(?:clima|correo|recordatorios|proyectos|objetivos|agenda|memoria)\s*:\s*$",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        self._evaluations = 0
        self._personality_adjustments = 0
        self._structural_fusions = 0

    @property
    def snapshot(self) -> CompanionExpressionSnapshot:
        return CompanionExpressionSnapshot(
            evaluations=self._evaluations,
            personality_adjustments=self._personality_adjustments,
            structural_fusions=self._structural_fusions,
        )

    def apply(self, text: str, *, preserve_greeting: bool = False) -> str:
        self._evaluations += 1
        adjusted = (
            text if preserve_greeting else self._remove_redundant_greeting(text)
        )
        adjusted = self._remove_foreign_openers(adjusted)
        adjusted = self._moderate_redundant_enthusiasm(adjusted)
        adjusted = self._remove_module_headings(adjusted)
        adjusted = self._apply_argentine_voice(adjusted)
        adjusted = self._smooth_structure(adjusted)
        adjusted = self._normalize_weather_units(adjusted)
        return adjusted.strip()

    @staticmethod
    def _remove_redundant_greeting(text: str) -> str:
        stripped = text.strip()
        # Preserve greeting-only answers without forcing every reply to start
        # with Hola.
        if (
            re.match(r"(?is)^¡?hola[!,.\s]+", stripped)
            and "ayudar" in stripped.casefold()
        ):
            return text
        if re.match(r"(?is)^¡?hola[!,.\s]+\S", stripped) and len(stripped.split()) > 3:
            return re.sub(r"(?is)^¡?hola[!,.\s]+", "", stripped, count=1)
        return text

    @staticmethod
    def _remove_foreign_openers(text: str) -> str:
        adjusted = re.sub(
            r"(?is)^\s*vale(?:[!,. :;-]+|$)",
            "",
            text,
            count=1,
        ).strip()
        replacements = (
            (r"\bno problem(?: then)?\b", ""),
            (r"\bokay then\b", ""),
            (r"\bok then\b", ""),
            (r"\ball right\b", ""),
            (r"\balright\b", ""),
        )
        for pattern, replacement in replacements:
            adjusted = re.sub(pattern, replacement, adjusted, flags=re.IGNORECASE)
        adjusted = re.sub(r"\s+([,.!?])", r"\1", adjusted)
        adjusted = re.sub(r"^[,.;:!?\s-]+", "", adjusted)
        adjusted = re.sub(r"[ \t]{2,}", " ", adjusted)
        return adjusted.strip()

    @classmethod
    def _moderate_redundant_enthusiasm(cls, text: str) -> str:
        parts = cls._PROTECTED_CODE.split(text)
        prose = parts[0]
        vos_opening = re.match(
            r"^\s*(?:\u00a1)?vos!\s+(?=\S)",
            prose,
            flags=re.IGNORECASE,
        )
        if vos_opening is not None:
            parts[0] = prose[vos_opening.end():]
            return "".join(parts)
        pattern = (
            r"^\s*\u00a1Excelente!\s+\u00a1Perfecto!"
            r"(?:\s+\u00a1Claro que s\u00ed!)?"
        )
        match = re.match(pattern, prose, flags=re.IGNORECASE)
        if match is None:
            return text

        opening = match.group()
        if re.search(
            r"\u00a1Claro que s\u00ed!",
            opening,
            flags=re.IGNORECASE,
        ):
            replacement = "Claro que s\u00ed."
        else:
            replacement = "Perfecto."

        parts[0] = replacement + prose[match.end():]
        return "".join(parts)

    def _remove_module_headings(self, text: str) -> str:
        lines = []
        for line in text.splitlines():
            if self._MODULE_HEADINGS.match(line.strip()):
                self._structural_fusions += 1
                continue
            lines.append(line)
        return "\n".join(lines)

    def _apply_argentine_voice(self, text: str) -> str:
        parts = self._PROTECTED_CODE.split(text)
        for index in range(0, len(parts), 2):
            parts[index] = self._apply_voice_to_prose(parts[index])
        return "".join(parts)

    def _apply_voice_to_prose(self, text: str) -> str:
        adjusted = text
        for pattern, replacement in self._REPLACEMENTS:
            updated, count = re.subn(
                pattern,
                replacement,
                adjusted,
                flags=re.IGNORECASE,
            )
            self._personality_adjustments += count
            adjusted = updated
        return adjusted

    @staticmethod
    def _normalize_weather_units(text: str) -> str:
        adjusted = re.sub(r"(?<=\d)\s*°C\b", " °C", text)
        adjusted = re.sub(r"(?<=\d)\s*%", "%", adjusted)
        adjusted = re.sub(r"(?<=\d)\s*km/h\b", " km/h", adjusted, flags=re.IGNORECASE)
        return adjusted

    @staticmethod
    def _smooth_structure(text: str) -> str:
        adjusted = re.sub(r"\n\s*[-*]\s+", "\n- ", text)
        adjusted = re.sub(r"(?<!\n)\n-(?=\s)", "\n\n-", adjusted)
        adjusted = re.sub(r"\n{3,}", "\n\n", adjusted)
        return adjusted
