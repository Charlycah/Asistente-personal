# ROBY XI.2 — M304.4

Base: M304.3 estable.

## Cambio incremental

Se corrigió la continuidad conversacional del clima cuando ROBY ofrece el
pronóstico después de informar las condiciones actuales.

La frase de seguimiento `dame el pronostico` ahora se normaliza como
`decime el pronóstico extendido` mientras exista contexto meteorológico
pendiente. De este modo no cae en el router de predicciones deportivas.

## Archivos modificados

- `app/runtime_ui_adapter.py`
- `tests/test_rp_20_38_conversational_personality.py`

## Validación

- Tests focalizados de clima, personalidad y actualidad: 42 OK.
- Suite completa: 6952 OK.
- Compilación de los archivos modificados: OK.
- Verificación manual de límite de 88 caracteres en los archivos modificados: OK.

El entorno de ejecución disponible para generar este ZIP no incluye Ruff,
por lo que `ruff check .` debe confirmarse en el entorno local de VS Code.
