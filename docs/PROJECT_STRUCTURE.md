# ROBY project structure

ROBY keeps production code grouped by responsibility while retaining a small
amount of historical package-local test placement for stable discovery and
ownership.

## Operational code

- `app/`: official runtime composition, resident services and presentation.
- `application/`: application contracts and use cases.
- `core/`: cognitive capabilities and consolidated historical foundations.
- `domain/`: domain models and rules.
- `infrastructure/`: local persistence and external-device adapters.
- `interfaces/`: console, voice and other input/output boundaries.
- `m3/`, `m4/`, `m5/`, `m6/`, `m7/`: stable historical packages still used
  by the certified runtime.

## Tests

- `tests/`: main behavioral, integration and certification suite.
- `core/tests/`: tests owned by foundational core components.
- package-local `tests/` below `m3`, `m4` and `m7`: tests retained beside the
  historical package they certify.

The distributed locations are intentional. Moving them only for appearance
would create broad import and discovery churn without improving ROBY's runtime.
New cross-cutting and refinement tests belong in the root `tests/` directory.

## Documentation

- `docs/refinement/`: RP and BRP behavioral refinement records.
- `docs/milestones/`: historical milestone records.
- `docs/adr/`: architectural decisions.

## Local state

- `.roby/`: ROBY's private household runtime state.
- `.env`, `credentials.json`, `token.pickle`: local operational configuration
  used by this private household installation.

## Transient artifacts

`__pycache__`, `.pytest_cache`, `*.pyc` and `*.pyo` are generated artifacts,
not source. Run this command whenever a clean project tree is desired:

```bash
python scripts/clean_project_artifacts.py
```
