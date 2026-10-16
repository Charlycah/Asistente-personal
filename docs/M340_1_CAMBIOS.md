# ROBY XI.2 M340.1 — Modo Dictado Inteligente

Base oficial: M340 (`ruff check .` OK, 7896 tests OK informados por el usuario).

## Capacidad incorporada

Modo de dictado local y explícito, separado del enrutador conversacional general.
Mientras el modo está activo, las transcripciones se agregan al documento y no se
procesan como consultas u órdenes normales para el modelo.

### Órdenes principales

- `Roby, iniciar dictado` / `modo dictado`
- `pausar dictado`
- `continuar dictado`
- `borrar última frase`
- `terminar dictado`
- `cancelar dictado`

### Puntuación hablada

Reconoce `punto`, `coma`, `punto y coma`, `dos puntos`, `nueva línea`,
`nuevo párrafo`, `signo de interrogación` y `signo de exclamación`.

## Compatibilidad

- No modifica el motor Vosk ni el contrato `VoiceInput`.
- No altera el enrutamiento normal cuando el dictado está inactivo.
- Funciona tanto con entrada escrita como con escucha continua.
- El texto se mantiene solamente durante la sesión de dictado y se presenta en
  la conversación al finalizar. No se escribe automáticamente en disco.

## Pruebas nuevas

`tests/test_m340_1_intelligent_dictation.py` cubre inicio, puntuación, pausa,
continuación, deshacer, finalización, cancelación y aislamiento de conversaciones
normales.
