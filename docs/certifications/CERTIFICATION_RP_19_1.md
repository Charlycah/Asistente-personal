# Certificación RP.19.1 — Agenda cognitiva persistente

Fecha: 2026-07-17

## Alcance certificado

- Persistencia SQLite inyectada en el `CognitiveAgendaManager` existente.
- Restauración antes del inicio del loop cognitivo oficial.
- Conservación de prioridad, estado, motivo y condiciones de reanudación.
- Cierre, archivo, reapertura y archivo automático por expiración.
- Tombstones terminales para evitar recreación automática.
- Sin scheduler, lifecycle, memoria o residente paralelo.
- Compatibilidad con RP.11–RP.18 y con la ejecución única de
  `OfficialROBYRuntime`.

## Evidencia

Pruebas nuevas: `tests/test_rp_19_1_persistent_cognitive_agenda.py`.

## Resultado de validación

- Ruff: limpio (`ruff check .`).
- Pytest completo: **6489 pruebas aprobadas**.
- Pruebas previas conservadas: **6483**.
- Pruebas nuevas RP.19.1: **6**.
- Entregable limpio de datos operativos privados y artefactos de caché.
