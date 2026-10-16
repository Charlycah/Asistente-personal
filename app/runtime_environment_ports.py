from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from application.reminders import ReminderConversationService
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.llm_provider import LLMRequest
from core.local_first_provider_policy import ProviderWorkload, ProviderWorkloadKind
from core.local_provider_runtime_adapter import LocalProviderRuntimeState
from core.personal_knowledge_base import KnowledgeOwner, PersonalKnowledgeBaseManager
from core.provider_health_evaluation import (
    ProviderCapability,
    ProviderHealthObservation,
    ProviderHealthState,
    ProviderKind,
)
from core.runtime_readiness_gate import RuntimeReadinessStatus
from core.task_intelligence import TaskIntelligenceManager

from .actionable_follow_up import ActionableFollowUpService
from .executive_working_memory import ExecutiveWorkingMemory
from .goal_project_review import GoalProjectReviewService
from .household_goals import HouseholdGoalService
from .household_knowledge import HouseholdKnowledgeService
from .household_projects import HouseholdProjectService
from .llm_provider_factory import RuntimeProviderRegistration
from .progress_check_in import ProgressCheckInService


class PersonalKnowledgeConversationInterceptionPort:
    """Passive runtime exposure of the existing M74 Personal Knowledge authority."""

    def __init__(
        self,
        manager: PersonalKnowledgeBaseManager,
        *,
        owner: KnowledgeOwner,
    ) -> None:
        self.manager = manager
        self.owner = owner
        self.service = self

    def intercept(self, request, *, now=None):
        del request, now
        return None


class TaskIntelligenceConversationInterceptionPort:
    """Runtime exposure of existing Task Intelligence without new authority."""

    def __init__(self, manager: TaskIntelligenceManager) -> None:
        self.manager = manager
        self.service = self

    def intercept(self, request, *, now=None):
        del request, now
        return None


@dataclass(frozen=True)
class EnvironmentReadinessRequest:
    owner: str


@dataclass(frozen=True)
class EnvironmentReadinessResult:
    request: EnvironmentReadinessRequest
    status: RuntimeReadinessStatus
    readiness_id: str


class EnvironmentReadinessPort:
    def resolve(self, request: GovernedConversationPipelineRequest):
        readiness_request = EnvironmentReadinessRequest(owner=request.owner)
        readiness_id = sha256(
            f"{request.owner.casefold()}|{request.session_id}|ready".encode()
        ).hexdigest()
        return EnvironmentReadinessResult(
            request=readiness_request,
            status=RuntimeReadinessStatus.READY,
            readiness_id=readiness_id,
        )


class ProviderObservationsPort:
    def __init__(
        self,
        local_provider,
        remote_providers: tuple[RuntimeProviderRegistration, ...] = (),
    ) -> None:
        self.local_provider = local_provider
        self.remote_providers = tuple(remote_providers)

    def observe(self, request: GovernedConversationPipelineRequest):
        del request
        health = self.local_provider.health()
        state_map = {
            LocalProviderRuntimeState.AVAILABLE: ProviderHealthState.AVAILABLE,
            LocalProviderRuntimeState.UNAVAILABLE: ProviderHealthState.UNAVAILABLE,
            LocalProviderRuntimeState.MISCONFIGURED: ProviderHealthState.MISCONFIGURED,
        }
        state = state_map[health.state]
        observations = [
            ProviderHealthObservation(
                provider_name=health.provider_name,
                provider_kind=ProviderKind.LOCAL,
                state=state,
                model_name=health.configured_model,
                endpoint=health.endpoint,
                capabilities=(ProviderCapability.TEXT, ProviderCapability.CODE),
                latency_ms=health.latency_ms,
                configuration_present=state is not ProviderHealthState.MISCONFIGURED,
                service_reachable=state is ProviderHealthState.AVAILABLE,
                detail=health.error_code or "",
            )
        ]
        observations.extend(
            ProviderHealthObservation(
                provider_name=item.provider.name,
                provider_kind=ProviderKind.REMOTE,
                state=ProviderHealthState.AVAILABLE,
                model_name=item.model,
                endpoint=item.endpoint,
                capabilities=(ProviderCapability.TEXT, ProviderCapability.CODE),
                latency_ms=None,
                configuration_present=True,
                service_reachable=True,
                detail="configured_remote_provider",
            )
            for item in self.remote_providers
        )
        return tuple(observations)


class ConversationWorkloadPort:
    def __init__(self, provider_mode: str = "auto") -> None:
        self.provider_mode = provider_mode

    def describe(self, request: GovernedConversationPipelineRequest):
        del request
        remote_required = self.provider_mode in {"gemini", "mistral"}
        detail = (
            f"requested_provider:{self.provider_mode}"
            if self.provider_mode != "auto"
            else "automatic_provider_selection"
        )
        return ProviderWorkload(
            ProviderWorkloadKind.CONVERSATION,
            remote_required=remote_required,
            detail=detail,
        )


