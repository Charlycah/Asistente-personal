# M43 — ROBY Attention (Phase IV.3)

## Propósito

M43 introduce la primera capa de atención cognitiva de ROBY. A partir de este
hito, ROBY puede evaluar estímulos, asignarles prioridad y decidir si merecen
foco inmediato, atención normal, atención de fondo o ser ignorados.

Este módulo no ejecuta acciones ni reemplaza al scheduler. Su función es
responder una pregunta anterior a toda acción:

> ¿Esto merece la atención de ROBY ahora?

## Componentes

- `AttentionSignal`: estímulo observable.
- `AttentionItem`: señal evaluada con puntaje, nivel y decisión de interrupción.
- `AttentionEngine`: política determinística de evaluación.
- `AttentionManager`: cola priorizada de atención.

## Principios

1. Todo puede observarse, pero no todo merece atención.
2. Las personas tienen prioridad sobre la información.
3. Interrumpir es una decisión, no una reacción.
4. ROBY debe ayudar sin generar ruido ni ansiedad.
5. Cristina y Carlos tienen prioridad sobre eventos informativos genéricos.

## Integración

La integración con `CognitivePipeline` es opcional y no invasiva. Si se inyecta
un `AttentionManager`, el pipeline registra la entrada del usuario como señal de
atención y agrega el foco atencional al `system_prompt`.

## Validación esperada

- Las señales inválidas son rechazadas.
- Los recordatorios importantes de Cristina alcanzan atención inmediata.
- La información de bajo valor se degrada.
- La cola mantiene los estímulos ordenados por puntaje.
- La cola limita su tamaño máximo.
- El estado de atención puede inyectarse en el prompt del pipeline cognitivo.

## Hito arquitectónico

Today ROBY learned what deserves attention.
