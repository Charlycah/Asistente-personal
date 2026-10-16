# M42 — ROBY Mental State (Phase IV.2)

## Propósito

M42 introduce el primer estado mental explícito de ROBY. Después de M41, ROBY ya
sabe quién es; con M42 puede representar cómo está en este momento: qué modo
cognitivo mantiene, cuál es su foco actual, qué objetivos activos conserva y qué
entradas o eventos recientes forman parte de su continuidad inmediata.

## Principios

- El estado mental no ejecuta acciones.
- El estado mental no consulta LLM.
- El estado mental no persiste memoria por sí mismo.
- El estado mental es una fotografía cognitiva legible por capas superiores.
- La Arquitectura 1.0 permanece intacta.

## Componentes

- `MentalMode`: modo actual de ROBY (`idle`, `listening`, `processing`,
  `planning`, `waiting`, `error`).
- `MentalEvent`: evento breve y serializable del estado interno.
- `ActiveGoal`: objetivo activo con prioridad y propietario opcional.
- `ROBYMentalState`: contenedor principal del estado mental.
- `ROBYMentalStateRegistry`: registro simple para resolver el estado activo.

## Integración

`CognitivePipeline` acepta ahora un `mental_state` opcional. Si se proporciona,
el pipeline registra la entrada del usuario, marca el procesamiento del turno e
inyecta líneas seguras de estado mental en el `system_prompt`.

## Validación

M42 añade pruebas específicas para:

- estado inicial determinista;
- observación de entrada de usuario;
- transición a procesamiento;
- objetivos activos ordenados por prioridad;
- finalización de objetivos;
- límite de eventos recientes;
- serialización segura;
- integración opcional con `CognitivePipeline`.

## Hito arquitectónico

Today ROBY learned to hold a mental state while processing the world.
