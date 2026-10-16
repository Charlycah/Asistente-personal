# ROBY XI.2 — GATE 5.C.1 — SURGICAL GREEN

## Official Governed Reasoning Runtime Canonical Investigation Episode/Budget State → Scoped Immutable Read-Only Introspection View

### Entrada certificada

- GATE 5.C.1 CONTRACT RED: certified by the user.
- Local RED result: 14.039 PASS + 4 intentional RED failures.
- Ruff clean after import hygiene fix.
- No lateral failures.

## Productive change

Only `app/governed_reasoning_runtime.py` changes productively.

It adds:

- frozen `GovernedInvestigationEpisodeBudgetIntrospectionView`;
- `OfficialGovernedReasoningRuntimeGateway.investigation_episode_budget_introspection(...)`.

The method requires exact `owner`, `session_id`, and `turn_id`, reuses the
existing `productive_explanatory_investigation_reentry(...)` read path, and
projects only the already-retained canonical `episode_state`.

### Preserved semantics

The view copies exactly:

- episode id;
- originating reasoning id;
- source reference;
- world snapshot id;
- requirement/plan/authorization/execution/local execution/reentry lineage;
- consumed acquisitions;
- max acquisitions;
- remaining acquisitions;
- current step;
- status;
- stopping reason.

Missing exact scope or missing canonical episode state returns `None`.

## Authority boundary

This GREEN does not:

- create EpisodeRegistry or BudgetManager;
- expose private stores;
- calculate a global budget;
- scan or merge unrelated episode families;
- execute Reasoning, Planning, Authorization, Execution, Reflection,
  Memory or Learning;
- modify UnifiedRuntimeObservability;
- modify Analysis Mode;
- open versions, certifications/quality, or G5-R4;
- modify `.roby/config.json`.

### Important bounded meaning

This view exposes the canonical investigation episode state that is already
retained by `OfficialGovernedReasoningRuntimeGateway` for the exact productive
turn. It does not claim to synthesize later transition state held by other
productive contributors. A later gate must reconcile that publication boundary
before any broader "latest active episode" claim is made.

## RED closure

The four intentional RED failures are closed by the new owner-level method and
frozen read-model type. The historical gateway byte-protection hash is
re-anchored to the post-GREEN candidate; the guard is preserved, not removed.

## STOP

No automatic publication into UnifiedRuntimeObservability or Analysis Mode.
