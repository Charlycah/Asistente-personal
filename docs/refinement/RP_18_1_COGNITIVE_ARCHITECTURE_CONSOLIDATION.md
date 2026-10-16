# RP.18.1 — Cognitive Architecture Consolidation

This refinement consolidates the RP.10–RP.18 continuous cognitive chain before
higher-level metacognition is introduced.

## Authoritative boundary

`app.continuous_internal_cognitive_loop.ContinuousInternalCognitiveLoop` is the
single owner of the resident RP.10–RP.18 state.

Consumers must depend on the read-only
`app.cognitive_state_provider.CognitiveStateProvider` protocol instead of
reaching into individual mutable components.

## Relationship with earlier cognitive subsystems

Earlier modules under `core/` and existing executive runtime modules remain
specialized certified subsystems. They are not deleted because they still have
active consumers and independent contracts. Future refinements must integrate
through adapters rather than create another competing owner.

| Concern | Authority after RP.18.1 |
|---|---|
| Resident RP.10–RP.18 state | `ContinuousInternalCognitiveLoop` |
| Read-only publication | `CognitiveStateProvider` |
| Governed reasoning pipeline | existing `core` runtime contracts |
| Operational execution | official capability registry and routing |
| Permissions and consent | existing governance layers |

## Reliability changes

- thread-safe snapshots through `RLock`;
- real thread liveness reflected by `snapshot.running`;
- explicit `stopped`, `running`, `degraded`, and `failed` statuses;
- last failure summary without storing private reasoning;
- consecutive-failure threshold;
- guaranteed final state update when the resident thread exits;
- immutable `current_state` publication boundary.

## Tree cleanup

- exact duplicate RP.04–RP.07 documents removed from the repository root;
- RP documentation unified under `docs/refinement/`;
- generated caches and bytecode excluded from the certified ZIP;
- historical modules retained only where active imports or tests prove they are
  still part of the certified architecture.
