import logging
import traceback
from dataclasses import dataclass

from core.error_policy import get_error_policy
from core.errors import AppError, ErrorCategory
from core.fallback import get_fallback_message
from core.metrics import metrics

logger = logging.getLogger(__name__)


@dataclass
class ErrorContext:
    trace_id: str
    request_id: str
    milestone: str
    component: str
    duration_ms: int
    conversation_context: dict | None = None


def log_error(error: AppError, context: ErrorContext) -> None:
    logger.error(
        "application_error",
        extra={
            "trace_id": context.trace_id,
            "request_id": context.request_id,
            "milestone": context.milestone,
            "component": context.component,
            "error_type": error.__class__.__name__,
            "category": error.category.value,
            "severity": error.severity.value,
            "recoverable": error.recoverable,
            "duration_ms": context.duration_ms,
            "conversation_context": context.conversation_context,
            "stack": traceback.format_exc(),
        },
    )


def to_user_message(error: AppError) -> str:
    return get_fallback_message(error)


def handle_error(error: AppError, context: ErrorContext) -> dict:
    policy = get_error_policy(error.category)

    metrics.increment("errors_total")

    if error.category == ErrorCategory.TOOL:
        metrics.increment("tool_failures_total")

    log_error(error, context)

    if policy.fallback:
        metrics.increment("fallbacks_total")
        message = to_user_message(error)
    else:
        message = "No pude completar la operación con los datos recibidos."

    if policy.user_visible:
        metrics.increment("user_visible_errors_total")

    return {
        "ok": False,
        "message": message,
        "error": {
            "category": error.category.value,
            "recoverable": error.recoverable,
        },
        "trace_id": context.trace_id,
        "request_id": context.request_id,
    }
