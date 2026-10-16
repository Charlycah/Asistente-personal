from core.error_handler import ErrorContext, handle_error
from core.errors import ErrorCategory, ToolAppError


def test_tool_error_returns_conversational_fallback():
    error = ToolAppError(
        "Tool failed",
        category=ErrorCategory.TOOL,
        component="tool_execution",
    )

    context = ErrorContext(
        trace_id="trace-1",
        request_id="req-1",
        milestone="M14",
        component="tool_execution",
        duration_ms=1200,
        conversation_context={},
    )

    response = handle_error(error, context)

    assert response["ok"] is False
    assert "herramienta" in response["message"].lower()
    assert response["trace_id"] == "trace-1"


def test_error_does_not_expose_exception_details():
    error = ToolAppError(
        "Exception: Timeout after 30s",
        category=ErrorCategory.TOOL,
        component="tool_execution",
    )

    context = ErrorContext(
        trace_id="trace-2",
        request_id="req-2",
        milestone="M14",
        component="tool_execution",
        duration_ms=30000,
        conversation_context={},
    )

    response = handle_error(error, context)

    assert "Exception" not in response["message"]
    assert "Timeout after 30s" not in response["message"]
