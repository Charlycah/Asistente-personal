# ROBY XI.2 — MASTER PLAN

## Local Music Playback Session Control — PRE-RED Reconciliation

### 1. Classification

- Block: PRE-RED RECONCILIATION / DOCUMENTARY
- Starting baseline: OWNER-CERTIFIED / GLOBAL GREEN
- Starting suite: 13,338 passed / 0 failed
- Starting Ruff: clean
- Selected horizon: LOCAL_MUSIC_SESSION_CONTROL
- Product change: NONE
- Test change: NONE
- New capability: NONE
- New authority: NONE
- B2 / B3 / B4: STOP

This block determines whether the existing governed local-music playback path has a
safe, minimal session-control seam.

It does not implement playback control.

### 2. Existing canonical chain

The current productive chain is:

`authorized root -> read-only catalogue -> governed selection -> explicit human
playback authorization -> LocalCommandMusicPlaybackExecutor -> configured player`

Existing owners remain:

- catalogue: `GovernedLocalMusicCatalogueV1`;
- selection: `GovernedLocalMusicSelectionV1`;
- start authorization: `GovernedLocalMusicPlaybackAuthorizationV1`;
- execution adapter: `LocalCommandMusicPlaybackExecutor`;
- conversational admission: existing local-music interception port;
- runtime registration: existing official capability registry.

No replacement owner is authorized.

### 3. Current executor semantics

`LocalCommandMusicPlaybackExecutor.play()` currently:

1. resolves the supplied path strictly;
2. rejects non-files;
3. invokes the configured command with the resolved file path;
4. redirects stdin/stdout/stderr to `DEVNULL`;
5. returns an immutable `LocalMusicPlaybackExecution`.

The returned execution contains:

- resolved path;
- configured command;
- `started=True`.

The runner result is not retained.

The executor does not currently retain:

- a `subprocess.Popen` object;
- process/session identity;
- active/inactive state;
- current-track state beyond the returned execution value;
- completion state;
- pause state;
- volume state;
- queue state.

Classification:

`PLAYBACK_EXECUTOR: START_ONLY / STATELESS_AFTER_LAUNCH`

### 4. Current process ownership

The default runner is `subprocess.Popen`.

However, current code discards the returned process object immediately.

Therefore:

`PROCESS_LAUNCHED != PROCESS_SESSION_OWNED`

and:

`PID_AVAILABLE_IN_OS != GOVERNED_SESSION_IDENTITY`

The current executor cannot prove that a later control request refers to the exact
player instance started by the governed playback request.

### 5. Existing authorization semantics

`GovernedLocalMusicPlaybackAuthorizationV1` authorizes start playback only when:

- intent is explicitly human-initiated; and
- selection resolves to exactly one governed catalogue entry.

Selection itself always has `playback_authorized=False`.

The current authorization object carries:

- authorization status;
- selected entry id;
- source reference;
- rationale.

It contains no session-control grant.

Therefore a future stop/pause/resume operation must not silently reuse a start
authorization as though it were a durable control token.

Classification:

`START_AUTHORIZATION: EXISTING / BOUNDED`

`SESSION_CONTROL_AUTHORIZATION: MISSING`

### 6. Current capability descriptor

The existing registered state-changing device capability is:

`music.local_playback.execute`

Its semantics are to play one uniquely selected track.

Its evidence output is:

`local_music_playback_started`

It does not claim:

- session creation;
- pause;
- resume;
- stop;
- next;
- previous;
- seek;
- volume.

A future control contract must not widen this descriptor accidentally before the
control semantics are established.

### 7. Existing conversational surface

The local-music interception port recognizes explicit start-playback phrases and
routes them through selection, authorization and execution.

No current control-language admission path was found for local music.

The current response:

`Reproduciendo <relative path>.`

asserts launch completion, not durable session ownership.

Classification:

`CONTROL_CONVERSATION_ADMISSION: MISSING`

### 8. Search for reusable control authority

Repository inspection found no canonical local-media or music-session control
authority.

Other pause/resume concepts belong to distinct domains such as:

- voice-input pausing;
- Planning state;
- goals/projects;
- Living Conversation;
- collaboration.

TTS playback configuration is also a separate voice-output concern.

These authorities must not be repurposed for music control.

Classification:

`REUSABLE_MUSIC_SESSION_CONTROL_AUTHORITY: NONE_FOUND`

This does not yet authorize creation of a new authority. The existing playback
executor must first be tested as the likely extension owner.

### 9. Control-by-control classification

#### 9.1 Stop

Stop is the narrowest candidate.

If the existing executor retained the exact process object it launched, terminating
that owned process could be causally tied to one governed playback execution.

