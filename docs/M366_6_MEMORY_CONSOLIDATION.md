# M366.6 — Memory Consolidation

## Propósito

Construir una frontera cognitiva pura que evalúe candidatos episódicos y emita recomendaciones trazables de retención, archivo o consolidación. La consolidación no convierte automáticamente una experiencia en verdad y no escribe en ninguna memoria.

## Autoridades reutilizadas

- `episodic_memory`: fuente canónica de experiencias candidatas.
- `memory_gateway`: autoridad canónica de memoria durable.
- `OfficialMemoryGateway`: única puerta operacional de escritura existente; M366.6 la declara pero no la invoca.

## Decisiones posibles

- `KEEP_EPISODIC`
- `PROPOSE_SEMANTIC`
- `PROPOSE_PROCEDURAL`
- `PROPOSE_LONG_TERM`
- `REQUEST_CONFIRMATION`
- `ARCHIVE_CANDIDATE`

Todas son recomendaciones. Ninguna decisión persiste datos o ejecuta acciones.

## Señales gobernadas

La evaluación determinista puede considerar repetición, relevancia, confianza, intención explícita, estructura procedural, sensibilidad personal y contradicción con recuerdos existentes.

- La contradicción fuerza revisión.
- La memoria personal o sensible exige confirmación.
- La repetición y la relevancia pueden producir una propuesta, nunca una verdad automática.
- La evidencia insuficiente permanece episódica.
- El archivo es una recomendación revisable, no un borrado irreversible.

## Límites

M366.6 no añade stores, migraciones, timers, tareas de fondo, resúmenes automáticos, aprendizaje autónomo ni modificaciones al runtime. Tampoco establece consciencia: aproxima funciones de selección y continuidad de memoria, no experiencia subjetiva.
