# M32 — Agent LLM Integration

## Objetivo

Conectar el `AgentLoop` con `LLMService` sin acoplar el loop a proveedores
concretos ni alterar los adaptadores de modelos creados en M30.

Este milestone convierte la capa LLM estabilizada en M29–M31 en una capacidad
invocable desde el ciclo del agente, manteniendo el mismo criterio incremental
de Architecture 1.0: un cambio pequeño, aislado y verificable.

## Alcance

M32 incorpora un ciclo LLM explícito en `AgentLoop` mediante inyección opcional
de `LLMService`.

El flujo queda:

```text
AgentLoop
   │
   ▼
LLMService
   │
   ▼
ProviderRouter
   │
   ▼
Provider concreto
```

## Cambios incluidos

- `AgentLoop` acepta un `LLMService` opcional.
- Se agrega `run_llm_once(...)` como ciclo unitario de generación LLM.
- El loop puede seleccionar un proveedor explícito mediante el servicio.
- Las respuestas LLM se normalizan a `AgentRuntimeResult`.
- Los errores del servicio se convierten en resultados seguros.
- El ciclo runtime tradicional (`run_once`) queda sin cambios funcionales.

## Fuera de alcance

M32 no introduce:

- selección automática de proveedor;
- fallback entre proveedores;
- memoria en el prompt;
- herramientas automáticas;
- UI o voz;
- llamadas reales a red en tests;
- cambios en Ollama, Gemini o Mistral.

## Validación

Tests específicos:

```text
tests/test_m32_agent_llm_integration.py
```

Cobertura principal:

- el ciclo runtime existente sigue funcionando con `LLMService` presente;
- el loop ejecuta un ciclo LLM mediante el servicio;
- el loop puede solicitar un proveedor explícito sin conocer su implementación;
- ausencia de servicio LLM produce resultado seguro;
- respuestas rechazadas se mapean a fallo controlado;
- errores del servicio se transforman en fallo seguro;
- protección reentrante evita tocar el servicio durante ciclos activos.

## Criterio de cierre

M32 se considera cerrado solo con:

```bash
ruff check .
pytest
```

ambos en verde.
