from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone

import pytest

from app.unified_cognitive_coordination import (
    UnifiedCognitiveCoordinator,
    project_strategy_application,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeOrchestrator,
    CognitiveStrategyApplicationOutcomeStatus,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_provider import LLMRequest

NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


@dataclass
class Contributor:
    name: str
    line: str = "ok"
    fail: bool = False
    calls: int = 0

    def contribute(self, **kwargs):
        self.calls += 1
        if self.fail:
            raise RuntimeError("private")
        if not self.line:
            return CognitiveRuntimeContribution(
                stage=self.name,
                status="skipped",
                rationale=("source_unavailable",),
            )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status="applied",
            prompt_lines=(f"{self.name}:{self.line}",),
            reference_ids=(f"ref:{self.name}",),
            rationale=("source_applied",),
        )


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="strategy-application",
        text=text,
    )


def _strategy(text: str):
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    result = coordinator.synthesize_strategy_advisory(_request(text))
    assert result is not None
    return result


def _llm() -> LLMRequest:
    return LLMRequest(prompt="resolver")


def test_strategy_changes_only_bounded_cognitive_order_and_preserves_lineage():
    strategy = _strategy(
        "Reflexioná sobre lo anterior, analizá las opciones y planificá cómo seguir."
    )
    application = project_strategy_application(strategy)
    runtime = CognitiveRuntimeOrchestrator(
        (
            Contributor("continuity"),
            Contributor("planning"),
            Contributor("reasoning"),
            Contributor("reflection"),
            Contributor("reliability"),
        )
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )

    assert tuple(item.stage for item in result.contributions) == (
        "continuity",
        "reasoning",
        "planning",
        "reflection",
        "reliability",
    )
    evidence = result.strategy_application_evidence
    assert evidence is not None
    assert evidence.strategy_fingerprint == strategy.source_fingerprint
    assert evidence.status is CognitiveStrategyApplicationOutcomeStatus.APPLIED
    assert evidence.requested_stage_sequence == (
        "reasoning",
        "planning",
        "reflection",
    )
    assert evidence.applied_stage_sequence == (
        "reasoning",
        "planning",
        "reflection",
    )


def test_no_strategy_preserves_historical_runtime_behavior():
    runtime = CognitiveRuntimeOrchestrator(
        (Contributor("planning"), Contributor("reasoning"))
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="resolver",
        request=_llm(),
        now=NOW,
    )
    assert tuple(item.stage for item in result.contributions) == (
        "planning",
        "reasoning",
    )
    assert result.strategy_application_evidence is None


