# ROBY XI.2 — Governed Reasoning / Learning source-neutral residency reconciliation

## Scope

Governed implementation only. Productive runtime reachability remains unchanged.

## Structural delta

- Removed `core/governed_reasoning/abstraction_learning_bridge.py`.
- Added `app/governed_relational_abstraction_learning_bridge.py`.
- Preserved `GovernedRelationalAbstractionLearningBridge` as the cross-capability
  integration type.
- Replaced Curiosity-specific evaluation output and `PreferenceLearning`
  aggregation with the existing source-neutral M369 chain:
  `LearningFoundation` → `GovernedLearningCandidateM369EvaluationV1`.
- Existing G6 explicit-human approval, G7 materialization and Memory writer/gateway
  remain the only downstream authority/writer path.
- No Composition Root/runtime registration was added.

## Governance invariants

- Reasoning owns abstraction production only.
- Learning owns evaluation/admission.
- Human approval remains mandatory for durable promotion.
- Memory persistence remains exclusively behind the existing governed Memory path.
- No new manager, authority, store, writer or evaluator.
- Absolute `core -> app` imports after reconciliation: 0.

## Local focused validation

The implementation worktree passed the focused HCE + G6/G7/G8 contract set before
packaging. A dedicated residency guardrail is included.

## Certification state

**IMPLEMENTED / PENDING OWNER CERTIFICATION**

Owner gate:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
