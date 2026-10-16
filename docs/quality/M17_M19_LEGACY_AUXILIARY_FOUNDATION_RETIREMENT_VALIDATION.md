# M17/M19 Legacy Auxiliary Foundation Retirement — Validation Record

## Scope

Retire only the disconnected historical auxiliary foundations:

- `core/event_publisher.py` (M17)
- `core/memory_pipeline.py` (M19)
- their direct historical component tests

No current authority, Composition Root, store, writer, persistence path, event system, observability system, or Cognitive Memory admission policy is replaced or widened.

## Historical evidence

M17/M19 milestone and audit documents remain preserved in their existing historical locations. The retirement does not rewrite their historical meaning.

## Expected owner baseline delta

Certified input baseline: **12,513 PASS · 0 FAIL · Ruff clean**.

- 3 M17 direct tests retired
- 3 M19 direct tests retired
- 1 architecture retirement guardrail added

Expected owner baseline after certification: **12,508 PASS · 0 FAIL · Ruff clean**.

## Owner certification

Status: **CLOSED / CERTIFIED — 12,508 PASS · 0 FAIL · Ruff clean**.

Run:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
