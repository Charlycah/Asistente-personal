# Post-M409.1 Reasoning Method Provenance Productive-Projection Retirement

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION

## Retired

- `app/governed_reasoning_method_provenance_productive_consumption.py`
- historical positive productive-consumption architecture suite
- transitional residency guardrail requiring the app consumer

## Preserved

- `GovernedReasoningMethodProvenanceFoundationV1`
- `GovernedReasoningMethodProvenance`
- `GovernedReasoningMethodProvenanceContextItem`
- H8 fail-closed causal-join semantics

## HCPDQ reconciliation

HCPDQ no longer imports or inspects the retired app consumption result. It inspects
the canonical derived provenance carrier and current core paths. The H8 conclusion
remains fail-closed: provenance context and conflict analysis have no demonstrated
shared causal lineage.

## Local validation

Focused HCPDQ + Post-M409.1 architecture set: 51 PASS / 0 FAIL.

Owner closure requires:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
