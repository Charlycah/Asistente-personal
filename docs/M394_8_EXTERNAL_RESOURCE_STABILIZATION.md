# M394.8 — Estabilización Integral de Recursos Externos

## Propósito

M394.8 cierra la serie M394 sin añadir capacidad productiva nueva. Consolida los contratos de registro, identidad, estado, autorización, conectividad, auditoría y recuperación segura bajo la única `ExternalResourceRegistryAuthority`.

## Contrato estabilizado

La serie M394 queda compuesta por:

1. M394.1 — Registro Gobernado de Recursos Externos.
2. M394.2 — Identidad Gobernada de Recursos Externos.
3. M394.3 — Estado Gobernado de Recursos Externos.
4. M394.4 — Autorizaciones Gobernadas de Recursos Externos.
5. M394.5 — Conectividad Gobernada de Recursos Externos.
6. M394.6 — Auditoría Gobernada de Recursos Externos.
7. M394.7 — Recuperación Segura de Recursos Externos.
8. M394.8 — Estabilización Integral de Recursos Externos.

M394.8 no agrega métodos públicos, estados, gestores ni rutas operativas. Fija como contrato la API alcanzada en M394.7 y exige determinismo, inmutabilidad, trazabilidad y separación entre conocimiento gobernado e interacción física.

## Invariantes de cierre

- `ExternalResourceRegistryAuthority` continúa siendo la única autoridad de la serie.
- No existen gestores paralelos de registro, identidad, estado, autorización, conectividad, auditoría o recuperación.
- `OfficialDeviceGateway` conserva su autoridad operacional y no depende del registro externo.
- La conectividad sigue siendo declarativa; no existe `connect()`.
- La recuperación sigue siendo cognitiva y de solo lectura; no restaura hardware.
- La auditoría permanece append-only.
- `.roby/credentials.json` no se modifica ni se crea.
- `CanonicalCognitiveCore(` conserva su posición contractual.
- No se incorporan sockets, HTTP, subprocess, polling, background, autenticación, activación ni ejecución externa.

## Validación

El cierre debe mantener Ruff limpio, baseline M361 reproducible y suite completa sin regresiones. Después de certificar M394.8 corresponde realizar la auditoría arquitectónica integral acordada antes de iniciar una nueva etapa.
