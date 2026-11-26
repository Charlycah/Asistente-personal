from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from .governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from .governed_conversational_source_selection import (
    GovernedConversationalSourceSelection,
    GovernedConversationalSourceSelectionRequest,
)
from .governed_information_sources import InformationRegion
from .governed_source_query import GovernedSourceQueryOrder
from .personal_interest_center import InterestTopic


class AppliedConversationalIntelligenceStatus(StrEnum):
    RECOGNIZED = "recognized"
    NOT_RECOGNIZED = "not_recognized"


@dataclass(frozen=True)
class AppliedConversationalIntelligenceInterpretation:
    text: str
    status: AppliedConversationalIntelligenceStatus
    request: GovernedConversationalSourceSelectionRequest | None
    matched_topics: frozenset[InterestTopic]


@dataclass(frozen=True)
class AppliedConversationalIntelligenceResult:
    interpretation: AppliedConversationalIntelligenceInterpretation
    selection: GovernedConversationalSourceSelection | None
    conversational_result: object | None
    natural_answer_text: str | None = None

    @property
    def answer_text(self) -> str | None:
        if self.natural_answer_text is not None:
            return self.natural_answer_text
        result = self.conversational_result
        if result is None:
            return None
        return getattr(result, "answer_text", None)


@dataclass(frozen=True)
class AppliedConversationalIntelligenceSnapshot:
    schema_version: str
    authority: str
    explicit_requests_only: bool
    uses_governed_source_selection: bool
    automatic_fetch_enabled: bool
    autonomous_initiatives_enabled: bool


