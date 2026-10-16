# CAP-11 — Authorization step N → existing Execution re-entry — RED

RED contractual añadido sin modificar producción.

Se exige reutilizar el owner existente de Execution para A3/A4, preservar A2/E2 y
detenerse antes de Reasoning re-entry. El RED también congela la semántica correcta de
E3: `AWAITING_REENTRY` con budget restante sigue siendo elegible para Reasoning re-entry.

La baseline productiva de entrada permanece 13.694 PASS + Ruff limpio.
