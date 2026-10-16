# M30 – Model Provider Adapters

## Objetivo

Implementar adaptadores concretos para modelos LLM sobre la capa neutral creada en M29, reutilizando el diseño conceptual de los módulos existentes de Ollama, Gemini y Mistral sin acoplar ROBY a sus dependencias externas.

## Alcance

M30 agrega proveedores concretos para:

- Ollama local.
- Gemini mediante cliente inyectable o SDK opcional.
- Mistral/OpenRouter mediante HTTP.

## Cambio mínimo

Se agrega `core/llm_model_providers.py` con tres implementaciones del contrato `LLMProvider`:

- `OllamaProvider`
- `GeminiProvider`
- `MistralProvider`

También se extiende `LLMRequest` con parámetros opcionales comunes:

- `max_tokens`
- `temperature`

## Decisiones

- Los proveedores devuelven `LLMResponse`; no devuelven strings de error mezclados con respuestas del modelo.
- La configuración se inyecta desde afuera; los providers no leen archivos de configuración.
- La caché no vive dentro del provider. Si ROBY cachea respuestas LLM, debe hacerlo en una capa superior.
- Las dependencias externas se mantienen opcionales o inyectables para conservar tests rápidos y deterministas.
- M30 no ejecuta llamadas reales a internet ni a Ollama durante tests.

## Validación

- Tests específicos: `tests/test_m30_model_providers.py`.
- Ruff limpio.
- Suite completa verde.

## Estado

CLOSED.
