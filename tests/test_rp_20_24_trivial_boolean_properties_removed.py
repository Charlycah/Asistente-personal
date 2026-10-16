from app.cognitive_agenda_manager import CognitiveAgendaSnapshot
from core.living_conversation.timing import ConversationTimingDecision
from core.mental_state import ROBYMentalState
from core.reasoning import ReasoningContext
from core.tool_runtime_integration.models import ToolRuntimeContext


def test_trivial_boolean_and_count_properties_are_not_public_api() -> None:
    assert not hasattr(CognitiveAgendaSnapshot, "open_items")
    assert not hasattr(ROBYMentalState, "has_active_goals")
    assert not hasattr(ReasoningContext, "has_workspace")
    assert not hasattr(ConversationTimingDecision, "ready_now")
    assert not hasattr(ToolRuntimeContext, "tool_call_performed")


def test_canonical_fields_remain_available() -> None:
    assert "items" in CognitiveAgendaSnapshot.__dataclass_fields__
    assert "active_goals" in ROBYMentalState.__dataclass_fields__
    assert "working_memory" in ReasoningContext.__dataclass_fields__
    assert "recommendation" in ConversationTimingDecision.__dataclass_fields__
    assert "gateway_result" in ToolRuntimeContext.__dataclass_fields__
