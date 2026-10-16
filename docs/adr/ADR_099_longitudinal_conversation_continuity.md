# ADR-099 — Longitudinal Conversation Continuity

## Estado
Aceptado para M97.

## Contexto
M93–M96 permiten gobernar, detectar, temporizar y componer una intervención. Faltaba una frontera explícita para conservar hilos temáticos durante días o meses y decidir si un tema merece retomarse sin repetir la misma propuesta, inventar contexto ni convertir memoria en autoridad de intervención.

## Decisión
Crear `core.living_conversation.continuity` como subsistema determinista de continuidad longitudinal.

La frontera introduce episodios conversacionales con procedencia, hilos por propietario y tema, estados de ciclo de vida, políticas de distancia temporal y presupuesto de reanudaciones, y evaluaciones auditables. Una evaluación apta produce únicamente una `ConversationOpportunity(kind="resume")`, que debe atravesar nuevamente M93, M95 y M96.

## Consecuencias
- La continuidad se representa como historia temática explícita, no como texto libre oculto.
- Cada reanudación conserva las fuentes del episodio más reciente.
- Un mismo episodio no puede proponerse dos veces.
- Los hilos resueltos, cerrados, vencidos o agotados no se reactivan automáticamente.
- Invitados, ausencia, `do_not_disturb` y contexto sensible bloquean o elevan la evaluación.
- M97 no habla, agenda, genera lenguaje, llama al LLM ni muta memorias externas.
