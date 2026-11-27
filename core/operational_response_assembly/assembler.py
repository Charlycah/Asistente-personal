from __future__ import annotations

from datetime import datetime, timezone

from core.gui06_diagnostic_probe import capture_diagnostic_stage
from core.governed_provider_execution_adapter import LocalProviderExecutionStatus
from core.knowledge_retrieval_execution import KnowledgeStepExecutionStatus

from .models import (
    InMemoryOperationalResponseRepository,
    OperationalEvidence,
    OperationalResponse,
    OperationalResponseAction,
    OperationalResponseAssemblyConfig,
    OperationalResponseAssemblyRequest,
    OperationalResponseRepository,
    OperationalResponseStatus,
)


class OperationalResponseAssembler:
    """Assembles already-governed execution outputs without new side effects."""

    def __init__(
        self,
        *,
        config: OperationalResponseAssemblyConfig | None = None,
        repository: OperationalResponseRepository | None = None,
    ) -> None:
        self.config = config or OperationalResponseAssemblyConfig()
        self.repository = repository or InMemoryOperationalResponseRepository()

    def assemble(
        self,
        request: OperationalResponseAssemblyRequest,
        *,
        now: datetime | None = None,
    ) -> OperationalResponse:
        created_at = now or datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            raise ValueError("operational response timestamp must be timezone-aware")
        provider = request.provider_execution
        retrieval = request.retrieval_execution
        common = dict(
            request=request,
            provider_execution_id=provider.execution_id if provider else "",
            retrieval_execution_id=retrieval.execution_id if retrieval else "",
            provider_call_performed=bool(provider and provider.provider_call_performed),
            retrieval_performed=bool(retrieval and retrieval.retrieval_performed),
            network_access_performed=bool(
                (provider and provider.network_access_allowed)
                or (retrieval and retrieval.network_access_performed)
            ),
            platform_mutation_performed=False,
            created_at=created_at,
        )
        if not request.assembly_requested:
            return self._save(
                OperationalResponse(
                    status=OperationalResponseStatus.NOT_APPLICABLE,
                    action=OperationalResponseAction.NONE,
                    response_text="",
                    evidence=(),
                    limitations=(),
                    rationale=("response_assembly_not_requested",),
                    **common,
                )
            )
        if not self.config.assembly_enabled:
            return self._save(
                OperationalResponse(
                    status=OperationalResponseStatus.WITHHELD,
                    action=OperationalResponseAction.WITHHOLD,
                    response_text="",
                    evidence=(),
                    limitations=(),
                    rationale=("response_assembly_disabled",),
                    **common,
                )
            )
        evidence, evidence_limitations = self._evidence(retrieval)
        if provider is None:
            status = (
                OperationalResponseStatus.WITHHELD
                if self.config.require_provider_response
                else OperationalResponseStatus.FAILED
            )
            return self._save(
                OperationalResponse(
                    status=status,
                    action=OperationalResponseAction.WITHHOLD
                    if status is OperationalResponseStatus.WITHHELD
                    else OperationalResponseAction.REPORT_FAILURE,
                    response_text="",
                    evidence=evidence,
                    limitations=evidence_limitations,
                    rationale=("accepted_provider_response_required",),
                    **common,
                )
            )
        if (
            provider.status is not LocalProviderExecutionStatus.COMPLETED
            or provider.response is None
            or not provider.response.accepted
        ):
            return self._save(
                OperationalResponse(
                    status=OperationalResponseStatus.FAILED,
                    action=OperationalResponseAction.REPORT_FAILURE,
                    response_text="",
                    evidence=evidence,
                    limitations=evidence_limitations,
                    rationale=("provider_execution_not_deliverable",),
                    **common,
                )
            )
        text = provider.response.text.strip()
        if not text:
            return self._save(
                OperationalResponse(
                    status=OperationalResponseStatus.FAILED,
                    action=OperationalResponseAction.REPORT_FAILURE,
                    response_text="",
                    evidence=evidence,
                    limitations=evidence_limitations,
                    rationale=("provider_response_empty",),
                    **common,
                )
            )
        if len(text) > self.config.maximum_response_characters:
            return self._save(
                OperationalResponse(
                    status=OperationalResponseStatus.WITHHELD,
                    action=OperationalResponseAction.WITHHOLD,
                    response_text="",
                    evidence=evidence,
                    limitations=evidence_limitations
                    + ("response_character_limit_exceeded",),
                    rationale=("provider_response_exceeds_assembly_limit",),
                    **common,
                )
            )
        limitations = list(evidence_limitations)
        if retrieval is not None and not retrieval.retrieval_performed:
            limitations.append("retrieval_produced_no_evidence")
        partial = bool(limitations)
        return self._save(
            OperationalResponse(
                status=OperationalResponseStatus.PARTIAL
                if partial
                else OperationalResponseStatus.COMPLETED,
                action=OperationalResponseAction.DELIVER_WITH_LIMITATIONS
                if partial
                else OperationalResponseAction.DELIVER_RESPONSE,
                response_text=text,
                evidence=evidence,
                limitations=tuple(limitations),
                rationale=("governed_execution_outputs_assembled",),
                **common,
            )
        )

    def _evidence(self, retrieval):
        if retrieval is None:
            return (), ()
        items = []
        limitations = []
        total = 0
        for step in retrieval.steps:
            if (
                step.status is not KnowledgeStepExecutionStatus.SUCCEEDED
                or step.artifact is None
            ):
                if step.status is KnowledgeStepExecutionStatus.FAILED:
                    limitations.append("retrieval_step_failed")
                continue
            if len(items) >= self.config.maximum_evidence_items:
                limitations.append("evidence_item_limit_reached")
                break
            artifact = step.artifact
            if total + len(artifact.content) > self.config.maximum_evidence_characters:
                limitations.append("evidence_character_limit_reached")
                break
            items.append(
                OperationalEvidence(
                    source=artifact.source.value,
                    query=artifact.query,
                    content=artifact.content,
                    references=artifact.references,
                )
            )
            total += len(artifact.content)
        return tuple(items), tuple(dict.fromkeys(limitations))

    def _save(self, response: OperationalResponse) -> OperationalResponse:
        capture_diagnostic_stage("P4a", text=response.response_text)
        self.repository.add(response)
        return response
