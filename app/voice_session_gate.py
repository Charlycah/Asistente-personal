from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class VoiceGateDecision:
    accepted: bool
    command: str = ""
    addressed: bool = False
    reason: str = ""


class VoiceSessionGate:
    """Wake-word gate for continuous listening.

    Audio may keep flowing for local recognition, but only explicitly addressed
    speech (or a short follow-up inside the active window) reaches ROBY.
    """

    def __init__(
        self,
        *,
        wake_aliases: tuple[str, ...],
        active_window_seconds: float = 30.0,
        min_words: int = 2,
        require_wake_word: bool = True,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        normalized_aliases = (
            alias.strip().casefold()
            for alias in wake_aliases
            if alias.strip()
        )
        aliases = tuple(dict.fromkeys(normalized_aliases))
        if not aliases:
            aliases = ("roby",)
        self._wake_aliases = aliases
        self._wake_pattern = "|".join(re.escape(alias) for alias in aliases)
        self._active_window_seconds = max(0.0, active_window_seconds)
        self._min_words = max(1, min_words)
        self._require_wake_word = require_wake_word
        self._clock = clock
        self._active_until = 0.0

    @property
    def active(self) -> bool:
        return self._clock() <= self._active_until

    def close(self) -> None:
        self._active_until = 0.0

    def renew(self) -> None:
        self._active_until = self._clock() + self._active_window_seconds

    def evaluate(self, transcript: str) -> VoiceGateDecision:
        heard = transcript.strip()
        if not heard:
            return VoiceGateDecision(False, reason="empty")

        folded = heard.casefold()
        wake_match = re.search(rf"\b(?:{self._wake_pattern})\b", folded)
        addressed = wake_match is not None

        if addressed:
            matches = list(
                re.finditer(rf"\b(?:{self._wake_pattern})\b", folded)
            )
            first = matches[0]
            last = matches[-1]
            prefix = heard[: first.start()].strip(" ,:;.!?-\t\r\n")
            suffix = heard[last.end() :].strip(" ,:;.!?-\t\r\n")
            command = suffix or prefix
            trailing_wake_only = (
                not suffix and self._word_count(prefix) < self._min_words
            )
            command = re.sub(
                rf"(?is)\b(?:{self._wake_pattern})\b[,:;.!?\s-]*",
                "",
                command,
            ).strip()
            self.renew()
            if not command or trailing_wake_only:
                return VoiceGateDecision(
                    False,
                    addressed=True,
                    reason="wake_only",
                )
            return VoiceGateDecision(True, command, True, "addressed")

        if not self._require_wake_word:
            if self._word_count(heard) < self._min_words:
                return VoiceGateDecision(False, reason="too_short")
            if self._looks_like_ambient_fragment(heard):
                return VoiceGateDecision(False, reason="ambient_fragment")
            return VoiceGateDecision(True, heard, False, "continuous")

        if not self.active:
            return VoiceGateDecision(False, reason="not_addressed")
        if (
            self._word_count(heard) < self._min_words
            and self._normalized_follow_up(heard) not in {
                "pronostico",
                "manana",
                "temperatura",
            }
        ):
            return VoiceGateDecision(False, reason="too_short")

        self.renew()
        return VoiceGateDecision(True, heard, False, "follow_up")


    @classmethod
    def _looks_like_ambient_fragment(cls, text: str) -> bool:
        """Reject short, low-information fragments commonly produced by TV audio.

        This is deliberately conservative: explicit wake-word speech is never
        filtered, and recognizable greetings, questions, commands or supported
        domains continue to pass through continuous listening.
        """
        normalized = cls._normalized_follow_up(text)
        words = re.findall(r"\b[a-z0-9]+\b", normalized)
        if not words or len(words) > 8:
            return False

        meaningful = {
            "hola", "buenas", "gracias", "roby", "correo", "correos",
            "mail", "gmail", "clima", "tiempo", "temperatura", "pronostico",
            "noticia", "noticias", "actualidad", "politica", "gobierno",
            "boca", "river", "racing", "futbol", "partido", "juega",
            "cuando", "como", "donde", "quien", "cual", "cuanto",
            "dame", "decime", "mostrame", "busca", "contame", "recordame",
            "apagate", "reiniciate", "escucha", "lee",
        }
        if any(word in meaningful for word in words):
            return False

        fillers = {
            "eh", "este", "esto", "esa", "ese", "una", "uno", "el", "la",
            "los", "las", "en", "de", "del", "y", "o", "pero", "bueno",
            "bien", "fue", "fuimos", "tenia", "fijese",
        }
        filler_count = sum(word in fillers for word in words)
        starts_as_fragment = words[0] in {
            "y", "o", "pero", "es", "era", "una", "uno", "este", "esto",
            "bien",
        }
        return starts_as_fragment and filler_count >= max(2, len(words) // 2)

    @staticmethod
    def _normalized_follow_up(text: str) -> str:
        decomposed = unicodedata.normalize("NFKD", text.casefold())
        return "".join(
            char for char in decomposed if not unicodedata.combining(char)
        ).strip()

    @staticmethod
    def _word_count(text: str) -> int:
        return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))
