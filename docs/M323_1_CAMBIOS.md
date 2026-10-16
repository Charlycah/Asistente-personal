# M323.1 — Marcadores Conversacionales

Incremento localizado sobre M323 validado.

## Cambio

- Se incorpora `ConversationalMarkerAnalyzer` dentro del Brain.
- Reconoce uno o varios marcadores al comienzo del turno.
- Expone los marcadores y el texto sustantivo restante.
- Distingue un marcador aislado de un pedido con contenido.
- No modifica la frase original ni interviene en motores, memoria o routing.

## Ejemplos

- `Bueno, decime el clima` → marcador `bueno` + `decime el clima`.
- `Bueno, a ver, mostrame noticias` → marcadores `bueno`, `a ver`.
- `Mmm...` → marcador aislado.
- `Decime si entonces llueve` → sin marcador inicial.
