# M391.8 — Estabilización y Evidencia Integral

## Objetivo

Cerrar y estabilizar la primera serie de la Época IV — Inteligencia Continua sin
introducir una nueva capacidad cognitiva operativa. M391.8 certifica la
coherencia arquitectónica, epistemológica y documental de M391.1–M391.7 y añade
un diagnóstico integral de sólo lectura.

## Serie estabilizada

- M391.1 — Consolidación Cognitiva Gobernada.
- M391.2 — Modelo Persistente del Mundo Gobernado.
- M391.3 — Simulación de Hipótesis y Escenarios Gobernada.
- M391.4 — Comprensión Causal y Predictiva Gobernada.
- M391.5 — Organización Personal Inteligente Gobernada.
- M391.6.1 — Toma de Decisiones Gobernada, corrección certificada.
- M391.7 — Predicción Gobernada.
- M391.8 — Estabilización y Evidencia Integral.

## Diagnóstico integral

`M391IntegralEvidenceDiagnostic` no posee `authority_id` y no participa del
runtime. Recibe de forma explícita evidencias ya producidas por la serie y emite
`M391IntegralEvidenceReport` con estado `complete`, `incomplete` o `conflict`.

El diagnóstico verifica únicamente invariantes de cierre: presencia de cada
etapa, versión de esquema, autoridad canónica, carácter de sólo lectura y
linajes explícitos entre M391.2→M391.3, M391.2→M391.4 y M391.4→M391.7.

Un conflicto se expone y nunca se repara automáticamente. Una etapa ausente se
mantiene como evidencia incompleta.

## Autoridades preservadas

M391.8 no crea ni reasigna autoridades. Conserva las autoridades certificadas:

- `PeriodicReflectionAuthority` para M391.1;
- `internal_world_model` para M391.2;
- `governed_reasoning` para M391.3, M391.4 y M391.7;
- `PersonalOrganizationAuthority` para M391.5;
- `unified_cognitive_coordination` / `CanonicalDecisionFacade` para M391.6.1.

## Fronteras

M391.8 no persiste estado, no modifica memoria o aprendizaje, no cambia el
modelo del mundo, no planifica, no reorganiza, no decide, no ejecuta y no inicia
threads, timers o procesos residentes. Tampoco accede a `.roby/credentials.json`.

`CanonicalCognitiveCore(` debe permanecer en su posición contractual del gateway
oficial.

## Evidencia de certificación

La línea de entrada oficial es M391.7, certificada con 10020 pruebas aprobadas,
Ruff limpio y baseline M361 reproducible.

La certificación local de M391.8 continúa requiriendo, en este orden:

```text
ruff check .
python scripts/generate_quality_baseline.py
pytest -q
```

El ZIP de entrega no incluye `.roby/credentials.json`; el archivo privado local
permanece bajo control exclusivo del usuario.
