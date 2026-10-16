# ROBY XI.2 — M406 Governed Web Panel Formal Closure

**Baseline de cierre:** M406.3 — Optional Productive Runtime Wiring  
**Validación oficial:** M361 sincronizada · Ruff limpio · 11.199 tests passed · 0 regresiones  
**Fecha:** 11 de agosto de 2026

## 1. Veredicto

**M406 — Governed Web Panel: CERRADO FORMALMENTE PARA EL ALCANCE LOCAL, READ-ONLY Y PRODUCTIVAMENTE INTEGRADO.**

No existe un bloqueo arquitectónico, operacional, lifecycle o de experiencia mínima que justifique M406.4.

LAN, autenticación, acceso remoto, streaming y control quedan fuera del alcance M406 y sólo pueden abrirse mediante un gate futuro específico.

## 2. Cadena cerrada

- **M406.1 — Governed Web Panel Foundation:** read model explícito, clasificación de exposición, stdlib HTTP, loopback `127.0.0.1`, `GET /api/status`, read-only.
- **M406.2 — Minimal Human Dashboard:** `GET /` server-rendered desde el mismo `GovernedWebPanelSnapshot`, sin JavaScript/polling/CDN ni nuevas fuentes.
- **M406.3 — Optional Productive Runtime Wiring:** servicio deshabilitado por defecto, opt-in, registrado como residente OPTIONAL dentro del `OfficialROBYRuntime` existente, sin segundo runtime ni segundo `RuntimeCompositionRoot`.

## 3. Ownership final

- runtime/diagnostics conservan ownership de system facts;
- M396/M397/M402 conservan residence/connectivity/node facts;
- M403 conserva synchronization facts;
- ExternalResourceRegistryAuthority conserva external-resource facts;
- M405 conserva el vocabulario de Information Classification;
- M406 posee únicamente proyección, exposure metadata y presentación HTTP/HTML.

M406 no es una authority de dominio ni una nueva frontera cognitiva.

## 4. Seguridad y exposición cerradas

- binding productivo: exactamente `127.0.0.1`;
- `0.0.0.0`, LAN y remoto: no autorizados;
- surface: read-only;
- `SENSITIVE` y `UNCLASSIFIED`: no expuestos;
- credenciales: nunca proyectadas;
- CORS: no habilitado;
- no acciones, device control, runtime control ni browser auto-open.

## 5. Failure isolation

El Panel es opcional. Un fallo de bind o startup degrada únicamente el residente Web Panel y no impide el arranque/continuidad del `OfficialROBYRuntime`. El shutdown del runtime detiene el listener.

## 6. Nivel de terminación

- **Arquitectura:** CLOSED.
- **Operación local:** CLOSED.
- **Lifecycle productivo:** CLOSED.
- **Experiencia humana local mínima:** CLOSED.
- **Hardware físico especial:** N/A para este scope software-local.
- **LAN / remoto / autenticación / control:** FUTURE SEPARATE SCOPE.

## 7. Invariantes permanentes

1. Web Panel es surface de presentación, no authority.
2. Domain truth permanece en owners canónicos existentes.
3. Toda exposición usa proyecciones explícitas y clasificadas.
4. Raw domain serialization está prohibida.
5. Credentials nunca forman parte de la proyección.
6. `SENSITIVE` y `UNCLASSIFIED` permanecen fuera del scope local cerrado.
7. El scope M406 permanece read-only.
8. El binding productivo local es loopback-only.
9. Cualquier non-loopback exposure requiere un nuevo security/authentication gate.
10. El lifecycle del Panel permanece subordinado al `OfficialROBYRuntime`.
11. El fallo del Panel no se convierte en fallo cognitivo.
12. No se permite segundo runtime, segundo root o segunda authority.
13. Missing source state se representa como unavailable/no-data, nunca como healthy inventado.
14. HTML y JSON consumen el mismo read model gobernado.
15. Control futuro no puede añadirse simplemente como nuevos métodos HTTP.

## 8. Qué NO abre M406.4

No abrir M406.4 por continuidad para:

- LAN;
- Internet/remoto;
- autenticación/TLS;
- WebSockets/SSE/polling;
- camera/media;
- GPS/location;
- memory/history;
- conversation UI;
- device/runtime control;
- administración de credenciales.

Esas líneas requieren necesidades y gates propios.

## 9. Validación

- M361: sincronizada;
- Ruff: limpio;
- pytest: **11.199 passed**;
- regresiones: **0**.

## 10. Decisión final

**M406 — Governed Web Panel: CERRAR FORMALMENTE.**

El siguiente trabajo debe volver al Estado Maestro Post-M406 y elegir el próximo pendiente por necesidad real, no por continuidad numérica.
