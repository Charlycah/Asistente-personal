# M29 — LLM Provider Layer

## Objetivo

Desacoplar ROBY del proveedor de modelos para poder usar distintos motores
como Ollama, Gemini, Mistral u otros sin acoplar el core a clientes concretos,
APIs externas, credenciales ni transporte HTTP.

M29 no implementa conectores reales. Solo estabiliza el contrato interno para
que los adaptadores específicos puedan añadirse en milestones posteriores.

## Revisión del material existente

Se revisó el ZIP disponible buscando módulos existentes relacionados con
`Interactuar con modelos`, `Ollama`, `Gemini`, `Mistral`, `LLM` o `provider`.
En el paquete analizado no apareció un módulo fuente reutilizable con esos
nombres. Por ese motivo, M29 sigue la metodología habitual: cambio mínimo,
contrato propio y sin importar código externo no verificado.

## Arquitectura

```text
LLMRequest
    ↓
LLMProviderLayer.generate()
    ↓
LLMProvider.generate()
    ↓
LLMResponse
```

## Componentes

- `LLMRequest`: solicitud neutral para un modelo.
- `LLMResponse`: respuesta normalizada del proveedor.
- `LLMProvider`: protocolo mínimo que cualquier motor debe cumplir.
- `LLMProviderLayer`: registro y router seguro de proveedores.
- `LLMProviderSnapshot`: estado observable sin exponer mutabilidad interna.

## Contrato

- El core no conoce Ollama, Gemini, Mistral ni SDKs concretos.
- El primer proveedor registrado queda activo por defecto.
- Se puede cambiar el proveedor activo explícitamente.
- Se puede enrutar una llamada a un proveedor específico sin cambiar el activo.
- Un prompt vacío devuelve una respuesta segura sin tocar el proveedor.
- Un proveedor ausente o desconocido devuelve una respuesta segura.
- Una falla inesperada del proveedor se convierte en una respuesta segura.
- No se introducen llamadas de red, credenciales, variables de entorno ni I/O.

## Tests

- `test_llm_provider_layer_starts_empty`
- `test_llm_provider_layer_registers_provider_and_uses_it_as_active`
- `test_llm_provider_layer_can_switch_between_registered_providers`
- `test_llm_provider_layer_can_route_to_explicit_provider_without_switching_active`
- `test_llm_provider_layer_rejects_empty_provider_names`
- `test_llm_provider_layer_returns_safe_result_without_active_provider`
- `test_llm_provider_layer_returns_safe_result_for_unknown_provider`
- `test_llm_provider_layer_returns_safe_result_for_empty_prompt_without_touching_provider`
- `test_llm_provider_layer_turns_provider_failures_into_safe_results`

## Estado

Completo.
