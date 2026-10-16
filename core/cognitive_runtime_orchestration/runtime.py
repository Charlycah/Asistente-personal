from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from core.llm_provider import LLMRequest
from core.visual_context_integration import IntegratedVisualContext

from .external_evidence import (
    EXTERNAL_EVIDENCE_STAGE,
    CognitiveExternalEvidenceAdmission,
    build_external_evidence_contribution,
)
from .models import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeContributor,
    CognitiveRuntimeOrchestrationResult,
    CognitiveRuntimeStageStatus,
    CognitiveStrategyApplicationEvidence,
    CognitiveStrategyApplicationOutcomeStatus,
    CognitiveStrategyApplicationStatus,
    GovernedCognitiveStrategyApplication,
)


class CognitiveRuntimeOrchestrator:
    """Coordinate cognitive contributors without granting execution authority."""

    def __init__(
        self,
        contributors: tuple[CognitiveRuntimeContributor, ...] = (),
    ) -> None:
        names = tuple(item.name.strip() for item in contributors)
        if any(not name for name in names):
            raise ValueError("cognitive contributors must have names")
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError("cognitive contributor names must be unique")
        self.contributors = tuple(contributors)
        self.last_result: CognitiveRuntimeOrchestrationResult | None = None

    def enrich(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime | None = None,
        external_evidence: tuple[CognitiveExternalEvidenceAdmission, ...] = (),
        integrated_visual_context: IntegratedVisualContext | None = None,
        strategy_application: GovernedCognitiveStrategyApplication | None = None,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        continuity_selection: object | None = None,
        continuity_context_surface: object | None = None,
    ) -> CognitiveRuntimeOrchestrationResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("cognitive orchestration time must be timezone-aware")
        contributions: list[CognitiveRuntimeContribution] = []
        prompt_lines: list[str] = []
        references: list[str] = []
        if external_evidence:
            contribution = build_external_evidence_contribution(external_evidence)
            contributions.append(contribution)
            if contribution.status is CognitiveRuntimeStageStatus.APPLIED:
                prompt_lines.extend(contribution.prompt_lines)
                references.extend(contribution.reference_ids)
        contributors = self._contributors_for_strategy(
            owner=owner,
            session_id=session_id,
            strategy_application=strategy_application,
        )
        visual_context_contribution = None
        if integrated_visual_context is not None:
            visual_contributors = tuple(
                item
                for item in contributors
                if item.name.strip().casefold() == "visual_context"
            )
            if len(visual_contributors) == 1:
                build_visual = getattr(visual_contributors[0], "build", None)
                if callable(build_visual):
                    visual_context_contribution = build_visual(
                        integrated_visual_context,
                        owner=owner,
                        session_id=session_id,
                    )
        for contributor in contributors:
            if contributor.name.strip().casefold() == EXTERNAL_EVIDENCE_STAGE:
                raise ValueError(
                    "external evidence is a reserved cognitive runtime stage"
                )
            try:
                contributor_kwargs = {
                    "owner": owner,
                    "session_id": session_id,
                    "text": text,
                    "request": request,
                    "now": timestamp,
                }
                if contributor.name.strip().casefold() == "reasoning":
                    if (
                        continuity_selection is not None
                        and continuity_context_surface is not None
                    ):
                        contributor_kwargs.update(
                            continuity_selection=continuity_selection,
                            continuity_context_surface=continuity_context_surface,
                        )
                    contributor_kwargs["visual_context_contribution"] = (
                        visual_context_contribution
                    )
                    contributor_kwargs["explicit_document_ids"] = explicit_document_ids
                    contributor_kwargs["explicit_sources"] = explicit_sources
                    contributor_kwargs["explicit_evidence_references"] = (
                        explicit_evidence_references
                    )
                if (
                    contributor.name.strip().casefold() == "visual_context"
                    and visual_context_contribution is not None
                ):
                    contribution = visual_context_contribution
                else:
                    contribution = contributor.contribute(**contributor_kwargs)
            except Exception:
                contribution = CognitiveRuntimeContribution(
                    stage=contributor.name,
                    status=CognitiveRuntimeStageStatus.FAILED,
                    rationale=("contributor_failure_contained",),
                )
            contributions.append(contribution)
            if contribution.status is CognitiveRuntimeStageStatus.APPLIED:
                prompt_lines.extend(contribution.prompt_lines)
                references.extend(contribution.reference_ids)
        enriched = request
        if prompt_lines:
            cognitive_section = "[Contexto cognitivo gobernado]\n" + "\n".join(
                f"- {line}" for line in prompt_lines
            )
            prompt_section = f"\n\n{cognitive_section}"
            system_prompt = cognitive_section
            if request.system_prompt and request.system_prompt.strip():
                system_prompt = (
                    f"{request.system_prompt.strip()}\n\n{cognitive_section}"
                )
            enriched = LLMRequest(
                prompt=f"{request.prompt}{prompt_section}",
                system_prompt=system_prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                metadata={
                    **request.metadata,
                    "cognitive_context": "included",
                    "cognitive_stages": ",".join(
                        item.stage
                        for item in contributions
                        if item.status is CognitiveRuntimeStageStatus.APPLIED
                    ),
                    "cognitive_reference_count": str(len(references)),
                },
                messages=request.messages,
            )
        application_evidence = self._build_strategy_application_evidence(
            owner=owner,
            session_id=session_id,
            strategy_application=strategy_application,
            contributions=tuple(contributions),
        )
        result = CognitiveRuntimeOrchestrationResult(
            owner=owner,
            session_id=session_id,
            request=enriched,
            contributions=tuple(contributions),
            strategy_application_evidence=application_evidence,
            created_at=timestamp,
        )
        self.last_result = result
        return result


    _STRATEGY_CONTROLLED_STAGES = frozenset(
        {"reasoning", "planning", "reflection", "executive"}
    )

    def _contributors_for_strategy(
        self,
        *,
        owner: str,
        session_id: str,
        strategy_application: GovernedCognitiveStrategyApplication | None,
    ) -> tuple[CognitiveRuntimeContributor, ...]:
        if strategy_application is None:
            return self.contributors
        if (
            strategy_application.owner.casefold() != owner.strip().casefold()
            or strategy_application.scope != session_id.strip()
        ):
            raise ValueError(
                "strategy application identity must match runtime identity"
            )
        if (
            strategy_application.status
            is CognitiveStrategyApplicationStatus.BLOCKED
        ):
            return self.contributors

        by_stage = {
            contributor.name.strip().casefold(): contributor
            for contributor in self.contributors
            if contributor.name.strip().casefold()
            in self._STRATEGY_CONTROLLED_STAGES
        }
        ordered = [
            by_stage[stage]
            for stage in strategy_application.requested_stage_sequence
            if stage in by_stage
        ]
        iterator = iter(ordered)
        projected: list[CognitiveRuntimeContributor] = []
        for contributor in self.contributors:
            stage = contributor.name.strip().casefold()
            if stage not in self._STRATEGY_CONTROLLED_STAGES:
                projected.append(contributor)
                continue
            replacement = next(iterator, None)
            if replacement is not None:
                projected.append(replacement)
        return tuple(projected)

    @staticmethod
    def _build_strategy_application_evidence(
        *,
        owner: str,
        session_id: str,
        strategy_application: GovernedCognitiveStrategyApplication | None,
        contributions: tuple[CognitiveRuntimeContribution, ...],
    ) -> CognitiveStrategyApplicationEvidence | None:
        if strategy_application is None:
            return None

        if (
            strategy_application.status
            is CognitiveStrategyApplicationStatus.BLOCKED
        ):
            status = CognitiveStrategyApplicationOutcomeStatus.BLOCKED
            requested: tuple[str, ...] = ()
            applied: tuple[str, ...] = ()
            skipped: tuple[str, ...] = ()
            failed: tuple[str, ...] = ()
            unmet = strategy_application.requested_capabilities
            refs: tuple[str, ...] = ()
            rationale = (
                "strategy_application:source_strategy_blocked",
                "strategy_application:runtime_behavior_preserved",
            )
        else:
            requested = strategy_application.requested_stage_sequence
            contribution_by_stage = {
                item.stage.casefold(): item
                for item in contributions
                if item.stage.casefold() in requested
            }
            unmet = tuple(
                stage for stage in requested if stage not in contribution_by_stage
            )
            applied = tuple(
                stage
                for stage in requested
                if stage in contribution_by_stage
                and contribution_by_stage[stage].status
                is CognitiveRuntimeStageStatus.APPLIED
            )
            skipped = tuple(
                stage
                for stage in requested
                if stage in contribution_by_stage
                and contribution_by_stage[stage].status
                is CognitiveRuntimeStageStatus.SKIPPED
            )
            failed = tuple(
                stage
                for stage in requested
                if stage in contribution_by_stage
                and contribution_by_stage[stage].status
                is CognitiveRuntimeStageStatus.FAILED
            )
            refs = tuple(
                dict.fromkeys(
                    reference
                    for stage in requested
                    if stage in contribution_by_stage
                    for reference in contribution_by_stage[stage].reference_ids
                )
            )
            if not requested:
                status = CognitiveStrategyApplicationOutcomeStatus.NOT_APPLICABLE
            elif (
                not unmet
                and not skipped
                and not failed
                and len(applied) == len(requested)
            ):
                status = CognitiveStrategyApplicationOutcomeStatus.APPLIED
            elif applied:
                status = (
                    CognitiveStrategyApplicationOutcomeStatus.PARTIALLY_APPLIED
                )
            else:
                status = CognitiveStrategyApplicationOutcomeStatus.BLOCKED
            rationale = (
                "strategy_application:bounded_runtime_projection",
                "strategy_application:truthful_stage_outcomes",
                "strategy_application:no_external_execution",
            )

        payload = repr(
            (
                strategy_application.source_fingerprint,
                owner.casefold(),
                session_id,
                status.value,
                requested,
                applied,
                skipped,
                failed,
                unmet,
                refs,
                rationale,
            )
        )
        source_fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return CognitiveStrategyApplicationEvidence(
            strategy_fingerprint=strategy_application.strategy_fingerprint,
            owner=owner,
            scope=session_id,
            status=status,
            requested_stage_sequence=requested,
            applied_stage_sequence=applied,
            skipped_stages=skipped,
            failed_stages=failed,
            unmet_requirements=unmet,
            contribution_reference_ids=refs,
            rationale_codes=rationale,
            source_fingerprint=source_fingerprint,
        )
