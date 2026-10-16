# ROBY XI.2 — Current Truth Consolidation + Root Cleanup — Validation Record

## Scope

Documentary and repository-root organization only. No productive Python source was edited.

## Verified in the integration workspace

- `python scripts/clean_project_caches.py` — PASS.
- `python scripts/generate_quality_baseline.py` — PASS.
- Regenerated `docs/quality/M361_QUALITY_BASELINE.json` compared with the source ZIP baseline — **exact JSON equality**.
- Focused documentation/root-authority regression set — **75 PASS / 0 FAIL**.
- Root documentary surface reduced from **231 MD/TXT files** to **12 MD files**.
- Historical root documents archived/preserved: **220**.

## Environment limitations

- `ruff check .` could not be executed because Ruff is not installed in the available runner and was not bundled in the project virtual environment.
- Full `pytest -q` was started twice and produced no failures in the executed prefix, but the external runner timeout stopped it before completion. Therefore this workspace does **not** claim a new full-suite certification.

## Certification rule

The source baseline remains the last certified baseline: **POST-G22 — 14,189 PASS · 0 FAIL · Ruff clean**.

Before treating this documentary cleanup package as a newly certified handoff, run in the normal ROBY development environment:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Expected architectural result: no productive baseline change and no regression caused by root-document relocation.
