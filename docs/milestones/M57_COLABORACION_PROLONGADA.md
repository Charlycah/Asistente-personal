# M57 — Colaboración Prolongada

## Objetivo

M57 incorpora una capa de convivencia orientada a sostener proyectos compartidos
más allá de un turno individual. Su propósito es mantener continuidad sobre un
objetivo común, conservar el foco actual y proponer próximos pasos verificables
sin inventar avances ni ejecutar tareas en segundo plano.

## Principios

- No reemplaza M50: consume el ciclo cognitivo y las capas de convivencia.
- No ejecuta trabajo futuro ni promete actividad fuera del turno actual.
- Distingue continuidad colaborativa de automatización implícita.
- Mantiene resultados auditables mediante snapshots inmutables.
- Se integra opcionalmente al `CognitivePipeline`.

## Componentes

- `CollaborationSignal`: señales de objetivo compartido, continuación,
  checkpoint, siguiente paso y entrega.
- `CollaborationStatus`: estado de la colaboración (`observed`, `active`,
  `sustained`, `paused`, `completed`).
- `CollaborationPolicy`: umbrales y límites de próximos pasos.
- `CollaborationSnapshot`: estado auditable para un turno.
- `CollaborationEngine`: motor puro de evaluación.
- `CollaborationManager`: fachada con historial y líneas de system prompt.

## Integración

M57 consume señales de:

- M52 — Memoria de convivencia.
- M53 — Iniciativa controlada.
- M55 — Personalidad estable.
- M56 — Rutinas y hábitos.

Dentro del pipeline, M57 se ejecuta después de M56 para usar rutinas y hábitos
como evidencia de continuidad operativa. La integración es acumulativa y no
modifica contratos previos.

## Contrato de seguridad

M57 no debe:

- afirmar que se realizó trabajo fuera del turno actual;
- reemplazar decisiones del usuario por continuidad automática;
- cerrar colaboraciones sin evidencia explícita;
- usar historial como excusa para inventar estado de proyecto;
- presionar al usuario con próximos pasos no solicitados.

## Pruebas

Se agrega `tests/test_m57_long_term_collaboration.py` cubriendo:

- validación de política;
- validación de snapshots;
- detección de flujo colaborativo por milestone;
- uso de historial como continuidad;
- rechazo de datetimes naïve;
- serialización;
- prompt sin historial;
- integración completa con `CognitivePipeline`.

## Estado

M57 queda integrado como una capa acumulativa de Fase V, posterior a M56 y
compatible con todos los milestones anteriores.
