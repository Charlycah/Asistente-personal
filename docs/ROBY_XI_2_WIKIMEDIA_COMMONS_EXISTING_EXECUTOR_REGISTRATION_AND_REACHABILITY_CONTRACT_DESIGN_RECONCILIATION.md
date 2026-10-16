# ROBY XI.2 — Wikimedia Commons Existing Executor Registration and Reachability
## Contract Design Reconciliation

### Certified baseline
Input: Owner-certified PRE-RED, 13,550 PASS / 0 FAIL, Ruff clean,
M361 reproducible. Productive Python remains unchanged in this design block.

### Classification
`CLASS_2_EXISTING_CAPABILITY_DEEPENING`

No new execution, selection, registry, gateway, planning, presentation, or
network authority is authorized.

### Canonical path
The contract must preserve exactly:

`runtime_environment_wiring`
→ `official_runtime_composition`
→ `OfficialConversationGateway.register_governed_source_query_adapter()`
→ `GovernedSourceQueryExecutor.register()`
→ `GovernedSourceQueryContract.admit_non_default_source()`
→ existing governed source registry
→ existing selector
→ existing selected-query execution.

### Governed runtime configuration contract
Canonical configuration names for the future RED/GREEN:

- `ROBY_WIKIMEDIA_COMMONS_ENABLED`
- `ROBY_WIKIMEDIA_COMMONS_USER_AGENT`

Rules:
1. Wikimedia is opt-in. The enabled flag defaults to false.
2. When disabled, the environment builder returns `None`.
3. When enabled, a non-blank `ROBY_WIKIMEDIA_COMMONS_USER_AGENT` is required.
4. Missing/blank User-Agent returns `None`; no network request is attempted.
5. Invalid adapter construction/configuration returns `None` through the
   existing fail-closed environment-wiring pattern.
6. No default browser User-Agent, fake contact, personal email/address, API
   key, or hardcoded operator identity is permitted.
7. The builder may accept an injected transport for deterministic tests, as
   the existing adapter contract already supports it.
8. The builder must not register anything itself.

Expected builder name:
`build_wikimedia_commons_governed_source_from_environment`.

### Official composition registration contract
`build_official_runtime_from_environment()` remains the composition authority.

It may:
1. call the governed environment builder once;
2. if the result is not `None`, call
   `conversation.register_governed_source_query_adapter()` with
   `WikimediaCommonsGovernedSourceAdapter.SOURCE_ID` and that adapter;
3. otherwise leave Wikimedia absent.

It must not:
- mutate `GovernedInformationSources` directly;
- call executor private state;
- create a provider-specific registry;
- bypass the gateway registration boundary;
- enable background/automatic fetch.

### Registration admission contract
No changes are required to `GovernedSourceQueryExecutor.register()`.

Existing behavior is authoritative:
- source id normalized;
- adapter declaration identity checked;
- non-default declaration admitted through the existing query contract;
- adapter stored in the canonical executor.

After successful registration:
- `wikimedia_commons` appears in the executor's registered sources;
- the same declaration is resolvable through the existing contract-owned
  runtime registry;
- duplicate equivalent admission remains idempotent under existing semantics;
- conflicting declaration identity remains rejected by existing semantics.

### Existing open-visual selection reachability
The contract must prove reachability using an explicitly constructed
`GovernedConversationalSourceSelectionRequest` with:
- `mode=OPEN_VISUAL_SUBJECT`;
- `topics=frozenset()`;
- non-empty `query_text`;
- global/no restrictive region compatible with the source;
- a bounded valid limit/timeout.

When Wikimedia is registered and no higher-ranked eligible open-visual source
is introduced by the fixture, the existing selector must return:
- `SELECTED`;
- source id `wikimedia_commons`;
- a `GovernedSourceQuery` preserving
  `OPEN_VISUAL_SUBJECT`, empty topics, and the query text.

When Wikimedia is not registered, the selector must not select it.

This proves selection reachability without changing selector ranking or
turning empty topics into wildcard topic eligibility.

### Existing execution reachability
With a registered Wikimedia adapter using an injected deterministic transport,
the existing selected-query path must execute through the canonical
`GovernedSourceQueryExecutor` and return provider raw items under the existing
governed result envelope.

The contract must prove:
- no direct adapter call from composition/gateway selection logic;
- executor observability/execution path remains in force;
- query timeout/limit continue to flow through the existing query object;
- no autonomous fetch occurs.

