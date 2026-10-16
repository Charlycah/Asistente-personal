# ROBY XI.2 — Wikimedia Commons Existing Executor Registration and Reachability
## Pre-RED Reconciliation

### Certified baseline
Input is the Owner-certified Wikimedia Commons adapter Post-GREEN state:
13,550 PASS / 0 FAIL, Ruff clean, M361 reproducible.

The adapter contract is closed and is not reopened.

### Existing canonical authorities found
No Wikimedia-specific execution authority is required.

`GovernedSourceQueryExecutor.register()` already:
1. normalizes the source id;
2. reads an adapter `source_declaration` when present;
3. verifies declaration identity matches adapter identity;
4. calls the existing query contract `admit_non_default_source()`;
5. stores the adapter in the canonical executor.

The existing selector already restricts candidates to registered sources and,
for `OPEN_VISUAL_SUBJECT`, additionally requires the explicit
`OPEN_VISUAL_SUBJECT_QUERY` capability.

`OfficialConversationGateway` already exposes:
- `register_governed_source_query_adapter()`;
- `execute_governed_source_query()`;
- selection against the executor's `registered_sources`;
- the existing selected conversational query path.

Therefore:
`WIKIMEDIA_REGISTRATION != NEW_EXECUTOR_AUTHORITY`.

### Existing composition precedent
The closest productive non-default precedent is Foursquare:
- `runtime_environment_wiring.py` constructs the optional adapter from
  governed environment/secret configuration;
- `official_runtime_composition.py` registers it through
  `OfficialConversationGateway.register_governed_source_query_adapter()`.

Wikimedia differs only in configuration shape:
it requires no provider API key, but its already-certified adapter requires a
non-blank descriptive User-Agent containing operator/contact identification.

### Exact registration seam
The registration seam is the existing official runtime composition, not the
gateway internals and not the executor implementation.

A bounded environment builder may construct
`WikimediaCommonsGovernedSourceAdapter` only when explicit governed
configuration supplies a valid User-Agent/contact identity. The official
runtime composition may then register that adapter through
`conversation.register_governed_source_query_adapter()`.

This reuses:
`runtime_environment_wiring -> official_runtime_composition ->
OfficialConversationGateway -> GovernedSourceQueryExecutor.register ->
GovernedSourceQueryContract.admit_non_default_source`.

No direct mutation of the source catalogue is authorized.

### Reachability meaning in this seam
For this block, productive reachability means:
1. the configured Wikimedia adapter can be constructed;
2. it is registered in the existing canonical executor;
3. its source declaration is admitted by the existing contract;
4. the existing selector can select it for an explicitly constructed
   `OPEN_VISUAL_SUBJECT` request;
5. the existing selected-query path can execute through the same executor.

It does NOT mean broad natural-language recognition for arbitrary subjects.

Current `AppliedConversationalIntelligence.interpret()` still requires a
recognized `InterestTopic` before it creates a request. That is a separate
admission residual and must not be silently repaired here.

Thus:
`EXECUTOR_REACHABILITY != GENERAL_NATURAL_LANGUAGE_REACHABILITY`.

### Configuration boundary
The adapter contract already forbids a blank User-Agent and forbids hardcoded
personal contact data.

The registration seam therefore requires governed configuration for the
Wikimedia User-Agent. No personal email/address may be embedded in product
code. Missing/blank configuration must fail closed by leaving the optional
adapter unconstructed/unregistered.

Exact environment variable naming is a Contract Design concern; PRE-RED does
not hardcode a new name prematurely.

### Files that must remain unchanged in this seam unless RED evidence proves
otherwise
- `app/governed_source_query_executor.py`;
- `app/governed_source_query.py`;
- `app/governed_conversational_source_selection.py`;
- `app/applied_conversational_intelligence.py`;
- `app/wikimedia_commons_governed_source.py`;
- external image presentation/composition modules;
- `OfficialConversationGateway` execution/selection authority.

The expected productive GREEN, if RED proves the seam, should be limited to
existing environment wiring and official runtime composition.

### Explicit exclusions
- no Wikimedia registry;
- no Wikimedia executor;
- no Wikimedia selector;
- no new gateway/planner/agent/manager;
- no autonomous/background fetch;
- no retry scheduler;
- no presentation change;
- no freshness ordering;
- no `GovernedInformationItem` change;
- no arbitrary-subject natural-language admission repair.

### Residual decomposition
Parent:
`WIKIMEDIA_COMMONS_EXISTING_EXECUTOR_REGISTRATION_AND_REACHABILITY`

Refined seams:
1. `WIKIMEDIA_COMMONS_GOVERNED_RUNTIME_CONFIGURATION_AND_REGISTRATION`
2. `WIKIMEDIA_COMMONS_EXISTING_OPEN_VISUAL_SELECTION_EXECUTION_REACHABILITY`

These should be proven by one bounded contract only if Contract Design can
express them without broadening natural-language admission.

Separate/later:
`GENERAL_OPEN_VISUAL_NATURAL_LANGUAGE_ADMISSION`
`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

### Contract Design authorization
The next authorized block is:
`WIKIMEDIA COMMONS EXISTING EXECUTOR REGISTRATION AND REACHABILITY —
CONTRACT DESIGN RECONCILIATION`.

No Contract RED is authorized yet because the exact governed environment
configuration contract and registration lifecycle must first be fixed.

### Formal state
`PRE_RED_RECONCILIATION: COMPLETE`
`PRODUCTIVE_PYTHON_DELTA: ZERO`
`CANONICAL_EXECUTOR: REUSE`
`CANONICAL_QUERY_CONTRACT: REUSE`
`CANONICAL_SELECTOR: REUSE`
`CANONICAL_GATEWAY: REUSE`
`REGISTRATION_SEAM: OFFICIAL_RUNTIME_COMPOSITION`
`ENVIRONMENT_WIRING_PRECEDENT: FOURSQUARE`
`GENERAL_NL_ADMISSION: OUT_OF_SCOPE / LATER`
`FRESHNESS: OUT_OF_SCOPE / LATER`
`NEW_AUTHORITY: NONE`
`CONTRACT_RED_AUTHORIZATION: NO`
`NEXT: CONTRACT_DESIGN_RECONCILIATION`

### Assistant verification note
Directly relevant contracts: 73 PASS in the assistant environment.\nA broader filename-selected composition run was not usable because two unrelated tests failed during collection on optional environment dependencies; it is not treated as product evidence.\nOwner full-suite certification of the input baseline remains authoritative: 13,550 PASS / 0 FAIL.\n

## Contract Design outcome
Canonical opt-in configuration fixed as ROBY_WIKIMEDIA_COMMONS_ENABLED and ROBY_WIKIMEDIA_COMMONS_USER_AGENT.\nProductive GREEN envelope, if proven by RED: runtime_environment_wiring.py and official_runtime_composition.py only.\nGeneral natural-language admission and freshness remain separate.\n