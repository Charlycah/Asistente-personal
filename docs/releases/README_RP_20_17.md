# RP.20.17 — Cognitive source adapter removal

## Goal
Remove the ceremonial `CognitiveSourceAdapter`, which only renamed invocation of an existing callable to `resolve()`.

## Changes
- Removed `CognitiveSourceAdapter` from `app/cognitive_runtime_sources.py`.
- Runtime composition now passes the bound methods of `OperationalCognitiveSource` directly.
- Cognitive contributor source contracts are typed callables.
- Contributors invoke their source directly.
- Test doubles were migrated from `resolve()` to `__call__()`.
- Structural tests prevent reintroduction of the adapter.

## Preserved boundaries
Reasoning, planning, reflection and executive contributors still validate domain status, ownership, review requirements and prompt projection. Only the zero-value forwarding object was removed.

## Certification
Run:

```powershell
ruff check .
pytest -q
```
