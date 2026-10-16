# M31 — LLM Service

## Estado

CLOSED

## Objetivo

Crear una fachada única para que el resto de ROBY consulte modelos sin conocer
proveedores concretos como Ollama, Gemini o Mistral.

M31 se apoya en:

- M29: contrato `LLMProvider`, `LLMRequest`, `LLMResponse`.
- M30: adaptadores concretos de modelos.

## Alcance

Incluido:

- `ProviderRouter` para registrar y resolver proveedores.
- `LLMService` para construir solicitudes normalizadas y delegar en el router.
- Defaults opcionales para `system_prompt`, `model`, `max_tokens`, `temperature` y `metadata`.
- Resultados seguros ante prompt vacío, proveedor faltante, proveedor desconocido y errores del proveedor.
- Tests específicos de milestone.

Excluido:

- Selección automática de proveedor.
- Fallback entre proveedores.
- Integración con memoria, voz, UI, herramientas o caché.
- Llamadas reales de red en tests.

## Diseño

```text
AgentLoop
    │
    ▼
LLMService
    │
    ▼
ProviderRouter
    │
    ├── OllamaProvider
    ├── GeminiProvider
    └── MistralProvider
```

`LLMService` solo recibe prompts, arma `LLMRequest`, resuelve un proveedor y
retorna `LLMResponse`.

`ProviderRouter` solo administra proveedores registrados y el proveedor por
defecto.

## Archivos

- `core/provider_router.py`
- `core/llm_service.py`
- `tests/test_m31_llm_service.py`

## Validación

- Ruff limpio.
- Suite completa verde.
- Sin dependencias de red ni API keys en tests.
