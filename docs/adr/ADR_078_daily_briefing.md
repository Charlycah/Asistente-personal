# ADR-078 — Daily Briefing gobernado

## Estado
Aceptado para M76.

## Contexto
ROBY dispone de memoria doméstica, documentos, conocimiento y tareas, pero necesita
una vista diaria breve que reduzca carga cognitiva sin transformar información en
ejecución autónoma.

## Decisión
Introducir `DailyBriefingManager` como compositor determinista y de solo lectura.
El módulo agrega señales de M72–M75, prioriza urgencias, conserva referencias y
produce texto en español. Scope Guard valida el dominio antes de generar el resumen.

## Consecuencias
- ROBY puede ofrecer resúmenes matutinos, vespertinos o bajo demanda.
- El briefing nunca compra, paga, envía ni ejecuta acciones externas.
- Los elementos mantienen fuente, severidad y referencia auditable.
- La entrega automática queda fuera de M76 y podrá añadirse con Scheduler.
