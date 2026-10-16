# ADR 228.6 — Gmail Successful Runtime Trace

## Estado

Aceptado.

## Contexto

M228.4 incorporó una traza diagnóstica determinista para fallos Gmail y M228.5
resolvió Client Secrets mediante precedencia gobernada. El camino saludable seguía
siendo deliberadamente silencioso, salvo por el anuncio funcional. Para aceptación
operacional y soporte resulta útil poder certificar las nueve etapas exitosas sin
convertir el diagnóstico en un preflight ni agregar ruido por defecto.

## Decisión

Se incorpora una traza saludable posterior al éxito y controlada por
`ROBY_GMAIL_DIAGNOSTIC_TRACE_ON_SUCCESS`.

- El valor por defecto es `false`.
- La traza se construye únicamente después de que `announce()` retorna con éxito.
- Gmail deshabilitado permanece silencioso.
- Un fallo conserva exclusivamente el reporte `DEGRADED` existente.
- No se inspeccionan nuevamente token, archivos, scopes o dependencias.
- No se exponen rutas, cuentas, credenciales ni excepciones.
- La traza saludable declara las nueve etapas como `OK` porque deriva del resultado
  runtime ya completado, no de una predicción ambiental.

## Salida estable

```text
GMAIL> READY [gmail/runtime_ready]: El subsistema Gmail completó correctamente el arranque.
GMAIL TRACE> 1/9 Runtime: OK
...
GMAIL TRACE> 9/9 Runtime Completion: OK
```

## Consecuencias

La salida histórica permanece inalterada por defecto. Los operadores pueden activar
una certificación visible del camino saludable sin modificar OAuth, Gmail API,
scopes, persistencia o capacidades del buzón.
