from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeOrchestrator,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import ConversationMessage, LLMRequest

NOW = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


@dataclass
class Contributor:
    name: str
    line: str = ""
    reference: str = ""
    fail: bool = False
    calls: int = 0

    def contribute(self, **kwargs):
        self.calls += 1
        if self.fail:
            raise RuntimeError("private detail")
        if not self.line:
            return CognitiveRuntimeContribution(
                stage=self.name,
                status="skipped",
                rationale=("not_applicable",),
            )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status="applied",
            prompt_lines=(self.line,),
            reference_ids=((self.reference,) if self.reference else ()),
            rationale=("context_selected",),
        )


def request():
    return LLMRequest(
        prompt="Hola",
        system_prompt="Sos ROBY",
        model="local",
        max_tokens=50,
        temperature=0.2,
        metadata={"original": "yes"},
    )


def test_empty_orchestration_preserves_exact_request():
    original = request()
    result = CognitiveRuntimeOrchestrator().enrich(
        owner="Carlos", session_id="main", text="Hola", request=original, now=NOW
    )
    assert result.request is original
    assert result.contributions == ()


def test_contributors_run_in_declared_order():
    first = Contributor("memory", "Dato recordado")
    second = Contributor("reasoning", "Conclusión gobernada")
    result = CognitiveRuntimeOrchestrator((first, second)).enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    assert tuple(item.stage for item in result.contributions) == ("memory", "reasoning")
    assert result.request.prompt.index("Dato recordado") < result.request.prompt.index(
        "Conclusión gobernada"
    )


def test_only_applied_contributions_modify_prompt():
    skipped = Contributor("presence")
    applied = Contributor("reasoning", "Usar evidencia disponible")
    result = CognitiveRuntimeOrchestrator((skipped, applied)).enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    assert "presence" not in result.request.prompt
    assert "Usar evidencia disponible" in result.request.prompt
    assert result.activated_stages == ("reasoning",)


def test_request_fields_and_metadata_are_preserved():
    result = CognitiveRuntimeOrchestrator((Contributor("reasoning", "Línea"),)).enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    assert result.request.system_prompt is not None
    assert result.request.system_prompt.startswith("Sos ROBY\n\n")
    assert "[Contexto cognitivo gobernado]" in result.request.system_prompt
    assert "- Línea" in result.request.system_prompt
    assert result.request.model == "local"
    assert result.request.max_tokens == 50
    assert result.request.temperature == 0.2
    assert result.request.metadata["original"] == "yes"
    assert result.request.metadata["cognitive_context"] == "included"


def test_contributor_failure_is_contained_without_private_message():
    contributor = Contributor("reasoning", fail=True)
    result = CognitiveRuntimeOrchestrator((contributor,)).enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    item = result.contributions[0]
    assert item.status is CognitiveRuntimeStageStatus.FAILED
    assert item.rationale == ("contributor_failure_contained",)
    assert "private detail" not in str(item)


def test_failure_does_not_stop_later_contributors():
    first = Contributor("reasoning", fail=True)
    second = Contributor("reflection", "Revisión disponible")
    result = CognitiveRuntimeOrchestrator((first, second)).enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    assert second.calls == 1
    assert result.activated_stages == ("reflection",)


def test_reference_count_is_exposed_without_reference_content_in_prompt():
    result = CognitiveRuntimeOrchestrator(
        (Contributor("reasoning", "Conclusión", "decision-1"),)
    ).enrich(owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW)
    assert result.request.metadata["cognitive_reference_count"] == "1"
    assert "decision-1" not in result.request.prompt


def test_orchestration_identifier_is_deterministic():
    contributor = Contributor("reasoning", "Conclusión")
    first = CognitiveRuntimeOrchestrator((contributor,)).enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    second_contributor = Contributor("reasoning", "Conclusión")
    second = CognitiveRuntimeOrchestrator((second_contributor,)).enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    assert first.orchestration_id == second.orchestration_id


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        CognitiveRuntimeOrchestrator().enrich(
            owner="Carlos",
            session_id="main",
            text="Hola",
            request=request(),
            now=datetime(2026, 7, 13),
        )


def test_duplicate_contributor_names_are_rejected_case_insensitively():
    contributors = (
        Contributor("Reasoning"),
        Contributor("reasoning"),
    )
    with pytest.raises(ValueError, match="unique"):
        CognitiveRuntimeOrchestrator(contributors)


def test_applied_contribution_requires_prompt_lines():
    with pytest.raises(ValueError, match="requires prompt lines"):
        CognitiveRuntimeContribution(
            stage="reasoning", status="applied", rationale=("selected",)
        )


def test_last_result_exposes_latest_orchestration():
    runtime = CognitiveRuntimeOrchestrator((Contributor("reasoning", "Conclusión"),))
    result = runtime.enrich(
        owner="Carlos", session_id="main", text="Hola", request=request(), now=NOW
    )
    assert runtime.last_result is result


def test_structured_messages_are_preserved_when_cognitive_guidance_is_added():
    original_messages = (
        ConversationMessage("user", "Dato inicial"),
        ConversationMessage("assistant", "Entendido"),
        ConversationMessage("user", "Seguimos"),
    )
    original = LLMRequest(
        prompt="legacy",
        system_prompt="Sistema existente",
        messages=original_messages,
    )
    result = CognitiveRuntimeOrchestrator(
        (Contributor("commitment", "No prometer trabajo futuro"),)
    ).enrich(
        owner="Carlos",
        session_id="main",
        text="Seguimos",
        request=original,
        now=NOW,
    )
    assert result.request.messages == original_messages
    assert result.request.system_prompt is not None
    assert result.request.system_prompt.startswith("Sistema existente\n\n")
    assert "No prometer trabajo futuro" in result.request.system_prompt
    assert "No prometer trabajo futuro" in result.request.prompt
