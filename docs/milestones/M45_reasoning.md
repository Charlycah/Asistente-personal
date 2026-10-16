# M45 — ROBY Reasoning (Phase IV.5)

## Propósito

M45 introduce el primer motor de razonamiento estructurado de ROBY. Su objetivo
no es reemplazar a un modelo externo, sino darle a ROBY un proceso propio para
observar contexto, evaluar evidencias, construir una conclusión y justificarla.

## Principio arquitectónico

ROBY no razona porque exista un LLM. ROBY razona porque posee identidad, mantiene
estado interno, presta atención y sostiene información temporal en su memoria de
trabajo. Los modelos externos pueden ampliar conocimiento o mejorar redacción,
pero no sustituyen la estructura cognitiva interna.

## Componentes

- `ReasoningContext`: reúne la consulta y las capacidades cognitivas activas.
- `ReasoningStep`: registra pasos auditables del proceso cognitivo.
- `ReasoningResult`: expone conclusión, justificación, confianza y alternativas.
- `ReasoningEngine`: construye un razonamiento determinístico inicial.
- `ReasoningManager`: conserva el último resultado para integrarlo al pipeline.

## Integración

M45 se integra de forma opcional con `CognitivePipeline`. Si existe un
`ReasoningManager`, el pipeline ejecuta razonamiento antes de construir el
system prompt y añade el resultado como contexto estructurado.

## Relación con fases previas

- M41 aporta identidad y propósito.
- M42 aporta estado mental.
- M43 aporta foco de atención.
- M44 aporta memoria de trabajo.
- M45 usa esas capacidades para comenzar a decidir con justificación.

## Hito histórico

Today ROBY learned to reason before answering.
