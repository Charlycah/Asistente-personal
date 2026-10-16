from datetime import datetime, timezone

from app.living_companion_runtime import LivingCompanionRuntime
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


class Interceptor:
    def __init__(self, trigger: str, response: str) -> None:
        self.trigger = trigger
        self.response = response
        self.calls = 0

    def intercept(self, request, *, now):
        del now
        if self.trigger not in request.text.casefold():
            return None
        self.calls += 1
        return GovernedOperationalInterception(response_text=self.response)


def request(text: str, session_id: str = "household-main"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def registry():
    item = OfficialRuntimeCapabilityRegistry()
    item.register(
        name="weather.household",
        description="Weather",
        interceptor=Interceptor("pronostico", "Manana llueve."),
    )
    item.register(
        name="household.daily_briefing",
        description="Briefing",
        interceptor=Interceptor("resumen", "Tenes una reunion a las 9."),
    )
    item.register(
        name="resident.reminders",
        description="Reminders",
        interceptor=Interceptor("recordatorios", "Lleva los documentos."),
    )
    return item


def test_accompanies_an_important_meeting_as_a_situation():
    runtime = LivingCompanionRuntime(registry())
    result = runtime.intercept(
        request("Manana tengo una reunion importante."),
        now=NOW,
    )
    assert result is not None
    assert "Revise lo importante" in result.response_text
    assert "Manana llueve" in result.response_text
    assert "reunion a las 9" in result.response_text


def test_explicit_questions_stay_in_the_normal_runtime():
    runtime = LivingCompanionRuntime(registry())
    assert runtime.intercept(request("Como esta el clima manana?"), now=NOW) is None


def test_companion_context_is_isolated_by_conversation():
    runtime = LivingCompanionRuntime(registry())
    runtime.intercept(request("Estoy preparando un viaje."), now=NOW)
    assert runtime.context_for(owner="Carlos", session_id="household-main") is not None
    assert runtime.context_for(owner="Carlos", session_id="other") is None


def test_high_risk_capabilities_are_not_used_implicitly():
    item = registry()
    camera = Interceptor("camara", "Foto tomada")
    item.register(
        name="camera.capture_runtime",
        description="Camera",
        interceptor=camera,
        risk="high",
        requires_confirmation=True,
    )
    runtime = LivingCompanionRuntime(item)
    result = runtime.intercept(request("Estoy preparando un viaje."), now=NOW)
    assert result is not None
    assert camera.calls == 0
    assert runtime.snapshot.accompanied_turns == 1


class ReasoningDecision:
    def __init__(self, conclusion: str, confidence_score: float) -> None:
        self.conclusion = conclusion
        self.confidence_score = confidence_score


class ReasoningResult:
    def __init__(
        self,
        conclusion: str,
        confidence_score: float,
        status: str = "completed",
    ) -> None:
        self.status = status
        self.decision = ReasoningDecision(conclusion, confidence_score)


class ReasoningSource:
    def __init__(self, result: ReasoningResult) -> None:
        self.result = result
        self.calls = 0

    def __call__(self, **kwargs):
        del kwargs
        self.calls += 1
        return self.result


def test_reasoning_source_can_admit_a_safe_situation_after_local_classifier_miss():
    source = ReasoningSource(
        ReasoningResult(
            (
                "La situacion describe preparacion domestica proxima "
                "y requiere organizacion."
            ),
            0.86,
        )
    )
    runtime = LivingCompanionRuntime(registry(), reasoning_source=source)

    result = runtime.intercept(
        request(
            "Manana viene alguien a casa y todavia me falta organizar varias cosas."
        ),
        now=NOW,
    )

    assert source.calls == 1
    assert result is not None
    assert "situacion" in result.response_text.casefold()
    assert "reunion a las 9" in result.response_text
    assert "Lleva los documentos" in result.response_text
    assert runtime.snapshot.last_situation == "general_situational_support"
