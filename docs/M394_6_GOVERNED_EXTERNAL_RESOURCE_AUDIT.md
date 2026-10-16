# M394.6 — Auditoría Gobernada de Recursos Externos

## Propósito

M394.6 amplía `ExternalResourceRegistryAuthority` con evidencia de auditoría explícita, inmutable y append-only para decisiones sobre recursos externos ya registrados.

## Autoridad

La única autoridad continúa siendo `ExternalResourceRegistryAuthority`. No se crean `AuditManager`, `ResourceHistoryManager` ni gestores paralelos.

## Contrato

`ExternalResourceAuditEvent` conserva `audit_id`, `resource_id`, `event_type`, valores anterior/nuevo, razón, declarador, instante explícito y revisión. `record_audit_event()` requiere un recurso ya registrado y no modifica el objeto `ExternalResourceRegistration`.

La autoridad expone `audit_history()`, `latest_audit()` y `audit_revision()` como vistas deterministas del historial append-only.

## Límites

M394.6 no descubre, conecta, autentica, autoriza, activa, ejecuta, persiste ni consulta recursos. No usa reloj propio ni I/O externo. No modifica `OfficialDeviceGateway`, `.roby/credentials.json` ni la posición contractual de `CanonicalCognitiveCore(`.
