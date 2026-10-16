# M367 Historical Inventory & Diagnostic Retirement + M368/M379/CCI-03 Contract Reconciliation

## Status

**IMPLEMENTED / PENDING OWNER CERTIFICATION**

Certified input baseline: **12,471 PASS · 0 FAIL · Ruff clean**.

## Retired executable surfaces

- `app/user_profile_model.py` + `core/user_profile_model.py` (M367.2)
- `app/project_knowledge_model.py` + `core/project_knowledge_model.py` (M367.3)
- `app/goals_objectives_model.py` + `core/goals_objectives_model.py` (M367.4)
- `app/context_state_model.py` + `core/context_state_model.py` (M367.5)
- `app/mental_model_stabilization.py` + `core/mental_model_stabilization.py` (M367.7)

Their positive historical milestone tests are retired with the executable surfaces. Historical milestone documentation is preserved.

## Explicitly retained

- M367.1 `app/internal_world_model_foundation.py`: evolved/current governed World Model façade under M391/M392.
- M367.6 `app/priority_reasoning.py` and current domain implementation: productive priority-reasoning capability.
- M368.1 `PlanningFoundation`: current read-only/non-executing planning authority.
- M379 `PersonalOrganizationAuthority`: current personal-organization façade.

## Contract reconciliation

M368.1 Planning now points directly to existing specialized owners instead of retired M367 umbrella inventories. M379 GOALS points to `core.household_goals:HouseholdGoalManager`, while cognitive goals remain separate. CCI-03 now uses current `MentalModel` and `GovernedMentalModelDecisionEvidenceProjector` evidence before the governed decision advisory and causal proof.

## Negative guarantees

No new authority, manager, registry, store, writer, persistence path, runtime, provider, background process or Composition Root was introduced.

## Validation

Focused validation: **63 PASS** across retained M367.1/M367.6, reconciled M368.1/M379, M367 retirement guardrails, current mental-model decision causality, and whole-system CCI certification. Pytest collection after the surgery is **12,427 tests** (50 historical positive tests retired; 6 replacement/reconciliation guardrails added). A local full-suite attempt was blocked first by absent private `.roby/config.json`; with a temporary non-packaged placeholder it ran without observed failure until the execution environment timeout, so this is not treated as owner certification. Final owner gate remains:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
