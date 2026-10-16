# APP BRAIN → INFRASTRUCTURE REPOSITORY LAYERING SEAM AUDIT

Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**

## Certified input baseline

**12,355 PASS · 0 FAIL · Ruff clean**.

## Audited anomaly

`application/brain/composition.py` imported and instantiated concrete persistence
implementations from `infrastructure.brain` and `infrastructure.repositories` even
though the composed application services already consume neutral repository contracts.

## Authority and residency findings

- `BrainService` consumes `BrainRepository`.
- `GoalProjectBrainAdapter` consumes `HouseholdGoalRepository` and
  `HouseholdProjectRepository`.
- `AtomicJsonBrainRepository`, `SQLiteHouseholdGoalRepository`, and
  `SQLiteHouseholdProjectRepository` remain valid infrastructure implementations.
- No duplicate Brain, Goal, Project, Memory, store, writer, manager, registry, or
  Composition Root was found or introduced.
- The affected BRAIN builders are diagnostic/non-visible-runtime composition surfaces;
  the official runtime Composition Root is unchanged.

## Bounded surgery

The existing BRAIN composition builders now receive repository contracts instead of
constructing infrastructure implementations:

- `BrainRepository`;
- `HouseholdGoalRepository`;
- `HouseholdProjectRepository`.

The diagnostic entry points construct the existing concrete repositories and inject them.
Builder names and application-level composition objects are preserved.

## Explicit exclusions

This surgery does not:

- move or retire any infrastructure repository;
- alter persistence schemas or paths;
- alter Memory authority or `OfficialMemoryGateway`;
- modify `app/runtime_root_factory.py`;
- audit or relocate `LocalIdentityProfileStore` or `JsonIdentityProfileStore`;
- touch `.roby` private/runtime state;
- retire any Post-M409.1 productive-consumption surface by analogy.

## Guardrail

`application/brain/composition.py` must not import `infrastructure.*` repository
implementations. Concrete repository construction belongs to a higher composition or
entry-point layer.

## Certification rule

This surgery remains **PENDING / NOT CERTIFIED** until the owner executes:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
