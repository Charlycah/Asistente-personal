# M400.3 — Governed External Intelligence Provider Integration

## Propósito

M400.3 conecta la frontera contractual M400.2 con la ruta multiprovider ya
gobernada. No crea un router, executor ni cerebro nuevo.

La integración recibe un `LocalProviderExecutionResult` ya producido por
`GovernedProviderExecutionAdapter` y lo transforma en un
`ExternalIntelligenceEnvelope` mediante la frontera M400.2:

**provider execution → external evidence envelope**

La integración no llama `generate()`, no selecciona providers y no decide qué
provider debe utilizar ROBY.

## Linaje obligatorio

Para admitir evidencia se exige:

1. solicitud M400.2 explícita de `inference_provider`;
2. mismo owner que la ejecución gobernada;
3. ejecución realmente intentada;
4. respuesta de provider presente;
5. provider seleccionado por la ruta gobernada;
6. target, ruta y resultado consistentes;
7. `route_id` y `execution_id` conservados como trazabilidad.

Los estados `completed`, `rejected` y `failed` pueden aportar evidencia. Un
resultado fallido no se convierte en respuesta aceptada: entra como evidencia
rechazada con el error del provider.

## Ollama y providers remotos

Ollama conserva su lugar local-first. Gemini y Mistral siguen siendo providers
remotos gobernados por la misma ruta existente. M400.3 no cambia preferencias,
fallback ni permisos de ejecución remota.

`execution_scope` y `network_used` siguen siendo dimensiones distintas. Un
Ollama local puede usar transporte localhost; por ello M400.3 recibe
`network_used` como hecho explícito de procedencia y no lo deduce de
`local/remote`.

## Autoridad

**capacidad/evidencia externa ≠ autoridad cognitiva**

`GovernedExternalProviderIntegration` es un adapter de integración y expone
`integration_id`, no `authority_id`. ROBY conserva interpretación y decisión.

M400.3:

- no selecciona ni ejecuta providers;
- no reemplaza `GovernedProviderRouter`;
- no reemplaza `GovernedProviderExecutionAdapter`;
- no reemplaza `RuntimeCompositionRoot`;
- no habilita fallback automático;
- no habilita red remota por sí mismo;
- no modifica memoria, planificación ni código operativo.
