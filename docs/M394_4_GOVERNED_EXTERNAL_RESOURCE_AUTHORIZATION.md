# M394.4 — Autorizaciones Gobernadas de Recursos Externos

## Propósito

M394.4 amplía la infraestructura externa gobernada para representar decisiones explícitas de autorización sobre recursos ya registrados. La autorización es política declarativa: no autentica, no conecta, no activa y no opera ningún recurso externo.

## Autoridad

`ExternalResourceRegistryAuthority` continúa siendo la única autoridad de la serie M394 para registro, identidad, estado descriptivo y autorización. No se crea `AuthorizationManager`, `PermissionController` ni otra autoridad paralela.

## Modelo

`ExternalResourceAuthorizationState` admite únicamente:

- `unknown`: no existe decisión explícita registrada;
- `authorized`: existe una autorización explícita;
- `denied`: existe una denegación o revocación explícita.

Una decisión explícita se representa mediante `ExternalResourceAuthorizationDecision`, que conserva `source`, `authorized_by`, `decided_at`, `reason` y `revision`. Las decisiones son inmutables y el historial es append-only dentro del registro inmutable actualizado.

Los recursos provenientes de M394.1–M394.3 permanecen compatibles: si no tienen historial de autorización, su estado de autorización es `unknown`.

## Operaciones gobernadas

La autoridad expone `authorize()`, `revoke_authorization()`, `authorization_state()` y `authorization_history()`.

`authorize()` y `revoke_authorization()` requieren evidencia declarada por el llamador. M394.4 no incorpora reloj propio: `authorized_at` debe recibirse explícitamente. Cada decisión aumenta una revisión local consecutiva y la autorización vigente siempre coincide con la última decisión del historial.

## Invariantes

- Autorización no modifica la identidad canónica del recurso.
- Autorización no modifica `known`, `available` o `unavailable`.
- `available` no implica `authorized`.
- `authorized` no implica `connected` ni `active`.
- No hay descubrimiento, polling, red, autenticación, conexión, activación ni ejecución.
- `OfficialDeviceGateway` conserva su autoridad existente.
- No se modifica `.roby/credentials.json`.
- `CanonicalCognitiveCore(` permanece en su posición contractual.
- No se añade persistencia ni background.

## Fuera de alcance

M394.4 no conecta cámaras, sensores, nodos, servicios ni dispositivos; no usa Wi‑Fi, sockets o APIs externas; no concede permisos del sistema operativo; y no convierte una autorización declarada en capacidad operacional. La conectividad gobernada pertenece a un incremento posterior.
