# ROBY XI.2 — MASTER PLAN

## Owned Local Music Playback Stop — SURGICAL GREEN

### 1. Classification

- Block: SURGICAL GREEN
- Starting contract: OWNER-CERTIFIED RED
- Starting RED: 6 expected failures / 13,341 other tests passed
- Starting Ruff: clean
- Selected residual: `OWNED_LOCAL_MUSIC_PLAYBACK_STOP`
- New capability: NONE
- New authority: NONE
- B2 / B3 / B4: STOP

### 2. Closed residual

The existing `LocalCommandMusicPlaybackExecutor` now retains the exact process-like
handle returned by the runner used for the governed launch.

It exposes one bounded `stop()` operation.

Invariant:

`NO_EXACT_OWNED_HANDLE -> NO_PROCESS_TERMINATION`

No operating-system process discovery is used.

### 3. Bounded stop evidence

`LocalMusicPlaybackStopExecution` reports only:

- `had_owned_process`;
- `stopped`.

It is transient execution evidence.

It is not:

- Cognitive Memory;
- Learning;
- preference state;
- queue state;
- durable session state.

### 4. Exact ownership

`play()` retains only the exact object returned by its configured runner.

`stop()` acts only on that retained object.

If no handle exists, stop fails closed.

If the retained object does not expose a callable `terminate`, ownership is cleared
and stop reports failure without attempting any alternate process discovery.

After successful termination, the executor clears the retained ownership.

### 5. Existing play compatibility

The historical `LocalMusicPlaybackExecution` result remains unchanged.

The existing launch still:

- resolves the selected file;
- passes the exact resolved path to the configured command;
- reports the same path;
- reports the same command;
- reports `started=True`.

No catalogue, selection or start-authorization semantics changed.

### 6. Explicit conversational admission

The existing `GovernedLocalMusicCatalogueInterceptionPort` now recognizes a small
explicit stop vocabulary:

- `detené la música`;
- `detene la musica`;
- `pará la música`;
- `para la musica`.

The stop request is checked before catalogue/selection routing.

Therefore stop does not require selecting a new track.

When no playback executor is configured, the request reports that local playback is
not configured.

When no exact process is owned, it reports that there is no active owned local
playback to stop.

When stop succeeds, it reports that local music was stopped.

### 7. Authority preservation

No new:

- `MusicManager`;
- `PlayerManager`;
- `PlaybackSessionManager`;
- playback executor;
- catalogue;
- selector;
- authorization authority.

was introduced.

The execution owner remains:

`LocalCommandMusicPlaybackExecutor`

The conversational admission owner remains the existing local-music interception
port.

### 8. Contract correction

During local GREEN verification, RED 2 exposed a defect in the test introspection.

The project uses:

`from __future__ import annotations`

Therefore `inspect.signature(stop).return_annotation` is represented as a deferred
annotation string.

Calling `dataclasses.fields()` directly on that string is invalid even when the
productive return model is a proper dataclass.

The contract test was corrected to resolve the existing annotation with:

`typing.get_type_hints(stop)["return"]`

before applying `dataclasses.fields()`.

This changes no intended RED semantic requirement.

It prevents production code from being distorted merely to satisfy an invalid test
introspection assumption.

### 9. Guardrails preserved

The GREEN does not introduce:

- OS process enumeration;
- `tasklist`;
- `taskkill`;
- `wmic`;
- `psutil`;
- pause;
- resume;
- next;
- previous;
- queue;
- seek;
- volume;
- autonomous playback stop;
- player-specific protocol;
- Windows-specific media API;
- persistent session database.

### 10. Capability registry

No new descriptor was introduced.

The existing:

`music.local_playback.execute`

remains the device-scoped state-changing playback capability.

The bounded stop is an operation over execution already owned by that same playback
authority.

No second registry authority is required.

### 11. Local verification

Directed contract plus local-music foundations:

`24 PASSED`

The set covers:

- nine owned-stop contract tests;
- existing playback foundation;
- existing selection foundation;
- existing catalogue foundation.

All modified Python files compile.

No new line over 88 characters was introduced in the modified product files,
corrected contract test or this document.

### 12. Global certification

Assistant-local verification is not Owner global certification.

The required Owner chain remains:

`python scripts/clean_project_caches.py`

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

No global closure is claimed until that certification is returned.

### 13. Protected horizons

This GREEN does not reopen:

- pause/resume;
- next/previous;
- volume;
- queue;
- H5;
- H6;
- humanization;
- B2;
- B3;
- B4.

### 14. Closure

`OWNED_LOCAL_MUSIC_PLAYBACK_STOP: LOCAL_GREEN`

`EXACT_PROCESS_OWNERSHIP: IMPLEMENTED`

`STOP_FAIL_CLOSED: IMPLEMENTED`

`EXPLICIT_HUMAN_STOP_ADMISSION: IMPLEMENTED`

`OS_PROCESS_DISCOVERY: NONE`

`PARALLEL_PLAYBACK_AUTHORITY: NONE`

`DIRECTED_VERIFICATION: 24 PASS`

`GLOBAL_CERTIFICATION: PENDING_OWNER`

`B2: STOP`

`B3: STOP`

`B4: STOP`
