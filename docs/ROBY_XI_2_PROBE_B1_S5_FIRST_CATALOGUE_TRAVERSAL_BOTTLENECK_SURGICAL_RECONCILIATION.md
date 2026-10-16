# ROBY XI.2 — Probe B1-S5 — First Catalogue Traversal Bottleneck — Surgical Reconciliation

## Baseline and observed productive evidence

Baseline: B1-S4B Productive Root Resolution Diagnostic Harness — Surgical Green.
The productive diagnostic resolved the governed root `D:\\Biblioteca`, entered the first
`GovernedLocalLibraryCatalogueV1.catalogue()` call, printed `catalogue[1] START`, and did
not reach `catalogue[1] END` within the observed run.

## Canonical owner

The existing owner is `core/governed_local_library/catalogue.py`:
`GovernedLocalLibraryCatalogueV1`. No new catalogue, index, scanner, manager, agent,
thread, cache, or authority is admitted by this reconciliation.

## Exact first-catalogue call structure

`catalogue()` delegates to `_scan_entries()`, then computes `_catalogue_fingerprint()`.
The scan uses `os.walk(root, followlinks=config.follow_symlinks)`.

For every visited directory, `_allowed_directories()` sorts child directory names and,
for each child, may call `Path.is_symlink()`, `Path.resolve(strict=False)`, and root
containment validation.

For every filename, the suffix is checked first. An admitted suffix increments
`scanned_count` and calls `_entry_from_path()`. That method may perform
`is_symlink()`, `resolve(strict=True)`, root containment validation, `is_file()`,
`stat()`, relative-path construction, and deterministic identity hashing.

After collection, entries are globally sorted and the catalogue fingerprint is built.

## Boundedness finding

`max_catalogue_entries` bounds the number of successfully collected admitted entries;
it does not bound directory traversal itself. Directories and files with non-admitted
suffixes may therefore be traversed before the collection limit is reached. The
existing CAP-17 boundedness test protects entry truncation, not a filesystem-work or
elapsed-time budget.

This distinction is relevant to a large nested library but is not, by itself, proof of
the exact expensive primitive on the user's filesystem.

## Protected CAP-17 invariants

The following existing contracts remain authoritative and must not be weakened to fix
performance: authorized-root containment, read-only catalogue behavior, rejection of
root escape, no external symlink following under the configured policy, deterministic
entry identity, relative-path/provenance preservation, bounded catalogue entries, and
no document-content reads during cataloguing.

## Adjudication

B1-S5 narrows the productive hang to `_scan_entries()` or the immediately following
catalogue finalization, but source inspection alone cannot distinguish whether the
observed delay is dominated by `os.walk`, directory resolution, admitted-file
resolution/stat, sorting, or fingerprint construction.

Therefore no productive CONTRACT RED is authorized yet. In particular, no cache,
persistent index, parallel scanner, timeout, thread, relaxed containment check, symlink
policy change, root restructuring, or catalogue-limit change is justified by the
current evidence.

## Next governed increment

Authorize a diagnostic-only B1-S5A probe that instruments the existing catalogue scan
without changing product semantics. It must report coarse progress and cumulative
stage timing/counts for directory admission and admitted-file entry construction, plus
final sorting/fingerprint timing if reached. It must not print book contents or require
reorganizing `D:\\Biblioteca`.

Only after the real productive filesystem identifies the dominant stage may a minimal
contract RED be designed against the existing owner.

## STOP

STOP before productive RED/GREEN and before Probe B2/B3/B4.
