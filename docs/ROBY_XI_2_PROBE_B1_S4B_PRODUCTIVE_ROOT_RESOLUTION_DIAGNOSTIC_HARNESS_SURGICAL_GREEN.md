# ROBY XI.2 — Probe B1-S4B — Productive Root Resolution Diagnostic Harness — SURGICAL GREEN

## Baseline

This increment starts from the B1-S4 diagnostic package. Product code remains byte-identical.

## Reconciliation

The official product bootstrap resolves the canonical `.roby/config.json` through
`resolve_roby_config_path()` and activates it with `activate_roby_config()` before
runtime composition. `environment.ROBY_LOCAL_LIBRARY_ROOT` is thereby projected to
the process environment.

The B1-S4 harness incorrectly read `ROBY_LOCAL_LIBRARY_ROOT` before performing that
canonical activation, so a shell invocation could stop even though Desktop was
correctly provisioned from `.roby/config.json`.

## Surgical GREEN

Only `scripts/diagnostics/probe_b1_s4_library_stage_timing.py` is changed. Before
reading the library root it now performs the same canonical configuration activation
used by the product bootstrap and reports the resolved config path.

No product module, CAP-17 authority, catalogue semantics, retrieval semantics, Desktop,
Reasoning, capability registry, or `.roby/config.json` is changed. No cache, index,
thread, timeout, or alternate authority is introduced.

## Execution

From the project root, with the normal virtual environment:

```text
python -m scripts.diagnostics.probe_b1_s4_library_stage_timing
```

The expected diagnostic now begins by reporting `B1-S4 config=...` and the governed
root, then measures catalogue, document read, and interceptor boundaries.

STOP after collecting the single productive timing run. No productive CONTRACT RED
is authorized by this increment.
