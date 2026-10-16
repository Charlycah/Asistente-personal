# Auditoría general de unificación — RP.20.1

## Cerrado en esta entrega

1. Ruta remota declarable pero no ejecutable.
2. Gemini dependiente del cliente legado `google.generativeai`.
3. Mistral apuntando por defecto a un modelo antiguo y a una ruta externa fija.
4. Falta de registro ambiental de los proveedores remotos.
5. Falta de trazabilidad de red cuando el LLM remoto produce la respuesta.
6. Falta de selección explícita `auto/local/gemini/mistral`.

## Elementos históricos todavía presentes, pero aislados

### `app.bootstrap.build_app`

Constructor anterior conservado para pruebas manuales y reconciliación. El
punto oficial continúa siendo `app.runtime_root_factory:build_runtime_root` y
`OfficialROBYRuntime`.

### `LLMProviderLayer`

Router mínimo de M29 usado por pruebas históricas. No participa del runtime
oficial.

### `ProviderRouter` y `LLMService`

Fachada de fases cognitivas anteriores. Sigue siendo dependencia de módulos y
pruebas antiguas, pero la conversación doméstica oficial usa el router
gobernado.

### Nombre `GovernedProviderExecutionAdapter`

El contrato público histórico se conserva para no romper 6531 pruebas previas.
Su implementación ahora ejecuta rutas locales y remotas únicamente cuando la
configuración gobernada lo autoriza.

## Recomendación posterior

Crear una etapa separada de retiro de compatibilidad que:

- mida importaciones reales fuera de tests;
- migre consumidores de `LLMService`;
- convierta `build_app` en delegador explícito o lo retire;
- renombre los contratos `LocalProviderExecution*` mediante aliases y una
  ventana de deprecación;
- elimine documentación de fases que ya no describa la ejecución oficial.

No conviene hacer esa eliminación junto con la activación de proveedores
remotos porque ampliaría innecesariamente la superficie de regresión.
