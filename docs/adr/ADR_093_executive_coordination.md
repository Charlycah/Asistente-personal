# ADR 093 — Executive Coordination

## Estado

Aceptado para M91.

## Contexto

M90 representa estrategias multihorizonte, mientras M46, M69, M70 y M75 cubren
planificación operativa, acciones gobernadas y tareas. Faltaba una capa que
tradujera un plan ejecutivo aprobado en directivas trazables para subsistemas,
sin ejecutar esas directivas ni eludir permisos.

## Decisión

Introducir `core.adaptive_cognition.executive_coordination` con coordinaciones y
directivas inmutables, repositorio versionado, máquina de estados y política que
prohíbe ejecución directa. Una coordinación solo puede originarse en un plan M90
aprobado o activo. Las directivas conservan subsistema, hito, prioridad,
dependencias, restricciones y estado.

## Invariantes

- Coordinación no equivale a ejecución.
- Solo se coordinan planes aprobados o activos.
- Toda directiva referencia un hito conocido del plan.
- Dependencias y secuencias son explícitas y válidas.
- Autonomía, revisión humana o prioridad crítica requieren revisión.
- Toda modificación crea una revisión inmutable y contigua.
- M91 no crea tareas, no invoca herramientas y no concede permisos.
- La ejecución permanece detrás de M69, M70 y sus controles.

## Consecuencias

M92 podrá integrar el ciclo adaptativo usando una frontera ejecutiva estable sin
acoplar cognición superior con ejecución concreta.
