# ROBY XI.2 M326.8 — Decision Journal

## Objetivo

Cerrar el pipeline lógico de autonomía con un journal append-only, determinista y
auditable para registrar ciclos de decisión ya validados.

## Nuevo módulo

- `core/controlled_autonomy/decision_journal.py`

## Contratos e implementación

- `JournalSnapshot`
- `InMemoryDecisionJournal`

La implementación satisface el protocolo existente `DecisionJournal`.

## Comportamiento

- conserva el orden de inserción;
- devuelve entradas mediante tuplas inmutables;
- produce snapshots independientes del estado futuro;
- rechaza `journal_id`, `decision_id` y `outcome_id` duplicados;
- consulta por journal, decisión, resultado, situación y candidato;
- separa entradas completadas de entradas pendientes;
- no ejecuta acciones ni persiste datos fuera de memoria.

## Validación

- 28 pruebas nuevas de M326.8;
- 7622 pruebas completas aprobadas en el entorno de construcción;
- compilación Python correcta;
- Ruff debe validarse en el entorno local del proyecto.
