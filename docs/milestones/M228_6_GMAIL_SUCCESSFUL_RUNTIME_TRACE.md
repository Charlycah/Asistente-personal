# M228.6 — Gmail Successful Runtime Trace

## Objetivo

Hacer observable el camino saludable completo de Gmail de manera optativa, estable
y libre de secretos, preservando todos los contratos certificados entre M228.2 y
M228.5.

## Alcance

- Reporte `READY` inmutable generado después de un éxito real.
- Nueve etapas con estado `OK`.
- Activación mediante `ROBY_GMAIL_DIAGNOSTIC_TRACE_ON_SUCCESS=true`.
- Ausencia total de preflight o llamadas Gmail adicionales.
- Comportamiento silencioso cuando Gmail está deshabilitado.
- Separación estricta entre reportes `READY` y `DEGRADED`.

## Fuera de alcance

- Nuevas acciones Gmail.
- Nuevos scopes.
- Mutaciones del buzón.
- Validación anticipada de archivos o credenciales.
- Inclusión de cuentas, rutas o material OAuth en la salida.

## Contrato operacional

Sin configuración adicional:

```text
ROBY> Tenés correos nuevos...
```

Con `ROBY_GMAIL_DIAGNOSTIC_TRACE_ON_SUCCESS=true`:

```text
ROBY> Tenés correos nuevos...
GMAIL> READY [gmail/runtime_ready]: El subsistema Gmail completó correctamente el arranque.
GMAIL TRACE> 1/9 Runtime: OK
...
GMAIL TRACE> 9/9 Runtime Completion: OK
```
