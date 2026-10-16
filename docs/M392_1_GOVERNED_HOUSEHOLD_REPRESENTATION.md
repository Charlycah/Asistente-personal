# M392.1 — Representación del Hogar Gobernada

## Objetivo

M392.1 inicia la serie M392 ampliando el modelo persistente del mundo con una
representación doméstica espacial explícita. La autoridad canónica continúa
siendo `internal_world_model`; el origen persistente de la evidencia continúa
siendo `HouseholdMemory` / `household_memory`.

## Alcance

La representación admite tres clases estructurales: `home`, `room` y `zone`.
También admite relaciones explícitas `contains`, `part_of`, `adjacent_to` y
`connected_to`. Cada espacio y cada relación debe conservar una referencia a
una entrada existente de `HouseholdMemory`.

M392.1 no interpreta texto libre para deducir habitaciones, zonas o geometría.
M392.1 no crea un repositorio, una base de datos, un gestor de hogar ni otra autoridad.
No agrega persistencia: reutiliza la evidencia ya persistida por la autoridad
doméstica existente.

## Invariantes

- Una única autoridad del modelo del mundo: `internal_world_model`.
- Fuente doméstica persistente: `household_memory`.
- Sólo evidencia estructurada y explícita.
- Una relación con extremos ausentes queda marcada para revisión.
- Una fuente archivada permanece visible pero inactiva.
- La representación es inmutable, determinista y de solo lectura.
- No crea inferencias espaciales ni resuelve inconsistencias silenciosamente.
- No controla dispositivos, no modifica Android y no cambia runtime.
- No inicia threads, timers ni procesos residentes.
- No accede a `.roby/credentials.json`.

## Relación con M391.2

M391.2 estableció la vista persistente gobernada del mundo. M392.1 no la
reemplaza: especializa el dominio `HOUSEHOLD` con estructura espacial explícita
y trazable, preservando las autoridades y almacenes ya certificados.
