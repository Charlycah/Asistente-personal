# M390.4 — Integración Relacional Segura

M390.4 integra el nodo canónico `relational_affective_context` con el mundo interior simulado sin crear una nueva autoridad relacional ni emocional.

`SafeRelationalAffectiveIntegration` es un evaluador puro y de solo lectura. Consume exclusivamente `CognitiveCycleNodeRecord` ya producido por `RelationalAffectiveEvidenceAdapter`; no recibe snapshots relacionales, perfiles de personalidad, texto conversacional, identidad ni sensores.

Reglas:

- `SimulatedInnerStateAuthority` continúa siendo la única autoridad del estado interior simulado.
- Un contexto relacional confirmado puede producir apertura relacional simulada.
- Interlocutor no resuelto, autoridades faltantes o evidencia degradada producen incertidumbre, no inferencia.
- Una violación de integridad permanece cautelosa y explícitamente riesgosa.
- No se infiere presencia física, identidad, relación, intención ni sentimiento real.
- No hay persistencia, memoria, aprendizaje, modificación de personalidad, permisos, runtime ni ejecución.
