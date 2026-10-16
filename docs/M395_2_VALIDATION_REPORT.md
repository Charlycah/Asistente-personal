# M395.2 — Validation Report

## Scope

Bootstrap and composition consolidation only. No new functional capability,
authority, gateway, provider, resident, or external I/O was introduced.

## Structural changes

- Added `app.runtime_bootstrap_contract` as a dependency-neutral home for stable
  runtime bootstrap identifiers.
- `roby_config` and `hal_config` no longer import the concrete runtime factory.
- The audited five-module bootstrap SCC is removed.
- `RuntimeCompositionRoot.compose()` remains the only public composition method
  but delegates cognitive contributor wiring to a private subordinate helper.
- `OFFICIAL_RUNTIME_FACTORY` remains re-exported by `runtime_root_factory` for
  compatibility.
- No secondary composition root was created.

## Validation

- Python compileall: passed.
- Focused bootstrap/composition/configuration tests: 47 passed.
- Default pytest collection: 10,312 tests.
- Full collection executed in four disjoint blocks:
  - 2,578 passed
  - 2,578 passed
  - 2,578 passed
  - 2,578 passed
- Total: **10,312 passed, 0 failed**.
- M361 quality baseline regenerated after the structural changes.

## Ruff

Ruff is not installed in the execution environment used to build this handoff.
Final certification therefore requires `ruff check .` in the normal ROBY venv.
