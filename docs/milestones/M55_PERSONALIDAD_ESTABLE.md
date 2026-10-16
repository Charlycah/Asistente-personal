# M55 — Personalidad Estable

## Estado

Cerrado como hito de la Fase V — Convivencia.

## Objetivo

M55 incorpora una capa de personalidad estable para que ROBY mantenga una
expresión consistente entre turnos, milestones y contextos sociales, sin
reemplazar el ciclo cognitivo M50 ni las capas de convivencia M51–M54.

La personalidad estable no decide acciones, no invoca herramientas y no muta
memoria externa. Su responsabilidad es modular la expresión visible de ROBY de
forma auditable.

## Componentes

- `core/stable_personality.py`
  - `PersonalityTrait`
  - `PersonalityExpression`
  - `StablePersonalityPolicy`
  - `StablePersonalitySnapshot`
  - `StablePersonalityEngine`
  - `StablePersonalityManager`
- `tests/test_m55_stable_personality.py`
- Integración opcional en `core/cognitive_pipeline.py`

## Contrato arquitectónico

M55 consume señales de:

- M51 — Presencia continua
- M52 — Memoria de convivencia
- M54 — Regulación social

Y produce una guía de personalidad para el prompt sistémico:

- expresión actual
- rasgos activos
- puntaje de consistencia
- motivo auditable
- guía de respuesta

## Rasgos base

La política por defecto conserva estos rasgos estables:

- calma
- precisión
- apoyo
- respeto
- consistencia

Estos rasgos pueden modularse en expresión, pero no se reemplazan según el
estado emocional o social del turno.

## Expresiones soportadas

- `neutral`
- `warm`
- `careful`
- `repairing`
- `direct`

## Garantías

- No rompe compatibilidad hacia atrás.
- No sustituye M54; lo respeta.
- No cambia decisiones de iniciativa.
- No modifica memoria persistente.
- Mantiene historial auditable.
- Expone `system_prompt_lines()` como el resto de la arquitectura cognitiva.

## Validación

Pruebas específicas añadidas:

- contrato de política
- contrato de snapshot
- línea base sin contexto
- reparación social
- respeto de límites
- historial del manager
- rechazo de `datetime` naive
- integración en `CognitivePipeline`

M55 queda integrado como una capa superior de convivencia, acumulativa y no
destructiva, sobre la base M50–M54.
