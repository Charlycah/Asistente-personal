# ROBY XI.2 --- POINT 7 / C2-LOCAL

# S2A PROVIDER CONFIGURATION + ENABLEMENT RECONCILIATION

## Status

**RECONCILIATION COMPLETE / CONFIGURATION OWNER IDENTIFIED / ENABLEMENT
OWNER IDENTIFIED / EXACT RED-READY RESIDUAL DEMONSTRATED / NO RED OPENED
/ NO PRODUCTIVE CODE MODIFIED**

Owner-certified entry:

**12,836 PASS · 0 FAIL · Ruff clean**

P7-C2-LOCAL-S1:

**OWNER-CERTIFIED / CLOSED**

Prior S2 classification:

**R0 / C1 / D0**

Target:

**C-C2-LOCAL-S2A --- PLACE/BUSINESS PROVIDER CREDENTIAL + EXPLICIT
ENABLEMENT OWNERSHIP RECONCILIATION.**

## 1. Executive conclusion

The final configuration/authorization uncertainty can be resolved by
reusing two already-existing canonical ownership surfaces:

1.  **credential ownership**:
    `infrastructure.config.secrets_loader.SecretsLoader` plus the
    existing `.roby/credentials.json` / environment compatibility path;

2.  **adapter enablement/execution ownership**:
    `OfficialConversationGateway` plus its existing
    `GovernedSourceQueryExecutor`.

No new secret store, configuration authority, network-authorization
manager, provider manager, retrieval executor or cognitive authority is
required.

The remaining C2-LOCAL provider edge is therefore now contractable.

## 2. Canonical credential ownership

The certified repository already contains:

`infrastructure/config/secrets_loader.py`

with `SecretsLoader`.

Its contract is:

-   canonical private credential lookup from supported ROBY credential
    files;
-   environment variables as an explicit compatibility override;
-   stable search roots;
-   `get(...)` for optional credentials;
-   `require(...)` for explicitly required credentials.

The canonical target is:

`.roby/credentials.json`.

Legacy `.roby/credencial.json` and `.hal/...` paths are compatibility
inputs.

`app/credentials.py` owns process activation/migration of known
credentials, but provider consumers may also read through
`SecretsLoader`, as the existing weather runtime already does.

### Finding

**A new Foursquare secret loader or provider credential store is not
justified.**

Provider credentials belong to the existing ROBY private
credential/configuration surface.

## 3. Existing credentialed runtime precedent

`build_weather_conversation_from_environment()` already demonstrates the
relevant pattern:

`environment feature flag` → `SecretsLoader().get(provider credential)`
→ fail closed when credential missing → construct provider
client/adapter → return bounded conversation integration.

This proves that ROBY already permits a provider-specific
environment/configuration builder to consume a credential from the
canonical secret store without making the credential part of Memory,
source metadata or conversation state.

### Important limitation

Weather is evidence of **configuration ownership**, not authority to
copy its whole architecture into C2-LOCAL.

C2-LOCAL already has its canonical source-query execution family and
must remain there.

## 4. `activate_credentials` and known-credential enumeration

`app.credentials.activate_credentials()` exposes a bounded list of known
local credentials into the current process.

Its current `KNOWN_CREDENTIALS` tuple does not include a Foursquare key.

That does **not** require a second credential system.

There are two existing compatible access patterns:

-   process activation through the canonical credential module;
-   direct `SecretsLoader().get(...)` at environment wiring time.

The narrower C2-LOCAL seam should not require global process activation
merely to obtain one provider secret.

### Disposition

**Use the existing `SecretsLoader` ownership at provider wiring time.**

Do not create a provider-specific credential file.

Do not put a key in the source registry.

Do not put a key in a `GovernedSourceQuery`.

Do not put a key in evidence/provenance metadata.

## 5. Credential-name policy

The reconciliation establishes the owner but does not need to expose or
create a real credential.

A future contractual RED may define a stable configuration key for the
selected provider because the provider itself is already fixed at the
bounded adapter edge.

That key is configuration vocabulary, not a new authority.

The contract must require:

-   missing/blank credential → provider remains unavailable;
-   placeholder credential → unavailable;
-   secret never returned in snapshots/results;
-   secret never copied into query parameters visible to ROBY evidence;
-   secret never persisted by the adapter;
-   fake credential may be injected in tests.

## 6. Canonical adapter-enable owner

`OfficialConversationGateway` already owns:

-   `register_governed_source_query_adapter(source_id, adapter)`;
-   `execute_governed_source_query(query)`;
-   explicit `enable_*_governed_source()` methods for NASA, Apple
    audiovisual, Argentina healthy eating and Cultura CABA.

Each existing enable method registers its adapter into the one existing
`GovernedSourceQueryExecutor`.

Therefore:

