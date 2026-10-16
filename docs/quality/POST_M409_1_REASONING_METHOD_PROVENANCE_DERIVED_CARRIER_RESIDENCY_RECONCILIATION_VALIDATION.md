# Post-M409.1 Reasoning Method Provenance Derived-Carrier Residency Reconciliation

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION

## Scope

Move only the neutral derived Method Provenance context carrier from the app-level
productive projection module into `core.governed_reasoning`.

## Current canonical surfaces

- `core/governed_reasoning/reasoning_method_provenance.py`
  - `GovernedReasoningMethodProvenanceFoundationV1`
  - `GovernedReasoningMethodProvenance`
- `core/governed_reasoning/derived_reasoning_method_provenance.py`
  - `GovernedReasoningMethodProvenanceContextItem`

## Preserved

- `app/governed_reasoning_method_provenance_productive_consumption.py`
- existing consumer/result/status semantics
- deterministic carrier identity, lineage and serialization
- neutral `ReasoningContextDerivedAssessment` compatibility

## Import boundary

The carrier is imported from its canonical submodule and intentionally not
re-exported eagerly from `core.governed_reasoning.__init__`.

## Local validation

Focused architecture validation: 35 PASS / 0 FAIL.

Owner closure requires:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
