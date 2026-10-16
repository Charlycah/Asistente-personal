# M56 — Rutinas y Hábitos

## Objetivo

M56 incorpora una capa de convivencia orientada a detectar y sostener patrones
repetidos de trabajo, seguimiento y colaboración. La intención no es ejecutar
tareas futuras ni imponer hábitos, sino reconocer rutinas observables para
reducir fricción y mantener continuidad entre turnos.

## Principios

- No reemplaza M50: consume el ciclo cognitivo y la cadena de convivencia.
- No crea automatizaciones ni compromisos por sí mismo.
- Diferencia señales observadas de instrucciones explícitas.
- Mantiene resultados auditables mediante snapshots inmutables.
- Se integra opcionalmente al `CognitivePipeline`.

## Componentes

- `RoutineSignal`: señales de continuidad, checkpoint, compromiso, repetición y
  soporte.
- `HabitSupportLevel`: nivel de soporte permitido (`observe`, `reinforce`,
  `suggest`, `stabilize`).
- `RoutineHabitPolicy`: umbrales y límites de guía.
- `RoutineHabitSnapshot`: estado auditable para un turno.
- `RoutineHabitEngine`: motor puro de evaluación.
- `RoutineHabitManager`: fachada con historial y líneas de system prompt.

## Integración

M56 consume señales de:

- M51 — Presencia continua.
- M52 — Memoria de convivencia.
- M55 — Personalidad estable.

Dentro del pipeline, M56 se ejecuta después de M55 para poder usar la expresión
de personalidad estable como parte de la confianza del patrón.

## Contrato de seguridad

M56 no debe:

- asumir que una rutina observada es una obligación permanente;
- presionar al usuario para sostener hábitos;
- crear recordatorios o tareas futuras;
- sustituir la decisión humana por automatización implícita.

## Pruebas

Se agrega `tests/test_m56_routines_habits.py` cubriendo:

- validación de política;
- validación de snapshots;
- detección de flujo de checkpoints;
- uso de historial como repetición;
- rechazo de datetimes naïve;
- serialización;
- prompt sin historial;
- integración completa con `CognitivePipeline`.

## Estado

M56 queda integrado como una capa acumulativa de Fase V, posterior a M55 y
compatible con todos los milestones anteriores.
