# RP.20.1 — Revisión general y LLM multiproveedor gobernado

## Objetivo

Revisar los puntos todavía no unificados del proyecto e integrar Ollama/local,
Gemini y Mistral en la única ruta oficial de respuesta de ROBY.

## Resultado de la auditoría

### Discontinuidad corregida

ROBY ya tenía:

- contrato neutral `LLMProvider`;
- adaptadores de Ollama, Gemini y Mistral;
- evaluación de salud local/remota;
- política local-first;
- router capaz de declarar `ROUTED_LOCAL` y `ROUTED_REMOTE`.

Sin embargo, el ejecutor oficial rechazaba toda ruta remota. Gemini y Mistral
existían como adaptadores aislados y pruebas de arquitectura, pero no podían
producir una respuesta dentro del `OfficialROBYRuntime`.

RP.20.1 cierra esa discontinuidad sin agregar otro runtime ni otra conversación.

### Compatibilidad histórica conservada

Se identificaron capas anteriores que permanecen por compatibilidad:

- `app.bootstrap.build_app`;
- `LLMProviderLayer`;
- `ProviderRouter` + `LLMService` de las fases iniciales;
- el nombre histórico `GovernedProviderExecutionAdapter`.

No participan del punto de entrada certificado de ROBY salvo pruebas de
compatibilidad. Eliminarlas en esta etapa habría mezclado una migración amplia
con la integración de proveedores. Quedan documentadas para una futura limpieza
controlada.

### Artefactos operativos encontrados en el ZIP recibido

El paquete de entrada contenía `.env`, bases `.roby`, memoria doméstica, tokens,
cachés y bytecode. Se usaron únicamente para verificar nombres de configuración.
El ZIP certificado no incluye ninguno de esos artefactos.

## Arquitectura final

La ejecución sigue esta única cadena:

1. `OfficialROBYRuntime`.
2. `RuntimeCompositionRoot`.
3. evaluación de salud de proveedores.
4. política local-first o selección explícita.
5. `GovernedProviderRouter`.
6. ejecutor gobernado de proveedor.
7. `OperationalResponseAssembler`.
8. respuesta por la ruta conversacional oficial.

No se crean conversaciones, memorias, schedulers, lifecycles ni residentes
paralelos.

## Selección de proveedor

`ROBY_LLM_PROVIDER` acepta:

- `auto`: usa el proveedor local si está disponible y recurre a Gemini/Mistral
  si el local no está disponible;
- `local` u `ollama`: exige la ruta local;
- `gemini`: exige ruta remota y prioriza Gemini;
- `mistral`: exige ruta remota y prioriza Mistral.

Las credenciales continúan exclusivamente en `.env`:

- `GEMINI_API_KEY`;
- `MISTRAL_API_KEY`;
- `OPENROUTER_API_KEY` como alternativa opcional para Mistral.

## Adaptadores recibidos

Los dos módulos aportados fueron útiles como referencia de intención, pero no se
copiaron directamente porque:

- cargaban una configuración ajena al runtime oficial;
- devolvían errores como texto aparentemente normal;
- no preservaban mensajes estructurados ni system prompt;
- no participaban de salud, routing, observabilidad o trazabilidad;
- usaban modelos y clientes anteriores.

Su funcionalidad quedó absorbida por los adaptadores gobernados existentes.

## Garantías

- una sola ejecución oficial;
- red declarada en la trazabilidad cuando responde Gemini o Mistral;
- fallback remoto deshabilitado por defecto fuera de la composición oficial;
- errores de proveedor contenidos como `LLMResponse` no aceptada;
- voseo rioplatense preservado mediante el system prompt doméstico común;
- modelos, endpoints y timeouts configurables por entorno;
- sin secretos en código o documentación.
