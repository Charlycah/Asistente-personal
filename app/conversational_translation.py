from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class TranslationRequest:
    source_text: str
    target_language: str
    explain: bool = False

    def prompt(self) -> str:
        mode = (
            "Traducí y después explicá brevemente las decisiones relevantes."
            if self.explain
            else (
                "Respondé únicamente con la traducción, sin introducción "
                "ni comentarios."
            )
        )
        return (
            "Actuá como traductor profesional. "
            f"Idioma de destino: {self.target_language}. "
            "Detectá automáticamente el idioma de origen. Conservá nombres propios, "
            "fechas, números, intención y formato. "
            f"{mode}\n\nTexto a traducir:\n{self.source_text}"
        )


class ConversationalTranslation:
    """Detects explicit translation requests without capturing ordinary dialogue."""

    _TRANSLATE = re.compile(
        r"^(?:roby[,:;.!?\s-]+)?"
        r"(?:traduc(?:i|í|ime|eme)|traduce|traducir)\s+"
        r"(?:esto\s+)?(?:al?|a\s+la|a\s+los|a\s+las)\s+"
        r"(?P<language>[\wáéíóúüñ -]+?)\s*[:,-]\s*(?P<text>.+)$",
        flags=re.IGNORECASE | re.DOTALL,
    )
    _MEANING = re.compile(
        r"^(?:roby[,:;.!?\s-]+)?"
        r"(?:que|qué)\s+significa\s+(?P<text>.+?)\s+"
        r"(?:en|al?)\s+(?P<language>[\wáéíóúüñ -]+)[?!.]*$",
        flags=re.IGNORECASE | re.DOTALL,
    )
    _EXPLAIN_MARKERS = (
        "y explica",
        "y explicá",
        "y explicame",
        "y explícame",
        "traducir y explicar",
        "traduccion explicada",
        "traducción explicada",
    )

    def parse(self, text: str) -> TranslationRequest | None:
        raw = " ".join(text.strip().split()).lstrip("¿¡")
        if not raw:
            return None
        explain = any(marker in raw.casefold() for marker in self._EXPLAIN_MARKERS)
        cleaned = self._remove_explanation_marker(raw)
        match = self._TRANSLATE.match(cleaned) or self._MEANING.match(cleaned)
        if match is None:
            return None
        source_text = match.group("text").strip(" \t\n\r\"'“”")
        language = match.group("language").strip(" \t\n\r\"'“”?.!")
        if not source_text or not language:
            return None
        return TranslationRequest(
            source_text=source_text,
            target_language=self._canonical_language(language),
            explain=explain,
        )

    @classmethod
    def _remove_explanation_marker(cls, text: str) -> str:
        cleaned = text
        for marker in cls._EXPLAIN_MARKERS:
            cleaned = re.sub(
                rf"\s*{re.escape(marker)}\s*",
                " ",
                cleaned,
                flags=re.IGNORECASE,
            )
        return " ".join(cleaned.split())

    @staticmethod
    def _canonical_language(language: str) -> str:
        normalized = unicodedata.normalize("NFKD", language.casefold())
        normalized = "".join(
            char for char in normalized if not unicodedata.combining(char)
        )
        aliases = {
            "ingles": "inglés",
            "english": "inglés",
            "espanol": "español",
            "castellano": "español",
            "spanish": "español",
            "italiano": "italiano",
            "italian": "italiano",
            "frances": "francés",
            "french": "francés",
            "aleman": "alemán",
            "german": "alemán",
            "portugues": "portugués",
            "portuguese": "portugués",
        }
        return aliases.get(normalized.strip(), language.strip())
