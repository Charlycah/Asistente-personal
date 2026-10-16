# M100 — Conversational Presence Engine

## Objetivo
Convertir una realización M99 en una presencia conversacional explícita, coherente y auditable, definiendo cómo se sitúa ROBY dentro del intercambio sin alterar el texto ni entregarlo.

## Alcance
- Posturas `responsive`, `attentive`, `companionable`, `reflective` y `restrained`.
- Relaciones `direct_reply`, `follow_up`, `continuation` y `spontaneous_entry`.
- Intensidad conversacional gobernada y acotada.
- Reconocimiento del turno previo cuando existe continuidad inmediata.
- Apertura controlada al siguiente turno.
- Asociación opcional con un hilo M97.
- Preservación de texto y fuentes M99.
- Estados `ready`, `abstained` y `review_required`.
- Persistencia mediante contrato y repositorio en memoria.

## Contratos principales
- `ConversationalPresenceStance`
- `ConversationalTurnRelation`
- `ConversationalPresenceStatus`
- `ConversationalPresencePolicy`
- `ConversationalPresenceRequest`
- `ConversationalPresence`
- `ConversationalPresenceRepository`
- `InMemoryConversationalPresenceRepository`
- `ConversationalPresenceEngine`

## Invariantes
1. Toda presencia referencia exactamente una realización M99.
2. El propietario coincide con el propietario gobernado en M93.
3. M100 nunca modifica el texto ni las fuentes de M99.
4. Sólo una realización `ready` puede producir presencia `ready`.
5. `abstained` y `review_required` tienen intensidad cero y no exponen señales de engagement.
6. Las entradas espontáneas respetan un límite de intensidad y requieren fuentes por defecto.
7. Una continuación puede preservar el identificador del hilo M97.
8. La apertura de seguimiento es explícita y gobernable.
9. M100 no reemplaza la presencia cognitiva general de M51.
10. M100 no entrega, habla, selecciona canal, agenda, usa herramientas ni modifica memoria.

## Integración

```text
M93–M98 inteligencia conversacional
              ↓
M99 realización textual neutral al canal
              ↓
M100 postura y presencia dentro del intercambio
              ↓
Futura capa gobernada de presentación/entrega
```

## Fuera de alcance
- Reescritura o generación de texto.
- Prosodia, voz, avatar o animación.
- Selección de dispositivo, canal o superficie.
- Entrega, notificación o scheduling.
- Inferencia de emociones del usuario.
- Mutación de memoria o relación.
- Aprendizaje desde reacciones.

## Criterios de aceptación
- API pública desde `core.living_conversation`.
- Presencias inmutables, deterministas y persistibles.
- Separación explícita respecto de M51 y M99.
- Propagación segura de abstención y revisión.
- Compatibilidad completa con M1–M99.
- Ruff limpio y suite completa sin regresiones.
