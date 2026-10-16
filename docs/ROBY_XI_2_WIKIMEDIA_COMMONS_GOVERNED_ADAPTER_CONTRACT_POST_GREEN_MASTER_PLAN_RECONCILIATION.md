# ROBY XI.2 — Wikimedia Commons Governed Adapter Contract
## Post-GREEN Master Plan Reconciliation

### Owner-certified input
The Surgical GREEN was Owner-certified with:
- 13,550 PASS / 0 FAIL;
- Ruff clean;
- M361 regenerated/reproducible;
- canonical user-corrected RED test integrated.

### Reconciliation result
The adapter seam is internally complete.

Canonical productive adapter:
`app.wikimedia_commons_governed_source.py`

The adapter remains bounded to the already-authorized contract:
- canonical source id `wikimedia_commons`;
- empty topics authorized only by explicit
  `OPEN_VISUAL_SUBJECT_QUERY`;
- existing governed source declaration/classification model;
- read-only HTTPS Wikimedia Commons Action API;
- File namespace;
- result hard bound 20;
- thumbnail width 640;
- configured non-blank User-Agent;
- query timeout propagation;
- bounded response size;
- image/HTTPS preview filtering;
- stable provider identity;
- attribution/license metadata preservation without legal inference;
- malformed provider payload fail-closed behavior.

### Architecture reconciliation
No productive Python file outside the adapter references
`wikimedia_commons` or `WikimediaCommonsGovernedSourceAdapter`.

Therefore the adapter is not yet registered into productive executor
composition and has not silently acquired reachability.

No provider-specific registry, selector, query executor, presenter, retry
manager, background loop, planner, agent, or authority was introduced.

The prerequisite historical guard migration remains semantically valid:
the temporary prohibition against the provider module was removed only
because this seam explicitly authorized that module. Parallel-authority
prohibitions remain.

### Scope boundaries preserved
- `GovernedInformationItem`: unchanged.
- canonical source selector: unchanged.
- canonical query contract/executor: unchanged in this seam.
- external image presentation: unchanged.
- natural-language admission: unchanged.
- freshness ordering: unchanged.
- official conversation gateway: unchanged.
- no registration/reachability implementation is hidden in this seam.

### Verification
Assistant relevant contract run: 66 PASS.

Owner certification remains authoritative for the full project:
13,550 PASS / 0 FAIL, Ruff clean, M361 reproducible.

### Residual classification
Internal residual for the adapter contract:
`NONE`.

Parent provider residual remains exactly:
`WIKIMEDIA_COMMONS_EXISTING_EXECUTOR_REGISTRATION_AND_REACHABILITY`.

This residual is separate from:
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`.

The next block must reconcile the existing executor/composition path before
any RED. It must reuse the canonical `GovernedSourceQueryExecutor`,
`admit_non_default_source`, and existing composition authority rather than
create a Wikimedia-specific registry/executor/selector.

### Formal state
`ADAPTER_CONTRACT: CLOSED / OWNER-CERTIFIED`
`POST_GREEN_RECONCILIATION: COMPLETE`
`ADAPTER_INTERNAL_RESIDUAL: NONE`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`EXECUTOR_REGISTRATION: NOT YET IMPLEMENTED`
`PRODUCTIVE_REACHABILITY: NOT YET IMPLEMENTED`
`PRESENTATION_RESIDUAL: NONE IN THIS SEAM`
`FRESHNESS: SEPARATE / LATER`
`NEW_AUTHORITY: NONE`
`NEXT_RESIDUAL: WIKIMEDIA_COMMONS_EXISTING_EXECUTOR_REGISTRATION_AND_REACHABILITY`
`NEXT_STEP: PRE-RED RECONCILIATION`


## Next residual PRE-RED outcome
Existing executor/query-contract/selector/gateway authorities are sufficient.\nExact registration seam: official runtime composition using governed environment wiring.\nGeneral arbitrary-subject natural-language admission remains separate.\n