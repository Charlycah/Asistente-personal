# M367.6 — Priority Reasoning

## Objetivo

Incorporar una evaluación transversal, determinista y explicable de prioridades
sobre candidatos ya admitidos por el modelo mental de ROBY.

## Autoridad

`priority_reasoning` es la autoridad descriptiva de esta capacidad y permanece
subordinada a `internal_world_model`. Reutiliza
`core.cognitive_priority.policy:DeterministicPriorityPolicy` y consume estado
desde `context_state_model` sin reemplazar ninguna política especializada.

## Factores gobernados

La evaluación puede considerar urgencia, importancia, alineación con objetivos,
relevancia contextual, proximidad de plazo, riesgo de seguridad y declaración
explícita del usuario. Los bloqueos excluyen candidatos y las contradicciones se
derivan a revisión.

## Frontera

La regla central establece que priorizar no autoriza actuar. La salida es una clasificación explicable, sin
persistencia, mutación de objetivos, ejecución, aprendizaje ni cambio del
runtime.
