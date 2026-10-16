# ROBY XI.2 — Wikimedia Commons Existing Executor Registration and Reachability
## Contract RED

### Owner-certified input
Contract Design was Owner-certified at 13,550 PASS / 0 FAIL, Ruff clean,
M361 reproducible.

### RED artifact
Exactly one architecture contract was added:

`tests/architecture/test_wikimedia_commons_existing_executor_registration_and_reachability_contract_red.py`

No productive Python file was changed.

### Contract coverage
The RED encodes the already-authorized design boundaries:
- canonical opt-in environment configuration;
- disabled-by-default behavior;
- fail-closed missing/blank User-Agent;
- canonical adapter construction with explicit User-Agent;
- injected deterministic transport;
- environment builder without registration/execution authority;
- official runtime consumption of the builder;
- registration through the existing gateway public surface;
- existing non-default source admission;
- existing `OPEN_VISUAL_SUBJECT` selector reachability;
- unregistered source remains unavailable;
- open mode/query text/empty topics/limit/timeout preservation;
- selected-query execution reaches the existing executor;
- no provider-specific registry/executor/selector/presenter/retry authority;
- no background network runtime;
- adapter remains closed;
- general natural-language admission and freshness remain outside the seam.

### RED result
Focal contract:
`8 FAILED / 4 PASSED`.

All eight failures converge on the same missing productive seam:
1. canonical Wikimedia environment configuration/builder is absent;
2. therefore disabled/enabled/fail-closed builder behavior cannot yet exist;
3. official runtime composition does not yet consume/register that builder.

The four passing obligations demonstrate that no deeper product repair is
needed for:
- existing non-default source admission;
- existing open-visual source selection after explicit registration;
- existing selected-query execution through the canonical executor;
- absence of parallel Wikimedia authorities and preservation of later
  residual boundaries.

This is the intended RED topology.

### Important execution-boundary clarification
The selected-query assertion proves that execution reaches the canonical
executor (`execution_enabled` plus deterministic execution id).

It deliberately does not require `GovernedInformationItem` deepening or
presentation projection in this seam. The already-certified adapter's raw
projection and later presentation authority remain separate.

### Productive GREEN authorization
The RED authorizes only the designed wiring seam:

1. `app/runtime_environment_wiring.py`
   - import the canonical Wikimedia adapter;
   - add
     `build_wikimedia_commons_governed_source_from_environment`;
   - opt-in via `ROBY_WIKIMEDIA_COMMONS_ENABLED`;
   - require explicit non-blank
     `ROBY_WIKIMEDIA_COMMONS_USER_AGENT`;
   - fail closed;
   - preserve injected transport for tests;
   - do not register or execute.

2. `app/official_runtime_composition.py`
   - import the canonical adapter and environment builder;
   - construct once;
   - if available, register via
     `conversation.register_governed_source_query_adapter()`;
   - use `WikimediaCommonsGovernedSourceAdapter.SOURCE_ID`.

No other productive Python change is authorized unless Owner execution
reveals a genuine contradiction requiring a new reconciliation.

### Explicitly forbidden in GREEN
- modifying the certified Wikimedia adapter;
- modifying the executor;
- modifying the query contract;
- modifying the selector;
- modifying gateway execution/selection authority;
- modifying AppliedConversationalIntelligence;
- changing presentation;
- changing freshness;
- changing GovernedInformationItem;
- creating provider-specific authority/registry/manager/loop.

### Formal state
`CONTRACT_RED: COMPLETE`
`FOCAL: 8 FAIL / 4 PASS`
`FAILURE_CONVERGENCE: CONFIGURATION_AND_OFFICIAL_REGISTRATION_WIRING_ONLY`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`ADAPTER: CLOSED / UNCHANGED`
`EXECUTOR: PROVEN REUSABLE / UNCHANGED`
`SELECTOR: PROVEN REUSABLE / UNCHANGED`
`GENERAL_NL_ADMISSION: OUT_OF_SCOPE`
`FRESHNESS: OUT_OF_SCOPE`
`NEW_AUTHORITY: NONE`
`SURGICAL_GREEN_AUTHORIZATION: YES / TWO PRODUCTIVE FILES ONLY`

## Canonical RED test correction and certification repair
The user-corrected contract test replaces the earlier assistant version.

Canonical test SHA-256:
`04c0fe1b78a98f2e9d14b0fa7d9edb4fee0dc07efb1f127cc28ac790507ddf08`

The correction removes the unused `inspect` import and preserves the contract.
Maximum line length: 88.

M361 was regenerated after integrating the corrected test.
Assistant verification:
- focal RED: 8 FAIL / 4 PASS;
- M361 reproducibility contract: 5 PASS;
- productive Python delta: ZERO.

The eight RED failures still converge only on the absent Wikimedia governed
environment builder and official runtime registration wiring.

Owner must run the normal local certification sequence on this repaired ZIP.
Expected contractual state is 8 intentional RED failures with Ruff clean and
M361 reproducible.


## Surgical GREEN outcome
Authorized two-file productive wiring implemented.\nAssistant focal: 12 PASS / 0 FAIL; related: 65 PASS / 0 FAIL.\nAdapter/executor/query contract/selector/gateway authority unchanged.\n