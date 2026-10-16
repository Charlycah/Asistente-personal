# M53 — Iniciativa Controlada

## Propósito

M53 extiende la FASE V — Convivencia para que ROBY pueda evaluar cuándo conviene intervenir, cuándo esperar, cuándo hacer una pregunta mínima y cuándo proponer el siguiente paso.

No introduce autonomía invasiva. No ejecuta acciones externas, no agenda tareas, no llama herramientas, no consulta LLM y no reemplaza el ciclo cognitivo M50. Su responsabilidad es producir una recomendación conversacional auditable para capas superiores.

## Regla arquitectónica

- M50 sigue siendo el núcleo cognitivo.
- M51 aporta presencia continua.
- M52 aporta memoria relacional de convivencia.
- M53 consume M51 y M52 para regular iniciativa.
- La iniciativa es opcional dentro del `CognitivePipeline`.
- La iniciativa propone o pregunta; nunca ejecuta por sí misma.
- Los límites explícitos del usuario tienen prioridad sobre cualquier iniciativa.
- Ningún contrato público previo queda roto.

## Componentes

### `InitiativeKind`

Clasifica la iniciativa considerada:

- `none`
- `wait`
- `ask_clarification`
- `offer_next_step`
- `suggest_routine`
- `protect_boundary`

### `InitiativeDecision`

Expone la decisión final:

- `suppress`
- `wait`
- `propose`
- `ask`

### `InitiativeCandidate`

Representa una posible iniciativa antes de aplicar contención relacional. Incluye tipo, confianza, razón, mensaje sugerido y fuente.

### `InitiativeSnapshot`

Resultado auditable del turno. Registra decisión, candidato, intervención sugerida si corresponde, motivo de contención y vínculos con snapshots de M51 y M52.

### `InitiativePolicy`

Define umbrales de propuesta, pregunta, confianza mínima y continuidad mínima. Mantiene la decisión determinística y testeable.

### `InitiativeEngine`

Motor puro de evaluación. Detecta señales de continuidad de proyecto, rutina de trabajo, ambigüedad y límites explícitos.

### `InitiativeManager`

Fachada estable de M53. Conserva historial en memoria de proceso y expone líneas de prompt del último snapshot.

## Integración con `CognitivePipeline`

`CognitivePipeline` acepta ahora un `initiative: InitiativeManager | None` opcional.

Flujo integrado:

```text
M50 Cognitive Cycle
        ↓
M51 Presence
        ↓
M52 Relationship Memory
        ↓
M53 Controlled Initiative
        ↓
System Prompt / capa superior
```

Si M53 no está configurado, el pipeline conserva el comportamiento anterior.

## Garantías

- No rompe M50, M51 ni M52.
- No altera memoria cognitiva M36-M39.
- No persiste datos por sí mismo.
- No ejecuta acciones externas.
- Respeta límites explícitos.
- Mantiene auditoría por snapshots.
- Es determinístico y testeable.

## Pruebas

Se agrega:

- `tests/test_m53_controlled_initiative.py`

Cobertura principal:

- validación de contratos;
- orden de umbrales de política;
- propuesta de siguiente paso con contexto suficiente;
- supresión cuando falta confianza relacional;
- respeto de límites explícitos;
- historial auditable del manager;
- snapshots inconsistentes rechazados;
- integración completa en `CognitivePipeline` junto a M50/M51/M52.

## Estado

Validado localmente con:

```bash
pytest
```

Resultado esperado:

```text
588 passed
```
