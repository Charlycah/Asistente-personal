# M97 — Longitudinal Conversation Continuity

## Objetivo
Dar a ROBY una continuidad conversacional explícita y gobernada a lo largo del tiempo, conservando temas, episodios y procedencia, y proponiendo una reanudación solamente cuando sea vigente, novedosa, privada y prudente.

## Alcance
- Episodios conversacionales inmutables y trazables.
- Hilos longitudinales por propietario y tema.
- Estados `open`, `dormant`, `resolved` y `closed`.
- Historia cronológica acotada.
- Distancia mínima y máxima de reanudación.
- Presupuesto máximo de reanudaciones por hilo.
- Prevención de episodios duplicados o semánticamente repetidos.
- Evaluaciones `resume`, `hold`, `do_not_resume`, `review_required` y `already_proposed`.
- Conversión segura a una oportunidad M93 de tipo `resume`.
- Repositorios en memoria mediante contratos.

## Contratos principales
- `ConversationEpisode`
- `ConversationThread`
- `LongitudinalContinuityPolicy`
- `ContinuityAssessment`
- `ConversationThreadRepository`
- `ContinuityAssessmentRepository`
- `LongitudinalConversationContinuity`

## Invariantes
1. Todo episodio conserva propietario, tema, resumen, fecha y al menos una fuente.
2. Los episodios de un hilo son únicos, compatibles y cronológicos.
3. Un hilo resuelto o cerrado no recibe nuevos episodios ni se retoma.
4. Un episodio idéntico o con el mismo contenido normalizado no se vuelve a registrar consecutivamente.
5. La reanudación exige distancia temporal suficiente y vigencia.
6. Un mismo episodio no produce dos oportunidades de reanudación.
7. Ausencia, invitados y `do_not_disturb` producen espera; un contexto sensible exige revisión.
8. La oportunidad de continuidad conserva exclusivamente el contenido y las fuentes del episodio más reciente.
9. M97 no decide intervención final, no genera lenguaje, no habla y no agenda.
10. Toda oportunidad M97 debe atravesar M93, M95 y M96.

## Integración

```text
Episodios y fuentes
        ↓
M97 mantiene el hilo y propone `resume`
        ↓
M93 gobierna
        ↓
M95 valida la ventana
        ↓
M96 compone el borrador
```

## Fuera de alcance
- Persistencia SQLite o remota.
- Resolución semántica mediante embeddings o LLM.
- Entrega por texto o voz.
- Scheduling o timers.
- Aprendizaje automático desde reacciones.
- Mutación de M52, M72, M74 o M85.

## Criterios de aceptación
- API pública desde `core.living_conversation`.
- Registros deterministas, inmutables y trazables.
- Prevención explícita de repetición.
- Compatibilidad completa con M1–M96.
- Ruff limpio y suite completa sin regresiones.