def test_unrequested_cognitive_stage_is_not_activated():
    strategy = _strategy("Analizá las opciones y decidí cuál conviene.")
    application = project_strategy_application(strategy)
    reflection = Contributor("reflection")
    runtime = CognitiveRuntimeOrchestrator(
        (Contributor("reasoning"), reflection, Contributor("executive"))
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    assert reflection.calls == 0
    assert "reflection" not in result.activated_stages
    assert "executive" not in result.activated_stages


def test_missing_required_runtime_stage_is_truthfully_partial():
    strategy = _strategy(
        "Analizá las opciones, planificá los pasos y después reflexioná "
        "sobre el resultado."
    )
    application = project_strategy_application(strategy)
    runtime = CognitiveRuntimeOrchestrator(
        (Contributor("reasoning"), Contributor("reflection"))
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    evidence = result.strategy_application_evidence
    assert evidence is not None
    assert evidence.status is (
        CognitiveStrategyApplicationOutcomeStatus.PARTIALLY_APPLIED
    )
    assert evidence.unmet_requirements == ("planning",)
    assert evidence.applied_stage_sequence == ("reasoning", "reflection")


def test_contributor_failure_is_contained_and_visible_as_partial():
    strategy = _strategy(
        "Analizá las opciones y después reflexioná sobre la respuesta."
    )
    application = project_strategy_application(strategy)
    runtime = CognitiveRuntimeOrchestrator(
        (Contributor("reasoning", fail=True), Contributor("reflection"))
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    evidence = result.strategy_application_evidence
    assert evidence is not None
    assert evidence.status is (
        CognitiveStrategyApplicationOutcomeStatus.PARTIALLY_APPLIED
    )
    assert evidence.failed_stages == ("reasoning",)
    assert evidence.applied_stage_sequence == ("reflection",)


def test_evidence_requirements_and_decision_are_not_runtime_contributors():
    strategy = _strategy(
        "Recordá lo acordado, mirá el clima, analizá las opciones "
        "y decidí cuál conviene."
    )
    application = project_strategy_application(strategy)
    assert application.evidence_requirements == ("memory", "weather")
    assert application.decision_required is True
    assert application.requested_stage_sequence == ("reasoning",)

    runtime = CognitiveRuntimeOrchestrator((Contributor("reasoning"),))
    result = runtime.enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    stages = tuple(item.stage for item in result.contributions)
    assert "memory" not in stages
    assert "weather" not in stages
    assert "decision" not in stages


def test_non_strategy_contributors_preserve_relative_order():
    strategy = _strategy("Reflexioná, analizá las opciones y planificá cómo seguir.")
    application = project_strategy_application(strategy)
    runtime = CognitiveRuntimeOrchestrator(
        (
            Contributor("continuity"),
            Contributor("planning"),
            Contributor("safety"),
            Contributor("reflection"),
            Contributor("reasoning"),
            Contributor("reliability"),
        )
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    stages = tuple(item.stage for item in result.contributions)
    assert (
        stages.index("continuity")
        < stages.index("safety")
        < stages.index("reliability")
    )


def test_owner_or_scope_mismatch_fails_closed():
    strategy = _strategy("Analizá las opciones y planificá cómo seguir.")
    application = project_strategy_application(strategy)
    runtime = CognitiveRuntimeOrchestrator(
        (Contributor("reasoning"), Contributor("planning"))
    )

    with pytest.raises(ValueError, match="identity"):
        runtime.enrich(
            owner="Cristina",
            session_id="strategy-application",
            text="resolver",
            request=_llm(),
            now=NOW,
            strategy_application=application,
        )


def test_application_evidence_is_read_only_non_learning_non_execution():
    strategy = _strategy("Analizá las opciones y planificá cómo seguir.")
    application = project_strategy_application(strategy)
    result = CognitiveRuntimeOrchestrator(
        (Contributor("reasoning"), Contributor("planning"))
    ).enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    evidence = result.strategy_application_evidence
    assert evidence is not None
    assert evidence.read_only is True
    assert evidence.persists is False
    assert evidence.creates_memory is False
    assert evidence.creates_learning is False
    assert evidence.executes_actions is False
    assert evidence.grants_authority is False


def test_blocked_strategy_preserves_historical_runtime_and_reports_blocked():
    request = _request("Analizá las opciones y decidí cuál conviene.")
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    strategy = coordinator.synthesize_strategy_advisory(
        request,
        available_capabilities=("reasoning",),
    )
    assert strategy is not None
    application = project_strategy_application(strategy)
    planning = Contributor("planning")
    reasoning = Contributor("reasoning")
    runtime = CognitiveRuntimeOrchestrator((planning, reasoning))
    result = runtime.enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    assert tuple(item.stage for item in result.contributions) == (
        "planning",
        "reasoning",
    )
    assert planning.calls == 1
    assert reasoning.calls == 1
    evidence = result.strategy_application_evidence
    assert evidence is not None
    assert evidence.status is CognitiveStrategyApplicationOutcomeStatus.BLOCKED


def test_requested_stage_that_skips_cannot_be_promoted_to_applied():
    strategy = _strategy(
        "Analizá las opciones y después reflexioná sobre la respuesta."
    )
    application = project_strategy_application(strategy)
    reasoning = Contributor("reasoning", line="")
    reflection = Contributor("reflection")
    result = CognitiveRuntimeOrchestrator((reasoning, reflection)).enrich(
        owner="Carlos",
        session_id="strategy-application",
        text="resolver",
        request=_llm(),
        now=NOW,
        strategy_application=application,
    )
    evidence = result.strategy_application_evidence
    assert evidence is not None
    assert evidence.status is (
        CognitiveStrategyApplicationOutcomeStatus.PARTIALLY_APPLIED
    )
    assert evidence.skipped_stages == ("reasoning",)
    assert "reasoning" not in evidence.applied_stage_sequence


def test_tampered_application_contract_is_rejected():

    strategy = _strategy("Analizá las opciones y planificá cómo seguir.")
    application = project_strategy_application(strategy)
    with pytest.raises(ValueError, match="fingerprint is inconsistent"):
        replace(application, requested_stage_sequence=("planning", "reasoning"))
