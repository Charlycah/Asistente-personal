# M395.5 — Validation Report

## Scope

M395.5 synthesizes existing orchestrators without adding capabilities or authorities.

## Structural result

- `OfficialConversationGateway.__init__`: 164 -> 28 lines.
- Historical `CanonicalCognitiveCore` constructor lineage remains on line 52.
- Cognitive evidence and governed conversation services are initialized through private phases of the same gateway.
- `CognitivePipeline.process_turn`: 325 -> 95 lines.
- Pre-memory observation is isolated in `_run_pre_memory_observations()`.
- Per-turn system-prompt assembly is delegated to `_build_system_prompt_for_turn()`.
- No Desktop refactor was included.
- No new orchestrator, manager, gateway, planner, coordinator, registry, or composition root was introduced.

## Validation

- New M395.5 architectural invariants: 6.
- Focused validation: 65 passed.
- Default collection: 10,330 tests.
- Full default suite executed in eight disjoint chunks: 10,330 passed, 0 failed.
- `python -m compileall`: clean.
- M361 quality baseline regenerated and reproducibility test passed after synchronization.
- `.roby` runtime state restored from the certified M395.4 handoff before packaging.

## Pending local certification

Ruff is not available in the packaging environment. Final certification requires:

```text
ruff check .
python scripts/generate_quality_baseline.py
pytest -q
```

Expected pytest result: `10330 passed`.
