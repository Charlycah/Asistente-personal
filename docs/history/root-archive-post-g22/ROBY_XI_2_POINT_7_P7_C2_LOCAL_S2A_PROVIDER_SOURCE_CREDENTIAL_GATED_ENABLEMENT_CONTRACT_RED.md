# ROBY XI.2 — POINT 7 / C2-LOCAL / S2A
# BOUNDED PLACE/BUSINESS PROVIDER SOURCE + CREDENTIAL-GATED ADAPTER ENABLEMENT
# CONTRACT RED

## Status

**RED CONTRACTUAL BUILT / OWNER CERTIFICATION PENDING / NO GREEN IMPLEMENTED**

Entry state: **12,836 PASS / 0 FAIL / Ruff clean**.

Authorized residual:

`R-C2-LOCAL-S2A — BOUNDED PLACE/BUSINESS PROVIDER SOURCE + CREDENTIAL-GATED ADAPTER ENABLEMENT COMPOSITION`.

## Contract frozen by RED

The future GREEN must reuse the existing authorities:

- `SecretsLoader` for private provider credential lookup;
- runtime environment wiring for provider availability/configuration;
- `OfficialConversationGateway` for explicit adapter enablement/registration;
- `GovernedSourceQueryExecutor` for execution;
- P7-C2-LOCAL-S1 for bounded query preparation.

The RED requires a canonical bounded source declaration with source id
`foursquare_places`, a `FoursquareGovernedSourceAdapter`, credential-gated
construction, injected transport for tests, explicit gateway enablement and an
environment builder using the existing secrets/configuration surfaces.

The information-source declaration itself must remain network-disabled and
automatic-fetch-disabled. The executable adapter may report network capability but
must remain automatic-fetch-disabled.

## Constitutional distinctions

`SOURCE DECLARATION ≠ ADAPTER ENABLEMENT`

`PROVIDER AVAILABLE ≠ NETWORK CALL AUTHORIZED NOW`

`QUERY PREPARATION ≠ ADAPTER ENABLEMENT ≠ NETWORK EXECUTION`

`CREDENTIAL ≠ QUERY DATA ≠ EVIDENCE ≠ MEMORY`

## Fail-closed requirements

Missing/blank provider credential must leave the provider unavailable. The secret
must not appear in snapshots, governed queries, result metadata or provenance.
P7-C2-LOCAL-S1 must remain unable to read credentials, register adapters or execute
retrieval.

No implicit IP-geolocation fallback is authorized.

## Test boundary

Contract tests use only fake credentials and injectable fake transport. They do not
make a live provider call and do not modify a real credential store.

## Explicitly out of scope

The RED does not authorize:

- a real provider credential;
- productive provider activation;
- live network access;
- global `retrieval_enabled=True`;
- provider fallback;
- background or persisted precise location;
- reservation/booking;
- navigation/routing;
- Memory/Learning writes;
- Planning/Execution;
- a new selector, retrieval executor, evidence authority, Reasoning authority,
  Local Brain, Restaurant Agent, Maps Brain or provider manager.

## Owner gate

Run:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Expected RED evidence: prior certified behavior remains intact and only the new S2A
contract fails because the provider source/adapter/enablement composition is absent.

**STOP after Owner RED certification. Do not advance to GREEN without explicit
Owner authorization.**
