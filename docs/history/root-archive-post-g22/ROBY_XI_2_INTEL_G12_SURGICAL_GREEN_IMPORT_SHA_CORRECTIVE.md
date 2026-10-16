# ROBY XI.2 — INTEL-G12 — SURGICAL GREEN IMPORT/SHA CORRECTIVE

## Scope
Integrates the user-corrected `app/governed_reasoning_runtime.py` import ordering
and reconciles only the three historical whole-file SHA guards that legitimately
changed as a consequence.

## Production file
`app/governed_reasoning_runtime.py`

Final SHA-256:
`bb5801db8fa7b3336106eb7dd323d6be03b8b06dc6d4cff3df3a7aa3202a804b`

No functional G12 logic was changed relative to the user-corrected file.

## Historical SHA guards reconciled
- Gate5C1
- Gate5C21
- Gate5C31

Each now expects the final production-file SHA above.

## Validation in assistant environment
- G12 + G11 + Gate5C1/C21/C31: 39 PASS.
- `app/governed_reasoning_runtime.py` compiles successfully.
- `docs/quality/M361_QUALITY_BASELINE.json` regenerated.
- Full Ruff/full pytest certification remains local.

## Required local certification
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
