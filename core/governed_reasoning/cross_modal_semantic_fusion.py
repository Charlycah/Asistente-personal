from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)


class CrossModalSemanticRelation(StrEnum):
    CORROBORATING = "corroborating"
    CONFLICTING = "conflicting"
    COMPLEMENTARY = "complementary"
    UNRESOLVED = "unresolved"
    REVIEW = "review"


@dataclass(frozen=True)
class CrossModalSemanticFusionAssessment:
    assessment_id: str
    proposition_id: str
    relation: CrossModalSemanticRelation | str
    reference_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    establishes_truth: bool = False
    truth_certified: bool = False
    proves_causality: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    persists_results: bool = False
    executes_actions: bool = False

    def __post_init__(self) -> None:
        proposition_id = self.proposition_id.strip()
        relation = CrossModalSemanticRelation(self.relation)
        refs = tuple(dict.fromkeys(self.reference_ids))
        rationale = tuple(self.rationale_codes)
        if not proposition_id:
            raise ValueError("cross-modal proposition id must not be blank")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("cross-modal assessment requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("cross-modal fusion must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                self.establishes_truth,
                self.truth_certified,
                self.proves_causality,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.persists_results,
                self.executes_actions,
            )
        ):
            raise ValueError("cross-modal assessment violates governed limits")
        object.__setattr__(self, "proposition_id", proposition_id)
        object.__setattr__(self, "relation", relation)
        object.__setattr__(self, "reference_ids", refs)
        object.__setattr__(self, "rationale_codes", rationale)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "cross_modal_semantic_fusion_assessment",
            "proposition_id": self.proposition_id,
            "relation": self.relation.value,
            "reference_ids": list(self.reference_ids),
            "rationale_codes": list(self.rationale_codes),
            "canonical_authority": self.canonical_authority,
            "read_only": self.read_only,
            "establishes_truth": self.establishes_truth,
            "truth_certified": self.truth_certified,
            "proves_causality": self.proves_causality,
            "modifies_world_model": self.modifies_world_model,
            "modifies_memory": self.modifies_memory,
            "modifies_learning": self.modifies_learning,
            "persists_results": self.persists_results,
            "executes_actions": self.executes_actions,
        }


