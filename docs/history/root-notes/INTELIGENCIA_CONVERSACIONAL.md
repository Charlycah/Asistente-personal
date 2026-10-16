# Roby XI.2 RP.20.42 — Inteligencia Conversacional

## Cierres breves

Roby reconoce agradecimientos y señales de cierre aunque el nombre aparezca en distinto orden.

- `No, Roby, gracias.` → `De nada.`
- `Después seguimos.` → `Perfecto. Hablamos después.`

Al cerrar, Roby no vuelve a mencionar el clima, la configuración ni una propuesta pendiente.

## Español rioplatense consistente

La capa visible elimina aperturas impropias como `Vale` y normaliza mezclas accidentales en inglés. El voseo continúa activo para expresiones como `querés`, `podés` y `tenés`.

## Migración automática de OpenWeather

Cuando `.roby/config.json` todavía no existe pero se encuentra `.hal/config.json`, Roby:

1. carga la configuración anterior;
2. conserva servicios y preferencias;
3. actualiza la identidad y la palabra de activación a `roby`;
4. guarda el resultado en `.roby/config.json`.

Cuando `.roby/credentials.json` no existe pero se encuentra `.hal/credentials.json`, Roby carga las credenciales anteriores y crea automáticamente `.roby/credentials.json`.

La clave esperada sigue siendo `OPENWEATHER_API_KEY`.