**OfficialConversationGateway + GovernedSourceQueryExecutor is the
canonical enablement/execution owner for the C2-LOCAL provider
adapter.**

No second provider registry or executor is justified.

## 7. Enablement semantics

Existing bounded source adapters expose:

`network_enabled=True` and `automatic_fetch_enabled=False`.

Their presence as adapter objects does not itself execute network I/O.

Network execution occurs only when:

1.  the adapter has been explicitly registered with the existing
    executor; and
2.  an explicit governed query is passed to
    `execute_governed_source_query(...)`.

This is the correct constitutional pattern for C2-LOCAL.

Required invariant:

`QUERY PREPARATION ≠ ADAPTER ENABLEMENT ≠ NETWORK EXECUTION`.

P7-C2-LOCAL-S1 must remain unable to register or enable the adapter.

## 8. Startup configuration vs conversational authorization

A critical distinction is required.

### Startup/provider availability

Startup configuration may determine whether the provider adapter is
**available for explicit governed use**.

This may depend on:

-   an explicit provider feature flag;
-   presence of a valid credential;
-   successful construction of the bounded adapter.

### Per-query execution

Provider availability does **not** authorize a network call.

Each network call still requires the existing explicit governed
source-query execution path.

Therefore:

`PROVIDER ENABLED AT STARTUP` ≠ `NETWORK CALL AUTHORIZED NOW`.

This preserves the earlier rule:

`EXPLICIT LOCAL INFORMATION NEED ≠ NETWORK AUTHORIZATION`

while allowing product configuration to make the bounded source
available.

## 9. Where startup wiring belongs

The certified product already centralizes environment-derived product
integrations in:

`app/runtime_environment_wiring.py`

and constructs the official runtime through the existing runtime
composition factories.

That is the appropriate ownership family for:

-   reading provider-enabled configuration;
-   reading the provider credential via `SecretsLoader`;
-   constructing the provider adapter when configured;
-   failing closed when disabled/misconfigured.

The adapter must then enter the existing conversation/source-query
authority rather than creating an independent runtime.

### Finding

**Provider construction belongs to existing environment/runtime wiring;
provider registration/execution belongs to
OfficialConversationGateway.**

This is a composition seam, not a new manager.

## 10. Fail-closed configuration contract

The provider must remain unavailable when any of these holds:

-   provider feature disabled;
-   credential absent;
-   credential blank;
-   credential placeholder/invalid at configuration boundary;
-   adapter construction failure.

Unavailable must mean:

-   no adapter registration;
-   no network call;
-   no fallback to implicit IP geolocation;
-   no fallback to another provider;
-   no global retrieval enablement.

A local/business query may then produce the existing
unavailable/not-supported bounded outcome rather than broadening
authority.

## 11. Testability

Existing governed source adapters already accept injectable transport.

The provider adapter should preserve that pattern.

RED/GREEN tests must use:

-   fake credential;
-   injected fake transport;
-   deterministic provider payloads;
-   no live network;
-   no real API key;
-   no secret file mutation.

This permits complete contract testing without turning external service
availability into test evidence.

## 12. Source declaration

S2 demonstrated that the canonical information-source registry has no
place/business source.

The provider source declaration may now be included in the bounded
provider-edge residual because the product capability and provider
contract have already been adopted.

But declaration must preserve:

`network_enabled=False` and `automatic_fetch_enabled=False`

at the information-source registry layer.

The executable adapter may separately expose its existing adapter-level
`network_enabled=True`, as current bounded source adapters do.

These two flags describe different layers and must not be collapsed.

## 13. Ambient-conversation boundary

Nothing in family conversational participation may:

-   read the provider credential;
-   enable the adapter;
-   register the adapter;
-   execute the query merely because a local topic is overheard.

Ambient participation may create conversational relevance only.

External network use remains a separately governed explicit execution
case.

Therefore the provider environment builder and enablement surface must
remain outside P7-R1/P7-C1 participation logic.

## 14. Candidate destruction

This reconciliation destroys the remaining competing hypotheses:

1.  **A new credential store is required.** Destroyed ---
    `SecretsLoader` already owns secrets.

2.  **A Foursquare-specific configuration manager is required.**
    Destroyed --- existing runtime environment wiring owns provider
    configuration.

3.  **The adapter should read credentials from the query.** Destroyed
    --- credentials are configuration, not query/evidence data.

4.  **The adapter should auto-register when S1 prepares a query.**
    Destroyed.

5.  **Source declaration should imply network enablement.** Destroyed.

6.  **Startup provider availability should imply per-query
    authorization.** Destroyed.

7.  **Ambient conversational participation may auto-enable the
    provider.** Destroyed.

8.  **The generic external retrieval runtime should own this provider.**
    Not demonstrated; the canonical S1 downstream remains the governed
    source-query family.

