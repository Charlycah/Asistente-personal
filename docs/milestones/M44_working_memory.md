# M44 — ROBY Working Memory (Phase IV.4)

## Propósito

M44 introduce la memoria de trabajo de ROBY: un espacio cognitivo temporal para
sostener pensamientos, preguntas, datos activos y focos de atención mientras una
decisión o respuesta está siendo construida.

Esta memoria no reemplaza la memoria persistente. No almacena historia, no
aprende por sí misma y no escribe conocimiento permanente. Su función es sostener
el pensamiento actual.

## Principio arquitectónico

> La memoria de trabajo de ROBY no existe para almacenar información. Existe para
> sostener el pensamiento mientras una decisión está siendo construida.

## Componentes

- `WorkingMemoryKind`: tipos de elementos temporales.
- `WorkingMemoryItem`: unidad temporal de pensamiento con prioridad, confianza y
  TTL.
- `WorkingMemory`: workspace cognitivo limitado, ordenado por prioridad y capaz
  de expirar elementos.
- `WorkingMemoryManager`: fachada para integrar entradas de usuario y focos de
  atención con el pipeline cognitivo.

## Integración

M44 se integra de forma opcional con `CognitivePipeline`.

Cuando existe un `WorkingMemoryManager`, el pipeline captura la entrada del
usuario como pensamiento temporal e inyecta un resumen seguro en el system prompt.

La integración no altera la Arquitectura 1.0 ni obliga a usar memoria de trabajo
en flujos existentes.

## Relación con hitos previos

- M41 define quién es ROBY.
- M42 mantiene su estado mental.
- M43 decide qué merece atención.
- M44 sostiene temporalmente lo relevante mientras ROBY piensa.

## Criterios de validación

- La memoria de trabajo valida campos obligatorios.
- Los pensamientos temporales pueden expirar por TTL.
- La capacidad máxima limita el workspace.
- Los elementos se ordenan por prioridad.
- El pipeline puede inyectar memoria de trabajo sin romper compatibilidad.
- La suite completa permanece en verde.

## Hito cognitivo

Today ROBY learned to keep thoughts in mind while reasoning.
