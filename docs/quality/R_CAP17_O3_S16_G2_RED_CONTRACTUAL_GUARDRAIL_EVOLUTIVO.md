# R-CAP17-O3-S16-G2 — RED contractual: historical SHA vs evolvable registry

**Status:** RED CONTRACTUAL; STOP BEFORE GREEN. No baseline promotion.

## Authority and evidence
- R-DOC-S1 historical test fixes `ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md` at SHA-256 `973b41c614b401915d0429bb3206f742fbfc1057779fd8fc57786130b6eeb320` and compares the *current root* to that digest.
- R-DOC-ROOT-1 governed historical archival contract explicitly classifies the registry, Current Truth and Cognitive Inventory master as evolvable root authorities **without historical SHA-256 freezing**; only eight static root authorities are byte-protected.
- The Windows S16 root registry SHA-256 is `93b96051c7af1e58cc88fe8c9026e716ae1974a36abfad48e3e7e442403bc24e`; the `docs/` copy is a distinct file and is not a substitute for the root authority.
- Historical S1 digest is evidence, **not** a license to rewrite or restore the current registry. Later governed evolution remains subject to its own contracts.

## Frozen RED scope
- Add only `tests/architecture/test_r_cap17_o3_s16_g2_evolvable_registry_guardrail_contract_red.py` and this record.
- Preserve S1 historical hash literal and all archival manifests, protected static hashes, and master authority files.
- RED asserts that the S1 live-root guardrail must not call `_sha256` to compare the evolvable master to its historical digest. It intentionally fails on the present S1 contract; two supporting checks should pass.
- No productive Python, existing test, root master, owner, runtime wiring, M377 RED, or model acquisition changes.

## Required Windows certification
```
ruff check .
pytest -q tests/architecture/test_r_cap17_o3_s16_g2_evolvable_registry_guardrail_contract_red.py
```
Expected: **2 PASS / 1 intentional FAIL**. Do not run GREEN until owner confirms this RED evidence. Existing S1 guardrail remains independently failing on current root, and M377 47 intentional RED remain HOLD.

## GREEN design boundary (not authorized here)
Retain the historical S1 SHA as trace, preserve eight static byte-frozen authorities and archive hashes, and reconcile only the obsolete live-root comparison with the later R-DOC-ROOT-1 evolvable policy. No simple hash replacement and no deletion of historical evidence. STOP.
