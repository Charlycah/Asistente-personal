from dataclasses import dataclass

from core.errors import ErrorCategory


@dataclass
class ErrorPolicy:
    retry: bool
    max_attempts: int
    fallback: bool
    user_visible: bool


ERROR_POLICIES: dict[ErrorCategory, ErrorPolicy] = {
    ErrorCategory.TIMEOUT: ErrorPolicy(
        retry=True,
        max_attempts=3,
        fallback=True,
        user_visible=True,
    ),
    ErrorCategory.TOOL: ErrorPolicy(
        retry=True,
        max_attempts=2,
        fallback=True,
        user_visible=True,
    ),
    ErrorCategory.RETRIEVAL: ErrorPolicy(
        retry=True,
        max_attempts=2,
        fallback=True,
        user_visible=True,
    ),
    ErrorCategory.LLM: ErrorPolicy(
        retry=True,
        max_attempts=2,
        fallback=True,
        user_visible=True,
    ),
    ErrorCategory.PARSING: ErrorPolicy(
        retry=False,
        max_attempts=1,
        fallback=True,
        user_visible=True,
    ),
    ErrorCategory.VALIDATION: ErrorPolicy(
        retry=False,
        max_attempts=1,
        fallback=False,
        user_visible=True,
    ),
    ErrorCategory.CANCELLATION: ErrorPolicy(
        retry=False,
        max_attempts=1,
        fallback=False,
        user_visible=False,
    ),
    ErrorCategory.PERSISTENCE: ErrorPolicy(
        retry=True,
        max_attempts=2,
        fallback=True,
        user_visible=True,
    ),
    ErrorCategory.UNKNOWN: ErrorPolicy(
        retry=False,
        max_attempts=1,
        fallback=True,
        user_visible=True,
    ),
}


def get_error_policy(category: ErrorCategory) -> ErrorPolicy:
    return ERROR_POLICIES.get(category, ERROR_POLICIES[ErrorCategory.UNKNOWN])
