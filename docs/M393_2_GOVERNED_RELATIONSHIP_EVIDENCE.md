# M393.2 — Evidencia Relacional Gobernada

M393.2 amplía el fundamento M393.1 sin crear otra autoridad. La capacidad sigue
perteneciendo a `relationship_memory`, materializada por
`RelationshipMemoryManager`, y continúa operando como una vista de solo lectura
sobre `RelationshipMemoryRecord` ya existentes.

## Alcance

Cada `RelationshipEvidenceReference` puede declarar explícitamente:

- referencia y autoridad fuente;
- clase de evidencia relacional;
- `EpistemicLevel` (`fact`, `inference`, `hypothesis`, `unknown`);
- estado de validación (`verified`, `unverified`, `disputed`, `rejected`);
- instante observado con zona horaria;
- notas codificadas de procedencia.

La vista enriquecida expone un `evidence_support_score` determinista derivado
exclusivamente de esas evidencias explícitas. El score sirve para observabilidad
y diagnóstico: no modifica la confianza histórica del
`RelationshipMemoryRecord`, no decide que una relación sea verdadera y no
promueve inferencias o hipótesis a hechos.

## Conflictos y ausencia

- evidencia disputada o rechazada conserva respaldo cero y permanece visible;
- evidencia desconocida o no verificada no se interpreta como confirmación;
- un registro sin evidencia sigue apareciendo como pendiente de revisión;
- el sistema no resuelve contradicciones ni completa metadatos faltantes.

## Compatibilidad

El contrato M393.1 permanece válido: las referencias creadas sin metadatos M393.2
se clasifican de forma conservadora como `unknown` + `unverified`. Esto evita
reescribir evidencia histórica o asumir validación retroactiva.

## Invariantes

- `relationship_memory` continúa siendo la única autoridad relacional;
- la evidencia debe llegar estructurada y explícita;
- el cálculo de respaldo es puro, inmutable y determinista;
- M393.2 no modifica registros, snapshots, persistencia ni heurísticas M52;
- `CanonicalCognitiveCore(` permanece fuera del cambio contractual;
- `.roby/credentials.json` permanece fuera de alcance.

## Fuera de alcance

M393.2 no añade captura automática de evidencia, inferencia desde texto libre,
resolución automática de conflictos, persistencia nueva, aprendizaje,
planificación, modificación de memoria, timers, background, automatización,
permisos ni ejecución.
