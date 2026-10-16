# M328.4 — Selección del próximo objetivo

- Selección determinista y auditable de objetivos persistentes.
- Puntaje compuesto por prioridad, revisión, progreso, bloqueos, riesgo y experiencia.
- Persistencia atómica en `.roby/autonomy/goal_selections.json`.
- Integración con `RuntimeExecutiveIntegration.select_next_goal()`.
- Selección separada de autorización y ejecución.
