# APP → MEMORY GATEWAY LAYERING SEAM AUDIT

Status: **CLOSED / CERTIFIED — owner baseline 12,355 PASS · 0 FAIL · Ruff clean**

## Baseline

Owner-certified input baseline: **12,354 PASS · 0 FAIL · Ruff clean**.

## Audited anomaly

`application/brain/composition.py` imported and instantiated
`app.memory_consolidation.OfficialMemoryGateway`.

## Authority and residency findings

- `OfficialMemoryGateway` remains the single operational Memory gateway and writer.
- `OfficialMemoryBrainAdapter` is read-only and already depends on `core.memory.MemoryStore`.
- `app/runtime_root_factory.py` already constructs the official operational gateway.
- BRAIN composition builders are not wired into the visible runtime.
- Their productive callers are diagnostic scripts.
- `CanonicalMemoryFacade` is not a layering successor because it also resides in `app` and delegates to `OfficialMemoryGateway`.

## Surgical decision

Invert only the diagnostic composition dependency:

- `application.brain.composition` accepts `MemoryStore`;
- diagnostic scripts construct the existing `OfficialMemoryGateway`;
- no new authority, store, writer, persistence, runtime wiring or behavior is introduced;
- `runtime_root_factory.py` is unchanged.

## Protected surfaces

No retirement by analogy is permitted for:

- `governed_evidence_acquisition_productive_consumption.py`;
- `governed_explanatory_model_productive_consumption.py`;
- `governed_independence_authorization_productive_consumption.py`;
- `governed_multi_hypothesis_productive_consumption.py`.

## Certification rule

Owner certification executed the official gate successfully:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
