from __future__ import annotations

from dataclasses import dataclass

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)
from core.knowledge_source_policy import KnowledgeSourceKind, KnowledgeSourceNeed


@dataclass(frozen=True)
class KnowledgeRuntimeAssessment:
    query: str
    need: KnowledgeSourceNeed


class OfficialKnowledgeRuntimeGateway:
    """Single official entry point for governed knowledge-source assessment."""

    _CURRENT_MARKERS = (
        "hoy",
        "actual",
        "actualizado",
        "actualizada",
        "último",
        "ultima",
        "última",
        "reciente",
        "noticia",
        "noticias",
        "precio",
        "cotización",
        "clima",
        "internet",
        "web",
    )
    _EXTERNAL_MARKERS = (
        "buscá",
        "busca",
        "consultá internet",
        "consulta internet",
        "fuentes externas",
        "en la web",
    )
    _VERIFICATION_MARKERS = (
        "verificá",
        "verifica",
        "confirmá",
        "confirma",
        "corroborá",
        "corrobora",
        "comprobá",
        "comprueba",
    )
    _LOCAL_MARKERS = (
        "mis documentos",
        "documento local",
        "archivos locales",
        "manual local",
        "biblioteca",
        "mis libros",
        "mis libro",
        "en mis libros",
    )
    _EXCLUSIVE_SOURCE_MARKERS = (
        "únicamente",
        "unicamente",
        "solamente",
        "solo",
        "sólo",
    )
    _EXTERNAL_PROHIBITION_MARKERS = (
        "no uses internet",
        "no use internet",
        "no consultes internet",
        "no consulte internet",
        "no busques en internet",
        "no busque en internet",
        "sin internet",
        "no uses la web",
        "no use la web",
        "sin fuentes externas",
    )
    _INSPECTION_PREFIXES = (
        "evaluá las fuentes para:",
        "evalua las fuentes para:",
        "evaluar fuentes para:",
        "qué fuentes usarías para:",
        "que fuentes usarias para:",
    )
    _STATUS_TRIGGERS = (
        "estado del runtime de conocimiento",
        "estado del conocimiento",
        "cómo funciona tu conocimiento",
        "como funciona tu conocimiento",
    )

    def describe(
        self, request: GovernedConversationPipelineRequest
    ) -> KnowledgeSourceNeed:
        return self.assess(request.text).need

    def assess_evidence_requirement(
        self,
        requirement: DiscriminatingEvidenceRequirement,
        internal_confidence: float,
        local_documents_available: bool,
    ) -> KnowledgeRuntimeAssessment:
        """Assess one structured reasoning evidence requirement without text markers."""
        query = "; ".join(requirement.missing_evidence_descriptions).strip()
        preferred_sources = (
            (KnowledgeSourceKind.LOCAL_DOCUMENTS,)
            if local_documents_available
            else ()
        )
        need = KnowledgeSourceNeed(
            query=query,
            internal_confidence=internal_confidence,
            local_documents_available=local_documents_available,
            preferred_sources=preferred_sources,
        )
        return KnowledgeRuntimeAssessment(query=query, need=need)

    def external_sources_allowed(self, text: str) -> bool:
        """Resolve explicit source-scope restrictions for the current turn."""
        normalized = " ".join(text.casefold().split())
        if any(marker in normalized for marker in self._EXTERNAL_PROHIBITION_MARKERS):
            return False
        local_scope = any(marker in normalized for marker in self._LOCAL_MARKERS)
        exclusive_scope = any(
            marker in normalized for marker in self._EXCLUSIVE_SOURCE_MARKERS
        )
        return not (local_scope and exclusive_scope)

    def assess(self, text: str) -> KnowledgeRuntimeAssessment:
        query = text.strip()
        normalized = query.casefold()
        current = any(marker in normalized for marker in self._CURRENT_MARKERS)
        local = any(marker in normalized for marker in self._LOCAL_MARKERS)
        explicit_external = (
            not local
            and any(marker in normalized for marker in self._EXTERNAL_MARKERS)
        )
        verification = any(
            marker in normalized for marker in self._VERIFICATION_MARKERS
        )
        confidence = 1.0
        preferred_sources: tuple[KnowledgeSourceKind, ...] = ()
        if local:
            confidence = 0.4
            preferred_sources = (KnowledgeSourceKind.LOCAL_DOCUMENTS,)
        elif current:
            confidence = 0.2
            preferred_sources = (
                KnowledgeSourceKind.NEWS,
                KnowledgeSourceKind.WEB,
            )
        elif explicit_external or verification:
            confidence = 0.5
            preferred_sources = (
                KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
                KnowledgeSourceKind.WEB,
            )
        need = KnowledgeSourceNeed(
            query=query,
            internal_confidence=confidence,
            current_information_required=current,
            explicit_external_request=explicit_external,
            verification_required=verification,
            local_documents_available=local,
            preferred_sources=preferred_sources,
        )
        return KnowledgeRuntimeAssessment(query=query, need=need)

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if normalized in self._STATUS_TRIGGERS:
            return GovernedOperationalInterception(
                response_text=(
                    "El runtime oficial de conocimiento está integrado. Evalúa "
                    "confianza interna, actualidad, verificación, documentos locales "
                    "y necesidad de fuentes externas antes de preparar una consulta. "
                    "La ejecución de red continúa gobernada por configuración."
                ),
                rationale="official_knowledge_runtime_status_completed",
            )
        query = self._inspection_query(request.text)
        if query is None:
            return None
        assessment = self.assess(query)
        need = assessment.need
        sources = ", ".join(source.value for source in need.preferred_sources)
        if not sources:
            sources = KnowledgeSourceKind.INTERNAL.value
        flags = []
        if need.current_information_required:
            flags.append("información actual")
        if need.verification_required:
            flags.append("verificación")
        if need.explicit_external_request:
            flags.append("consulta externa explícita")
        if need.local_documents_available:
            flags.append("documentos locales")
        classification = ", ".join(flags) if flags else "conocimiento interno"
        return GovernedOperationalInterception(
            response_text=(
                f"Evaluación de conocimiento para: {assessment.query}\n"
                f"Clasificación: {classification}.\n"
                f"Confianza interna: {need.internal_confidence:.2f}.\n"
                f"Fuentes preferidas: {sources}.\n"
                "Esta evaluación prepara la ruta; no autoriza por sí sola acceso a red."
            ),
            rationale="official_knowledge_source_assessment_completed",
        )

    def _inspection_query(self, text: str) -> str | None:
        normalized = text.strip().casefold()
        for prefix in self._INSPECTION_PREFIXES:
            if normalized.startswith(prefix):
                query = text.strip()[len(prefix) :].strip()
                return query or None
        return None