This is not possible with current code because the process object is discarded.

Classification:

`STOP_CONTROL: CAUSAL_RESIDUAL / MINIMAL_OWNER_EXTENSION_PLAUSIBLE`

#### 9.2 Pause and resume

Portable `subprocess.Popen` semantics do not provide a cross-player music pause or
resume contract.

A process suspension mechanism is not necessarily equivalent to media pause and may
be platform-specific.

No configured-player control protocol is currently modeled.

Classification:

`PAUSE_RESUME: PLAYER_OR_PLATFORM_PROTOCOL_UNRESOLVED`

Do not include pause/resume in the first RED.

#### 9.3 Next / previous

The existing architecture plays one explicitly selected track.

There is no queue authority and no ordered playback session.

`next` and `previous` therefore have no canonical target semantics.

Classification:

`NEXT_PREVIOUS: REQUIRES_QUEUE_OR_ORDER_SEMANTICS / NOT_READY`

Do not create a queue merely to satisfy control vocabulary.

#### 9.4 Volume

The existing music executor does not own device volume or player volume.

Voice-output volume is a separate TTS concern and must not be reused.

Classification:

`MUSIC_VOLUME: DEVICE_OR_PLAYER_AUTHORITY_UNRESOLVED`

Do not include volume in the first RED.

### 10. Smallest demonstrated residual

The broad reselection candidate was:

`LOCAL_MUSIC_SESSION_CONTROL`

PRE-RED narrows it to:

`OWNED_LOCAL_MUSIC_PLAYBACK_STOP`

Exact missing phenomenon:

After ROBY starts one authorized local track through its configured command, ROBY
does not retain enough exact execution ownership to stop that same launched playback
through the existing governed music path.

This residual does not require:

- a queue;
- preference learning;
- MusicMemory;
- a second player;
- a second catalogue;
- a second selector;
- pause/resume;
- volume;
- autonomous control.

### 11. Canonical owner decision

The likely canonical extension owner is the existing:

`LocalCommandMusicPlaybackExecutor`

Reason:

- it is already the only adapter that launches the configured local player;
- exact process ownership originates at its `runner` call;
- retaining only its own returned process does not create a second playback engine;
- stop execution belongs at the same device-execution boundary as start execution.

No new `MusicManager`, `PlayerManager`, `PlaybackSessionManager` or parallel executor
is justified.

Decision:

`SESSION_EXECUTION_OWNER: EXISTING_LOCAL_COMMAND_MUSIC_PLAYBACK_EXECUTOR`

### 12. Required bounded state

A first stop contract requires only enough transient state to identify the exact
process launched by this executor.

Candidate state:

- the runner-returned process handle;
- the corresponding resolved source path;
- whether the executor currently owns an active launch.

This state must be:

- process-local;
- non-durable;
- not Cognitive Memory;
- not Learning;
- not a music-preference store;
- not a queue;
- replaced or explicitly resolved when another track is started.

No persistent session database is justified.

### 13. Process protocol boundary

Tests currently inject a runner that returns a generic object.

A stop contract cannot safely assume every injected runner result implements
`terminate()` without changing the testable execution protocol.

The RED should therefore contract the smallest process-handle behavior needed by the
existing executor.

It must not bind core music policy to Windows APIs or a specific media player.

Potential protocol surface:

- launch through the existing runner;
- retain the returned process-like handle;
- terminate only the retained owned handle;
- report whether an owned process existed.

Exact naming remains a CONTRACT RED decision.

### 14. Replacement-start semantics

Current behavior permits repeated `play()` calls.

PRE-RED does not authorize an implicit stop of a previous track when a new track is
started.

Automatically terminating a prior process would change current start semantics.

Therefore:

`PLAY_NEW_TRACK_AUTO_STOPS_OLD: NOT_AUTHORIZED`

The first stop contract must preserve historical `play()` behavior unless a separate
contract explicitly changes it.

### 15. Completion and stale-handle semantics

The current executor does not observe process completion.

A robust future implementation may need a bounded way to determine whether the
retained process is still active.

But the first contract must avoid inventing platform-specific lifecycle semantics.

At minimum, stop must fail closed when:

- no process was ever retained;
- the retained handle cannot be controlled;
- the handle is already known to be unavailable.

Whether `poll()` is required belongs to CONTRACT RED after compatibility inspection.

### 16. Authorization boundary for stop

Start playback requires explicit human intent.

A stop operation changes device state and should also require an explicit human
control request at the conversational admission boundary.

It must not be triggered by:

- autonomous initiative;
- curiosity;
- background policy;
- personality;
- Unified Experience;
- provider-generated free text.

Decision:

`STOP_INITIATION_POLICY: EXPLICIT_HUMAN_REQUEST_ONLY`

