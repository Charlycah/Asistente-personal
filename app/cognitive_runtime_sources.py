from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from types import SimpleNamespace

from core.adaptive_cognition import (
    CoordinationStatus,
    ExecutivePlanHorizon,
    ExecutivePlanStatus,
    ReflectionImportance,
    ReflectionOutcome,
)
from core.cognitive_planning import CognitivePlanner
from core.cognitive_planning.models import CognitiveNeed
from core.governed_reasoning import GovernedReasoningStatus


def _identifier(kind: str, owner: str, session_id: str, text: str) -> str:
    payload = f"{kind}|{owner.casefold()}|{session_id}|{text.strip()}"
    return sha256(payload.encode("utf-8")).hexdigest()



def _needs(text: str) -> tuple[CognitiveNeed, ...]:
    return CognitivePlanner().assess_cognitive_needs(text)


@dataclass(frozen=True)
class OperationalCognitiveSource:
    """Deterministic, advisory-only source for the official cognitive runtime."""

    def reasoning(self, *, owner: str, session_id: str, text: str, now: datetime):
        del now
        if CognitiveNeed.REASONING not in _needs(text):
            return None
        base = _identifier("reasoning", owner, session_id, text)
        return SimpleNamespace(
            status=GovernedReasoningStatus.COMPLETED,
            result_id=f"reasoning-{base}",
            context=SimpleNamespace(
                context_id=f"context-{base}",
                query=SimpleNamespace(owner=owner),
            ),
            inference_run=SimpleNamespace(run_id=f"inference-{base}"),
            conflict_analysis=SimpleNamespace(analysis_id=f"conflict-{base}"),
            decision=SimpleNamespace(
                decision_id=f"decision-{base}",
                conclusion=(
                    "Descomponer la solicitud, preservar sus restricciones y "
                    "responder sin ejecutar acciones implícitas."
                ),
                confidence_score=0.75,
                limitations=("El análisis se basa únicamente en el texto del turno.",),
                assumptions=(
                    "La solicitud es consultiva salvo instrucción "
                    "operacional explícita.",
                ),
            ),
            explanation=SimpleNamespace(
                answer_id=f"explanation-{base}",
                confidence_label="moderada",
                summary=(
                    "Se aplicó razonamiento gobernado y conservador al turno actual."
                ),
            ),
        )

    def planning(self, *, owner: str, session_id: str, text: str, now: datetime):
        del now
        if CognitiveNeed.PLANNING not in _needs(text):
            return None
        base = _identifier("planning", owner, session_id, text)
        objective = SimpleNamespace(
            objective_id=f"objective-{base}",
            title="Resolver la solicitud de forma verificable",
            success_criteria=("Respuesta clara", "Restricciones preservadas"),
        )
        milestone = SimpleNamespace(
            milestone_id=f"milestone-{base}",
            sequence=1,
            title="Analizar y responder",
        )
        return SimpleNamespace(
            owner=owner,
            plan_id=f"plan-{base}",
            title="Plan cognitivo del turno",
            purpose="Estructurar la respuesta sin ejecutar acciones autónomas.",
            normalized_horizon=ExecutivePlanHorizon.NEAR,
            normalized_status=ExecutivePlanStatus.APPROVED,
            constraints=("No ejecutar herramientas sin autorización.",),
            objectives=(objective,),
            milestones=(milestone,),
            reflection_ids=(),
            mental_model_ids=(),
            knowledge_proposal_ids=(),
        )

    def reflection(self, *, owner: str, session_id: str, text: str, now: datetime):
        del now
        if CognitiveNeed.REFLECTION not in _needs(text):
            return None
        base = _identifier("reflection", owner, session_id, text)
        observation = SimpleNamespace(
            observation_id=f"observation-{base}",
            normalized_importance=ReflectionImportance.MEDIUM,
            description=(
                "Conviene declarar incertidumbre y separar análisis de ejecución."
            ),
        )
        return SimpleNamespace(
            record_id=f"reflection-{base}",
            normalized_outcome=ReflectionOutcome.IMPROVING,
            requires_review=False,
            summary="Revisión consultiva del enfoque antes de responder.",
            observations=(observation,),
            recommendations=("Mantener una respuesta trazable y prudente.",),
            assessment_ids=(),
            episode_ids=(),
            mental_model_ids=(),
        )

    def coordination(self, *, owner: str, session_id: str, text: str, now: datetime):
        del now
        if CognitiveNeed.COORDINATION not in _needs(text):
            return None
        base = _identifier("executive", owner, session_id, text)
        directive = SimpleNamespace(
            directive_id=f"directive-{base}",
            milestone_id=f"milestone-{base}",
            sequence=1,
            title="Coordinar razonamiento, planificación y reflexión",
            normalized_subsystem=SimpleNamespace(value="reasoning"),
            priority=SimpleNamespace(value="high"),
            normalized_status=SimpleNamespace(value="active"),
            dependencies=(),
            constraints=("No ejecutar acciones autónomas.",),
        )
        return SimpleNamespace(
            owner=owner,
            coordination_id=f"coordination-{base}",
            plan_id=f"plan-{base}",
            normalized_status=CoordinationStatus.APPROVED,
            revision=1,
            requires_review=False,
            constraints=("Preservar gobernanza y permisos.",),
            directives=(directive,),
        )


class CognitiveCapabilityMarker:
    """Registry marker; cognitive enrichment remains in the official pipeline."""

    def intercept(self, request, *, now):
        del request, now
        return None
