from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable

from .governed_conversational_query import GovernedConversationalQueryResult
from .governed_conversational_source_selection import (
    GovernedConversationalSourceSelection,
    GovernedConversationalSourceSelectionRequest,
)
from .governed_information_sources import InformationRegion
from .personal_interest_center import InterestTopic


class PersonalOnDemandBulletinStatus(StrEnum):
    RECOGNIZED = "recognized"
    NOT_RECOGNIZED = "not_recognized"
    COMPLETED = "completed"
    EMPTY = "empty"


@dataclass(frozen=True)
class PersonalOnDemandBulletinSnapshot:
    schema_version: str
    authority: str
    under_demand_only: bool
    automatic_execution_enabled: bool
    autonomous_initiatives_enabled: bool
    uses_canonical_governed_flow: bool
    sections: tuple[str, ...]


@dataclass(frozen=True)
class PersonalOnDemandBulletinSection:
    name: str
    selection: GovernedConversationalSourceSelection
    result: GovernedConversationalQueryResult | None


@dataclass(frozen=True)
class PersonalOnDemandBulletinResult:
    text: str
    status: PersonalOnDemandBulletinStatus
    sections: tuple[PersonalOnDemandBulletinSection, ...]
    answer_text: str | None


class PersonalOnDemandBulletin:
    """Builds a household bulletin only after an explicit conversational request."""

    SCHEMA_VERSION = "m345.5"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    _REQUEST_TERMS = (
        "boletín personal",
        "boletin personal",
        "boletín para nosotros",
        "boletin para nosotros",
        "qué hay interesante para nosotros",
        "que hay interesante para nosotros",
        "resumen personal de hoy",
        "nuestro boletín",
        "nuestro boletin",
    )
    _SECTIONS = (
        (
            "Espacio",
            frozenset({InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}),
            "James Webb",
            InformationRegion.GLOBAL,
        ),
        (
            "Cultura en CABA",
            frozenset({InterestTopic.CULTURE_CABA}),
            "agenda cultural",
            InformationRegion.CABA,
        ),
        (
            "Audiovisual",
            frozenset({InterestTopic.RELEASES}),
            "estrenos audiovisuales",
            InformationRegion.GLOBAL,
        ),
        (
            "Alimentación saludable",
            frozenset({InterestTopic.HEALTHY_EATING}),
            "alimentación saludable",
            InformationRegion.ARGENTINA,
        ),
    )

    @property
    def snapshot(self) -> PersonalOnDemandBulletinSnapshot:
        return PersonalOnDemandBulletinSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            under_demand_only=True,
            automatic_execution_enabled=False,
            autonomous_initiatives_enabled=False,
            uses_canonical_governed_flow=True,
            sections=tuple(section[0] for section in self._SECTIONS),
        )

    def recognizes(self, text: str) -> bool:
        normalized = " ".join(text.split())
        if not normalized:
            raise ValueError("personal bulletin text cannot be empty")
        folded = normalized.casefold()
        return any(term in folded for term in self._REQUEST_TERMS)

    def execute(
        self,
        text: str,
        *,
        execute_request: Callable[
            [GovernedConversationalSourceSelectionRequest],
            tuple[
                GovernedConversationalSourceSelection,
                GovernedConversationalQueryResult | None,
            ],
        ],
    ) -> PersonalOnDemandBulletinResult:
        normalized = " ".join(text.split())
        if not self.recognizes(normalized):
            return PersonalOnDemandBulletinResult(
                text=normalized,
                status=PersonalOnDemandBulletinStatus.NOT_RECOGNIZED,
                sections=(),
                answer_text=None,
            )

        sections = tuple(
            self._execute_section(
                name=name,
                topics=topics,
                query_text=query_text,
                region=region,
                original_text=normalized,
                execute_request=execute_request,
            )
            for name, topics, query_text, region in self._SECTIONS
        )
        answer = self._compose_answer(sections)
        status = (
            PersonalOnDemandBulletinStatus.COMPLETED
            if any(section.result and section.result.items for section in sections)
            else PersonalOnDemandBulletinStatus.EMPTY
        )
        return PersonalOnDemandBulletinResult(
            text=normalized,
            status=status,
            sections=sections,
            answer_text=answer,
        )

    @staticmethod
    def _execute_section(
        *,
        name: str,
        topics: frozenset[InterestTopic],
        query_text: str,
        region: InformationRegion,
        original_text: str,
        execute_request: Callable,
    ) -> PersonalOnDemandBulletinSection:
        request = GovernedConversationalSourceSelectionRequest(
            text=original_text,
            topics=topics,
            query_text=query_text,
            limit=3,
            region=region,
        )
        selection, result = execute_request(request)
        return PersonalOnDemandBulletinSection(
            name=name,
            selection=selection,
            result=result,
        )

    @staticmethod
    def _compose_answer(
        sections: tuple[PersonalOnDemandBulletinSection, ...],
    ) -> str:
        lines = ["Este es el boletín personal para vos y Cristina:"]
        for section in sections:
            result = section.result
            if result is None or not result.items:
                continue
            titles = tuple(
                dict.fromkeys(item.normalized.title for item in result.items)
            )
            visible = "; ".join(f"«{title}»" for title in titles[:2])
            lines.append(f"{section.name}: {visible}.")
        if len(lines) == 1:
            return (
                "Entendí el pedido del boletín personal, pero las fuentes gobernadas "
                "habilitadas no devolvieron información válida en este momento."
            )
        return "\n".join(lines)
