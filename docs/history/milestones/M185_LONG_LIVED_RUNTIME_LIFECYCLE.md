# M185 — Long-Lived Runtime Lifecycle

## Objective

Make ROBY's official local runtime safe to keep alive for the full duration of the laptop session while preserving one composition, one process owner, explicit lifecycle metadata, graceful shutdown, and zero new cognitive authority.

## Scope

M185 adds:

- a long-lived lifecycle wrapper around the official M179 bootstrap;
- an exclusive local lease preventing concurrent official runtimes;
- persistent heartbeat metadata with private file permissions;
- generation tracking across process restarts;
- explicit running, degraded, stopped, and failed states;
- stale-heartbeat detection for operational diagnosis;
- graceful lease release and bootstrap shutdown on normal and exceptional exits;
- environment-driven lifecycle paths and timing;
- integration of the lifecycle with the official `main.py` console entrypoint.

## Operational sequence

1. `main.py` builds the M180 conversation runtime.
2. M185 acquires the exclusive local lease.
3. M179 starts the single M178 composition root.
4. The console processes turns through M177 and updates the heartbeat after activity.
5. Recoverable console failures are reduced to an exception class and mark the lifecycle degraded.
6. EOF, `/exit`, `/quit`, interruption, or exception closes M179 and releases the lease.
7. A later process creates a new lifecycle generation while preserving conversation, trace, and memory stores.

## Privacy and governance

The lifecycle store contains only owner/session identity, process id, generation, timestamps, state, and a sanitized exception class. It contains no prompts, responses, memory records, tool payloads, provider output, or secrets. Lease and heartbeat files are written with mode `0600`.

## Configuration

- `ROBY_RUNTIME_LEASE_PATH` (default `.roby/runtime.lease`)
- `ROBY_RUNTIME_HEARTBEAT_PATH` (default `.roby/runtime_heartbeat.json`)
- `ROBY_RUNTIME_HEARTBEAT_SECONDS` (default `30`)
- `ROBY_RUNTIME_STALE_SECONDS` (default `120`)

## Exclusions

M185 does not add background cognition, autonomous retries, process spawning, OS service installation, distributed locks, remote supervision, scheduled work, or self-healing tool/provider execution. It completes the local operational development runtime lifecycle only.
