# ROBY XI.2 --- POINT 7 / P7-C2-LOCAL-S2A / RC1

# NON-DEFAULT GOVERNED SOURCE EXTENSION SEAM RECONCILIATION

## Status

**RECONCILIATION COMPLETE / EXACT CANONICAL EXTENSION SEAM IDENTIFIED /
CORRECTED RED-READY / NO PRODUCTIVE CODE MODIFIED / NO RED CORRECTION
OPENED**

Entry state:

-   P7-C2-LOCAL-S2A RED: Owner-certified.
-   First GREEN: rejected by Owner gate.
-   GREEN failure reconciliation: complete.
-   Protected `OfficialConversationGateway`: must remain byte-identical.
-   M343.5 default registry: must remain exactly six sources.
-   Credential/provider requirements from S2A remain valid.

------------------------------------------------------------------------

## 1. Governing constraints rechecked

The reconciliation was performed against the certified RED baseline and
the current governance documents.

The controlling rule remains:

**one brain → one authority per capability → integration before
expansion → surgical changes → full regression gates.**

No candidate is acceptable if it:

-   creates a second source registry;
-   creates a second query contract;
-   creates a second query executor;
-   mutates protected gateway bytes;
-   expands the M343.5 default six-source tuple;
-   bypasses source validation;
-   hides provider identity;
-   converts provider availability into automatic network authority.

------------------------------------------------------------------------

## 2. Existing canonical object graph

The protected `OfficialConversationGateway` already constructs one
shared `GovernedInformationSources()` instance.

That same registry instance is supplied to:

1.  `GovernedConversationalSourceSelector`;
2.  `GovernedInformationNormalizer`;
3.  `GovernedSourceQueryContract`.

The query contract is then supplied to the one
`GovernedSourceQueryExecutor`.

Therefore the canonical graph is already:

`ONE GovernedInformationSources instance` → selector → normalizer →
`ONE GovernedSourceQueryContract` → `ONE GovernedSourceQueryExecutor` →
protected gateway public surfaces.

This is important because a legitimate extension must enter this
existing graph, not construct a parallel graph.

------------------------------------------------------------------------

## 3. M343.5 registry capability

`GovernedInformationSources` is not structurally limited to six sources.

Its constructor accepts:

`Iterable[GovernedInformationSource]`.

The six-source restriction belongs to:

`DEFAULT_GOVERNED_INFORMATION_SOURCES`

and to the behavior of a bare:

`GovernedInformationSources()`.

Internally the canonical registry already owns a mutable indexed mapping
`self._sources`.

Therefore the missing capability is not a new registry type.

It is an **explicit canonical extension operation** on the existing
registry instance.

### Required invariant

Before explicit extension:

`GovernedInformationSources().snapshot.sources == certified six defaults`.

After explicit extension of a runtime-owned instance:

that instance may know an additional inactive declaration, while the
module-level default tuple and every fresh bare registry remain
unchanged.

Thus:

**DEFAULT MEMBERSHIP ≠ INSTANCE-LOCAL EXPLICIT EXTENSION.**

------------------------------------------------------------------------

## 4. M344.0 query-contract capability

`GovernedSourceQueryContract.prepare(query)` already asks its owned
registry:

`self._sources.source_for(query.source_id)`.

Therefore no provider-specific validation branch is required.

If the same registry instance is explicitly extended, the existing
M344.0 `prepare()` path naturally validates the non-default source using
the same rules as the default sources.

The query contract does not need a Foursquare special case.

The missing seam is only a governed way for the canonical
executor-registration path to cause the source declaration to enter the
contract's already-owned registry.

------------------------------------------------------------------------

## 5. M344.1 executor capability

`GovernedSourceQueryExecutor.register(source_id, adapter)` is already
the canonical adapter-registration operation.

`OfficialConversationGateway.register_governed_source_query_adapter(...)`
already delegates to it.

The gateway therefore does **not** need a new provider-specific method.

However, current `register()` only records:

`source_id → adapter`

inside `_adapters`.

It does not admit a non-default `GovernedInformationSource` into the
registry used by its contract.

That is the exact missing extension seam.

------------------------------------------------------------------------

## 6. Exact surviving seam

The smallest architecture-preserving seam is:

**EXPLICIT ADAPTER REGISTRATION WITH AN OPTIONAL SELF-DESCRIBED INACTIVE
GOVERNED SOURCE DECLARATION → EXISTING CONTRACT-OWNED REGISTRY INSTANCE
EXTENSION → EXISTING ADAPTER REGISTRATION.**

Conceptually:

`credential-gated Foursquare adapter` +
`inactive GovernedInformationSource declaration carried by that adapter`
→ existing protected
`OfficialConversationGateway.register_governed_source_query_adapter(...)`
→ existing `GovernedSourceQueryExecutor.register(...)` → **\[NEW GENERIC
NON-DEFAULT SOURCE EXTENSION LOGIC\]** → existing
`GovernedSourceQueryContract` → existing `GovernedInformationSources`
instance → adapter registration → explicit later `execute(...)` → STOP.

