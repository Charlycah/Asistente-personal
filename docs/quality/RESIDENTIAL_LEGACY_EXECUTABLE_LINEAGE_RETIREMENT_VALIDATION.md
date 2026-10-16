# Residential / MINI-PC / distributed-residence legacy executable lineage retirement

Status: **CLOSED / CERTIFIED**

Entry certified baseline: **13,209 PASS · 0 FAIL · Ruff clean**.

Owner certification result: **12,534 PASS · 0 FAIL · Ruff clean** (`pytest -q`: 12,534 passed in 275.25s; `ruff check .`: All checks passed).

## Governed scope

The implementation removes the legacy distributed-residence executable lineage only after de-wiring its optional productive seams. It preserves the neutral laptop runtime surfaces that merely share similar names.

Retired implementation roots:

- `core/residence_domain/`
- `core/connectivity_domain/`
- `core/physical_transport/`
- `core/governed_synchronization/`
- `core/resident_runtime_service/`
- `core/residential_node/`
- `core/residential_perception/`
- `core/residential_remote_presence/`
- `application/residential_perception/`
- `application/residential_remote_presence/`
- Residential connectivity/node/process entrypoints under `app/`
- `infrastructure/residential_deployment_dependencies.py`

Mixed surfaces reconciled, not removed:

- `app/runtime_root_factory.py` — only Residential Remote Presence wiring removed.
- `app/web_panel_sources.py` — Residential/Synchronization projections removed; Runtime/ExternalResources projections preserved.
- M405.1 — neutral InformationClassification taxonomy preserved.
- M406.1 — neutral localhost/read-only Web Panel and ExternalResources projection preserved.

Explicitly preserved:

- `app/resident_component_registry.py`
- local Web Panel runtime/read-model/HTTP service
- `domain/information_classification.py`
- Device/Presence authorities
- Camera/Vision authorities
- `core/external_resource_registry.py`
- Household organization/knowledge

Historical M396→M409 documents, ADRs, milestones, manifests and prior quality evidence are preserved without retroactive rewriting. Private `.roby` state is outside the surgery and must not be packaged.

Owner certification command sequence:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
