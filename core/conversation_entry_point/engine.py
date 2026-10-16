from __future__ import annotations

import re
from datetime import datetime, timezone

from .models import (
    ConversationEntryAction,
    ConversationEntryConfig,
    ConversationEntryKind,
    ConversationEntryRepository,
    ConversationEntryRequest,
    ConversationEntryResult,
    InMemoryConversationEntryRepository,
    readiness_allows_entry,
)


class ConversationEntryPoint:
    """Classifies the first conversational intent without generating a reply."""

    def __init__(
        self,
        *,
        config: ConversationEntryConfig | None = None,
        repository: ConversationEntryRepository | None = None,
    ) -> None:
        self.config = config or ConversationEntryConfig()
        self.repository = repository or InMemoryConversationEntryRepository()

    @property
    def last_entry(self) -> ConversationEntryResult | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def classify(
        self,
        request: ConversationEntryRequest,
        *,
        now: datetime | None = None,
    ) -> ConversationEntryResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("conversation entry timestamp must be timezone-aware")
        result = self._classify(request, timestamp)
        self.repository.add(result)
        return result

    def _classify(
        self,
        request: ConversationEntryRequest,
        timestamp: datetime,
    ) -> ConversationEntryResult:
        if not request.conversation_requested:
            return self._result(
                request,
                timestamp,
                ConversationEntryKind.NOT_APPLICABLE,
                ConversationEntryAction.NONE,
                "",
                False,
                False,
                "conversation_entry_not_requested",
            )
        if not readiness_allows_entry(request.readiness_result):
            return self._result(
                request,
                timestamp,
                ConversationEntryKind.NOT_APPLICABLE,
                ConversationEntryAction.WITHHOLD,
                "",
                False,
                False,
                "runtime_readiness_does_not_allow_conversation_entry",
            )

        normalized = self._normalize(request.text)
        addressed = self._addressed_to_roby(normalized)
        semantic_text = self._remove_assistant_name(normalized)
        if len(semantic_text) < self.config.minimum_text_length:
            return self._result(
                request,
                timestamp,
                (
                    ConversationEntryKind.ATTENTION
                    if addressed
                    else ConversationEntryKind.INCOMPLETE
                ),
                (
                    ConversationEntryAction.ROUTE_TO_ATTENTION
                    if addressed
                    else ConversationEntryAction.REQUEST_COMPLETION
                ),
                normalized,
                addressed,
                True,
                "assistant_attention_requested" if addressed else "message_incomplete",
            )

        kind, action, rationale = self._intent(semantic_text)
        return self._result(
            request,
            timestamp,
            kind,
            action,
            normalized,
            addressed,
            True,
            rationale,
        )

    def _intent(
        self, text: str
    ) -> tuple[ConversationEntryKind, ConversationEntryAction, str]:
        words = set(re.findall(r"[\w]+", text.casefold()))
        greeting_words = {"hola", "buenas", "buen", "buenos", "hey", "ey"}
        farewell_words = {"chau", "adios", "hasta", "nos", "vemos"}
        continuation_words = {"ademas", "tambien", "entonces", "sigamos", "continuemos"}
        request_words = {
            "busca",
            "buscame",
            "decime",
            "hace",
            "haz",
            "mostrame",
            "revisa",
            "revisame",
            "calcula",
            "crea",
            "escribi",
        }
        question_words = {
            "que",
            "como",
            "cuando",
            "donde",
            "cual",
            "quien",
            "por",
            "puede",
            "podes",
        }
        if words & farewell_words:
            return (
                ConversationEntryKind.FAREWELL,
                ConversationEntryAction.ROUTE_TO_FAREWELL,
                "farewell_detected",
            )
        if words and words <= greeting_words:
            return (
                ConversationEntryKind.GREETING,
                ConversationEntryAction.ROUTE_TO_GREETING,
                "greeting_detected",
            )
        if words & request_words:
            return (
                ConversationEntryKind.REQUEST,
                ConversationEntryAction.ROUTE_TO_ACTION,
                "request_detected",
            )
        if "?" in text or words & question_words:
            return (
                ConversationEntryKind.QUESTION,
                ConversationEntryAction.ROUTE_TO_REASONING,
                "question_detected",
            )
        if words & continuation_words:
            return (
                ConversationEntryKind.CONTINUATION,
                ConversationEntryAction.ROUTE_TO_CONTEXT,
                "continuation_detected",
            )
        return (
            ConversationEntryKind.COMMENT,
            ConversationEntryAction.ROUTE_TO_DIALOGUE,
            "comment_detected",
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().split())

    def _addressed_to_roby(self, text: str) -> bool:
        words = set(re.findall(r"[\w]+", text.casefold()))
        return any(name in words for name in self.config.assistant_names)

    def _remove_assistant_name(self, text: str) -> str:
        result = text
        for name in self.config.assistant_names:
            result = re.sub(rf"\b{re.escape(name)}\b", " ", result, flags=re.IGNORECASE)
        return " ".join(result.strip(" ,.!?;:").split())

    @staticmethod
    def _result(
        request: ConversationEntryRequest,
        timestamp: datetime,
        kind: ConversationEntryKind,
        action: ConversationEntryAction,
        normalized_text: str,
        addressed_to_roby: bool,
        conversational: bool,
        rationale: str,
    ) -> ConversationEntryResult:
        return ConversationEntryResult(
            request=request,
            kind=kind,
            action=action,
            normalized_text=normalized_text,
            addressed_to_roby=addressed_to_roby,
            conversational=conversational,
            response_generation_allowed=False,
            provider_call_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )
