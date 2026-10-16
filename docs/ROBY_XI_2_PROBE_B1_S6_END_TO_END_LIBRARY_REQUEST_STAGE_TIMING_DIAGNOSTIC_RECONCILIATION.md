# ROBY XI.2 — Probe B1-S6 — End-to-End Library Request Stage Timing

Status: DIAGNOSTIC RECONCILIATION.

## Purpose

Measure one canonical admitted local-library request end to end after B1-S5A showed
that an isolated first catalogue traversal completes on the productive library.

## Boundaries

The diagnostic changes no productive authority or semantics. It reuses the
existing conversation interceptor, catalogue/search authority, unified retrieval
execution gateway, selection validation path, and document reader. Timing wrappers
only emit stage boundaries, elapsed time, counts, filename, and content character
count; they do not print document content.

No cache, index, thread, timeout, security relaxation, catalogue limit change, or
new authority is introduced.

## Required productive observation

Run:

`python -m scripts.diagnostics.probe_b1_s6_end_to_end_library_request_stage_timing`

The first stage that emits START without a corresponding END is the next
reconciliation boundary. STOP before any productive CONTRACT RED/GREEN.
