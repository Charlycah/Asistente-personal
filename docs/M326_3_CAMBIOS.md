# ROBY XI.2 M326.3 — Action Candidate Generator

## Alcance

M326.3 agrega una capa determinista que transforma una `DecisionSituation` en
una lista ordenada de `ActionCandidate` declarativos.

## Componentes

- `ActionTemplate`
- `CandidateRule`
- `CandidateGenerationStatus`
- `CandidateGenerationResult`
- `ActionCandidateGenerator`
- `DeterministicActionCandidateGenerator`
- `default_candidate_rules()`

## Garantías

- No evalúa riesgo ni confianza de acciones.
- No decide, autoriza ni ejecuta acciones.
- Conserva trazabilidad mediante `situation_id`, `candidate_rule_id` y orden.
- Los identificadores de candidatos son deterministas.
- Situaciones desconocidas producen `unsupported`.
- Cada regla incluye una alternativa explícita `do_nothing`.
