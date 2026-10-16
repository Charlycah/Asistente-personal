# M46 — ROBY Planning (Phase IV.6)

## Propósito

M46 introduce la planificación cognitiva de ROBY: la capacidad de convertir un
objetivo o una decisión razonada en un plan estructurado, auditable y preparado
para ejecución futura.

ROBY no ejecuta impulsivamente. Primero identifica el objetivo, reúne contexto,
considera la atención activa, usa memoria de trabajo, toma en cuenta el
razonamiento previo y construye un camino posible.

## Principio arquitectónico

La planificación vive por encima de la Arquitectura 1.0. No reemplaza runtime,
recordatorios, memoria ni herramientas. Los coordina de manera cognitiva.

Cadena actual de Fase IV:

```text
M41 Identity
  ↓
M42 Mental State
  ↓
M43 Attention
  ↓
M44 Working Memory
  ↓
M45 Reasoning
  ↓
M46 Planning
```

## Componentes

### PlanGoal

Representa el objetivo que ROBY intenta alcanzar.

### PlanStep

Representa una acción dentro del camino, con prioridad, estado y dependencias.

### PlanningContext

Agrupa las fuentes cognitivas disponibles:

- identidad;
- estado mental;
- atención;
- memoria de trabajo;
- razonamiento previo;
- propietario del objetivo.

### Plan

Resultado estructurado de planificación. Incluye objetivo, pasos, estado,
fundamento, progreso y próximo paso posible.

### PlanningEngine

Motor determinístico inicial. Genera planes básicos y auditables sin depender de
un modelo externo.

### PlanningManager

Fachada de integración para exponer el último plan al Cognitive Pipeline y
permitir ciclo de vida: activar, pausar, completar y cancelar.

## Integración con CognitivePipeline

M46 se integra de forma opcional. Si se inyecta un `PlanningManager`, el pipeline
construye un plan a partir del turno actual y añade el plan al system prompt.

Esto permite que un LLM, cuando exista, redacte mejor sobre una planificación que
pertenece a ROBY. El modelo externo no sustituye el planificador.

## Filosofía

> ROBY no ejecuta tareas inmediatamente. Primero construye un plan que refleje el
> mejor camino conocido para alcanzar un objetivo, respetando su identidad, el
> contexto, las prioridades y las necesidades de Carlos y Cristina.

## Validación esperada

- Nuevas pruebas: `tests/test_m46_planning.py`.
- Regresión completa en verde.
- Integración no invasiva con M41–M45.

## Hito histórico

Today ROBY learned to turn intention into a plan.
