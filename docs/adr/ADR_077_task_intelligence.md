# ADR-077 — Task Intelligence para operaciones personales

## Estado

Aceptado.

## Contexto

M71–M74 incorporaron límites operativos, memoria doméstica, ingreso documental y
conocimiento personal. ROBY necesitaba convertir esas fuentes en trabajo concreto
sin confundir organización con ejecución autónoma.

## Decisión

Introducir `TaskIntelligenceManager` como subsistema de dominio responsable de:

- crear candidatos de tarea con procedencia auditable;
- exigir revisión humana para sugerencias automáticas o de baja confianza;
- priorizar mediante importancia, urgencia, plazo y estado;
- modelar dependencias acíclicas;
- identificar tareas listas para comenzar;
- mantener estados y evidencia de finalización;
- derivar planes cognitivos sin ejecutar acciones externas;
- integrarse con Household Memory, Document Inbox y Personal Knowledge Base;
- someter todas las tareas a Scope Guard.

La persistencia se mantiene detrás del contrato `TaskRepository` y M75 aporta una
implementación determinista en memoria.

## Consecuencias

ROBY puede responder de forma estructurada qué conviene atender primero y por qué,
pero no completa tareas ni realiza operaciones externas por iniciativa propia. La
integración futura con agenda, briefing y scheduler deberá conservar esta separación
entre recomendación, planificación y ejecución autorizada.
