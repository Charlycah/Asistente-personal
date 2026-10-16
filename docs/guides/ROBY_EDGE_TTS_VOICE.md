# ROBY Edge TTS voice

ROBY uses Microsoft Edge TTS for desktop speech output.

Install the optional runtime dependency:

```powershell
& ".\venv\Scripts\python.exe" -m pip install "edge-tts==7.3.1"
```

Default profile:

```text
ROBY_VOICE_ENABLED=true
ROBY_VOICE_PROVIDER=edge-tts
ROBY_EDGE_TTS_VOICE=es-AR-TomasNeural
ROBY_EDGE_TTS_RATE=-8%
ROBY_EDGE_TTS_PITCH=-12Hz
ROBY_EDGE_TTS_VOLUME=+0%
```

Alternative Argentine female voice:

```text
ROBY_EDGE_TTS_VOICE=es-AR-ElenaNeural
ROBY_EDGE_TTS_PITCH=-8Hz
```

The integration degrades to silent output if `edge-playback` is unavailable.
It does not prevent ROBY from starting. Edge TTS is an online service.
