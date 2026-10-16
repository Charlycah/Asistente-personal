# Governed Local Music Collection → Selection Foundation

## Boundary

Selection is a pure, non-executing authority over the already governed read-only music
catalogue. It may identify one catalogue entry or return ambiguity/not-found.

Selection never resolves into playback authorization. Every selection result carries
`playback_authorized=False`.

Deterministic policy:
- one exact title/filename match → selected;
- one bounded catalogue match → selected;
- multiple plausible matches → fail closed to human disambiguation;
- no match → no selection.

The productive conversational seam accepts explicit selection language and reports the
chosen catalogue path while stating that selection does not authorize or start
playback.

No new persistence, MusicMemory, player, device authority, autonomous initiative or
preference-learning authority is introduced.

Canonical boundary:

`read-only catalogue → governed selection → selected catalogue entry`

Future boundary:

`selected catalogue entry → separate playback authorization/execution gate`.
