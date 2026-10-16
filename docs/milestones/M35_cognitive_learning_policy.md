# M35 — Cognitive Learning Policy

## Objetivo

Iniciar el "cerebro" de ROBY con una capa mínima que decida qué partes de una
conversación merecen convertirse en memoria.

M35 no escribe todavía en una base de datos, no recupera recuerdos y no activa
comentarios proactivos. Su responsabilidad es producir candidatos de aprendizaje
seguros y explícitos para milestones posteriores.

## Alcance

- Clasificar contenido conversacional como:
  - convención del proyecto,
  - preferencia del usuario,
  - conocimiento estable,
  - contexto temporal,
  - ruido.
- Decidir una acción:
  - guardar,
  - omitir,
  - revisar.
- Adjuntar metadata cognitiva de M33 y M34.

## Fuera de alcance

- Persistencia real en DB.
- Recuperación de memoria.
- Proactividad.
- Llamadas LLM.
- Cambios en proveedores.
- Cambios en UI, voz o herramientas.

## Criterios de cierre

- Tests específicos para la política de aprendizaje.
- Suite completa verde.
- Ruff limpio.
- Sin regresiones de M27–M34.

## Resultado

ROBY empieza a distinguir qué vale la pena aprender antes de tener una memoria
cerebral persistente. Esto evita guardar ruido y prepara el camino para una DB
cognitiva controlada.
