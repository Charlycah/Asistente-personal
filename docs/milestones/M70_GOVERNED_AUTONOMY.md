# M70 — Governed Autonomy

## Propósito

M70 cierra la Fase VI definiendo el marco de autonomía gobernada de ROBY. A
partir de este hito, la autonomía no significa ejecución libre: significa
capacidad para proponer, justificar, solicitar autorización y actuar únicamente
bajo políticas explícitas.

## Principio rector

ROBY puede razonar y proponer acciones. ROBY no debe ejecutar acciones externas
sensibles sin consentimiento explícito, revisión cuando corresponda y registro
auditable.

## Componentes

- `GovernedAutonomyPolicy`
- `GovernedAutonomyDecision`
- `GovernedAutonomySnapshot`
- `GovernedAutonomyManager`
- `GovernedAutonomyStatus`
- `GovernedAutonomySignal`

## Integración

M70 consume los snapshots de:

- M62 — Capability Registry
- M63 — Permissions & Consent
- M61 — Tool Gateway
- M69 — Autonomous Action Planning

No ejecuta herramientas y no reemplaza ninguna capa anterior. Su función es
aplicar una decisión de gobierno común para todas las capacidades presentes y
futuras.

## Reglas de gobernanza

- ROBY puede proponer acciones antes de ejecutarlas.
- ROBY no ejecuta acciones sensibles sin consentimiento explícito.
- Las acciones de escritura, dispositivo o alto riesgo requieren revisión.
- Ante conflicto entre políticas, prevalece la más restrictiva.
- Toda decisión autónoma debe ser auditable.
- Toda decisión autónoma debe poder explicarse al usuario.

## Ejemplos

- Clima: puede proponerse como capacidad de bajo riesgo.
- Lectura de correo: puede gobernarse como lectura de bajo riesgo.
- Redacción/envío de correo: requiere revisión y consentimiento.
- Cámara: requiere permiso explícito y queda bloqueada hasta obtenerlo.

## Tests

- Tests M70: 12 casos.
- Cadena Fase VI M61–M70: 100 casos.
- Suite completa esperada: 745 tests.

## Cierre de fase

Con M70, Fase VI queda cerrada arquitectónicamente: ROBY ya dispone de gateway,
registro semántico de capacidades, permisos, adapters reales, planificación
autónoma limitada y gobernanza final para decidir cuándo puede proponer,
cuándo debe pedir permiso y cuándo debe bloquear una acción.
