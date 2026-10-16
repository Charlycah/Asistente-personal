# ROBY XI.2 — Probe B1-S4 — Productive Library Search Stage Timing — DIAGNOSTIC RED

## Classification

DIAGNOSTIC EVIDENCE ONLY. Product code change: NONE. Contract RED: NOT YET AUTHORIZED.
New authority: NONE. Baseline: user-supplied Probe B1-S3 reconciliation ZIP, containing the locally certified B1-S2 surgical GREEN.

## Purpose

Measure the already-demonstrated productive B1 hang without changing search, catalogue, retrieval, reading, Unified Retrieval, Reasoning, Desktop, or CAP-17 semantics.

The diagnostic reuses the canonical classes and the governed `ROBY_LOCAL_LIBRARY_ROOT`. It does not hardcode `D:\\Biblioteca`.

## Diagnostic boundaries

The harness prints flushed START/END markers for:

1. the complete interceptor call;
2. every canonical `catalogue()` call, numbered in execution order;
3. the canonical `DocumentReadingService.read_text()` call;
4. the final interception rationale and response length, without dumping book content.

If execution stops after a START marker, that is direct evidence of the active stage. If all END markers appear, elapsed times distinguish material latency from response-projection concerns.

## Execution

From the project root, with the same environment used by productive ROBY:

`python -m scripts.diagnostics.probe_b1_s4_library_stage_timing`

Do not reformulate the request. The harness contains the original Probe B1 phrase and performs one diagnostic execution.

## Interpretation

- `catalogue[1] START` without its END: first full-root catalogue is the blocking boundary.
- `catalogue[1] END`, then `catalogue[2] START` without END: stale-selection revalidation / second catalogue is the blocking boundary.
- both catalogue END markers followed by `document_read START` without END: selected-document reading/parsing is the blocking boundary.
- `document_read END` but no `interceptor END`: remaining synchronous Unified Retrieval / conversation completion is the blocking boundary.
- `interceptor END` appears promptly: the direct CAP-17 path completed; the productive Desktop/caller projection must be reconciled separately rather than changing CAP-17.

## Governance

This probe does not add caching, indexing, threads, timeouts, background work, progress managers, or a parallel catalogue. It does not modify product code. Timing subclasses exist only inside the diagnostic script and delegate directly to the canonical implementations.

STOP after collecting the first clean output. Do not authorize CONTRACT RED until the timing evidence identifies an exact causal seam and its existing owner.