The generic extension logic belongs in the existing source-query family,
not in the gateway and not in provider-specific orchestration.

------------------------------------------------------------------------

## 7. Recommended generic contract shape

The corrected RED should contract behavior, not unnecessarily freeze
exact method names.

A compatible minimal design is:

1.  a non-default adapter may expose one immutable
    `GovernedInformationSource` declaration;
2.  the declaration's `source_id` must exactly match the normalized
    registration `source_id`;
3.  the declaration must remain inactive: `network_enabled=False`,
    `automatic_fetch_enabled=False`;
4.  during explicit executor registration, the canonical source-query
    family admits that declaration into the same registry instance
    already owned by the query contract;
5.  the adapter is then registered in the existing executor;
6.  no network call occurs during either declaration admission or
    registration;
7.  execution remains a separate explicit call.

Implementation may place the small generic admission operation on
`GovernedInformationSources`, `GovernedSourceQueryContract`, or both,
provided the single object graph and authority remain intact.

The RED should not freeze a private helper name unless necessary.

------------------------------------------------------------------------

## 8. Why adapter-carried declaration is the narrowest composition

The protected gateway's existing public registration surface accepts
only:

`source_id, adapter`.

It cannot receive a third source-declaration argument without gateway
surgery.

The gateway must remain byte-identical.

Therefore the additional declaration has to be reachable through an
object already crossing that protected boundary.

The adapter is that object.

This does not make the adapter the registry authority.

The adapter merely **carries immutable provider metadata**.

Admission and validation remain owned by the existing canonical
source-query/registry family.

Thus:

**ADAPTER DESCRIBES SOURCE ≠ ADAPTER OWNS SOURCE REGISTRY.**

------------------------------------------------------------------------

## 9. Atomic registration semantics

For a non-default source, explicit registration must be atomic from the
caller's perspective:

-   validate source declaration;
-   validate declaration ID == registration ID;
-   admit declaration to the existing runtime registry;
-   register adapter.

Failure at validation must leave the provider unavailable.

This prevents states such as:

-   adapter registered but source unknown to contract;
-   source admitted but mismatched adapter identity;
-   provider silently shadowing an existing source.

A duplicate source ID with a non-identical declaration must fail closed.

A provider adapter must not be allowed to overwrite a certified default
source declaration.

------------------------------------------------------------------------

## 10. Compatibility with default adapters

Existing adapters such as NASA are already default-declared sources.

The generic extension must preserve their current registration behavior.

Therefore:

-   adapters without an attached non-default declaration continue to
    register only against already-known sources;
-   a registration for an unknown source without an explicit declaration
    fails closed;
-   an adapter carrying a declaration may extend only the runtime-owned
    registry instance;
-   default source declarations remain unchanged.

This preserves all existing M344.x call sites.

------------------------------------------------------------------------

## 11. Selection and normalization compatibility

Because selector, normalizer and query contract share the same
`GovernedInformationSources` instance created by the gateway, an
instance-local extension has a useful property:

the newly admitted source becomes visible to the existing
selector/normalizer/query contract **without gateway surgery and without
a second registry**.

No new conversational selector is justified.

No provider-specific normalizer authority is justified at this seam.

Provider response normalization remains subject to the existing governed
conversational path and later evidence governance.

------------------------------------------------------------------------

## 12. Credential and network boundary remains unchanged

RC1 does not reopen credential ownership.

The provider adapter may still be constructed by existing environment
wiring using `SecretsLoader`.

Missing/blank credential must fail closed before registration.

Explicit registration means:

**PROVIDER AVAILABLE IN THIS RUNTIME**

It does not mean:

**NETWORK CALL AUTHORIZED NOW.**

Network I/O remains inside the adapter's `execute(query)` and occurs
only after an explicit call through the existing executor.

No registration or source admission may perform network I/O.

------------------------------------------------------------------------

## 13. Candidate destruction

### A. New provider-specific gateway method

**DESTROYED.**

Protected gateway hash forbids it and the generic registration surface
already exists.

### B. Add Foursquare to `DEFAULT_GOVERNED_INFORMATION_SOURCES`

**DESTROYED.**

M343.5 protects the six-source default.

### C. Second Foursquare registry/contract/executor

**DESTROYED.**

Canonical authorities already exist.

### D. External mutation of gateway private fields

**DESTROYED.**

Violates ownership and encapsulation.

### E. Adapter registration without source admission

**DESTROYED.**

Executor revalidation would reject the unknown source.

### F. Source admission without identity coupling to adapter registration

**DESTROYED.**

Could produce mismatched provenance/adapter identity.

### G. Provider-specific branch inside `prepare()`

**DESTROYED.**

Existing generic source validation is sufficient once the source is
canonically admitted.

### H. Hidden global registry mutation

**DESTROYED.**

Would make runtime availability implicit and non-local.

------------------------------------------------------------------------

## 14. Exact corrected RED seam

The GREEN-failure residual is now RED-ready as:

**R-C2-LOCAL-S2A-RC1 --- EXPLICIT NON-DEFAULT GOVERNED SOURCE
DECLARATION ADMISSION THROUGH EXISTING SOURCE-QUERY EXECUTOR
REGISTRATION.**

