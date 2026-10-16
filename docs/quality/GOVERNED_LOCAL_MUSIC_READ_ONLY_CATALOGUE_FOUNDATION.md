# Governed Local Music Collection → Read-Only Catalogue Foundation

## Boundary

This increment creates a separate governed local-music catalogue authority without
reusing Pinacoteca, Library, IntelligentAudioService, VoiceOutput or any playback
authority.

The configured source is explicit and opt-in through `ROBY_LOCAL_MUSIC_ROOT`.
If the variable is absent, the capability is not provisioned.

The catalogue:
- scans only the authorized root;
- is read-only;
- ignores non-audio suffixes;
- does not follow symlinks by default;
- rejects paths that escape the authorized root;
- records bounded metadata and provenance references;
- never copies, edits, deletes or plays source files.

The official runtime registers `music.local_catalogue.read` only when a valid source
root is configured.

## Deliberate exclusions

This foundation does not implement:
- playback;
- play/pause/stop/next;
- automatic music selection;
- preference learning;
- durable MusicMemory;
- ID3/tag mutation;
- autonomous background scanning;
- Pinacoteca reuse.

Future selection and playback remain separate governed gates.

Canonical boundary:

`explicit authorized music root → read-only catalogue → official capability registry`

Future boundary:

`catalogue → governed selection → playback execution`.
