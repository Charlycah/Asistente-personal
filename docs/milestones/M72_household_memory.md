# M72 - Household Memory

## Objetivo

Añadir memoria doméstica estructurada para contactos, turnos, vencimientos,
garantías, servicios, trámites, mantenimiento y notas del hogar.

## Componentes

- `HouseholdMemoryEntry`: entidad inmutable y validada.
- `HouseholdMemoryRepository`: contrato de persistencia.
- `InMemoryHouseholdMemoryRepository`: implementación determinista inicial.
- `HouseholdMemoryManager`: alta, actualización, consulta y ciclo de vida.
- `HouseholdMemorySnapshot`: resumen auditable y contexto para prompts.

## Seguridad

Toda entrada se evalúa mediante M71 Scope Guard. Se bloquean bancos,
billeteras, pagos, finanzas y compras. Las decisiones médicas, legales o
acciones externas requieren revisión y no se almacenan automáticamente.

## Criterios de cierre

- Tests específicos de M71 y M72 verdes.
- Suite completa verde.
- Ruff sin errores en el entorno local.
- ADR y documentación del milestone incorporados.