Required conceptual chain:

`M343.5 DEFAULT SIX UNCHANGED` + `CREDENTIAL-GATED PROVIDER ADAPTER` +
`IMMUTABLE INACTIVE NON-DEFAULT SOURCE DECLARATION` → protected existing
gateway registration surface → existing canonical executor registration
→ **generic declaration validation + instance-local canonical registry
admission** → existing query contract can prepare source → existing
executor holds adapter → explicit execution remains separate → STOP.

------------------------------------------------------------------------

## 15. Corrected RED contractual requirements

A surgical corrected RED should prove all of the following.

1.  `OfficialConversationGateway` remains byte-identical to the
    certified hash.
2.  `DEFAULT_GOVERNED_INFORMATION_SOURCES` remains exactly six sources.
3.  A fresh bare `GovernedInformationSources()` remains exactly six
    sources.
4.  A canonical registry instance supports explicit admission of a valid
    inactive non-default declaration without mutating module defaults.
5.  Duplicate/mismatched extension fails closed.
6.  Existing `GovernedSourceQueryContract` validates an explicitly
    admitted source without provider-specific branches.
7.  Existing `GovernedSourceQueryExecutor.register(...)` is the single
    adapter registration authority.
8.  Registration can consume an adapter-carried immutable source
    declaration for an otherwise unknown source.
9.  Registration rejects unknown sources when no explicit declaration is
    supplied.
10. Declaration ID and adapter registration ID must match.
11. Registration performs no network I/O.
12. Existing default-source adapters continue to register unchanged.
13. Foursquare adapter retains credential-required construction.
14. Missing/blank credential fails closed.
15. Secret remains absent from snapshots/query/results/provenance.
16. Fake injected transport remains supported.
17. No implicit IP geolocation fallback.
18. Existing gateway public registration method is reused unchanged.
19. S1 cannot register, enable or execute the provider.
20. No second registry/selector/query contract/executor/network
    authority.
21. No Memory/Learning/Planning/Execution.
22. No reservation/booking/navigation.
23. No live network test.

------------------------------------------------------------------------

## 16. What the corrected RED must remove

The prior RED assertions below are now disproven and must not survive:

-   bare `GovernedInformationSources()` must already contain
    `foursquare_places`;
-   `OfficialConversationGateway` must implement
    `enable_foursquare_governed_source`.

Their removal is not weakening governance.

It is a correction that restores compatibility with stronger
pre-existing certified invariants.

------------------------------------------------------------------------

## 17. Productive reachability boundary after RC1

Even after the corrected RED and eventual GREEN, the proof would
establish:

`explicit configured provider` →
`explicit canonical runtime registration` → `S1 prepared query` →
`existing executor can execute provider query`.

It would still not by itself certify:

-   live Foursquare service availability;
-   real credential presence;
-   ordinary-turn local/business end-to-end result;
-   M400/M401 admission of a live place/business result;
-   P7-C2-S1 reasoning consumption for that result;
-   final conversational productive reachability.

Those remain downstream evidence questions.

------------------------------------------------------------------------

## 18. R / C / D

After RC1:

**R = 1**

Exact RED-ready residual:

**R-C2-LOCAL-S2A-RC1 --- EXPLICIT NON-DEFAULT GOVERNED SOURCE
DECLARATION ADMISSION THROUGH EXISTING SOURCE-QUERY EXECUTOR
REGISTRATION.**

**C = 0**

No additional architectural reconciliation is required before correcting
the RED.

**D = 0**

No master constitutional principle requires revision.

------------------------------------------------------------------------

## 19. Required next governed movement

Only after explicit Owner authorization:

**CORRECTED RED CONTRACTUAL P7-C2-LOCAL-S2A-RC1**

The corrected RED must be built from the last Owner-certified RED
baseline, not from the rejected GREEN.

It must:

-   preserve the Owner-corrected S2A test formatting/import hygiene;
-   surgically replace only the two invalid placement assumptions;
-   add generic extension-seam contracts;
-   keep all still-valid provider/credential boundaries;
-   contain no productive implementation;
-   run Ruff clean;
-   produce only the expected corrected-RED failures;
-   STOP for Owner certification before any GREEN re-entry.

------------------------------------------------------------------------

## 20. Final disposition

**P7-C2-LOCAL-S2A / RC1 RECONCILIATION: COMPLETE.**

Result:

`PROTECTED GATEWAY` + `M343.5 DEFAULT SIX` +
`SHARED RUNTIME REGISTRY INSTANCE` + `EXISTING M344.0 CONTRACT` +
`EXISTING M344.1 EXECUTOR` + `EXISTING GATEWAY REGISTRATION SURFACE` →
exact missing seam: **GENERIC INSTANCE-LOCAL NON-DEFAULT SOURCE
ADMISSION DURING EXPLICIT EXECUTOR REGISTRATION** → **R1 / C0 / D0** →
**CORRECTED RED-READY** → **STOP**.

No productive code modified.