class AppliedConversationalIntelligence:
    """Turns explicit everyday language into the existing governed query flow."""

    SCHEMA_VERSION = "m345.0"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"

    _VISUAL_SEARCH_SUBJECT = re.compile(
        r"^[\s¿¡]*(?:roby[\s,:]+)?(?:pod[eé]s\s+|puedes\s+)?"
        r"(?:busc[aá](?:me|r|rme)?|mostr[aá](?:me|r|rme)?|mu[eé]strame|"
        r"ense[ñn][aá]me|quiero\s+ver|me\s+mostr[aá]s)\s+"
        r"(?:(?:las|los|una|un|unas|unos|algunas)\s+)?"
        r"(?:fotos?|fotograf[ií]as?|im[aá]gen(?:es)?)\s+de\s+"
        r"(?P<subject>.+)$",
        re.IGNORECASE,
    )

    _TOPIC_TERMS = (
        (
            InterestTopic.EVIDENCE_BASED_NUTRITION,
            (
                "nutrición basada en evidencia",
                "nutricion basada en evidencia",
                "guías alimentarias",
                "guias alimentarias",
            ),
        ),
        (
            InterestTopic.HEALTHY_RECIPES,
            ("recetas saludables", "receta saludable", "comidas saludables"),
        ),
        (
            InterestTopic.MEDITERRANEAN_CUISINE,
            ("dieta mediterránea", "dieta mediterranea", "cocina mediterránea"),
        ),
        (
            InterestTopic.ARGENTINE_CUISINE,
            ("cocina argentina saludable", "comida argentina saludable"),
        ),
        (
            InterestTopic.HEALTHY_EATING,
            (
                "alimentación saludable",
                "alimentacion saludable",
                "comer saludable",
                "comida sana",
            ),
        ),
        (
            InterestTopic.HARD_SCIENCE_FICTION,
            ("ciencia ficción dura", "ciencia ficcion dura", "hard sci-fi"),
        ),
        (
            InterestTopic.DOCUMENTARIES,
            ("documentales", "documental"),
        ),
        (
            InterestTopic.SCIENCE_FICTION,
            ("ciencia ficción", "ciencia ficcion", "sci-fi"),
        ),
        (
            InterestTopic.RELEASES,
            ("estrenos", "estreno", "nuevos lanzamientos"),
        ),
        (
            InterestTopic.SERIES,
            ("series", "serie", "temporadas", "temporada"),
        ),
        (
            InterestTopic.CINEMA,
            ("películas", "peliculas", "película", "pelicula", "cine"),
        ),
        (
            InterestTopic.FREE_ACTIVITIES,
            ("actividades gratuitas", "eventos gratis", "planes gratis"),
        ),
        (
            InterestTopic.MUSEUMS,
            ("museos", "museo"),
        ),
        (
            InterestTopic.THEATRE,
            ("teatro", "obras teatrales", "obra teatral"),
        ),
        (
            InterestTopic.MUSIC,
            ("música", "musica", "conciertos", "concierto"),
        ),
        (
            InterestTopic.CULTURE_CABA,
            (
                "cultura caba",
                "cultura en buenos aires",
                "agenda cultural",
                "actividades culturales",
                "eventos culturales",
                "qué hacer en buenos aires",
                "que hacer en buenos aires",
            ),
        ),
        (
            InterestTopic.JAMES_WEBB_SPACE_TELESCOPE,
            ("james webb", "telescopio webb", "webb"),
        ),
        (
            InterestTopic.INTERNATIONAL_SPACE_STATION,
            ("estación espacial", "estacion espacial", "iss"),
        ),
        (
            InterestTopic.NASA_MISSIONS,
            ("nasa", "artemis", "misión espacial", "mision espacial"),
        ),
        (
            InterestTopic.SPACE_EXPLORATION,
            ("exploración espacial", "exploracion espacial"),
        ),
    )
    _EXPLICIT_QUERY_TERMS = (
        "buscá",
        "busca",
        "buscar",
        "novedades",
        "noticias",
        "qué hay",
        "que hay",
        "contame",
        "informame",
        "agenda cultural",
        "actividades culturales",
        "eventos culturales",
        "qué hacer",
        "que hacer",
        "planes para",
        "estrenos",
        "estreno",
        "qué películas",
        "que peliculas",
        "qué series",
        "que series",
        "recomendame",
        "qué comer",
        "que comer",
        "recetas saludables",
        "alimentación saludable",
        "alimentacion saludable",
        "guías alimentarias",
        "guias alimentarias",
    )

    @property
    def snapshot(self) -> AppliedConversationalIntelligenceSnapshot:
        return AppliedConversationalIntelligenceSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            explicit_requests_only=True,
            uses_governed_source_selection=True,
            automatic_fetch_enabled=False,
            autonomous_initiatives_enabled=False,
        )

    def interpret(
        self, text: str
    ) -> AppliedConversationalIntelligenceInterpretation:
        normalized = " ".join(text.split())
        if not normalized:
            raise ValueError("applied conversational text cannot be empty")
        folded = normalized.casefold()
        topics = frozenset(
            topic
            for topic, terms in self._TOPIC_TERMS
            if any(term in folded for term in terms)
        )
        is_explicit = any(term in folded for term in self._EXPLICIT_QUERY_TERMS)
        visual_search = self._VISUAL_SEARCH_SUBJECT.match(normalized)
        visual_query = (
            visual_search["subject"].rstrip(".,;:!?¡¿").strip()
            if visual_search
            else ""
        )
        if visual_query.casefold() in {"hubble", "telescopio hubble"}:
            topics = topics | {InterestTopic.SPACE_EXPLORATION}
            visual_query = "Hubble"
        elif visual_query.casefold() == "las nuevas misiones de la nasa":
            visual_query = "new NASA missions"
        visual_nouns = (
            "foto", "fotograf\u00eda", "fotografia",
            "imagen", "im\u00e1genes", "imagenes",
        )
        visual_verbs = (
            "mostrame", "mostrar", "mu\u00e9strame", "muestrame",
            "ver ", "verme ", "ens\u00e9\u00f1ame", "ens\u00e9\u00f1ame",
        )
        is_visual_request = (
            any(term in folded for term in visual_nouns)
            and any(term in folded for term in visual_verbs)
        )
        visual_order = (
            GovernedSourceQueryOrder.NEWEST_FIRST
            if self._has_explicit_visual_freshness(folded)
            else None
        )
        if not topics:
            visual_subject = (
                visual_query
                or (self._open_visual_subject(normalized) if is_visual_request else None)
            )
            if visual_subject is None:
                return AppliedConversationalIntelligenceInterpretation(
                    text=normalized,
                    status=AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED,
                    request=None,
                    matched_topics=topics,
                )
            return AppliedConversationalIntelligenceInterpretation(
                text=normalized,
                status=AppliedConversationalIntelligenceStatus.RECOGNIZED,
                request=GovernedConversationalSourceSelectionRequest(
                    text=normalized,
                    topics=topics,
                    query_text=visual_subject,
                    limit=5,
                    region=InformationRegion.GLOBAL,
                    order=visual_order,
                    mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
                ),
                matched_topics=topics,
            )
        if not (is_explicit or is_visual_request):
            return AppliedConversationalIntelligenceInterpretation(
                text=normalized,
                status=AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED,
                request=None,
                matched_topics=topics,
            )
        return AppliedConversationalIntelligenceInterpretation(
            text=normalized,
            status=AppliedConversationalIntelligenceStatus.RECOGNIZED,
            request=GovernedConversationalSourceSelectionRequest(
                text=normalized,
                topics=topics,
                query_text=visual_query or self._query_text(normalized),
                limit=5,
                region=self._region_for(topics),
                order=visual_order,
            ),
            matched_topics=topics,
        )

    @staticmethod
    def _has_explicit_visual_freshness(folded: str) -> bool:
        visual_terms = ("fotos", "foto", "imágenes", "imagenes", "imagen")
        return any(
            f"las últimas {visual_term} de " in folded
            or f"las ultimas {visual_term} de " in folded
            or f"las {visual_term} más recientes de " in folded
            or f"las {visual_term} mas recientes de " in folded
            for visual_term in visual_terms
        )

    @staticmethod
    def _open_visual_subject(text: str) -> str | None:
        folded = text.casefold()
        visual_terms = ("fotos", "foto", "imágenes", "imagenes", "imagen")
        markers = tuple(
            marker
            for visual_term in visual_terms
            for marker in (
                f"mostrame {visual_term} de ",
                f"mostrame las últimas {visual_term} de ",
                f"mostrame las ultimas {visual_term} de ",
                f"mostrame las {visual_term} más recientes de ",
                f"mostrame las {visual_term} mas recientes de ",
            )
        )
        marker_end = None
        for marker in markers:
            marker_start = folded.find(marker)
            if marker_start >= 0:
                marker_end = marker_start + len(marker)
                break
        if marker_end is None:
            return None
        subject = text[marker_end:].strip().rstrip(".,;:!?¡¿").strip()
        if not subject or not any(character.isalnum() for character in subject):
            return None
        return subject

    @staticmethod
    def _region_for(topics: frozenset[InterestTopic]) -> InformationRegion:
        cultural_topics = {
            InterestTopic.CULTURE_CABA,
            InterestTopic.MUSIC,
            InterestTopic.THEATRE,
            InterestTopic.MUSEUMS,
            InterestTopic.FREE_ACTIVITIES,
        }
        if topics.intersection(cultural_topics):
            return InformationRegion.CABA
        healthy_topics = {
            InterestTopic.HEALTHY_EATING,
            InterestTopic.EVIDENCE_BASED_NUTRITION,
            InterestTopic.HEALTHY_RECIPES,
            InterestTopic.MEDITERRANEAN_CUISINE,
            InterestTopic.ARGENTINE_CUISINE,
        }
        if topics.intersection(healthy_topics):
            return InformationRegion.ARGENTINA
        return InformationRegion.GLOBAL

    @staticmethod
    def _query_text(text: str) -> str:
        folded = text.casefold()
        if "receta" in folded or "comidas saludables" in folded:
            return "recetas saludables"
        if "mediterr" in folded:
            return "alimentación mediterránea saludable"
        if any(
            term in folded
            for term in ("nutric", "guías alimentarias", "guias alimentarias")
        ):
            return "nutrición basada en evidencia"
        if any(
            term in folded
            for term in (
                "alimentación saludable",
                "alimentacion saludable",
                "comer saludable",
                "comida sana",
            )
        ):
            return "alimentación saludable"
        if "museo" in folded:
            return "museos"
        if "teatro" in folded or "obra teatral" in folded:
            return "teatro"
        if any(term in folded for term in ("música", "musica", "concierto")):
            return "música"
        if any(term in folded for term in ("gratis", "gratuita", "gratuito")):
            return "actividades gratuitas"
        if "ciencia ficción dura" in folded or "ciencia ficcion dura" in folded:
            return "ciencia ficción dura"
        if "documental" in folded:
            return "documentales"
        if "ciencia ficción" in folded or "ciencia ficcion" in folded:
            return "ciencia ficción"
        if "serie" in folded or "temporada" in folded:
            return "series"
        if "película" in folded or "pelicula" in folded or "cine" in folded:
            return "películas"
        if "estreno" in folded or "lanzamiento" in folded:
            return "estrenos audiovisuales"
        if any(
            term in folded
            for term in (
                "agenda cultural",
                "actividades culturales",
                "eventos culturales",
                "qué hacer en buenos aires",
                "que hacer en buenos aires",
            )
        ):
            return "agenda cultural"
        if "james webb" in folded or "telescopio webb" in folded:
            visual_terms = (
                "foto", "fotograf\u00eda", "fotografia",
                "imagen", "im\u00e1genes", "imagenes",
            )
            if any(term in folded for term in visual_terms):
                return text
            return "James Webb"
        if "artemis" in folded:
            return "Artemis"
        if "iss" in folded or "estación espacial" in folded:
            return "International Space Station"
        if "nasa" in folded:
            return "NASA"
        return text
