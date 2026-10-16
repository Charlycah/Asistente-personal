from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.living_conversation.continuity import (
    ConversationEpisode,
    ConversationThread,
    LongitudinalConversationContinuity,
)
from core.living_conversation.integration import (
    LivingConversationIntegrationStatus,
    LivingConversationNextMove,
)
from core.living_conversation.interests import (
    IntellectualInterestEvidence,
    IntellectualInterestEvidenceKind,
    SharedIntellectualInterest,
)
from core.living_conversation_runtime_integration import (
    LivingConversationRuntimeProjection,
)
from core.stable_personality import StablePersonalityEngine


class LongitudinalTopicAdmissionStatus(str, Enum):
    ADMITTED = "admitted"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class LongitudinalTopicAdmission:
    status: LongitudinalTopicAdmissionStatus
    topic_key: str | None
    source_reference_ids: tuple[str, ...]
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("topic admission rationale must not be empty")
        if self.status is LongitudinalTopicAdmissionStatus.ADMITTED:
            if self.topic_key is None or not self.topic_key.strip():
                raise ValueError("admitted topic key must not be blank")
            if not self.source_reference_ids:
                raise ValueError("admitted topic must preserve provenance")
        elif self.topic_key is not None or self.source_reference_ids:
            raise ValueError("abstained topic admission must not carry identity")




class LongitudinalTurnObservationStatus(str, Enum):
    RECORDED = "recorded"
    ABSTAINED = "abstained"


@dataclass(frozen=True)
class LongitudinalTurnObservation:
    turn_id: str
    status: LongitudinalTurnObservationStatus
    admission: LongitudinalTopicAdmission
    thread: ConversationThread | None

    def __post_init__(self) -> None:
        if not self.turn_id.strip():
            raise ValueError("longitudinal observation turn id must not be blank")
        if self.status is LongitudinalTurnObservationStatus.RECORDED:
            if self.admission.status is not LongitudinalTopicAdmissionStatus.ADMITTED:
                raise ValueError("recorded observation requires admitted topic")
            if self.thread is None:
                raise ValueError("recorded observation requires conversation thread")
        elif self.thread is not None:
            raise ValueError("abstained observation must not carry conversation thread")


@dataclass(frozen=True)
class ConversationRuntimeSnapshot:
    owner: str
    session_id: str
    expression: str
    consistency_score: float
    next_move: str
    integration_id: str