### Natural-language boundary
This contract MUST NOT require
`AppliedConversationalIntelligence.interpret()` to recognize arbitrary visual
subjects.

Current topic recognition remains unchanged.

Therefore:
`CONFIGURED_PROVIDER_REACHABILITY != GENERAL_NATURAL_LANGUAGE_ADMISSION`.

A natural-language request such as an arbitrary unknown subject is not a RED
obligation here.

Separate residual:
`GENERAL_OPEN_VISUAL_NATURAL_LANGUAGE_ADMISSION`.

### Freshness and presentation boundaries
Not part of this contract:
- recency ranking / "latest" semantics;
- presentation/UI changes;
- attribution UI;
- `GovernedInformationItem` deepening.

`EXTERNAL_IMAGE_FRESHNESS_ORDERING` remains later.

### Productive GREEN envelope if RED proves the contract
Expected productive Python delta is limited to:
1. `app/runtime_environment_wiring.py`
2. `app/official_runtime_composition.py`

The already-certified
`app/wikimedia_commons_governed_source.py`
must remain unchanged.

The executor, query contract, selector, gateway execution logic, applied
conversational intelligence, presentation modules, and information-item model
must remain unchanged unless Contract RED exposes a genuine contradiction.

### Contract RED obligations
A single bounded architecture contract should demonstrate at least:

1. canonical Wikimedia environment builder exists;
2. disabled-by-default returns `None`;
3. enabled + missing User-Agent returns `None`;
4. enabled + blank User-Agent returns `None`;
5. enabled + explicit User-Agent constructs the canonical adapter;
6. configured User-Agent is passed to the adapter without a hardcoded fallback;
7. injected transport is preserved for deterministic testing;
8. environment builder does not itself register the adapter;
9. official runtime composition attempts optional Wikimedia construction;
10. successful construction registers via the gateway public registration
    method and canonical source id;
11. unavailable configuration leaves Wikimedia unregistered;
12. successful registration admits the non-default declaration through the
    existing executor/contract path;
13. registered Wikimedia becomes eligible for an explicit
    `OPEN_VISUAL_SUBJECT` request;
14. unregistered Wikimedia is not selectable;
15. selection preserves open mode, empty topics, query text, limit, timeout;
16. selected-query execution uses the existing executor and returns governed
    Wikimedia raw results with deterministic injected transport;
17. no automatic/background fetch is introduced;
18. no Wikimedia-specific registry/executor/selector/presenter/retry authority
    exists;
19. adapter module remains unchanged by GREEN;
20. arbitrary-subject natural-language recognition is not asserted;
21. freshness ordering is not asserted.

The RED must fail because runtime configuration/registration wiring is absent,
not because of fixture/import/API mismatches or optional unrelated services.

### Formal state
`CONTRACT_DESIGN_RECONCILIATION: COMPLETE`
`CLASSIFICATION: CLASS_2_EXISTING_CAPABILITY_DEEPENING`
`WIKIMEDIA_ENABLED_ENV: ROBY_WIKIMEDIA_COMMONS_ENABLED`
`WIKIMEDIA_USER_AGENT_ENV: ROBY_WIKIMEDIA_COMMONS_USER_AGENT`
`DEFAULT_ENABLEMENT: FALSE`
`MISSING_CONFIGURATION: FAIL_CLOSED / UNREGISTERED`
`REGISTRATION_AUTHORITY: OFFICIAL_RUNTIME_COMPOSITION`
`EXECUTOR: REUSE / UNCHANGED`
`QUERY_CONTRACT: REUSE / UNCHANGED`
`SELECTOR: REUSE / UNCHANGED`
`GATEWAY_EXECUTION_LOGIC: REUSE / UNCHANGED`
`ADAPTER: CLOSED / UNCHANGED`
`GENERAL_NL_ADMISSION: OUT_OF_SCOPE`
`FRESHNESS: OUT_OF_SCOPE`
`NEW_AUTHORITY: NONE`
`CONTRACT_RED_AUTHORIZATION: YES / THIS CONTRACT ONLY`


## Contract RED outcome
Focal RED: 8 FAIL / 4 PASS.\nFailures converge only on absent governed environment builder and official runtime registration wiring.\nExisting admission, selector, and executor reachability are already proven reusable.\n