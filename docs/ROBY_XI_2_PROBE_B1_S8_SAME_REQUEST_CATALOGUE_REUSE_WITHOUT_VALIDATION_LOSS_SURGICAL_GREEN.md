# ROBY XI.2 — Probe B1-S8 — Same-Request Catalogue Reuse Without Validation Loss — Surgical GREEN

## Baseline

B1-S7 CONTRACT RED, locally certified with the three new failures isolated from the twelve historical failures.

## Demonstrated seam

A successful local-library request catalogued the same governed root twice. B1-S6 measured about 8.5 seconds for each traversal. B1-S7 established that retrieval of the selected entry must not require the second full catalogue traversal while stale selected entries and provenance mismatches remain rejected.

## Surgical change

The existing `GovernedLocalLibraryCatalogueV1` remains the authority for authorized-root resolution and entry construction. It now exposes a narrow `validate_selected_entry()` operation that validates only the selected source reference against the governed root, reconstructs that one entry through the existing `_entry_from_path()` rules, and compares current identity and provenance.

`GovernedLocalDocumentRetrieverV1._validate_selection()` delegates to that existing catalogue authority instead of invoking `catalogue()` a second time.

No cache, index, manager, planner, agent, authority, background loop, timeout, thread, or alternate library path was introduced. Root containment, symlink policy, deterministic entry identity, current file metadata, and provenance checks remain owned by the existing catalogue.

## Local directed evidence in the build environment

- B1-S7 contract plus selected-document handoff and EPUB contracts: 34 passed.
- Broader directly related CAP-17 set: 79 passed.
- `py_compile` passed for both modified productive modules.
- Modified productive modules contain no lines longer than 88 characters.

Ruff is not available in the build environment; local certification remains authoritative for Ruff and the complete suite.

## STOP boundary

This GREEN does not authorize B2/B3/B4 until local certification and a productive B1 timing retry confirm the second full catalogue traversal is absent while the request still completes correctly.
