# Governed Local Music Collection → Playback Authorization / Execution Foundation

## Architectural finding

ROBY had microphone/audio-input infrastructure and TTS voice output, but no canonical
local music-file playback authority. This gate therefore does not repurpose
`audio_engine` or `VoiceOutput`.

## Boundary

Playback is split into two responsibilities:

1. `GovernedLocalMusicPlaybackAuthorizationV1` authorizes only when:
   - the request is explicitly human-initiated; and
   - the existing governed selector produced exactly one selected catalogue entry.
2. `LocalCommandMusicPlaybackExecutor` receives only the resolved path of an already
   authorized catalogue entry and launches the explicitly configured local player.

Playback provisioning is explicit through `ROBY_LOCAL_MUSIC_PLAYBACK_COMMAND`.
Without that setting, `music.local_playback.execute` is not registered.

The executor appends the resolved selected file path to the configured command. The
catalogue remains the path/provenance authority and rejects paths outside the authorized
music root.

## Fail-closed behavior

- selection alone never authorizes playback;
- ambiguous selection never executes;
- missing selection never executes;
- absent playback command never registers the playback capability;
- no autonomous playback exists;
- no preference learning, queue, pause, stop, next, volume control or MusicMemory is
  introduced in this foundation.

Canonical chain:

`authorized music root → read-only catalogue → governed selection → explicit human
playback authorization → configured local playback executor → device`

The invariant remains:

`catalogue != selection != playback authorization != playback execution`.
