# HAL Edge TTS voice

HAL uses Microsoft Edge TTS for desktop speech output.

Install the optional runtime dependency:

```powershell
& ".\venv\Scripts\python.exe" -m pip install "edge-tts==7.3.1"
```

Default profile:

```text
HAL_VOICE_ENABLED=true
HAL_VOICE_PROVIDER=edge-tts
HAL_EDGE_TTS_VOICE=es-AR-TomasNeural
HAL_EDGE_TTS_RATE=-8%
HAL_EDGE_TTS_PITCH=-12Hz
HAL_EDGE_TTS_VOLUME=+0%
```

Alternative Argentine female voice:

```text
HAL_EDGE_TTS_VOICE=es-AR-ElenaNeural
HAL_EDGE_TTS_PITCH=-8Hz
```

The integration degrades to silent output if `edge-playback` is unavailable.
It does not prevent HAL from starting. Edge TTS is an online service.
