# ROBY XI.2 — INTEL-G8 — Source-neutral materialization → existing memory write adapter — CONTRACT RED

## Estado

CONTRACT RED. Baseline de entrada: G8 corrective structural-reasoning GREEN certificado,
14.108 PASS, Ruff clean, 0 FAIL, 0 regressions.

## Propósito

Congelar la única generalización permitida después de G8: una propuesta durable
source-neutral ya aprobada y estructuralmente elegible debe poder ser admitida por el
`GovernedMemoryWriteAdapterFoundation` existente y producir únicamente un
`GovernedMemoryWriteRequest` inerte.

## Autoridad

No se crea adapter, writer, manager, gateway ni authority nuevos. La autoridad de adaptación
sigue siendo `GovernedMemoryWriteAdapterFoundation`. La autoridad de escritura futura sigue
siendo `OfficialMemoryGateway`, pero este gate no la invoca.

## Contrato source-neutral

Para `LearningCategory.STABLE_KNOWLEDGE`, una propuesta G8 válida conserva:

- `learning_candidate_id` exacto;
- `policy_candidate_id` exacto;
- `preference_candidate_id == ""`;
- evidencia estructural gobernada exacta;
- alcance durable explícito;
- fingerprints G6/G7 y evidencia M369 exactos.

El adapter debe admitir esa genealogía sin fabricar `PreferenceCandidate`,
`preference_candidate_id` ni `CuriosityLearningKind.PREFERENCE` como provenance.
La metadata source-neutral debe conservar `policy_candidate_id` y la categoría canónica
`stable_knowledge`.

## Compatibilidad histórica

Las propuestas históricas de preferencia continúan usando `preference_candidate_id` y
`learning_kind` sin regresión. La generalización es backward-compatible y no reescribe
historia.

## STOP

El resultado máximo de este gate es un `GovernedMemoryWriteRequest` con las garantías
inertes ya existentes. Queda prohibido:

- invocar `OfficialMemoryGateway`;
- persistir Memory;
- llamar runtime productivo;
- crear un writer paralelo;
- crear un adapter G8 paralelo;
- fabricar provenance Preference/Curiosity;
- convertir WRITE REQUEST en PERSISTED MEMORY.

`MATERIALIZATION PROPOSAL != WRITE REQUEST != PERSISTED MEMORY`.

## RED esperado

Cinco fallos contractuales intencionales deben demostrar que el adapter histórico todavía
exige `preference_candidate_id` y serializa metadata histórica de forma incondicional.
No se modifica código productivo en CONTRACT RED.
