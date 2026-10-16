# M398.1 — Validation Record

## Increment

**M398.1 — Physical Transport Constitution**

## Baseline inherited

- M397.11 formally closed.
- 10,687 tests passed in the user's official environment.
- Ruff clean.
- Zero known regressions.

## Validation performed in build environment

The build environment does not provide Ruff, so Ruff certification is deliberately
left to the user's official project environment.

The test suite was executed by partitions because the monolithic invocation exceeded
the container execution-duration limit without reporting a test failure. The exact
default collection contains **10,702 tests**.

Validated partitions:

- `tests/architecture`: 1,463 passed;
- four exhaustive partitions of root `tests/test_*.py`: 2,265 + 2,303 + 2,240 +
  2,258 passed;
- project-collected tests under `core/tests`, `m3`, `m4` and `m7`: 173 passed.

Total: **10,702 passed, 0 failed**.

Additional checks:

- M398.1 focused tests: 15 passed;
- M397.11 + M398.1 focused compatibility run: 26 passed;
- repository Python AST parse: clean;
- M361 quality baseline regenerated after the final source formatting change;
- M361 reproducibility test: passed;
- no concrete network runtime introduced by M398.1.

## Certification gate remaining

Run in the official environment:

```text
ruff check .
python scripts/generate_quality_baseline.py
pytest -q
```

Expected full-suite count: **10,702 passed**. If Ruff is clean and the full suite passes,
M398.1 may be certified as the official baseline for the next M398 increment.
