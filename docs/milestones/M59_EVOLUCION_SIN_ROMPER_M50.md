# M59 — Evolución sin romper la arquitectura M50

## Propósito

M59 agrega una capa de protección evolutiva para permitir que ROBY siga
creciendo sin sustituir ni debilitar la arquitectura cerrada en M50. Su función
no es crear un nuevo ciclo cognitivo, sino preservar M50 como ancla y convertir
cada extensión posterior en una capacidad opcional, auditable y compatible hacia
atrás.

## Alcance

- Confirmar que `CognitiveCycleManager` sigue siendo el ancla de orquestación.
- Detectar señales de preservación contractual, compatibilidad, validación y
  extensión opcional.
- Calibrar el estado de evolución: `safe`, `guarded`, `needs_review` o
  `blocked`.
- Registrar contratos protegidos y chequeos requeridos antes de cerrar un hito.
- Asociar snapshots upstream de las capas M51-M58 cuando existan.
- Exponer líneas de `system_prompt` para guiar futuras respuestas técnicas.

## Componentes

- `core/evolution_guard.py`
  - `EvolutionSignal`
  - `EvolutionStatus`
  - `EvolutionGuardPolicy`
  - `EvolutionGuardSnapshot`
  - `EvolutionGuardEngine`
  - `EvolutionGuardManager`

## Integración

`CognitivePipeline` acepta opcionalmente `evolution_guard`. Si está presente,
M59 observa el turno después de M58 y antes de construir el prompt final. La
integración es no destructiva: todos los parámetros son opcionales y los campos
previos del resultado del pipeline se mantienen intactos.

## Garantías

- M50 permanece como ancla de ciclo cognitivo.
- Ninguna capa posterior reemplaza contratos públicos existentes.
- Las extensiones nuevas se conectan como dependencias opcionales.
- La compatibilidad hacia atrás se trata como requisito explícito.
- Ruff y Pytest quedan modelados como compuertas de validación.
- Snapshots inmutables y serializables.

## Validación

Pruebas agregadas:

- `tests/test_m59_evolution_guard.py`

Validación local realizada:

- M59 específico: 8 tests en verde.
- M50-M59: 80 tests en verde.
- Suite completa: 636 tests en verde.
