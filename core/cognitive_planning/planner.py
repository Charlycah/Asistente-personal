from __future__ import annotations

import re

from .models import (
    CognitiveIntent,
    CognitiveNeed,
    CognitivePlan,
    ContextRequirement,
    EvidenceLevel,
    FreshnessRequirement,
    PlannedResponseDecision,
    ToolRequirement,
)


class CognitivePlanner:
    """Build a deterministic pre-response plan without executing it."""

    _QUESTION = re.compile(
        r"\?|\b(?:qué|que|cómo|como|cuál|cual|quién|quien|por qué|por que)\b",
        re.IGNORECASE,
    )
    _CURRENT = re.compile(
        r"\b(?:hoy|ahora|actual(?:es|idad|mente)?|reciente(?:s|mente)?|"
        r"últim[oa]s?|ultim[oa]s?|noticias?|qué pasó|que paso|"
        r"qué está pasando|que esta pasando|esta semana|este mes|ayer|anoche)\b",
        re.IGNORECASE,
    )
    _DYNAMIC = re.compile(
        r"\b(?:presidente|gobierno|elecciones?|ley(?:es)?|precio(?:s)?|"
        r"cotización|cotizacion|dólar|dolar|mercados?|acciones?|bitcoin|"
        r"partido|resultado|openai|nasa|spacex|apple|microsoft|"
        r"lanzamiento|actualización|actualizacion|versión|version)\b",
        re.IGNORECASE,
    )
    _WEATHER = re.compile(
        r"\b(?:clima|tiempo|temperatura|lluvia|llueve|pronóstico|pronostico|"
        r"meteorológic[oa]s?)\b",
        re.IGNORECASE,
    )
    _WEATHER_IRRELEVANT = re.compile(
        r"\b(?:clima|tiempo|temperatura|lluvia|pronóstico|pronostico|"
        r"meteorológic[oa]s?)\b"
        r".{0,32}\b(?:no (?:es|resulta|será|sera) relevante|ya no (?:es|resulta) "
        r"relevante|no importa)\b",
        re.IGNORECASE,
    )
    _CALENDAR = re.compile(
        r"\b(?:agenda|calendario|reunión|reunion|evento|qué tengo|que tengo)\b",
        re.IGNORECASE,
    )
    _MEMORY = re.compile(
        r"\b(?:recordá|recorda|recuerda|recordamos|te acordás|te acordas|"
        r"habíamos|habiamos|dijimos antes|mencionamos antes|acordamos antes|"
        r"conversación anterior|conversacion anterior|\w+ anterior)\b",
        re.IGNORECASE,
    )
    _ACTION = re.compile(
        r"^\s*(?:creá|crea|agendá|agenda|enviá|envia|borrá|borra|"
        r"guardá|guarda|activá|activa|desactivá|desactiva|recordame)\b",
        re.IGNORECASE,
    )
    _FOLLOW_UP = re.compile(
        r"^\s*[¿¡]?\s*(?:y\b|eso\b|esa\b|ese\b|lo anterior\b|por qué\b|por que\b)",
        re.IGNORECASE,
    )
    _COGNITIVE_NEED_PATTERNS = {
        CognitiveNeed.REASONING: re.compile(
            r"\b(?:analiz(?:á|a|ar)|razon(?:á|a|ar)|evalu(?:á|a|ar)|"
            r"compar(?:á|a|ar)|sopes(?:á|a|ar)|pon(?:é|e|er) en la balanza)\b",
            re.IGNORECASE,
        ),
        CognitiveNeed.PLANNING: re.compile(
            r"(?:\b(?:planific(?:á|a|ar)|estructur(?:á|a|ar) un plan|"
            r"traz(?:á|a|ar) un plan)\b|\bsecuencia de pasos\b|"
            r"\borden(?:á|a|ar)\b.{0,80}\b(?:primero|después|despues|al final)\b)",
            re.IGNORECASE,
        ),
        CognitiveNeed.REFLECTION: re.compile(
            r"(?:\b(?:reflexion(?:á|a|ar)|revis(?:á|a|ar) críticamente|"
            r"revis(?:á|a|ar) criticamente|pens(?:á|a|ar) de nuevo)\b|"
            r"\bvolv(?:é|e|er) sobre\b.{0,80}\b(?:puntos? débiles?|"
            r"puntos? debiles?|omisiones?)\b)",
            re.IGNORECASE,
        ),
        CognitiveNeed.COORDINATION: re.compile(
            r"(?:\b(?:coordin(?:á|a|ar)|integr(?:á|a|ar) estas partes)\b|"
            r"\b(?:partes|componentes)\b.{0,80}\b(?:trabaj(?:en|ar) juntas?|"
            r"funcion(?:en|ar) como (?:un )?conjunto)\b)",
            re.IGNORECASE,
        ),
        CognitiveNeed.DECISION: re.compile(
            r"\b(?:decid(?:ir|a|í|i)|decisión|decision|conviene|qué conviene|"
            r"que conviene|eleg(?:í|i|ir)|seleccion(?:á|a|ar)|escog(?:é|e|er)|"
            r"opt(?:á|a|ar))\b",
            re.IGNORECASE,
        ),
    }

    _QUOTED_SPAN_RE = re.compile(
        r'(?:"[^"\n]*"|“[^”\n]*”|«[^»\n]*»|\'[^\'\n]*\')'
    )
    _LOCAL_NEGATION_RE = re.compile(
        r"(?:^|\b)(?:no|sin|ni)\s+$",
        re.IGNORECASE,
    )

    def assess_cognitive_needs(self, text: str) -> tuple[CognitiveNeed, ...]:
        """Return bounded advisory cognitive needs without executing anything."""
        normalized = " ".join(text.strip().split())
        if not normalized:
            return ()
        semantic_text = self._mask_quoted_spans(normalized)
        return tuple(
            need
            for need, pattern in self._COGNITIVE_NEED_PATTERNS.items()
            if self._has_asserted_match(pattern, semantic_text)
        )

    @classmethod
    def _mask_quoted_spans(cls, text: str) -> str:
        return cls._QUOTED_SPAN_RE.sub(
            lambda match: " " * len(match.group(0)),
            text,
        )

    @classmethod
    def _has_asserted_match(cls, pattern: re.Pattern[str], text: str) -> bool:
        for match in pattern.finditer(text):
            prefix = text[max(0, match.start() - 48) : match.start()]
            clause_prefix = re.split(r"[.!?;,:]", prefix)[-1]
            if cls._LOCAL_NEGATION_RE.search(clause_prefix):
                continue
            return True
        return False

    def plan(self, text: str) -> CognitivePlan:
        normalized = " ".join(text.strip().split())
        if not normalized:
            return CognitivePlan(
                intent=CognitiveIntent.CLARIFICATION,
                required_context=(ContextRequirement.CURRENT_TURN,),
                required_tools=(ToolRequirement.NONE,),
                freshness=FreshnessRequirement.NONE,
                minimum_evidence=EvidenceLevel.NONE,
                response_decision=PlannedResponseDecision.RESPOND,
                rationale_codes=("empty_or_incomplete_turn",),
            )

        rationale: list[str] = []
        contexts = [ContextRequirement.CURRENT_TURN]
        tools: list[ToolRequirement] = []

        if self._FOLLOW_UP.search(normalized):
            contexts.append(ContextRequirement.CONVERSATION)
            rationale.append("contextual_follow_up_detected")

        if self._MEMORY.search(normalized):
            contexts.extend(
                (ContextRequirement.CONVERSATION, ContextRequirement.PERSONAL_MEMORY)
            )
            tools.append(ToolRequirement.MEMORY)
            rationale.append("memory_dependency_detected")

        weather_relevant = (
            self._WEATHER.search(normalized)
            and not self._WEATHER_IRRELEVANT.search(normalized)
        )
        if weather_relevant:
            intent = CognitiveIntent.CURRENT_INFORMATION
            tools.append(ToolRequirement.WEATHER)
            rationale.append("weather_information_detected")
            freshness = FreshnessRequirement.CURRENT
            evidence = EvidenceLevel.SINGLE_SOURCE
            decision = PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED
        elif self._CURRENT.search(normalized) or (
            self._QUESTION.search(normalized) and self._DYNAMIC.search(normalized)
        ):
            intent = CognitiveIntent.CURRENT_INFORMATION
            tools.append(ToolRequirement.CURRENT_AFFAIRS)
            rationale.append("current_information_detected")
            freshness = FreshnessRequirement.CURRENT
            evidence = EvidenceLevel.CORROBORATED
            decision = PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED
        elif self._ACTION.search(normalized):
            intent = CognitiveIntent.ACTION
            tools.append(ToolRequirement.CAPABILITY_ROUTER)
            rationale.append("action_request_detected")
            freshness = FreshnessRequirement.NONE
            evidence = EvidenceLevel.INTERNAL
            decision = PlannedResponseDecision.RESPOND
        elif self._CALENDAR.search(normalized):
            intent = CognitiveIntent.INFORMATION
            tools.append(ToolRequirement.CALENDAR)
            rationale.append("calendar_information_detected")
            freshness = FreshnessRequirement.CURRENT
            evidence = EvidenceLevel.SINGLE_SOURCE
            decision = PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED
        elif self._QUESTION.search(normalized):
            intent = CognitiveIntent.INFORMATION
            rationale.append("information_request_detected")
            freshness = FreshnessRequirement.NONE
            evidence = EvidenceLevel.INTERNAL
            decision = PlannedResponseDecision.RESPOND
        else:
            intent = CognitiveIntent.CONVERSATION
            rationale.append("conversational_turn_detected")
            freshness = FreshnessRequirement.NONE
            evidence = EvidenceLevel.NONE
            decision = PlannedResponseDecision.RESPOND

        if not tools:
            tools.append(ToolRequirement.NONE)
        return CognitivePlan(
            intent=intent,
            required_context=self._deduplicate(contexts),
            required_tools=self._deduplicate(tools),
            freshness=freshness,
            minimum_evidence=evidence,
            response_decision=decision,
            rationale_codes=tuple(rationale),
        )

    @staticmethod
    def _deduplicate(values):
        return tuple(dict.fromkeys(values))
