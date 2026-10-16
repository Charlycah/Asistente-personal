# M87 — Meta-Reasoning

M87 permite que ROBY evalúe un resultado de M84 como proceso cognitivo gobernado.
Produce un `MetaReasoningAssessment` inmutable con juicio, puntuación, hallazgos,
referencias y recomendaciones.

## Invariantes

- El assessment no reemplaza la conclusión evaluada.
- No se reejecuta razonamiento automáticamente.
- Las recomendaciones no autorizan acciones.
- Los modelos mentales son contexto referenciado, no objetos mutados.
- Todo hallazgo conserva referencias al resultado y a la decisión.
