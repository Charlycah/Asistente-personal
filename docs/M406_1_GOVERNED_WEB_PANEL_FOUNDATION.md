# ROBY XI.2 — M406.1 Governed Web Panel Foundation

**Baseline de partida:** Estado Maestro Post-M405 — M361 sincronizada · Ruff limpio · 11.161 tests passed · 0 regresiones.

## Objetivo

Materializar la primera superficie Web gobernada y productiva de ROBY sin crear una nueva autoridad, runtime o raíz de composición.

Cadena mínima:

`owners existentes → read-model explícito → HTTP stdlib loopback → GET /api/status`.

## Alcance implementado

- `application/governed_web_panel.py`
  - `GovernedWebPanelSnapshot` immutable y no autoritativo;
  - secciones `system`, `residence`, `synchronization`, `resources`;
  - clasificación explícita M405 por sección;
  - degradación independiente `AVAILABLE / UNAVAILABLE / NO_DATA`;
  - ninguna persistencia ni autorización de acción.
- `app/web_panel_sources.py`
  - proyecciones mínimas desde owners ya existentes;
  - M402 se reutiliza para estado residencial;
  - M403 se reutiliza sin exponer payload sincronizado;
  - External Resource Registry se proyecta sin endpoint, metadata ni credenciales;
  - runtime oficial se observa sin adquirir lifecycle ownership.
- `infrastructure/web_panel_http.py`
  - Python stdlib `ThreadingHTTPServer`;
  - binding obligatorio `127.0.0.1`;
  - puerto configurable/efímero;
  - `GET /api/status` y `HEAD /api/status`;
  - `POST/PUT/PATCH/DELETE` rechazados con 405;
  - `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`;
  - CORS no habilitado;
  - fallo de bind queda confinado al Panel.

## Clasificación de exposición

- System summary: `PERSONAL`.
- Residence summary: `PRIVATE`.
- Synchronization summary: `PRIVATE`.
- Resources summary: `PRIVATE`.
- `SENSITIVE`: no permitido en foundation.
- `UNCLASSIFIED`: no permitido en foundation.

La surface local-private puede mostrar `PRIVATE` sólo porque M406.1 está estrictamente limitada a loopback. Esto no convierte esos datos en `PUBLIC`.

## Ownership preservado

- runtime / diagnostics: hechos operacionales del sistema;
- M396: identidad de residencia;
- M397: conectividad/readiness;
- M402: representación integrada del nodo residencial;
- M403: synchronization;
- ExternalResourceRegistryAuthority: recursos externos;
- M405: vocabulario de clasificación;
- M406.1: sólo proyección, serialización y presentación HTTP.

## Invariantes M406.1

1. El Panel Web es una surface, no una authority.
2. No existe `WebPanelAuthority`, `WebRuntime` ni segundo `RuntimeCompositionRoot`.
3. El HTTP adapter depende sólo del read-model del Panel.
4. Binding no-loopback falla cerrado.
5. No hay endpoints de mutación.
6. No hay memoria, conversaciones, cámara/media, GPS ni credenciales.
7. No se reutiliza M398 como transporte Web.
8. No se recomputa verdad de M402/M403/Registry.
9. Los modelos fuente no se serializan en bruto.
10. La indisponibilidad de una sección no derriba las demás.
11. El fallo del listener no es fallo cognitivo.
12. No se introduce dependencia Web third-party.

## Fuera de alcance

- HTML/CSS/JS dashboard;
- WebSockets o streaming;
- LAN / `0.0.0.0` / acceso remoto;
- authentication/login;
- actions, device control o runtime control;
- historial/memoria/conversaciones;
- cámara, media, ubicación o datos sensibles;
- CORS;
- persistencia/cache de Panel.

## Validación esperada

M406.1 agrega 18 tests dirigidos. La baseline Post-M405 era 11.161 tests, por lo que el total esperado del candidato es 11.179 tests, sujeto a `pytest --collect-only` y validación oficial completa.
