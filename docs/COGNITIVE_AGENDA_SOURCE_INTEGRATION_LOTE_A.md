# ROBY XI.2 — Cognitive Agenda Source Integration — Lote A

## Estado

Implementación mínima read-only sobre la baseline Post–Whole Personal System E2E.

## Integrado

- Goals: proyección read-only desde el manager productivo ya registrado.
- Projects: proyección read-only desde el manager productivo ya registrado.
- Ambos desembocan en el mismo `CognitiveAgendaManager`.
- No se crea persistencia, scheduler, manager ni authority adicional.
- La política de admisión evita copiar inventarios completos:
  - Goal: ACTIVE y con `next_step` o `target_date`.
  - Project: ACTIVE y con `next_step`.

## Open Commitments

El contrato de `open_commitments` ya existía y continúa cubierto por tests, pero durante la
implementación se verificó que la baseline no expone actualmente un owner persistente/read model
canónico de “compromisos abiertos” que Desktop pueda consultar sin inventar estado o derivarlo de
una fuente no autoritativa.

Por gobernanza, **no se fabrica ese owner en Lote A**. El wiring existente permanece disponible,
pero su conexión productiva queda diferida a un contrato específico cuando exista o se identifique
una fuente canónica verificable.

Esto corrige una suposición del Audit/Go-No-Go previo: había soporte de consumo, pero no quedó
demostrada una fuente productiva canónica de conteo de compromisos abiertos.

## Validación ejecutada en este entorno

- tests del nuevo Lote A + RP.11 + RP.10 + RP.19.1: 35 PASS.
- agregando Whole Personal System E2E: 40 PASS.
- `py_compile` de archivos modificados: PASS.
- Ruff no está instalado en este runtime; gate local obligatorio pendiente.
- Suite completa local obligatoria pendiente.

## Archivos productivos modificados

- `app/always_on_personal_runtime_wiring.py`
- `app/desktop_bootstrap.py`

## Test añadido

- `tests/test_cognitive_agenda_source_integration_lote_a.py`

## Regla de promoción

No promover esta baseline hasta ejecutar localmente:

```text
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

y confirmar ausencia de regresiones.
