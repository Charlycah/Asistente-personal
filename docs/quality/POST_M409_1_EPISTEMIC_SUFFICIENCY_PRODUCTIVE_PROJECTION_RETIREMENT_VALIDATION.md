# Post-M409.1 Epistemic Sufficiency Productive-Projection Retirement

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION

## Retired

- `app/governed_epistemic_sufficiency_productive_consumption.py`
- historical positive productive-consumption architecture suite
- transitional residency guardrail requiring the app consumer

## Preserved

- `GovernedEpistemicSufficiencyAssessmentFoundationV1`
- `GovernedEpistemicSufficiencyAssessment`
- `GovernedDerivedEpistemicSufficiencyContextAssessment`
- neutral `ReasoningContextDerivedAssessment` compatibility
- H2 fail-closed causal-join semantics

## HCPDQ reconciliation

HCPDQ scripts no longer import or inspect the retired app consumption result.
They use the canonical derived Sufficiency carrier or canonical core paths for
read-only structural evidence. The H2 conclusion remains that metadata/context
availability is not causal evidence for abstention.

## Local validation

Focused HCPDQ + architecture set: 47 PASS / 0 FAIL.

Final owner certification requires:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
