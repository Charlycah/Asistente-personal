# M394.7 — Recuperación Segura de Recursos Externos

## Propósito

M394.7 amplía `ExternalResourceRegistryAuthority` con recuperación cognitiva segura y de solo lectura sobre recursos externos ya registrados. No crea una autoridad paralela ni realiza operaciones sobre hardware, red, servicios o dispositivos.

## Contrato

La recuperación produce `ExternalResourceRecoverySnapshot`, una representación inmutable que contiene el registro gobernado actual del recurso y la evidencia de auditoría disponible.

La evidencia se clasifica explícitamente como:

- `registered_only`: existe registro gobernado pero no hay eventos de auditoría disponibles.
- `audited`: existe historial de auditoría y el snapshot referencia su revisión y último `audit_id`.

M394.7 no reconstruye estados históricos que nunca fueron persistidos o auditados como estructura completa. No inventa información ausente.

## Operaciones

- `recover_resource_snapshot(resource_id)`: construye un snapshot inmutable sin mutar el recurso ni la auditoría.
- `validate_recovery(snapshot)`: verifica que el snapshot continúe coincidiendo con el conocimiento gobernado actual y con la revisión de auditoría vigente.

## Invariantes

- La única autoridad sigue siendo `ExternalResourceRegistryAuthority`.
- No existe `RecoveryManager`, `RestoreManager` ni gestor paralelo.
- Recuperar no modifica registro, identidad, estado, autorización, conectividad ni auditoría.
- Recuperar no crea nuevos eventos.
- Recuperar es idempotente mientras la evidencia gobernada no cambie.
- Un snapshot previo queda inválido cuando cambia el recurso o la revisión de auditoría.
- No se abre red, socket, proceso, conexión, autenticación ni interacción física.
- `OfficialDeviceGateway` permanece sin cambios.
- `.roby/credentials.json` no se modifica.
- `CanonicalCognitiveCore(` conserva su posición contractual.

## Fuera de alcance

Persistencia de snapshots, restauración física de dispositivos, rollback operativo, reconexión, descubrimiento, autenticación, activación y ejecución externa permanecen fuera de M394.7.
