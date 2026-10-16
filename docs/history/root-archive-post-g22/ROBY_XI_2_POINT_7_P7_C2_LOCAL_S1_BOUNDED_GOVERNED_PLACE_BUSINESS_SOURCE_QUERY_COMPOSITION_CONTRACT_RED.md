# ROBY XI.2 — P7-C2-LOCAL-S1
# BOUNDED GOVERNED PLACE / BUSINESS SOURCE-QUERY COMPOSITION — CONTRACT RED

## Status

**RED CONTRACTUAL / PRODUCTIVE SEAM INTENTIONALLY ABSENT / OWNER CERTIFICATION REQUIRED**

Entry baseline: **12,825 PASS · 0 FAIL · Ruff clean**.

## Residual

`R-C2-LOCAL-S1 — EXPLICIT LOCAL/BUSINESS INFORMATION NEED + BOUNDED GEOGRAPHIC CONTEXT → REGISTERED GOVERNED FOURSQUARE PLACE-SEARCH SOURCE QUERY CONTRACT → STOP BEFORE RETRIEVAL EXECUTION.`

Canonical ROBY semantics remain **GOVERNED PLACE / BUSINESS SOURCE QUERY**. Foursquare is a bounded provider-edge candidate, not a canonical cognitive authority.

## Required contract

The future seam must:

1. require explicit local/business/place/restaurant information intent;
2. require bounded explicit geographic context;
3. support textual locality (`near`) without requiring precise device location;
4. fail closed when geography is absent, preventing implicit IP-geolocation fallback;
5. accept bounded query text, fields and result limit;
6. reuse `GovernedConversationalSourceSelector`, `GovernedSourceQuery`, `GovernedSourceQueryContract` and the existing source/retrieval architecture;
7. preserve the provider at the adapter/source edge rather than creating a vendor-shaped ROBY authority;
8. STOP before retrieval/network execution;
9. preserve source/provider provenance for the downstream evidence path;
10. preserve `DISCOVERY ≠ RESERVATION`;
11. preserve `PLACE DISCOVERY ≠ NAVIGATION`;
12. create no Memory, Learning, Planning or Execution authority;
13. create no Local Brain, Restaurant Agent, Maps Brain, selector, retrieval coordinator, evidence authority or Reasoning authority.

## Explicitly out of scope

This RED does not authorize API credentials, live Foursquare calls, production provider registration, automatic fallback, IP geolocation, background location access, durable location storage, reservations, navigation, ratings/reviews as truth, Memory/Learning writes, Planning/Execution, or global generic retrieval enablement.

## Expected RED

The contract expects the productive module:

`app.governed_place_business_source_query_composition`

with type:

`GovernedPlaceBusinessSourceQueryComposition`

and bounded `compose(...)` semantics.

The module is intentionally absent in RED. Contract tests must fail only for that missing seam; existing architecture remains unchanged.

## Owner gate

Run locally:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Expected disposition: Ruff clean and only the new RED tests failing because the bounded composition module is missing. Do not advance to GREEN until Owner certification is supplied.
