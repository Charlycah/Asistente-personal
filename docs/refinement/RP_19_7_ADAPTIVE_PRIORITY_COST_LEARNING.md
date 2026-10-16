# RP.19.7 — Aprendizaje adaptativo de prioridades y costos

## Objetivo

Permitir que la agenda cognitiva canónica ajuste gradualmente su planificación a partir del historial real de ejecución, sin modelos externos, otro runtime, scheduler, residente ni memoria paralela.

## Diseño

Las estimaciones declaradas por las fuentes siguen siendo autoritativas e inmutables. El aprendizaje se representa mediante dos ajustes separados y acotados:

- `adaptive_priority_adjustment`;
- `adaptive_cost_adjustment`.

Los valores efectivos se calculan dentro del `CognitiveAgendaManager` y sólo afectan la utilidad deliberativa. El valor base aportado por metas, proyectos, recordatorios u otras fuentes no se sobrescribe.

## Evidencia utilizada

- avance explícito: incrementa prioridad efectiva y reduce costo efectivo;
- estancamiento real: reduce prioridad efectiva e incrementa costo efectivo;
- revisión metacognitiva: ajusta ambas estimaciones según calidad de avance y claridad;
- cada evidencia produce un único evento persistente y explicable.

## Límites e invariantes

- tasa y límite se configuran en `CognitiveAgendaPolicy`;
- los ajustes quedan saturados dentro de `adaptive_adjustment_limit`;
- un simple `refresh` sin nueva evidencia no vuelve a aprender el mismo evento;
- el aprendizaje no cierra, archiva ni ejecuta asuntos;
- `reset_adaptation(...)` permite volver a las estimaciones base;
- toda la información se guarda en la misma SQLite de RP.19.1–RP.19.6.

## Observabilidad

Cada asunto conserva:

- cantidad de eventos de aprendizaje;
- fecha del último aprendizaje;
- rationale determinista;
- prioridad efectiva;
- costo cognitivo efectivo.

El snapshot publica `adaptive_learning` y `adaptive_learning_rationale` de forma aditiva.
