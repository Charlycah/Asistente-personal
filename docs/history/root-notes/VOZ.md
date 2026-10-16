# Perfiles de voz de ROBY

La voz se configura en `.roby/config.json`, dentro de `services.voice`.

Perfil predeterminado:

```json
"voice": {
  "enabled": true,
  "provider": "edge-tts",
  "profile": "warm_male",
  "voice": "",
  "rate": "",
  "pitch": "",
  "volume": ""
}
```

Perfiles disponibles:

- `warm_male`: masculina, rioplatense, cálida y segura.
- `warm_companion`: femenina, rioplatense, cálida y pausada.
- `classic_roby`: voz masculina anterior.
- `clear_neutral`: femenina y más ágil.
- `night`: femenina, más lenta y suave.

Los campos vacíos permiten que el perfil controle toda la voz. `voice`, `rate`, `pitch` y `volume` pueden completarse para ajustes manuales y tienen prioridad sobre el perfil. Para volver a la voz anterior, use:

```json
"profile": "classic_roby",
"voice": "es-AR-TomasNeural",
"rate": "-8%",
"pitch": "-12Hz"
```

ROBY utiliza Edge TTS; no imita ni clona la voz de ninguna persona o personaje.
