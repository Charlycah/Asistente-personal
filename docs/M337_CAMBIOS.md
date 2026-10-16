# M337 — Foco cognitivo

## Objetivo

Agregar una representación explícita y determinista de un único foco cognitivo,
sin integrar todavía esta capacidad al runtime principal.

## Archivos agregados

- `core/cognitive_focus/models.py`
- `core/cognitive_focus/resolver.py`
- `core/cognitive_focus/manager.py`
- `core/cognitive_focus/__init__.py`
- `tests/test_m337_cognitive_focus.py`

## Comportamiento

- `Focus` describe un foco inmutable, tipado, priorizado y con timestamps.
- `PriorityFocusResolver` acepta un candidato solo si no existe foco o si tiene
  prioridad estrictamente mayor.
- `FocusManager` mantiene un único foco en memoria y refleja su título mediante
  la frontera pública `CognitiveStateUpdater`.
- `replace_focus()` permite un reemplazo explícito sin aplicar prioridad.
- `clear_focus()` limpia el foco cognitivo de manera controlada.
- Una persistencia fallida no altera el foco local.

## Límites deliberados

M337 no incorpora múltiples focos, persistencia propia, planificación,
inferencia, reglas autónomas ni integración con el runtime.
