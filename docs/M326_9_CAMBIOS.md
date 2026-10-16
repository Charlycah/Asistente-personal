# M326.9 — Controlled Autonomy Orchestrator

## Objetivo

Encadenar las capas deterministas de autonomía controlada en un único ciclo
coherente, auditable y sin capacidad de ejecución.

## Incorporado

- `ControlledAutonomyOrchestrator` como puerto de coordinación.
- `DeterministicControlledAutonomyOrchestrator` como implementación pura.
- `ControlledAutonomyResult` como vista inmutable de todas las etapas.
- `OrchestrationStatus` para distinguir ciclos completados y observaciones sin
  situación accionable.
- `default_controlled_autonomy_orchestrator()` para componer las reglas y
  adaptadores deterministas ya validados.

## Flujo

1. Evalúa una `RuntimeObservation`.
2. Detiene el ciclo si no existe una `DecisionSituation`.
3. Genera candidatos.
4. Evalúa riesgo y confianza.
5. Produce una decisión de política.
6. Aplica la compuerta de autonomía.
7. Registra la decisión gobernada en el `DecisionJournal`.

## Límites

- No ejecuta acciones.
- No reintenta, revierte, degrada ni notifica.
- No crea resultados ficticios.
- No registra entradas cuando no se identificó una situación.
- No modifica los componentes validados de M326.2 a M326.8.

## Validación del entorno de construcción

- 28 pruebas nuevas.
- 7650 pruebas totales superadas.
- `compileall` correcto.
