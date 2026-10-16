# ADR-137: Ambient Observation Resolution

## Status
Accepted

## Decision
M135 introduces a provider-neutral resolution boundary over the governed `AmbientContext` produced by M134. It selects one declarative ambient representation for a declared purpose while preserving ownership, observation lineage, confidence governance, provenance policy, and deterministic behavior.

The milestone may select raw-signal, snapshot, temporal-window, aggregate, or event representations. It only declares which future understanding capability is required. It cannot access sensors, infer presence or activity, analyze acoustics or environmental conditions, infer space, automate systems, or call external providers.

## Consequences
Future ambient interpretation layers receive a stable `ResolvedAmbientObservation` contract without depending on sensor implementations. Ambiguous, absent, weak, external, or lineage-invalid candidates are reviewed or blocked rather than inferred.
