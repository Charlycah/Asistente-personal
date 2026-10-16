# M52 — Memoria de Convivencia

## Propósito

M52 extiende la FASE V — Convivencia para que ROBY pueda conservar una memoria relacional mínima, auditable y estable sobre la forma de trabajar con el usuario.

No reemplaza la memoria cognitiva M36-M39 ni la persistencia M18-M21. M52 agrega una capa superior de convivencia que interpreta señales relacionales: ritmo de trabajo, preferencias explícitas, límites, confianza y continuidad.

## Regla arquitectónica

- M50 sigue siendo el núcleo cognitivo.
- M51 aporta presencia continua.
- M52 consume la presencia y el turno del usuario para actualizar contexto relacional.
- La memoria de convivencia es opcional dentro del `CognitivePipeline`.
- No llama al LLM, no ejecuta herramientas y no escribe en almacenamiento externo.
- No rompe contratos previos.

## Componentes

### `RelationshipMemoryKind`

Clasifica señales relacionales en:

- `interaction_pattern`
- `user_preference`
- `project_rhythm`
- `trust_signal`
- `boundary`
- `transient`

### `RelationshipMemoryAction`

Define la acción de política:

- `remember`: conservar como memoria relacional.
- `review`: requiere más contexto futuro.
- `ignore`: no es estable para convivencia.

### `RelationshipMemoryRecord`

Entrada auditable de memoria de convivencia. Incluye contenido, tipo, confianza, razón, etiquetas, origen, fecha e ID.

### `RelationshipMemoryCandidate`

Candidato previo al registro. Permite separar detección, decisión y almacenamiento.

### `RelationshipMemorySnapshot`

Vista del estado relacional actual. Expone:

- familiaridad;
- confianza relacional;
- continuidad;
- registros conservados;
- candidatos revisados o ignorados;
- presencia M51 asociada.

### `RelationshipMemoryPolicy`

Política pura basada en umbrales configurables. Decide si un candidato se recuerda, se revisa o se ignora.

### `RelationshipMemoryEngine`

Motor determinístico. Detecta patrones de convivencia sin efectos secundarios.

### `RelationshipMemoryManager`

Fachada estable para consumir M52 desde el pipeline y desde futuras capas de convivencia.

## Integración con M51

Cuando existe `PresenceManager`, el pipeline primero actualiza M51 y luego entrega el snapshot de presencia a M52.

```text
Usuario
  -> CognitivePipeline
  -> M50 CognitiveCycle
  -> M51 PresenceManager
  -> M52 RelationshipMemoryManager
  -> Prompt del sistema enriquecido
```

## Garantías

- Sin refactor destructivo.
- Sin dependencia obligatoria de M51.
- Sin persistencia concreta acoplada.
- Sin iniciativa autónoma.
- Salida auditable mediante `to_dict()` y `system_prompt_lines()`.
- Compatible con todos los milestones previos.

## Pruebas

Se agrega `tests/test_m52_relationship_memory.py`, cubriendo:

- validación de contratos;
- política de umbrales;
- registro de preferencias/ritmo de proyecto;
- revisión de patrones débiles;
- descarte de contexto transitorio;
- acumulación con presencia M51;
- serialización auditable;
- integración opcional con `CognitivePipeline`.
