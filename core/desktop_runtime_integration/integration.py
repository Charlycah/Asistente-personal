from __future__ import annotations

from datetime import datetime, timezone

from core.operational_response_assembly import (
    OperationalResponseAction,
    OperationalResponseStatus,
)
from core.roby_console_application import (
    ConsoleTurnAction,
    ConsoleTurnStatus,
    ROBYConsoleApplication,
    ROBYConsoleSessionRequest,
)
from core.runtime_readiness_gate import RuntimeReadinessStatus

from .models import (
    DesktopRuntimeAction,
    DesktopRuntimeIntegrationConfig,
    DesktopRuntimeRepository,
    DesktopRuntimeRequest,
    DesktopRuntimeResult,
    DesktopRuntimeStatus,
    InMemoryDesktopRuntimeRepository,
    OperationalDesktopPipeline,
)


class _NullConsoleIO:
    def read(self, prompt: str) -> str | None:
        return None

    def write(self, text: str) -> None:
        return None


class DesktopRuntimeIntegration:
    """Connects desktop input to already-governed conversational boundaries."""

    def __init__(
        self,
        *,
        pipeline: OperationalDesktopPipeline,
        console_application: ROBYConsoleApplication | None = None,
        config: DesktopRuntimeIntegrationConfig | None = None,
        repository: DesktopRuntimeRepository | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.console_application = console_application or ROBYConsoleApplication(
            io=_NullConsoleIO()
        )
        self.config = config or DesktopRuntimeIntegrationConfig()
        self.repository = repository or InMemoryDesktopRuntimeRepository()

    def submit(
        self,
        request: DesktopRuntimeRequest,
        *,
        now: datetime | None = None,
    ) -> DesktopRuntimeResult:
        created_at = now or datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            raise ValueError("desktop runtime timestamp must be timezone-aware")
        if not request.text:
            return self._save(
                DesktopRuntimeResult(
                    request=request,
                    status=DesktopRuntimeStatus.NEEDS_INPUT,
                    action=DesktopRuntimeAction.REQUEST_INPUT,
                    response_text=self.config.incomplete_response,
                    console_turn=None,
                    operational_response=None,
                    provider_call_performed=False,
                    network_access_performed=False,
                    platform_mutation_performed=False,
                    rationale=("desktop_input_incomplete",),
                    created_at=created_at,
                )
            )
        if len(request.text) > self.config.maximum_input_characters:
            return self._save(
                DesktopRuntimeResult(
                    request=request,
                    status=DesktopRuntimeStatus.WITHHELD,
                    action=DesktopRuntimeAction.WITHHOLD,
                    response_text=self.config.withheld_response,
                    console_turn=None,
                    operational_response=None,
                    provider_call_performed=False,
                    network_access_performed=False,
                    platform_mutation_performed=False,
                    rationale=("desktop_input_character_limit_exceeded",),
                    created_at=created_at,
                )
            )
        readiness = request.readiness_result
        if readiness.status is RuntimeReadinessStatus.BLOCKED or readiness.blocked:
            return self._save(
                DesktopRuntimeResult(
                    request=request,
                    status=DesktopRuntimeStatus.BLOCKED,
                    action=DesktopRuntimeAction.REPORT_BLOCKED,
                    response_text=self.config.blocked_response,
                    console_turn=None,
                    operational_response=None,
                    provider_call_performed=False,
                    network_access_performed=False,
                    platform_mutation_performed=False,
                    rationale=("runtime_readiness_blocked_desktop_execution",),
                    created_at=created_at,
                )
            )
        console_request = ROBYConsoleSessionRequest(
            owner=request.owner,
            readiness_result=readiness,
            session_id=request.session_id,
        )
        turn = self.console_application.process_turn(
            console_request,
            request.text,
            sequence=1,
            now=created_at,
        )
        if (
            turn.status is ConsoleTurnStatus.DELIVERED
            and turn.action is ConsoleTurnAction.WRITE_RESPONSE
        ):
            return self._save(
                DesktopRuntimeResult(
                    request=request,
                    status=DesktopRuntimeStatus.DELIVERED,
                    action=DesktopRuntimeAction.PRESENT_RESPONSE,
                    response_text=turn.response_text,
                    console_turn=turn,
                    operational_response=None,
                    provider_call_performed=False,
                    network_access_performed=False,
                    platform_mutation_performed=False,
                    rationale=("m172_greeting_delivered_to_desktop",),
                    created_at=created_at,
                )
            )
        try:
            response = self.pipeline.execute(
                owner=request.owner,
                session_id=request.session_id,
                text=request.text,
            )
        except Exception:
            return self._save(
                DesktopRuntimeResult(
                    request=request,
                    status=DesktopRuntimeStatus.FAILED,
                    action=DesktopRuntimeAction.REPORT_FAILURE,
                    response_text=self.config.failure_response,
                    console_turn=None,
                    operational_response=None,
                    provider_call_performed=False,
                    network_access_performed=False,
                    platform_mutation_performed=False,
                    rationale=("operational_desktop_pipeline_failed",),
                    created_at=created_at,
                )
            )
        return self._from_operational(request, response, created_at)

    def _from_operational(self, request, response, created_at):
        common = dict(
            request=request,
            console_turn=None,
            operational_response=response,
            provider_call_performed=response.provider_call_performed,
            network_access_performed=response.network_access_performed,
            platform_mutation_performed=False,
            created_at=created_at,
        )
        if (
            response.status
            in (OperationalResponseStatus.COMPLETED, OperationalResponseStatus.PARTIAL)
            and response.action
            in (
                OperationalResponseAction.DELIVER_RESPONSE,
                OperationalResponseAction.DELIVER_WITH_LIMITATIONS,
            )
            and response.response_text
        ):
            return self._save(
                DesktopRuntimeResult(
                    status=DesktopRuntimeStatus.DELIVERED,
                    action=DesktopRuntimeAction.PRESENT_RESPONSE,
                    response_text=response.response_text,
                    rationale=("m175_operational_response_delivered_to_desktop",),
                    **common,
                )
            )
        if response.status is OperationalResponseStatus.WITHHELD:
            return self._save(
                DesktopRuntimeResult(
                    status=DesktopRuntimeStatus.WITHHELD,
                    action=DesktopRuntimeAction.WITHHOLD,
                    response_text=self.config.withheld_response,
                    rationale=("m175_operational_response_withheld",),
                    **common,
                )
            )
        return self._save(
            DesktopRuntimeResult(
                status=DesktopRuntimeStatus.FAILED,
                action=DesktopRuntimeAction.REPORT_FAILURE,
                response_text=self.config.failure_response,
                rationale=("m175_operational_response_not_deliverable",),
                **common,
            )
        )

    def _save(self, result: DesktopRuntimeResult) -> DesktopRuntimeResult:
        self.repository.add(result)
        return result
