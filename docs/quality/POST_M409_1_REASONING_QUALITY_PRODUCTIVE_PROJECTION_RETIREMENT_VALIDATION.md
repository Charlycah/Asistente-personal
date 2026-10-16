# Post-M409.1 Reasoning Quality Productive-Projection Retirement

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION

## Scope

Retire the app-level Reasoning Quality productive-consumption adapter after the
derived carrier obtained canonical residency under `core.governed_reasoning`.

## Retired

- `app/governed_reasoning_quality_productive_consumption.py`
- its historical positive productive-consumption architecture suite
- the transitional residency guardrail that required the app consumer

## Preserved

- `GovernedReasoningQualityAssessmentFoundationV1`
- `GovernedDerivedReasoningQualityContextAssessment`
- neutral `ReasoningContextDerivedAssessment`
- the certified import-boundary rule preventing eager package-root re-export

## Reconciliation

The Method Provenance architecture test now composes the canonical Reasoning
Quality Foundation and neutral derived carrier directly. It no longer imports a
historical Reasoning Quality productive-consumption test or adapter.

## Local validation

Focused architecture set: 35 PASS / 0 FAIL.

Final closure requires the owner gate:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
