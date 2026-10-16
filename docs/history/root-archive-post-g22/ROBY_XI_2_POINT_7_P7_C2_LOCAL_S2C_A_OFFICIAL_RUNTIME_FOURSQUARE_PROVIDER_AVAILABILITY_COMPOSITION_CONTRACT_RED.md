# ROBY XI.2 — P7-C2-LOCAL-S2C-A — CONTRACTUAL RED

## Exact seam

**R-C2-LOCAL-S2C-A — OFFICIAL RUNTIME PROVIDER AVAILABILITY COMPOSITION**

`build_official_runtime_from_environment(...)`
→ existing `build_foursquare_governed_source_from_environment(...)`
→ existing `OfficialConversationGateway.register_governed_source_query_adapter(...)`
→ provider available in the canonical runtime
→ **STOP WITHOUT NETWORK EXECUTION**.

## Contract

The RED requires the existing official runtime builder to consume the existing
credential/feature-gated Foursquare builder. A returned adapter must be
registered through the existing public gateway registration surface. `None`
must leave the provider unavailable and fail closed.

Startup provider availability must not execute a source query, authorize a
network call, infer per-turn authorization, or mutate the protected gateway.

## Frozen distinctions

- PROVIDER AVAILABLE ≠ NETWORK CALL AUTHORIZED NOW.
- STARTUP REGISTRATION ≠ PROVIDER EXECUTION.
- CREDENTIAL AVAILABILITY ≠ TURN AUTHORIZATION.
- SOURCE REGISTRATION ≠ QUERY PREPARATION.
- QUERY PREPARATION ≠ NETWORK EXECUTION.
- APPLICATION COMPOSITION ≠ NEW CAPABILITY AUTHORITY.

## Reused authorities

- official runtime construction: `build_official_runtime_from_environment`;
- provider configuration/credential gate:
  `build_foursquare_governed_source_from_environment` + `SecretsLoader`;
- provider adapter: `FoursquareGovernedSourceAdapter`;
- source admission/adapter registration: existing gateway/executor surface.

No new provider manager, registry, selector, executor, gateway, brain, agent,
or network authority is authorized.

## Expected RED

Existing provider builder and registration authorities already pass their
existence/behavior checks. RED failures must be limited to the missing official
runtime composition that consumes the builder, handles `None`, and registers a
returned adapter.

## Out of scope

- provider execution;
- S2C-B per-turn composition;
- local/business conversational publication;
- implicit network authorization;
- live credentials/network tests;
- location acquisition or persistence;
- booking/reservation/navigation;
- Memory/Learning/Planning/Execution;
- gateway surgery;
- Point 9.

## STOP

**RED CONTRACT ONLY. NO PRODUCTIVE IMPLEMENTATION. STOP BEFORE GREEN.**
