# ROBY XI.2 — Probe B1-S5A — First Catalogue Internal Stage Timing — Diagnostic

## Baseline

B1-S5 First Catalogue Traversal Bottleneck — Surgical Reconciliation, locally certified.

## Purpose

Measure the already-demonstrated first-catalogue delay inside the existing CAP-17
catalogue owner without changing product semantics or the authorized library.

## Diagnostic surface

`scripts/diagnostics/probe_b1_s5a_catalogue_internal_stage_timing.py` is an external,
diagnostic-only subclass of `GovernedLocalLibraryCatalogueV1`. It mirrors the canonical
`_scan_entries()` sequence and reuses the canonical `_allowed_directories()` and
`_entry_from_path()` implementations. It activates the same governed `.roby/config.json`
route used by the productive runtime before resolving `ROBY_LOCAL_LIBRARY_ROOT`.

The probe reports cumulative timing/counts for `os.walk` advancement, directory
admission, filename sorting/suffix admission, admitted-file entry construction, final
entry sorting, and catalogue fingerprinting. Progress is emitted periodically so an
incomplete run still identifies the active stage. It prints no document content.

## Governance boundary

No product module, CAP-17 invariant, root configuration, catalogue limit, symlink
policy, cache, index, thread, timeout, or retrieval behavior is changed. `D:\Biblioteca`
is not hardcoded and must not be reorganized for this probe.

## Interpretation

The probe is evidence gathering only. A productive CONTRACT RED remains unauthorized
until the real filesystem run demonstrates the dominant internal stage and the
corresponding existing owner/seam.

## STOP

STOP after one diagnostic execution. Do not proceed to productive RED/GREEN or Probe
B2/B3/B4 until the output is reconciled.
