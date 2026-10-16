# ROBY XI.2 — Probe B1-S7 — Same-Request Catalogue Reuse Without Validation Loss — CONTRACT RED

## Evidence entering this increment

B1-S6 measured one productive request over the governed local library at about 17.1 s.
The first catalogue took about 8.55 s and the validation catalogue about 8.47 s;
document reading took about 0.02 s. The request completed successfully.

## Existing owner and seam

`GovernedLocalLibraryCatalogueV1.search()` creates the governed catalogue used for
selection. `GovernedLibrarySelection` already preserves the selected `entry_id`,
`source_reference`, and `catalogue_fingerprint`. The existing
`GovernedLocalDocumentRetrieverV1._validate_selection()` calls `catalogue()` again
and uses that second full traversal to re-establish freshness, membership, and
provenance before reading.

The owner remains the existing governed local-library handoff/retrieval path. This
increment does not authorize a cache, index, manager, planner, thread, timeout, or
new authority.

## Contract RED

For one same-request search -> explicit selection -> retrieval flow:

1. the initial search may catalogue the authorized root once;
2. retrieval of that selection must not require a second full catalogue traversal;
3. the selected entry must still be rejected if it became stale after selection;
4. provenance mismatch must still be rejected;
5. document content must continue to be read through the existing document reader;
6. authorized-root, containment, deterministic identity, provenance, and stale-entry
   protections remain owned by the existing CAP-17 surfaces.

The contract deliberately specifies observable behavior rather than prescribing the
GREEN implementation. In particular, passing the RED by merely deleting validation
is forbidden by the stale-entry and provenance assertions.

## STOP boundary

This is CONTRACT RED only. No productive implementation is authorized in this
increment. B2/B3/B4 remain stopped until B1 is productively acceptable.
