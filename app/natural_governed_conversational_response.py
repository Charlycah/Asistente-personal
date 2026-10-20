from __future__ import annotations

from dataclasses import dataclass

from .governed_conversational_query import (
    GovernedConversationalQueryResult,
    GovernedConversationalQueryStatus,
)
from .governed_conversational_source_selection import (
    GovernedConversationalSourceSelection,
    GovernedConversationalSourceSelectionStatus,
)
from .governed_visual_image_admission import (
    admit_governed_visual_images,
)
from .relevance_evaluator import RelevanceRecipient


@dataclass(frozen=True)
class NaturalGovernedConversationalResponseSnapshot:
    schema_version: str
    authority: str
    maximum_titles: int
    preserves_structured_result: bool
    network_enabled: bool
    autonomous_execution_enabled: bool


class NaturalGovernedConversationalResponse:
    """Builds a concise household-facing answer from governed query results."""

    SCHEMA_VERSION = "m345.1"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    MAXIMUM_TITLES = 3

    @property
    def snapshot(self) -> NaturalGovernedConversationalResponseSnapshot:
        return NaturalGovernedConversationalResponseSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            maximum_titles=self.MAXIMUM_TITLES,
            preserves_structured_result=True,
            network_enabled=False,
            autonomous_execution_enabled=False,
        )

    def compose(
        self,
        *,
        query_text: str,
        selection: GovernedConversationalSourceSelection,
        result: GovernedConversationalQueryResult | None,
    ) -> str:
        subject = self._subject(query_text)
        if selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE:
            return (
                f"Entendí que querés saber sobre {subject}, pero todavía no tengo "
                "una fuente gobernada disponible para responderte."
            )
        if result is None:
            return f"No pude completar la consulta sobre {subject}."
        if result.status is GovernedConversationalQueryStatus.FAILED:
            return (
                f"No pude consultar la fuente disponible sobre {subject} en este "
                "momento."
            )
        if result.status is GovernedConversationalQueryStatus.EMPTY:
            admitted = admit_governed_visual_images(
                selection=selection,
                result=result,
            )
            if admitted:
                count = len(admitted)
                noun = "imagen" if count == 1 else "im?genes"
                return f"Encontr? {count} {noun} sobre {subject}."
            return (
                f"Consulté la fuente disponible, pero no encontré novedades válidas "
                f"sobre {subject}."
            )
        return self._successful_answer(subject, result)

    def _successful_answer(
        self,
        subject: str,
        result: GovernedConversationalQueryResult,
    ) -> str:
        titles = tuple(
            dict.fromkeys(item.normalized.title for item in result.items)
        )
        relevance = self._relevance_phrase(result)
        if len(titles) == 1:
            return f"Encontré una novedad sobre {subject}{relevance}: «{titles[0]}»."
        visible = titles[: self.MAXIMUM_TITLES]
        joined = "; ".join(f"«{title}»" for title in visible)
        remaining = len(titles) - len(visible)
        tail = f" También hay {remaining} más." if remaining else ""
        return (
            f"Encontré {len(titles)} novedades sobre {subject}{relevance}. "
            f"Las principales son: {joined}.{tail}"
        )

    @staticmethod
    def _relevance_phrase(result: GovernedConversationalQueryResult) -> str:
        recipients = {
            item.relevance.recipient
            for item in result.items
            if item.relevance.should_share
        }
        if recipients == {RelevanceRecipient.BOTH}:
            return " para vos y Cristina"
        if recipients == {RelevanceRecipient.CARLOS}:
            return " para vos"
        if recipients == {RelevanceRecipient.CRISTINA}:
            return " para Cristina"
        return ""

    @staticmethod
    def _subject(query_text: str) -> str:
        cleaned = " ".join(query_text.split()).strip(" .,:;!?¿¡")
        return cleaned or "el tema que consultaste"
