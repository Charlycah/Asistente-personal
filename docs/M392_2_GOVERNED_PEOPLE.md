# M392.2 — Personas Gobernadas

## Objetivo

M392.2 amplía el modelo persistente del mundo con una representación explícita,
inmutable y trazable de personas conocidas. `internal_world_model` conserva la
única autoridad canónica de representación; los perfiles de identidad y
`relationship_memory` conservan sus propias autoridades de persistencia.

## Alcance

Una persona sólo puede aparecer cuando su nombre está declarado por un
`PersonalIdentityProfile` gobernado. Las señales relacionales pueden vincularse
a una persona únicamente mediante un `RelationshipMemoryRecord.record_id`
explícito suministrado por el llamador.

M392.2 no interpreta texto libre para identificar personas, no resuelve
ambigüedades de identidad, no infiere a quién pertenece una memoria relacional
y no crea un `PeopleManager`, repositorio, base de datos o perfil paralelo.

## Invariantes

- Una única autoridad del modelo del mundo: `internal_world_model`.
- La identidad sigue perteneciendo a `personal_identity_profile`.
- La memoria relacional sigue perteneciendo a `relationship_memory`.
- No crea personas a partir de conversación, sensores o detección visual.
- No promueve una señal relacional a hecho personal sin enlace explícito.
- Fuentes ausentes o inconsistentes quedan marcadas para revisión.
- La representación es determinista, inmutable y de solo lectura.
- No añade persistencia, ejecución, automatización ni cambios de runtime.
- No accede a `.roby/credentials.json`.

## Relación con M391.2 y M392.1

M391.2 estableció la vista persistente del mundo y M392.1 especializó el hogar.
M392.2 incorpora personas dentro de la misma autoridad descriptiva sin fusionar
ni duplicar los almacenes de identidad o relación existentes.
