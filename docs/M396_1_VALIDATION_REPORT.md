# M396.1 — Validation Report

## Scope

M396.1 abre la época Distributed Residence mediante constitución arquitectónica y
sin cambios de código productivo, runtime, APIs públicas, persistencia, transporte,
sincronización ni ejecución.

## Architectural result

- Se preserva M395.5 como línea base funcional heredada.
- La laptop queda formalizada como `Primary Residence` / hogar operacional canónico.
- Se definen `Extended Residence` y `Presence Endpoint` sin crear instancias
  adicionales de ROBY.
- Se formalizan Residence Awareness, Interaction Locality, Experiential Continuity,
  Home Continuity y Presence Mobility.
- Se fijan los invariantes M396-I00 a M396-I20.
- No se crea `DistributedResidenceAuthority`: M396.1 conserva y delimita las
  autoridades existentes M394/M395 y los contratos históricos de Device, Presence,
  Context Continuity, Context Transfer y Resident Runtime.
- `ResidentComponentRegistry` permanece reservado a componentes internos del runtime
  y no se reutiliza como registro de lugares de residencia.
- `.roby/credentials.json` permanece fuera de alcance.

## Validation

- `pytest --collect-only -q`: 10,330 tests collected.
- Suite completa ejecutada en ocho grupos disjuntos de archivos obtenidos desde la
  colección oficial: 10,330 passed, 0 failed.
- Distribución de los ocho grupos: 1255 + 1265 + 1284 + 1353 + 1309 + 1334 + 1269
  + 1261 = 10,330.
- `python scripts/generate_quality_baseline.py`: ejecutado correctamente.
- M396.1 no modifica archivos Python productivos ni de pruebas.

## Pending local certification

`ruff` no está instalado en el entorno de empaquetado actual, la misma limitación
registrada por M395.5. La certificación final local debe ejecutar:

```text
ruff check .
python scripts/generate_quality_baseline.py
pytest -q
```

Resultado esperado de pytest: `10330 passed`.

## Certification state

M396.1 queda **arquitectónicamente cerrada y funcionalmente no invasiva**, pendiente
únicamente de la verificación Ruff local para la certificación final del handoff.
