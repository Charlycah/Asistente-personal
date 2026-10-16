# ROBY XI.2 — Probe B1-S3 — Productive Library Search Hang Reconciliation

## Classification

DOCUMENTARY / DIAGNOSTIC RECONCILIATION ONLY.

Product change: NONE. Contract RED: NOT YET AUTHORIZED. New authority: NONE.
Baseline: Probe B1-S2 — Conversational Library Query Admission — SURGICAL GREEN, locally certified by the user with Ruff clean and 12 historical failures / 13305 passes.

## Productive evidence that opened this reconciliation

After B1-S2, the user repeated the original productive request against the real authorized library rooted at `D:\\Biblioteca`:

`Roby, busca en la biblioteca el libro Robots e Imperio y decime cuando lo encontras`

The UI remained at the submitted request and no ROBY response was produced. This differs from pre-B1-S2 behavior, which returned an immediate NO_MATCH containing the over-broad conversational query.

This is sufficient to keep Probe B1 productively RED, but not sufficient by itself to identify the blocking call.

## Canonical route verified in the certified source

The productive user-library path remains owned by existing authorities:

1. `GovernedLocalLibraryConversationInterceptionPort.intercept(...)` admits the request.
2. B1-S2 `_search_query(...)` bounds the demonstrated phrase to `Robots e Imperio`.
3. `GovernedLocalLibraryConversationV1.handle_user_request(...)` converges into `handle_admitted_request(...)`.
4. `GovernedLocalLibraryCatalogueV1.search(...)` calls `catalogue()` synchronously.
5. `catalogue()` calls `_scan_entries()` and walks the authorized root with `os.walk(...)`, resolving/stat-ing admitted files up to `max_catalogue_entries` (productive default 10,000).
6. For a selected match, `GovernedLocalDocumentRetrieverV1.retrieve_selected(...)` calls `_validate_selection(...)`.
7. `_validate_selection(...)` calls `self._library.catalogue()` again and compares the catalogue fingerprint before selecting the entry.
8. The selected document is then synchronously read by `DocumentReadingService.read_text(...)` through Unified Retrieval before `intercept(...)` can return its `GovernedOperationalInterception` response.

There is no asynchronous/background boundary in this route and no intermediate user-facing progress result in the inspected path.

## Exact structural observation

A successful unique conversational lookup can therefore perform at least two complete catalogue constructions in the same foreground request:

- first catalogue: `GovernedLocalLibraryCatalogueV1.search(...) -> catalogue()`;
- second catalogue: `GovernedLocalDocumentRetrieverV1._validate_selection(...) -> catalogue()`.

Each catalogue construction re-walks the authorized root and recomputes entry metadata/fingerprint. With a real root containing thousands of books, this is a credible latency/blocking candidate.

The second scan is not accidental dead code: it currently protects the stale-catalogue/provenance invariant by requiring the selected entry to belong to a catalogue whose fingerprint still matches the search-time selection.

## What is NOT demonstrated

The productive observation does NOT yet prove which of the following consumed the foreground request:

- first catalogue scan;
- second catalogue/fingerprint validation scan;
- selected-document read/parsing;
- Unified Retrieval execution around the bound retriever;
- response projection after the interceptor returns.

The assistant environment cannot execute against the user's real `D:\\Biblioteca`, so elapsed-time behavior of that root cannot be truthfully reproduced here.

Accordingly, it would be premature to add caching, threads, timeouts, a background scanner, a new index, a progress manager, or a second catalogue authority.

## Governance reconciliation

The Master Capability Registry names `GovernedLocalLibraryCatalogueV1 + DocumentReading + Knowledge + governed_reasoning + CAP-11 Episode` as the CAP-17 authority boundary and requires pre-change identification of productive callers and protected contracts. It also forbids another Reasoning, Planning, retrieval or Episode authority.

The current evidence does not justify changing those ownership boundaries. If a latency residual is demonstrated, the first owner to test is the existing CAP-17 catalogue/retrieval path, not Desktop and not a new manager.

## Adjudication

`PROBE B1-S3 — RECONCILED / PRODUCTIVE HANG CONFIRMED / EXACT BLOCKING CALL NOT YET PROVEN`

- B1-S2 query admission remains locally GREEN.
- Probe B1 end-to-end remains productively RED.
- Structural candidate: repeated synchronous full-root catalogue construction on the foreground request.
- Exact causal seam: NOT YET CERTIFIED.
- CONTRACT RED: NOT YET AUTHORIZED.
- Product code change: NOT AUTHORIZED.

## Next governed evidence step

Before any GREEN or optimization, obtain bounded timing evidence from the existing owner boundary. The next diagnostic must distinguish at minimum:

A. entry into `library.search(query)` and return from the first catalogue/search;
B. entry into selected-document retrieval and return from stale-selection validation (second catalogue);
C. return from `DocumentReadingService.read_text(...)` / Unified Retrieval;
D. return of the final operational interception to the productive conversation caller.

The diagnostic must not alter search semantics, add a new authority, cache the catalogue, introduce background work, or repair the symptom. Once one boundary is shown not to return (or to consume the material latency) on `D:\\Biblioteca`, that exact seam can be evaluated for a minimal CONTRACT RED.

STOP before CONTRACT RED.