9.  **A new network authorization authority is needed.** Destroyed ---
    explicit adapter registration plus explicit governed query execution
    already provides the bounded execution surface.

10. **A live provider call is required before RED.** Destroyed ---
    injected transport supports contractual testing.

## 15. Exact residual after reconciliation

The prior C candidate now becomes an exact RED-ready residual:

**R-C2-LOCAL-S2A --- BOUNDED PLACE/BUSINESS PROVIDER SOURCE +
CREDENTIAL-GATED ADAPTER ENABLEMENT COMPOSITION.**

Exact conceptual seam:

`EXISTING SecretsLoader / runtime environment configuration` →
`EXPLICIT PROVIDER AVAILABILITY CONFIG` → **\[MISSING BOUNDED
PLACE/BUSINESS SOURCE DECLARATION + CREDENTIAL-GATED ADAPTER
CONSTRUCTION / EXPLICIT GATEWAY ENABLEMENT\]** →
`EXISTING OfficialConversationGateway` →
`EXISTING GovernedSourceQueryExecutor` →
`OWNER-CERTIFIED S1 PREPARED QUERY` →
`STOP BEFORE LIVE NETWORK IN CONTRACTUAL RED`.

The RED can use fake transport and fake credential while proving the
complete authorization/configuration boundary.

## 16. What the RED may contract

A future RED may require the smallest bounded provider-edge contract:

1.  canonical place/business source declaration exists;
2.  declaration itself remains network-disabled /
    automatic-fetch-disabled;
3.  bounded provider adapter exists under the existing source-query
    adapter protocol;
4.  adapter requires credential at construction/configuration boundary;
5.  credential is not present in snapshots/query/results/provenance;
6.  missing credential fails closed;
7.  provider availability is explicitly configured;
8.  adapter registration is owned by `OfficialConversationGateway` /
    existing executor;
9.  S1 query preparation cannot register/enable the adapter;
10. explicit execution remains required;
11. injected transport is supported;
12. no live network in tests;
13. no implicit IP geolocation;
14. no provider fallback;
15. no Memory/Learning/Planning/Execution;
16. no reservation/navigation;
17. no second selector/retrieval/evidence/Reasoning authority.

## 17. What RED must not freeze unnecessarily

The RED should not require:

-   a real API key;
-   a particular user's credential value;
-   modification of a real credential file;
-   live provider availability;
-   a new generic credential abstraction;
-   a new generic provider manager;
-   automatic provider activation;
-   provider fallback;
-   ratings/reviews/photos;
-   reservation APIs;
-   navigation APIs.

The provider-specific endpoint/request mapping belongs to the bounded
adapter, but only fields necessary for the already-certified S1 contract
should be tested.

## 18. R / C / D

After S2A reconciliation:

**R = 1**

**R-C2-LOCAL-S2A --- BOUNDED PLACE/BUSINESS PROVIDER SOURCE +
CREDENTIAL-GATED ADAPTER ENABLEMENT COMPOSITION.**

**C = 0**

Credential/configuration and enablement ownership are now reconciled
against existing canonical authorities.

**D = 0**

No constitutional/documentary contradiction remains.

## 19. Required next governed movement

The next justified movement is:

**RED CONTRACTUAL P7-C2-LOCAL-S2A --- BOUNDED PLACE/BUSINESS PROVIDER
SOURCE + CREDENTIAL-GATED ADAPTER ENABLEMENT COMPOSITION**

Only after explicit phase authorization.

The RED must remain test-only/documentary and use fake credential + fake
transport.

## 20. Frozen boundaries

Nothing in this reconciliation authorizes:

-   creating or supplying a real provider credential;
-   editing the Owner's credential store;
-   live provider calls;
-   productive provider activation;
-   implicit IP geolocation;
-   provider fallback;
-   global retrieval enablement;
-   background location;
-   durable precise-location storage;
-   reservation/booking;
-   navigation/routing;
-   Memory/Learning;
-   Planning/Execution;
-   Local Brain / Restaurant Agent / Maps Brain;
-   second selector/retrieval/evidence/Reasoning authority;
-   reopening S1, P7-C2-S1, P7-C2-SCI-S1, P7-R1/P7-C1, E1-B or Point 9.

## 21. Final disposition

**P7-C2-LOCAL / S2A PROVIDER CONFIGURATION + ENABLEMENT RECONCILIATION:
COMPLETE.**

Result:

`CANONICAL SECRET OWNER = EXISTING SecretsLoader` →
`CONFIGURATION OWNER = EXISTING RUNTIME ENVIRONMENT WIRING` →
`ENABLEMENT OWNER = EXISTING OfficialConversationGateway` →
`EXECUTION OWNER = EXISTING GovernedSourceQueryExecutor` →
`PROVIDER EDGE = EXACT RESIDUAL` → **R1 / C0 / D0** → **STOP BEFORE
RED**.

No productive code modified.