class GovernedCrossModalSemanticFusionEvaluator:
    """Relates admitted audio and visual evidence without certifying truth."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def evaluate(
        self,
        *,
        proposition_id: str,
        audio: CognitiveRuntimeContribution | None,
        visual: CognitiveRuntimeContribution | None,
    ) -> CrossModalSemanticFusionAssessment:
        proposition = proposition_id.strip()
        if not proposition:
            raise ValueError("cross-modal proposition id must not be blank")

        relation, rationale = self._relate(proposition, audio, visual)
        refs = self._reference_ids(audio, visual)
        fingerprint = sha256(
            "|".join((proposition, relation.value, *refs, *rationale)).encode()
        ).hexdigest()
        return CrossModalSemanticFusionAssessment(
            assessment_id=f"cross-modal-{fingerprint[:16]}",
            proposition_id=proposition,
            relation=relation,
            reference_ids=refs,
            rationale_codes=rationale,
        )

    def _relate(
        self,
        proposition: str,
        audio: CognitiveRuntimeContribution | None,
        visual: CognitiveRuntimeContribution | None,
    ) -> tuple[CrossModalSemanticRelation, tuple[str, ...]]:
        if not self._usable(audio) or not self._usable(visual):
            return (
                CrossModalSemanticRelation.UNRESOLVED,
                ("cross_modal:requires_two_admitted_modalities",),
            )
        assert audio is not None
        assert visual is not None
        if not self._lineage_compatible(audio, visual):
            return (
                CrossModalSemanticRelation.REVIEW,
                ("cross_modal:lineage_requires_review",),
            )

        audio_text = self._normalize(" ".join(audio.prompt_lines))
        visual_text = self._normalize(" ".join(visual.prompt_lines))
        proposition_tokens = self._tokens(proposition)

        if self._explicit_conflict(proposition_tokens, audio_text, visual_text):
            return (
                CrossModalSemanticRelation.CONFLICTING,
                ("cross_modal:modalities_support_incompatible_states",),
            )
        if self._corroborating(proposition_tokens, audio_text, visual_text):
            return (
                CrossModalSemanticRelation.CORROBORATING,
                ("cross_modal:modalities_support_same_event_hypothesis",),
            )
        if self._complementary(proposition_tokens, audio_text, visual_text):
            return (
                CrossModalSemanticRelation.COMPLEMENTARY,
                ("cross_modal:modalities_add_compatible_event_context",),
            )
        return (
            CrossModalSemanticRelation.UNRESOLVED,
            ("cross_modal:semantic_relation_not_established",),
        )

    @staticmethod
    def _usable(contribution: CognitiveRuntimeContribution | None) -> bool:
        return (
            contribution is not None
            and contribution.status is CognitiveRuntimeStageStatus.APPLIED
            and bool(contribution.prompt_lines)
        )

    @staticmethod
    def _lineage_compatible(
        audio: CognitiveRuntimeContribution,
        visual: CognitiveRuntimeContribution,
    ) -> bool:
        def session_markers(refs: tuple[str, ...]) -> set[str]:
            markers = set()
            for ref in refs:
                lowered = ref.casefold()
                if "session-" in lowered:
                    markers.add(lowered.split("session-", 1)[1].split("-", 1)[0])
            return markers

        audio_sessions = session_markers(audio.reference_ids)
        visual_sessions = session_markers(visual.reference_ids)
        return not (
            audio_sessions
            and visual_sessions
            and audio_sessions.isdisjoint(visual_sessions)
        )

    @staticmethod
    def _reference_ids(
        audio: CognitiveRuntimeContribution | None,
        visual: CognitiveRuntimeContribution | None,
    ) -> tuple[str, ...]:
        refs = []
        for contribution in (audio, visual):
            if contribution is not None:
                refs.extend(contribution.reference_ids)
        return tuple(dict.fromkeys(refs))

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value.casefold())
        return "".join(char for char in decomposed if not unicodedata.combining(char))

    @classmethod
    def _tokens(cls, proposition: str) -> set[str]:
        normalized = cls._normalize(proposition.replace("_", " "))
        return {token for token in normalized.split() if len(token) > 2}

    @staticmethod
    def _explicit_conflict(
        proposition_tokens: set[str],
        audio_text: str,
        visual_text: str,
    ) -> bool:
        running = {"running", "funcionando", "encendida", "encendido"}
        stopped = {"apagado", "apagada", "detenida", "detenido"}
        audio_running = any(token in audio_text for token in running)
        visual_stopped = any(token in visual_text for token in stopped)
        visual_running = any(token in visual_text for token in running)
        audio_stopped = any(token in audio_text for token in stopped)
        relevant = bool(
            proposition_tokens.intersection({"machine", "maquina", "running"})
        )
        return relevant and (
            (audio_running and visual_stopped)
            or (visual_running and audio_stopped)
        )

    @staticmethod
    def _corroborating(
        proposition_tokens: set[str],
        audio_text: str,
        visual_text: str,
    ) -> bool:
        alarm_audio = "alarma" in audio_text
        alarm_visual = (
            "luz roja" in visual_text
            or "luz-roja" in visual_text
            or "alarm" in visual_text
        )
        alarm_proposition = bool(
            proposition_tokens.intersection({"alarm", "alarma", "equipment"})
        )
        return alarm_proposition and alarm_audio and alarm_visual

    @staticmethod
    def _complementary(
        proposition_tokens: set[str],
        audio_text: str,
        visual_text: str,
    ) -> bool:
        alarm_proposition = bool(
            proposition_tokens.intersection({"alarm", "alarma"})
        )
        audio_alarm = "alarma" in audio_text
        visual_context = any(
            token in visual_text
            for token in ("panel", "persona", "workspace", "equipo")
        )
        return alarm_proposition and audio_alarm and visual_context
