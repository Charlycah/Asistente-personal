from core.errors import AppError, ErrorCategory


def fallback_for_retrieval() -> str:
    return (
        "No encontré información suficiente, "
        "pero puedo responder con el contexto disponible."
    )


def fallback_for_llm() -> str:
    return (
        "No pude generar una respuesta completa en este momento. "
        "Podemos intentarlo nuevamente o simplificar la consulta."
    )


def fallback_for_tool() -> str:
    return (
        "No pude acceder a esa herramienta ahora. "
        "Puedo continuar con una alternativa si está disponible."
    )


def fallback_for_parsing() -> str:
    return (
        "Recibí una respuesta con formato inválido. "
        "Puedo intentar reconstruirla o pedir una versión más simple."
    )


def fallback_for_orchestrator() -> str:
    return (
        "Hubo un problema coordinando la operación. Puedo intentar una ruta más simple."
    )


def fallback_for_persistence() -> str:
    return (
        "No pude guardar o recuperar algunos datos, "
        "pero puedo continuar sin persistencia temporalmente."
    )


def fallback_generic() -> str:
    return (
        "Ocurrió un problema inesperado. "
        "Podemos intentarlo nuevamente o buscar otra forma de resolverlo."
    )


def get_fallback_message(error: AppError) -> str:
    match error.category:
        case ErrorCategory.RETRIEVAL:
            return fallback_for_retrieval()

        case ErrorCategory.LLM:
            return fallback_for_llm()

        case ErrorCategory.TOOL:
            return fallback_for_tool()

        case ErrorCategory.PARSING:
            return fallback_for_parsing()

        case ErrorCategory.ORCHESTRATOR:
            return fallback_for_orchestrator()

        case ErrorCategory.PERSISTENCE:
            return fallback_for_persistence()

        case ErrorCategory.TIMEOUT:
            return (
                "No pude completar esa operación a tiempo. "
                "¿Quieres que lo intente nuevamente?"
            )

        case ErrorCategory.VALIDATION:
            return (
                "Hay un problema con los datos recibidos. "
                "Revisa la información e inténtalo nuevamente."
            )

        case _:
            return fallback_generic()
