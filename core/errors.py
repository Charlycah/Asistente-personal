from enum import Enum


class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    CANCELLATION = "cancellation"
    TOOL = "tool"
    RETRIEVAL = "retrieval"
    LLM = "llm"
    PARSING = "parsing"
    ORCHESTRATOR = "orchestrator"
    PERSISTENCE = "persistence"
    UNKNOWN = "unknown"


class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recoverable: bool = False,
        component: str = "unknown",
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.recoverable = recoverable
        self.component = component
        self.original_error = original_error


class RecoverableError(AppError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, recoverable=True, **kwargs)


class NonRecoverableError(AppError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, recoverable=False, **kwargs)


class TimeoutAppError(RecoverableError):
    pass


class CancellationAppError(NonRecoverableError):
    pass


class ValidationAppError(NonRecoverableError):
    pass


class ToolAppError(RecoverableError):
    pass


class RetrievalAppError(RecoverableError):
    pass


class LLMAppError(RecoverableError):
    pass


class ParsingAppError(RecoverableError):
    pass


class OrchestratorAppError(RecoverableError):
    pass


class PersistenceAppError(RecoverableError):
    pass