class EnvironmentInferenceRequestPort:
    def __init__(self, working_memory: ExecutiveWorkingMemory | None = None) -> None:
        self.working_memory = working_memory

    def build(self, request: GovernedConversationPipelineRequest) -> LLMRequest:
        prompt = request.text
        if self.working_memory is not None:
            context = self.working_memory.prompt_context(
                owner=request.owner,
                session_id=request.session_id,
            )
            if context:
                prompt = f"{context}\n\nMensaje actual: {request.text}"
        normalized = " ".join(request.text.casefold().split())
        normalized = normalized.strip(" \t\r\n.,!?")

        if normalized.startswith("please "):
            normalized = normalized[len("please "):]
        elif normalized.startswith("por favor, "):
            normalized = normalized[len("por favor, "):]
        elif normalized.startswith("por favor "):
            normalized = normalized[len("por favor "):]

        english_instructions = (
            "answer in english",
            "respond in english",
            "reply in english",
            "responde en ingles",
            "responde en ingl\u00e9s",
            "respond\u00e9 en ingl\u00e9s",
            "contestame en ingl\u00e9s",
            "cont?stame en ingl?s",
        )

        for courtesy_suffix in (", please", ", por favor"):
            if normalized.endswith(courtesy_suffix):
                normalized = normalized[:-len(courtesy_suffix)].rstrip()

        explicit_english = any(
            normalized == instruction
            or normalized.startswith(instruction + " ")
            or normalized.startswith(instruction + ",")
            or normalized.startswith(instruction + ":")
            for instruction in english_instructions
        )
        system_prompt = (
            DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
            .system_prompt_for_language("en")
            if explicit_english
            else DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt
        )
        return LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            metadata={"owner": request.owner, "session": request.session_id},
        )


class DailyBriefingConversationInterceptionPort:
    def __init__(self, service) -> None:
        self.service = service

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        normalized = request.text.strip().casefold()
        triggers = (
            "resumen del día",
            "resumen diario",
            "briefing diario",
            "qué tengo hoy",
            "que tengo hoy",
        )
        if not any(trigger in normalized for trigger in triggers):
            return None
        return GovernedOperationalInterception(
            response_text=self.service.generate(now=now),
            rationale="daily_household_briefing_completed",
        )


class HandledResultConversationInterceptionPort:
    rationale = "operational_conversation_completed"

    def __init__(self, service) -> None:
        self.service = service

    def _handle(self, request: GovernedConversationPipelineRequest, *, now):
        return self.service.handle(request.text, now=now)

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        result = self._handle(request, now=now)
        if not result.handled:
            return None
        return GovernedOperationalInterception(
            response_text=result.response_text,
            rationale=self.rationale,
        )


class ReminderConversationInterceptionPort(HandledResultConversationInterceptionPort):
    rationale = "resident_reminder_conversation_completed"

    def __init__(self, service: ReminderConversationService) -> None:
        super().__init__(service)

    def _handle(self, request: GovernedConversationPipelineRequest, *, now):
        return self.service.handle(
            owner=request.owner,
            text=request.text,
            now=now,
        )


class HouseholdKnowledgeConversationInterceptionPort(
    HandledResultConversationInterceptionPort
):
    rationale = "household_knowledge_conversation_completed"

    def __init__(self, service: HouseholdKnowledgeService) -> None:
        super().__init__(service)


class HouseholdProjectConversationInterceptionPort(
    HandledResultConversationInterceptionPort
):
    rationale = "household_project_conversation_completed"

    def __init__(self, service: HouseholdProjectService) -> None:
        super().__init__(service)


class ActionableFollowUpConversationInterceptionPort(
    HandledResultConversationInterceptionPort
):
    rationale = "actionable_follow_up_conversation_completed"

    def __init__(self, service: ActionableFollowUpService) -> None:
        super().__init__(service)


class ProgressCheckInConversationInterceptionPort(
    HandledResultConversationInterceptionPort
):
    rationale = "progress_check_in_conversation_completed"

    def __init__(self, service: ProgressCheckInService) -> None:
        super().__init__(service)


class GoalProjectReviewConversationInterceptionPort(
    HandledResultConversationInterceptionPort
):
    rationale = "goal_project_review_conversation_completed"

    def __init__(self, service: GoalProjectReviewService) -> None:
        super().__init__(service)


class HouseholdGoalConversationInterceptionPort(
    HandledResultConversationInterceptionPort
):
    rationale = "household_goal_conversation_completed"

    def __init__(self, service: HouseholdGoalService) -> None:
        super().__init__(service)
