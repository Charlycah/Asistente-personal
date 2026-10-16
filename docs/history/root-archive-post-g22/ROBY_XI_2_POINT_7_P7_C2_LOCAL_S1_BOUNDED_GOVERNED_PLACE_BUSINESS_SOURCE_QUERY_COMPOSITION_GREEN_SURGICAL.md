# ROBY XI.2 — P7-C2-LOCAL-S1
# BOUNDED GOVERNED PLACE / BUSINESS SOURCE-QUERY COMPOSITION — GREEN SURGICAL

## Status

**GREEN QUIRÚRGICO BUILT / OWNER CERTIFICATION REQUIRED**

Owner-certified RED entry:

- Ruff clean.
- 12,826 PASS.
- 10 expected RED FAIL.
- All RED failures were caused by the intentionally absent bounded composition seam.

## Productive change

Added exactly one productive module:

`app/governed_place_business_source_query_composition.py`

No existing productive module was modified.

The module defines:

- `GovernedPlaceBusinessSourceQueryCompositionStatus`;
- frozen `GovernedPlaceBusinessSourceQueryCompositionResult`;
- `GovernedPlaceBusinessSourceQueryComposition`.

## Governed responsibility

The seam performs only:

`EXPLICIT LOCAL/BUSINESS INTENT`
+ `BOUNDED EXPLICIT GEOGRAPHIC CONTEXT`
+ `BOUNDED QUERY / FIELDS / LIMIT`
→ `EXISTING GovernedConversationalSourceSelector`
→ `EXISTING GovernedSourceQuery`
→ `EXISTING GovernedSourceQueryContract.prepare(...)`
→ **PREPARED QUERY**
→ **STOP BEFORE RETRIEVAL**.

It does not perform network I/O.

## Geographic contract

Supported bounded forms are:

- textual locality through `near`;
- explicit `ll` + `radius`;
- explicit `ne` + `sw` bounds.

A plain locality string is normalized to `near`.

Missing or malformed geography fails closed as `NOT_AUTHORIZED`.

There is no implicit provider location fallback and no device-location acquisition.

## Provider edge

The seam recognizes only already-registered governed source IDs carrying the bounded
`foursquare` provider marker.

It does not register Foursquare in the canonical source registry and does not create
credentials or activate a provider.

Canonical ROBY semantics remain governed place/business source-query composition;
the provider remains at the adapter/source edge.

## Bounds

- maximum result limit: 20;
- maximum distinct requested fields: 12;
- query text must be non-empty;
- fields must be non-empty;
- registered provider source must already exist in `GovernedInformationSources`.

The existing query contract remains the final pre-retrieval validator.

## Frozen authority boundaries

The module creates no authority for:

- retrieval/network execution;
- reservation/booking;
- navigation/routing;
- Memory;
- Learning;
- Planning;
- Execution;
- provider fallback;
- background location;
- persistent location;
- a Local Brain, Restaurant Agent, Maps Brain, selector, retrieval coordinator,
  evidence authority or Reasoning authority.

## Local verification

Focal contractual suite:

`11 passed`.

Direct probe demonstrated:

- locality text becomes `near`;
- fields remain bounded source-query parameters;
- provider provenance marker is preserved;
- prepared query has `execution_enabled == False`.

`py_compile` passed.

Maximum productive-module line length: 84 characters.

Productive module SHA-256:

`598dcd07cedf897ec1dbd4e7334c74c660bae5711a4fe0ebf62497d05d1a03ac`

Ruff is not installed in the assistant execution environment, so no Ruff
certification is claimed here.

A full assistant-side pytest run was attempted but exceeded the execution timeout;
therefore no assistant-side full-suite certification is claimed.

## Owner gate

Run locally:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Expected disposition: Ruff clean, all former RED failures GREEN, and no regression
outside P7-C2-LOCAL-S1.

Do not advance beyond P7-C2-LOCAL-S1 until Owner certification is supplied.
