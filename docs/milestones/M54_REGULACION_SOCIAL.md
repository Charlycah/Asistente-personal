# M54 — Regulación Social

## Estado

Cerrado sobre la base oficial M53.

## Propósito

M54 extiende la FASE V — Convivencia para que ROBY pueda regular el tono, la distancia social y la forma de intervenir antes de producir una respuesta.

No reemplaza M50, M51, M52 ni M53. Consume sus señales para generar una guía social auditable: cuándo reconocer, cuándo reparar, cuándo respetar un límite, cuándo reducir iniciativa y cuándo confirmar un siguiente paso.

## Principios

- La regulación social no ejecuta acciones externas.
- No modifica memoria persistente.
- No toma decisiones de razonamiento general.
- No sustituye la iniciativa controlada.
- Solo produce guía social para capas superiores.
- Mantiene compatibilidad hacia atrás si no se configura en el pipeline.

## Componentes

### `SocialTone`

Enum de tonos sociales recomendados:

- `neutral`
- `careful`
- `supportive`
- `boundary_respecting`
- `repairing`

### `SocialDistance`

Enum de distancia relacional:

- `reserved`
- `balanced`
- `familiar`

### `SocialRegulationAction`

Enum de acción regulatoria:

- `none`
- `acknowledge`
- `respect_boundary`
- `reduce_initiative`
- `repair_trust`
- `confirm_next_step`

### `SocialRegulationPolicy`

Política determinística de umbrales para confianza, continuidad y familiaridad.

### `SocialRegulationSnapshot`

Resultado auditable del turno. Registra tono, distancia, acción, confianza, motivo, guía social y vínculos con snapshots de M51, M52 y M53.

### `SocialRegulationEngine`

Motor puro de M54. Evalúa el texto del usuario y el contexto de convivencia para generar una regulación social.

### `SocialRegulationManager`

Fachada estable de M54. Conserva historial en memoria de proceso y expone líneas de prompt del último snapshot.

## Integración con el pipeline

Cuando se configura `SocialRegulationManager`, `CognitivePipeline` ejecuta la secuencia:

```text
M50 Cognitive Cycle
  -> M51 Presence
  -> M52 Relationship Memory
  -> M53 Controlled Initiative
  -> M54 Social Regulation
  -> Memory Integration
  -> Prompt Builder
  -> LLM Service opcional
```

Si M54 no está configurado, el pipeline conserva el comportamiento anterior.

## Garantías de compatibilidad

- No rompe M50, M51, M52 ni M53.
- No cambia contratos obligatorios del pipeline.
- La integración es opcional.
- Los snapshots son inmutables y serializables.
- El prompt sistémico incorpora la regulación solo cuando existe manager configurado.

## Pruebas

Archivo agregado:

- `tests/test_m54_social_regulation.py`

Cobertura principal:

- validación de política;
- validación de contrato de snapshot;
- respeto de límites explícitos;
- reparación ante señales de error;
- confirmación de siguiente paso cuando M53 autoriza iniciativa;
- historial auditable del manager;
- rechazo de timestamps naive;
- integración completa en `CognitivePipeline` junto a M50/M51/M52/M53.

## Resultado

M54 queda cerrado como capa de regulación social de convivencia. ROBY ahora puede modular cómo responde socialmente antes de ejecutar una respuesta, apoyándose en presencia, memoria relacional e iniciativa controlada.
