# RP.18.3 — Integración oficial del núcleo RP.10–RP.18

## Objetivo

Integrar el núcleo cognitivo residente desarrollado entre RP.10 y RP.18 en la
raíz oficial de ejecución, sin crear lifecycles paralelos ni registrar cada
servicio interno como si fuera un proceso independiente.

## Decisión arquitectónica

`CognitiveCoreRuntime` es la frontera residente única del núcleo cognitivo.
Delega `start()` y `stop()` a `ContinuousInternalCognitiveLoop`, que ya posee el
hilo y el ciclo real, y expone referencias inmutables a los nueve subsistemas:

- RP.10 Continuous Internal Cognitive Loop
- RP.11 Cognitive Agenda Manager
- RP.12 Cognitive Agenda Reasoning
- RP.13 Cognitive Reflection Engine
- RP.14 Cognitive Thought Stream
- RP.15 Cognitive Hypothesis Workspace
- RP.16 Cognitive World Model
- RP.17 Cognitive Episodic Memory
- RP.18 Cognitive Self Model

## Integración oficial

El runtime de escritorio registra el núcleo con el identificador canónico
`cognitive_core_runtime`. El identificador anterior
`continuous_cognitive_loop` deja de representar un residente separado.

## Límites

Esta etapa no modifica la ruta conversacional, la ruta general de capacidades
ni la observabilidad global. Tampoco introduce recuperación automática. Esas
responsabilidades pertenecen a los pasos posteriores del roadmap.
