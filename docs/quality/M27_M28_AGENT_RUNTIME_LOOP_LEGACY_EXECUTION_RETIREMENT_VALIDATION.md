# M27/M28 Agent Runtime / Agent Loop Legacy Execution Retirement — Validation Record

## Scope

Retire only the disconnected historical execution lineage:

- `core/agent_runtime.py` (M27)
- `core/agent_loop.py` (M28)
- M32 LLM integration at the AgentLoop boundary
- M40 CognitivePipeline integration at the AgentLoop boundary
- their direct AgentLoop lineage tests

Preserve `core/llm_service.py`, `core/provider_router.py`, and `core/cognitive_pipeline.py`. No replacement runtime, Composition Root, provider route, or cognitive authority is introduced.

## Certified input baseline

**12,508 PASS · 0 FAIL · Ruff clean**.

## Expected owner baseline delta

- 4 M27 direct tests retired
- 5 M28 direct tests retired
- 7 M32 AgentLoop integration tests retired
- 6 M40 AgentLoop integration tests retired
- 1 architecture retirement guardrail added

Expected owner baseline after certification: **12,487 PASS · 0 FAIL · Ruff clean**.

## Owner certification

Status: **CLOSED / CERTIFIED**.

Owner certification on 2026-09-09:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q

All checks passed!
12487 passed in 240.88s (0:04:00)
```

Certified owner baseline: **12,487 PASS · 0 FAIL · Ruff clean**.
