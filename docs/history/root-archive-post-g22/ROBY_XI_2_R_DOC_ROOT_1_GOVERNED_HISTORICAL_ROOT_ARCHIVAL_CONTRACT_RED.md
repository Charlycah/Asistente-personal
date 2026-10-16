# ROBY XI.2 — R-DOC-ROOT-1 Governed Historical Root Archival — CONTRACT RED

## Status

**CONTRACT RED — STOP BEFORE GREEN.**

## Owner

Existing repository/root documentation governance. No new documentary authority is introduced.

## Phenomenon

Twenty-six closed historical/reconciliation Point 7 documents remain in repository root even though the existing root policy reserves root for current canonical authorities and operational entry points. The historical owner already exists at `docs/history/root-archive-post-g22/` and the existing cleanup trace is `docs/history/CURRENT_TRUTH_ROOT_CLEANUP_MANIFEST.md`.

## Frozen scope

- MOVE exactly 26 named historical documents from root to `docs/history/root-archive-post-g22/`.
- Preserve each filename exactly.
- Preserve each file byte-for-byte; SHA-256 values are frozen in the RED test.
- Preserve exactly 8 static root Markdown authorities byte-for-byte.
- Preserve 3 evolvable master authorities at root without historical SHA-256 freezing:
  `ROBY_XI_2_CURRENT_TRUTH.md`, `ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md`, and
  `ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md`.
- DELETE: 0.
- Semantic rename: 0.
- Productive Python change: 0.
- New authority/registry/manager: 0.
- Semantic updates to Current Truth, Capability Registry, and Cognitive Inventory Master: out of scope for this archival contract; their content may evolve only under their own governed blocks.

## Contract surface

`tests/architecture/test_r_doc_root_1_governed_historical_root_archival_contract_red.py`

The contract freezes:

1. the exact 26-file move manifest;
2. the exact historical destination;
3. SHA-256 identity after archival;
4. absence of each moved artifact from root;
5. presence and byte identity of the 8 static protected root authorities;
6. root presence, without historical byte freezing, of the 3 evolvable master authorities;
7. the bounded cardinalities 26 MOVE / 8 BYTE-PROTECTED / 3 EVOLVABLE ROOT.

## Expected RED

On the certified pre-surgery baseline, the archival test must fail because the first historical candidate still exists in root and its archive destination does not yet exist. The protected-root, evolvable-root, and bounded-scope tests must already pass.

## GREEN boundary

GREEN may only perform the frozen structural moves and append the corresponding trace to the existing cleanup manifest. It must not change productive code or semantic authorities.

## STOP

After RED local certification: **STOP BEFORE GREEN**.
