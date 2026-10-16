# ROBY XI.2 — GATE 5.C.2.1 — SURGICAL GREEN

## Explicit Exact Investigation Scope → UnifiedRuntimeObservability Immutable Episode/Budget Projection

### Certified RED entry

GATE 5.C.2.1 CONTRACT RED was certified locally by the user as:
**14,046 PASS + 7 intentional RED failures · Ruff clean · no lateral failures**.

## Productive change

Only `app/unified_runtime_observability.py` changes productively.

Added frozen value object `InvestigationEpisodeBudgetObservabilityScope` with exactly:
- `owner`
- `session_id`
- `turn_id`

Added optional `investigation_scope=` to `UnifiedRuntimeObservability.snapshot(...)`.

Added optional frozen snapshot field `investigation_episode_budget`.

When and only when explicit scope and the canonical governed reasoning runtime are both present, observability delegates once to:

`runtime.root.dependencies.governed_reasoning_runtime.investigation_episode_budget_introspection(...)`

and publishes the exact returned `GovernedInvestigationEpisodeBudgetIntrospectionView`.

## Semantics

- no explicit scope → `None`;
- reasoning runtime not provisioned → `None`;
- no exact canonical episode → `None`;
- present exact episode → exact owner-level frozen view;
- no scope inference;
- no latest-episode selection;
- no private-store scan;
- no global budget;
- no cross-domain episode fusion.

## Preserved boundaries

`app/official_conversation_gateway.py` remains byte-identical. Analysis Mode is not changed.
`app/governed_reasoning_runtime.py` remains byte-identical; GATE 5.C.1 owner authority is reused.
`.roby/config.json` remains byte-identical.
No new manager, registry, graph, runtime, authority, persistence, Memory/Learning, Planning N+1, G5-R3d, G5-R3e or G5-R4 is opened.

Historical byte guards were re-anchored only where the now-legitimate observability change made the old byte hash obsolete. The GATE 5.C.1 owner-scope guard was narrowed from forbidding any unified publication to forbidding private reasoning-store access; Analysis Mode remains forbidden from this projection.

## Productive hashes

- `app/unified_runtime_observability.py`: `970b141c6db77477b74473f128042c24235637ae06a876e2ff07e00dea88676a`
- `app/official_conversation_gateway.py`: `737ba00cb82cf58dd890876996af52d74b9efad57e11641ebb5918671567b9c9`
- `app/governed_reasoning_runtime.py`: `26a9f4f6c1fb629f857f5b2943b9d80a56edc641ba38a730e900317704e008ba`
- `.roby/config.json`: `11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5`

## Assistant targeted validation

GATE 5.C.2.1 + GATE 5.C.1 protection + GATE 5.B.4.1 protection + M361 reproducibility:
**32 PASS · 0 FAIL**.

Full-suite and Ruff certification remain the user's local certification step.
