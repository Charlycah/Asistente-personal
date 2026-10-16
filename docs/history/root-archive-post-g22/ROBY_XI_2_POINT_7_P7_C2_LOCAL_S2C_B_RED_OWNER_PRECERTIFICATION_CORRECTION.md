# ROBY XI.2 — P7-C2-LOCAL-S2C-B — RED OWNER PRE-CERTIFICATION CORRECTION

## Scope

This correction changes no productive code and does not alter the S2C-B contractual RED semantics.

It corrects only the RED artifact defects observed in the first Owner gate:

1. the contractual test import block was rewritten in a Ruff/isort-compatible first-party form;
2. `docs/quality/M361_QUALITY_BASELINE.json` was regenerated after the RED test was present.

The unrelated Owner-side `PermissionError` reading
`docs/M394_5_GOVERNED_EXTERNAL_RESOURCE_CONNECTIVITY.md` is not repaired or masked by this artifact.

## Local verification

- S2C-B focal contract: **7 PASS / 9 expected RED FAIL**.
- M361 reproducibility tests: **5 PASS / 0 FAIL**.
- `py_compile`: PASS.
- maximum contractual-test line length: **87**.
- productive code: unchanged.

## Expected Owner gate

Run:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

For RED certification, the only test failures attributable to S2C-B must be the same nine contractual RED failures. The M394.5 filesystem `PermissionError`, if it recurs, remains an environment/filesystem condition and prevents full Owner certification until resolved locally.

**STOP BEFORE GREEN.**
