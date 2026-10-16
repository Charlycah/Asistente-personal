# ROBY XI.2 — MASTER PLAN

## Owned Local Music Playback Stop — CONTRACT RED

### Classification

- Block: CONTRACT RED
- Starting state: PRE-RED reconciled
- Selected residual: `OWNED_LOCAL_MUSIC_PLAYBACK_STOP`
- Product change: NONE
- Authority change: NONE
- New capability: NONE
- Expected state: RED
- B2 / B3 / B4: STOP

### Contract purpose

The RED contracts one narrow missing behavior:

After the existing governed playback executor launches an explicitly authorized
local track, it must be able to stop only the exact process-like handle returned by
that same launch.

The contract does not introduce a general media-control system.

### Existing authority

The canonical execution owner remains:

`LocalCommandMusicPlaybackExecutor`

No `MusicManager`, `PlayerManager`, `PlaybackSessionManager`, second executor or
parallel playback authority is permitted.

### RED 1 — exact process ownership

`play()` must retain the exact process-like object returned by its existing runner.

The contract does not permit reconstructing ownership from:

- executable name;
- operating-system process enumeration;
- guessed PID;
- catalogue entry;
- source path alone.

### RED 2 — bounded stop result

The existing executor must expose one bounded stop operation with an explicit result
model.

The result must communicate at least:

- whether an owned process existed;
- whether stop was performed.

The result is execution evidence, not Memory or Learning.

### RED 3 — owned handle only

When one exact handle is owned, stop must target that handle and no other process.

After successful stop, the executor must no longer claim ownership of that handle.

### RED 4 — fail closed without ownership

When no owned handle exists:

- no process may be launched;
- no process may be searched;
- no process may be terminated;
- stop reports that nothing owned was stopped.

Invariant:

`NO_EXACT_OWNED_HANDLE -> NO_PROCESS_TERMINATION`

### RED 5 — historical play compatibility

The existing `LocalMusicPlaybackExecution` contract remains valid.

Playback must still:

- resolve the selected file;
- invoke the configured command with that exact path;
- report the existing path, command and started fields.

The stop increment must not redefine selection or start authorization.

### RED 6 — explicit conversational stop

The existing local-music interception surface must recognize an explicit human stop
request and delegate to the same existing playback executor.

The contract does not authorize autonomous stop.

### RED 7 — stop is independent of new selection

Stopping an already-owned playback does not require catalogue search or track
selection.

If no playback is owned, the request must still resolve fail-closed without
launching a player.

### RED 8 — no OS process discovery and no parallel authority

The implementation must not introduce process discovery by executable name or a
second playback/session manager.

Exact ownership must originate only from the existing runner return value.

### RED 9 — richer controls remain excluded

This RED does not contract:

- pause;
- resume;
- next;
- previous;
- queue;
- seek;
- volume.

Those require separate evidence and authority reconciliation.

### Registry boundary

The existing playback descriptor remains device-scoped and state-changing.

This first RED does not require a new capability descriptor.

The conversational stop is treated as a bounded control of the execution already
owned by the existing playback authority.

No descriptor widening beyond this exact owned-stop behavior is authorized.

### Process protocol boundary

The RED intentionally contracts only the smallest process-like behavior required by
stop:

- the runner returns a handle;
- the executor retains that exact handle;
- the handle can be terminated by the executor.

No Windows API, player-specific protocol or persistent session database is required.

### State boundary

Any retained process ownership is:

- transient;
- local to the existing executor;
- non-durable;
- not Cognitive Memory;
- not Learning;
- not preference state;
- not a queue.

### Protected boundaries

This contract must not alter:

- authorized-root catalogue semantics;
- selection semantics;
- explicit start authorization;
- provider or LLM routing;
- Unified Experience;
- personality;
- Reasoning;
- Planning;
- TTS or voice-input control;
- visual Pinacoteca semantics;
- `D:\Pinacoteca` deployment hardcoding.

### Expected RED

The new contract contains nine tests.

Expected failing tests:

1. exact runner handle is not retained;
2. bounded stop operation/result does not exist;
3. owned handle cannot yet be stopped;
4. fail-closed stop operation does not yet exist;
5. explicit stop phrase is not yet admitted;
6. stop without selection is not yet handled.

Expected passing guardrails:

- historical play execution remains compatible;
- no OS discovery or parallel authority exists;
- richer controls remain absent.

Therefore expected directed result:

`6 FAILED / 3 PASSED`

No product implementation is authorized inside this CONTRACT RED block.

### Closure

`CONTRACT_RED: AUTHORED`

`EXPECTED_RED_FAILURES: 6`

`EXPECTED_GUARDRAIL_PASSES: 3`

`PRODUCT_CHANGE: NONE`

`NEW_AUTHORITY: NONE`

`NEXT_ACTION_AFTER_OWNER_RED_CERTIFICATION:
OWNED_LOCAL_MUSIC_PLAYBACK_STOP_SURGICAL_GREEN`

`B2: STOP`

`B3: STOP`

`B4: STOP`
