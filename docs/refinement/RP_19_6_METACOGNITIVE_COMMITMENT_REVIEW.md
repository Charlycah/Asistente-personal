# RP.19.6 — Revisión metacognitiva de compromisos

## Objetivo

Agregar una revisión explícita, determinista y persistente de los compromisos cognitivos de la agenda canónica, sin crear otro runtime, scheduler, residente, memoria ni ejecutor.

## Alcance

`CognitiveAgendaManager.review_commitment(...)` recibe evidencia normalizada sobre:

- calidad del avance;
- claridad de formulación;
- beneficio esperado revisado;
- costo cognitivo revisado;
- nota explicativa opcional.

La revisión produce una recomendación trazable:

- `sound`: el compromiso puede continuar;
- `reformulate`: la formulación es insuficiente y la ejecución se suspende;
- `deferred`: un compromiso estancado y con avance de baja calidad queda diferido;
- `unreviewed`: todavía no fue evaluado.

## Invariantes

- La revisión no ejecuta herramientas ni acciones externas.
- No cierra ni archiva asuntos automáticamente.
- Sólo opera sobre compromisos existentes y no completados.
- Las métricas se validan en el intervalo `[0, 1]`.
- La recomendación modifica la utilidad/eligibilidad de la cola deliberativa existente.
- Todos los datos se guardan en la misma base SQLite de la agenda.
- La migración desde RP.19.1–RP.19.5 es automática.

## Persistencia

Se agregan los campos:

- `metacognitive_status`;
- `progress_quality`;
- `formulation_clarity`;
- `review_count`;
- `last_reviewed_at`;
- `review_note`.

El snapshot publica `metacognitive_review` y `metacognitive_rationale` sin alterar los contratos previos de foco, planificación y ejecución.