No durable reuse of the start authorization is required.

### 17. Conversational boundary

The existing local-music interception port is the correct productive admission
surface.

A future first control may recognize explicit stop phrases only.

It must not infer stop from ambiguous conversational language.

Potential examples are documentary only:

- `detené la música`;
- `detene la musica`;
- `pará la música`;
- `para la musica`.

Exact accepted language belongs to CONTRACT RED.

### 18. Capability registration boundary

The existing playback capability is state-changing and device-scoped.

Two options exist:

1. deepen `music.local_playback.execute` to include explicit stop semantics;
2. add a separate control descriptor while reusing the same execution authority.

PRE-RED does not yet choose between them.

Because the current descriptor explicitly means play one selected track, silently
widening it is not automatically safe.

CONTRACT RED must determine the smallest registry representation without creating a
second execution authority.

Classification:

`CONTROL_DESCRIPTOR_SHAPE: UNRESOLVED / CONTRACT_DECISION_REQUIRED`

### 19. Failure behavior

A future stop operation must fail closed.

It must not:

- kill arbitrary processes;
- search the OS for a player by executable name;
- terminate by guessed PID;
- stop TTS or voice input;
- mutate catalogue or selection state;
- launch another command as fallback unless separately contracted;
- claim success without exact owned execution evidence.

The safe invariant is:

`NO_EXACT_OWNED_HANDLE -> NO_PROCESS_TERMINATION`

### 20. Windows and player portability

The user's deployment platform is Windows, but product architecture must not hardcode
a personal player or Windows-only process-control assumption without an explicit
adapter contract.

Generic process termination is narrower than media pause/next/volume.

This supports selecting stop as the first residual and excluding richer controls.

### 21. Protected boundaries

The first control increment must not change:

- catalogue authority;
- root traversal/security;
- selection authority;
- start authorization semantics;
- Cognitive Memory;
- Learning;
- personality;
- Unified Experience ownership;
- Reasoning;
- Planning;
- initiative policy beyond explicit human admission;
- TTS/VoiceOutput;
- visual Pinacoteca;
- `D:\Pinacoteca` hardcoding.

### 22. PRE-RED decision

Evidence is sufficient to narrow the broad horizon to one causal residual.

Selected residual:

`OWNED_LOCAL_MUSIC_PLAYBACK_STOP`

Canonical execution owner:

`LocalCommandMusicPlaybackExecutor`

Required architectural move:

retain only the exact process-like handle returned by the existing launch and expose
a bounded stop operation over that owned handle.

Still unresolved before GREEN:

- exact process-handle protocol;
- stop result model;
- registry descriptor shape;
- exact conversational phrases;
- stale/completed handle behavior;
- compatibility with current injected runner tests.

These are contract questions, not reasons to create another manager.

### 23. RED authorization

This PRE-RED authorizes a narrow CONTRACT RED.

`RED_AUTHORIZED: YES`

The RED must prove at least:

1. the executor retains the exact handle returned by its own runner;
2. stop targets only that retained handle;
3. no owned handle means no termination;
4. existing play path remains compatible;
5. explicit conversational stop is required;
6. no catalogue selection is required to stop an already-owned execution;
7. no OS process discovery is introduced;
8. no second playback/session authority is created;
9. pause/resume/next/previous/volume remain out of scope;
10. runtime registration remains governed and device-scoped.

### 24. Next action

`MASTER PLAN — OWNED LOCAL MUSIC PLAYBACK STOP — CONTRACT RED`

STOP before product implementation.

### 25. Closure

`LOCAL_MUSIC_SESSION_CONTROL: NARROWED`

`SELECTED_RESIDUAL: OWNED_LOCAL_MUSIC_PLAYBACK_STOP`

`PLAYBACK_EXECUTOR: START_ONLY / STATELESS_AFTER_LAUNCH`

`EXACT_PROCESS_OWNERSHIP: CURRENTLY_MISSING`

`SESSION_EXECUTION_OWNER: EXISTING_LOCAL_COMMAND_MUSIC_PLAYBACK_EXECUTOR`

`PAUSE_RESUME: NOT_AUTHORIZED`

`NEXT_PREVIOUS: NOT_AUTHORIZED`

`VOLUME: NOT_AUTHORIZED`

`QUEUE: NOT_AUTHORIZED`

`RED_AUTHORIZED: YES`

`NEXT_ACTION: OWNED_LOCAL_MUSIC_PLAYBACK_STOP_CONTRACT_RED`

`PRODUCT_CHANGE: NONE`

`TEST_CHANGE: NONE`

`B2: STOP`

`B3: STOP`

`B4: STOP`
