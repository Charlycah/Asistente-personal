# M367.7 — Mental Model Stabilization

## Objetivo

Cerrar la serie M367 mediante una auditoría determinista y de solo lectura sobre
las autoridades gobernadas del Modelo Mental.

## Autoridad

`mental_model_stabilization` audita, pero no reemplaza, a:

- `internal_world_model`
- `user_profile_model`
- `project_knowledge_model`
- `goals_objectives_model`
- `context_state_model`
- `priority_reasoning`

## Invariantes

La auditoría verifica autoridad única, jerarquía correcta, superficies de solo
lectura, ausencia de persistencia agregada, ausencia de cambios de runtime,
separación entre prioridad y acción y un grafo de dependencias acíclico.

## Frontera

M367.7 no agrega inteligencia, memoria, inferencia, planificación ni ejecución.
No modifica el runtime y no persiste resultados. El informe es explicable,
repetible y apto para regresión arquitectónica.

## Resultado esperado

Un informe `STABLE` sólo se emite cuando todas las invariantes pasan y no existen
autoridades duplicadas, huérfanas o cíclicas.
