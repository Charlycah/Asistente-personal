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
        r"^[\s¿¡]*(?:roby[\s,:]+)?(?:por favor[,\s]+)?"
        r"(?:(?:pod[eé]s|puedes|podr[ií]as)\s+)?"
        r"(?:busc[aá](?:me|r|rme)?|mostr[aá](?:me|r|rme)?|mu[eé]strame|"
        r"ense[ñn][aá](?:me|r|rme)|quiero\s+ver|me\s+(?:mostr[aá]s|busc[aá]s)|"
        r"traeme|dame|pasame|ten[eé]s|hay)\s+"
        r"(?:(?:las|los|una|un|unas|unos|alguna|algunas)\s+)?"
        r"(?:fotos?|fotograf[ií]as?|im[aá]gen(?:es)?)"
        r"(?:\s+(?:in[eé]dit[ao]s?|nuev[ao]s?|recientes?))?"
        r"\s+(?:de|del|sobre)\s+"
        r"(?P<subject>.+?)(?:[,\s]+(?:por favor|roby))?[.?!]*$",
        re.IGNORECASE,
    )

    _BARE_VISUAL_REQUEST = re.compile(
        r"^[\s¿¡]*(?:roby[\s,:]+)?(?:mostr[aá]me|mu[eé]strame|pasame|dame|"
        r"quiero\s+ver|busc[aá](?:me)?)\s+(?:las?\s+)?"
        r"(?:fotos?|im[aá]gen(?:es)?)(?:\s+(?:in[eé]dit[ao]s?|nuev[ao]s?))?"
        r"(?:[,\s]+roby)?[\s.!?]*$",
        re.IGNORECASE,
    )

    @classmethod
    def is_bare_visual_request(cls, text: str) -> bool:
        return cls._BARE_VISUAL_REQUEST.fullmatch(text.strip()) is not None

    _EXACT_IMAGE_REQUEST = re.compile(
        r"\b(?:im[aá]gen(?:es)?|fotos?|fotograf[ií]as?)\s+in[eé]dit[ao]s?\b",
        re.IGNORECASE,
    )

    @classmethod
    def requires_original_images(cls, text: str) -> bool:
        return cls._EXACT_IMAGE_REQUEST.search(text) is not None

    _SPACE_VISUAL_TOPICS = frozenset({
        InterestTopic.NASA_MISSIONS,
        InterestTopic.SPACE_EXPLORATION,
        InterestTopic.JAMES_WEBB_SPACE_TELESCOPE,
        InterestTopic.INTERNATIONAL_SPACE_STATION,
    })

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
        is_visual_request = bool(visual_query) or self._is_visual_intent(folded)
        if not is_visual_request:
            topics = topics.difference(self._SPACE_VISUAL_TOPICS)
        visual_order = (
            GovernedSourceQueryOrder.NEWEST_FIRST
            if self._has_explicit_visual_freshness(folded)
            else None
        )
        if not topics or (visual_query and not topics.intersection(self._SPACE_VISUAL_TOPICS)):
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
                    topics=frozenset(),
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
        query_text = visual_query or self._query_text(normalized)
        if is_visual_request:
            visual_subject = self._open_visual_subject(normalized)
            if visual_subject is not None:
                subject_folded = visual_subject.casefold()
                query_folded = query_text.casefold()
                import re
                if re.search(
                    r'\b' + re.escape(query_folded)
                    + r'\s+(?:de|del|sobre)\s+\S',
                    subject_folded,
                ):
                    query_text = visual_subject
        return AppliedConversationalIntelligenceInterpretation(
            text=normalized,
            status=AppliedConversationalIntelligenceStatus.RECOGNIZED,
            request=GovernedConversationalSourceSelectionRequest(
                text=normalized,
                topics=topics,
                query_text=query_text,
                limit=5,
                region=self._region_for(topics),
                order=visual_order,
            ),
            matched_topics=topics,
        )

    @staticmethod
    def _is_visual_intent(text: str) -> bool:
        import re
        import unicodedata

        def normalize(value):
            value = unicodedata.normalize("NFKD", value.casefold())
            return "".join(
                c for c in value
                if not unicodedata.combining(c)
            )

        normalized = normalize(text)
        words = set(re.findall(r"\b\w+\b", normalized))

        visual = {
            "foto", "fotos", "fotografia", "fotografias",
            "imagen", "imagenes", "ilustracion", "ilustraciones",
        }
        actions = {
            "mostrame", "mostrar", "mostra", "muestrame", "ver",
            "quiero", "tenes", "tienes", "busca", "buscar",
            "buscame", "ensenarme", "conseguir",
        }
        explanatory = {
            "explicame", "explicar", "analiza", "analizar",
            "procesa", "procesar", "significa",
        }

        if not words.intersection(visual):
            return False

        if re.search(
            r"\b(?:no|nunca)\s+(?:(?:\w+)\s+){0,3}"
            r"(?:ver|mostrar|mostrame|buscar|fotos|imagenes)\b",
            normalized,
        ):
            return False

        if words.intersection(explanatory):
            return False

        if re.search(r"\bque\s+es\b", normalized):
            return False

        if "noticias" in words:
            return False

        if words.intersection(actions):
            return True

        return len(words) <= 5


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
        import re
        import unicodedata

        def fold(value: str) -> str:
            normalized = unicodedata.normalize(
                "NFKD", value.casefold()
            )
            return "".join(
                character
                for character in normalized
                if not unicodedata.combining(character)
            )

        # Preserve character positions by applying the same
        # normalization to each original character.
        folded = "".join(fold(c) for c in text)

        pattern = re.compile(
            r"\b(?:fotos?|fotografias?|imagenes|imagen|"
            r"ilustraciones|ilustracion)\s+"
            r"(?:de|del)\s+"
            r"(?P<subject>[^.!?;,]+)",
            re.IGNORECASE,
        )

        match = pattern.search(folded)
        if match is None:
            return None

        start, end = match.span("subject")
        subject = text[start:end].strip()

        if not subject or not any(c.isalnum() for c in subject):
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
        if (
            "james webb" in folded
            or "telescopio webb" in folded
            or "webb" in folded
        ):
            return "James Webb"
        if "artemis" in folded:
            return "Artemis"
        if "iss" in folded or "estación espacial" in folded:
            return "International Space Station"
        if "nasa" in folded:
            return "NASA"
        return text