class OfficialConversationRuntimeGateway:
    """Explicit, advisory source for ROBY's official living conversation path."""

    _ACTIVATION_TRIGGERS = (
        "activá conversación viva",
        "activa conversación viva",
        "adaptá la conversación",
        "adapta la conversación",
        "evaluá el estilo conversacional",
        "evalua el estilo conversacional",
    )
    _STATUS_TRIGGERS = (
        "estado del runtime conversacional",
        "estado de la conversación viva",
        "cómo está tu conversación",
        "como esta tu conversacion",
    )

    def __init__(
        self,
        personality: StablePersonalityEngine | None = None,
        continuity: LongitudinalConversationContinuity | None = None,
    ) -> None:
        self.personality = personality or StablePersonalityEngine()
        self.continuity = continuity or LongitudinalConversationContinuity()
        self._last_snapshot: ConversationRuntimeSnapshot | None = None
        self._longitudinal_observations_by_turn_id: dict[
            str, LongitudinalTurnObservation
        ] = {}

    @property
    def snapshot(self) -> ConversationRuntimeSnapshot | None:
        return self._last_snapshot

    def supply_explicit_longitudinal_topic_declaration(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        topic_key: str,
    ) -> IntellectualInterestEvidence:
        if not owner.strip():
            raise ValueError("explicit topic declaration owner must not be blank")
        if not session_id.strip():
            raise ValueError("explicit topic declaration session id must not be blank")
        if not turn_id.strip():
            raise ValueError("explicit topic declaration turn id must not be blank")
        if not topic_key.strip():
            raise ValueError("explicit topic declaration topic key must not be blank")
        if topic_key != " ".join(topic_key.split()):
            raise ValueError(
                "explicit topic declaration topic key must already be canonical"
            )
        return IntellectualInterestEvidence(
            topic=topic_key,
            kind=IntellectualInterestEvidenceKind.EXPLICIT,
            confidence=1.0,
            source_reference_id=f"conversation:{session_id}/turn:{turn_id}",
            note="explicit_longitudinal_topic_declaration",
        )

    def admit_longitudinal_topic(
        self,
        *,
        evidence: IntellectualInterestEvidence | SharedIntellectualInterest | None,
        topic_key: str | None,
    ) -> LongitudinalTopicAdmission:
        if evidence is None or topic_key is None:
            return LongitudinalTopicAdmission(
                status=LongitudinalTopicAdmissionStatus.ABSTAIN,
                topic_key=None,
                source_reference_ids=(),
                rationale=("explicit_governed_topic_identity_absent",),
            )
        candidate = topic_key.strip()
        if isinstance(evidence, IntellectualInterestEvidence):
            if evidence.kind is not IntellectualInterestEvidenceKind.EXPLICIT:
                return LongitudinalTopicAdmission(
                    status=LongitudinalTopicAdmissionStatus.ABSTAIN,
                    topic_key=None,
                    source_reference_ids=(),
                    rationale=("explicit_governed_topic_identity_absent",),
                )
            sources = (evidence.source_reference_id,)
        else:
            if not evidence.explicit:
                return LongitudinalTopicAdmission(
                    status=LongitudinalTopicAdmissionStatus.ABSTAIN,
                    topic_key=None,
                    source_reference_ids=(),
                    rationale=("explicit_governed_topic_identity_absent",),
                )
            sources = tuple(evidence.source_reference_ids)
        if not candidate:
            return LongitudinalTopicAdmission(
                status=LongitudinalTopicAdmissionStatus.ABSTAIN,
                topic_key=None,
                source_reference_ids=(),
                rationale=("explicit_governed_topic_identity_absent",),
            )
        if candidate != evidence.topic:
            return LongitudinalTopicAdmission(
                status=LongitudinalTopicAdmissionStatus.ABSTAIN,
                topic_key=None,
                source_reference_ids=(),
                rationale=("topic_identity_not_exactly_supported",),
            )
        if (
            not sources
            or len(set(sources)) != len(sources)
            or any(not item.strip() for item in sources)
        ):
            return LongitudinalTopicAdmission(
                status=LongitudinalTopicAdmissionStatus.ABSTAIN,
                topic_key=None,
                source_reference_ids=(),
                rationale=("topic_identity_provenance_insufficient",),
            )
        return LongitudinalTopicAdmission(
            status=LongitudinalTopicAdmissionStatus.ADMITTED,
            topic_key=candidate,
            source_reference_ids=sources,
            rationale=("explicit_governed_topic_identity_admitted",),
        )

    def observe_longitudinal_productive_turn(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        summary: str,
        occurred_at: datetime,
        evidence: SharedIntellectualInterest | None,
        topic_key: str | None,
    ) -> LongitudinalTurnObservation:
        if not turn_id.strip():
            raise ValueError("productive conversation turn id must not be blank")
        existing = self._longitudinal_observations_by_turn_id.get(turn_id)
        if existing is not None:
            return existing
        admission = self.admit_longitudinal_topic(
            evidence=evidence,
            topic_key=topic_key,
        )
        if admission.status is LongitudinalTopicAdmissionStatus.ABSTAIN:
            observation = LongitudinalTurnObservation(
                turn_id=turn_id,
                status=LongitudinalTurnObservationStatus.ABSTAINED,
                admission=admission,
                thread=None,
            )
        else:
            assert admission.topic_key is not None
            turn_reference = f"conversation:{session_id}/turn:{turn_id}"
            sources = tuple(
                dict.fromkeys((*admission.source_reference_ids, turn_reference))
            )
            thread = self.record_productive_episode(
                owner=owner,
                session_id=session_id,
                topic_key=admission.topic_key,
                summary=summary,
                source_reference_ids=sources,
                occurred_at=occurred_at,
            )
            observation = LongitudinalTurnObservation(
                turn_id=turn_id,
                status=LongitudinalTurnObservationStatus.RECORDED,
                admission=admission,
                thread=thread,
            )
        self._longitudinal_observations_by_turn_id[turn_id] = observation
        return observation

    def read_prior_longitudinal_episodes(
        self,
        *,
        owner: str,
        topic_key: str,
    ) -> tuple[ConversationEpisode, ...]:
        if not owner.strip():
            raise ValueError("conversation owner must not be blank")
        if not topic_key.strip():
            raise ValueError("conversation topic key must not be blank")
        thread_id = sha256(f"{owner}|{topic_key}".encode("utf-8")).hexdigest()
        thread = self.continuity.thread_repository.get(thread_id)
        if thread is None:
            return ()
        return thread.episodes

    def record_productive_episode(
        self,
        *,
        owner: str,
        session_id: str,
        topic_key: str,
        summary: str,
        source_reference_ids: tuple[str, ...],
        occurred_at: datetime,
    ) -> ConversationThread:
        if not session_id.strip():
            raise ValueError("conversation session id must not be blank")
        episode = ConversationEpisode(
            owner=owner,
            topic_key=topic_key,
            summary=summary,
            source_reference_ids=source_reference_ids,
            occurred_at=occurred_at,
        )
        return self.continuity.record(episode)

    def resolve(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        now: datetime,
    ):
        if not self._is_activation_request(text):
            return None
        personality = self.personality.evaluate_turn(text, now=now)
        integration_id = sha256(
            f"conversation|{owner.casefold()}|{session_id}|{text.strip()}".encode(
                "utf-8"
            )
        ).hexdigest()
        expression = personality.normalized_expression.value
        next_move = LivingConversationNextMove.EXPLORE
        self._last_snapshot = ConversationRuntimeSnapshot(
            owner=owner,
            session_id=session_id,
            expression=expression,
            consistency_score=personality.consistency_score,
            next_move=next_move.value,
            integration_id=integration_id,
        )
        prompt = (
            "Mantener una expresión "
            f"{expression}, continuidad estable y una pregunta breve solo si "
            "aporta valor; preservar siempre el turno del usuario."
        )
        return LivingConversationRuntimeProjection(
            owner=owner,
            status=LivingConversationIntegrationStatus.READY,
            eligible_for_activation=True,
            preserve_user_floor=True,
            rhythm="steady",
            selected_prompt=prompt,
            next_move=next_move,
            integration_id=integration_id,
            stage_reference_ids=(personality.snapshot_id,),
            source_kind="official_conversation_runtime",
        )

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        normalized = request.text.strip().casefold()
        if not any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return None
        snapshot = self.snapshot
        if snapshot is None:
            text = (
                "Runtime conversacional oficial: disponible, sin una evaluación "
                "registrada. La adaptación se activa únicamente por solicitud "
                "explícita."
            )
        else:
            text = "\n".join(
                (
                    "Estado del runtime conversacional oficial:",
                    f"- Expresión: {snapshot.expression}",
                    f"- Consistencia: {snapshot.consistency_score:.2f}",
                    f"- Próximo movimiento: {snapshot.next_move}",
                    "- Activación: únicamente por solicitud explícita.",
                )
            )
        return GovernedOperationalInterception(
            response_text=text,
            rationale="official_conversation_runtime_status_completed",
        )

    def _is_activation_request(self, text: str) -> bool:
        normalized = text.strip().casefold()
        return any(trigger in normalized for trigger in self._ACTIVATION_TRIGGERS)
