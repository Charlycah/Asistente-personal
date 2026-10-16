# Post-M409.1 Epistemic Sufficiency Derived-Carrier Residency Reconciliation

Status: IMPLEMENTED / PENDING OWNER CERTIFICATION

## Scope

Move only the neutral derived Epistemic Sufficiency context carrier from the
app-level productive projection module into `core.governed_reasoning`.

## Current canonical surfaces

- `core/governed_reasoning/epistemic_sufficiency.py`
  - `GovernedEpistemicSufficiencyAssessmentFoundationV1`
  - `GovernedEpistemicSufficiencyAssessment`
- `core/governed_reasoning/derived_epistemic_sufficiency_assessment.py`
  - `GovernedDerivedEpistemicSufficiencyContextAssessment`

## Preserved

- `app/governed_epistemic_sufficiency_productive_consumption.py`
- existing consumer/result/status semantics
- deterministic carrier identity, lineage and serialization
- neutral `ReasoningContextDerivedAssessment` compatibility

## Import boundary

The carrier is imported from its canonical submodule. It is intentionally not
re-exported eagerly from `core.governed_reasoning.__init__`.

## Local validation

Focused architecture validation: 31 PASS / 0 FAIL.

Owner closure requires:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
