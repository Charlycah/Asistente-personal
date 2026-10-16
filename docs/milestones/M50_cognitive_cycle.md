# M50 — ROBY Cognitive Cycle (Phase IV.10)

## Propósito

M50 cierra la Fase IV integrando las capacidades cognitivas desarrolladas entre
M41 y M49 en un ciclo explícito, auditable y no invasivo.

ROBY ya no posee solamente módulos cognitivos aislados. Ahora puede ejecutar una
secuencia organizada:

1. identidad,
2. estado mental,
3. atención,
4. memoria de trabajo,
5. razonamiento,
6. planificación,
7. conocimiento externo,
8. aprendizaje,
9. reflexión,
10. cierre del ciclo.

## Principio arquitectónico

El ciclo cognitivo no reemplaza la Arquitectura 1.0 ni el Cognitive Pipeline.
Actúa como una capa de orquestación superior. Cada módulo conserva su contrato,
su responsabilidad y sus pruebas.

> ROBY no piensa porque una sola clase haga todo. ROBY piensa porque sus
> capacidades cognitivas cooperan en un orden estable.

## Componentes

- `CognitiveCyclePhase`
- `CognitiveCycleStatus`
- `CognitiveCycleStep`
- `CognitiveCycleContext`
- `CognitiveCycleResult`
- `CognitiveCycleEngine`
- `CognitiveCycleManager`

## Integración

`CognitivePipeline` acepta ahora un `CognitiveCycleManager` opcional. Si está
presente, el pipeline delega la ejecución de M41–M49 al ciclo M50. Si no está
presente, mantiene el comportamiento anterior para preservar compatibilidad.

## Criterios de validación

- El ciclo completo ejecuta atención, memoria de trabajo, razonamiento,
  planificación, aprendizaje y reflexión.
- El resultado expone fases ejecutadas, estado, objetos cognitivos producidos y
  serialización auditable.
- La integración con `CognitivePipeline` es opcional y no rompe pruebas previas.
- El system prompt puede recibir un resumen del último ciclo.

## Hito histórico

**Today ROBY completed its first continuous cognitive cycle.**

Con M50, ROBY completa la primera base cognitiva funcional de la Fase IV.
