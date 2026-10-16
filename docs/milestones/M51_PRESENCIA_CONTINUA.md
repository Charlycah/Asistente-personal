# M51 — Presencia continua

## Propósito

M51 inaugura la FASE V — Convivencia. Su objetivo no es que ROBY responda mejor a un turno aislado, sino que pueda sostener una presencia continua, observable y regulada junto al usuario.

M51 se construye sobre M50. No reemplaza el ciclo cognitivo, no modifica sus fases y no introduce autonomía invasiva. La presencia consume señales del ciclo ya ejecutado y las transforma en un estado de convivencia.

## Regla arquitectónica

- M50 sigue siendo el núcleo cognitivo.
- M51 es una capa superior de convivencia.
- La presencia es opcional dentro del `CognitivePipeline`.
- Ningún contrato público previo queda roto.
- La presencia no llama al LLM, no ejecuta herramientas y no inicia acciones externas.

## Componentes

### `PresenceSignal`

Señal mínima y auditable. Puede representar:

- turno del usuario;
- ciclo M50 completado;
- ciclo M50 parcial;
- silencio contextual;
- reinicio de continuidad.

### `PresenceSnapshot`

Estado observable de presencia continua. Incluye:

- modo de presencia;
- puntuación de continuidad;
- última interacción del usuario;
- ciclo cognitivo asociado;
- señales usadas para calcular el estado.

### `PresencePolicy`

Política pura que decide el modo de presencia a partir de umbrales configurables.

### `PresenceEngine`

Motor determinístico de evaluación. No tiene efectos secundarios ni dependencia de UI, almacenamiento, voz, red o LLM.

### `PresenceManager`

Fachada estable para consumir M51 desde el pipeline y desde futuras capas de convivencia.

## Modos

- `dormant`: sin continuidad reciente.
- `recovering`: ROBY detectó interacción, pero la continuidad todavía es baja.
- `available`: ROBY está disponible de forma estable.
- `attentive`: ROBY está atento al vínculo actual.
- `accompanying`: ROBY sostiene acompañamiento continuo.

## Integración con M50

Cuando existe un `CognitiveCycleManager`, el pipeline conserva el flujo M50 y luego informa a M51 el resultado del ciclo. M51 registra la presencia asociando el snapshot al `cycle_id` de M50.

```text
Usuario
  -> CognitivePipeline
  -> M50 CognitiveCycle
  -> M51 PresenceManager
  -> Prompt del sistema enriquecido
```

## Garantías

- Sin refactor destructivo.
- Sin acoplamiento a interfaces concretas.
- Sin iniciativa no solicitada.
- Sin dependencia obligatoria del ciclo M50.
- Salida auditable mediante `to_dict()` y `system_prompt_lines()`.

## Pruebas

Se agrega `tests/test_m51_presence.py`, cubriendo:

- validación de contratos;
- política de umbrales;
- actualización por turno de usuario;
- continuidad vinculada a ciclo M50 completado;
- silencio sin acción autónoma;
- serialización auditable;
- integración opcional con `CognitivePipeline`.
