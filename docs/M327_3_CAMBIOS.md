# ROBY XI.2 — M327.3

## Persistencia del diario de decisiones

- Se incorpora `JsonlDecisionJournal`, un adaptador append-only persistente.
- La ruta predeterminada del runtime es
  `.roby/autonomy/decision_journal.jsonl`.
- Cada decisión gobernada se escribe y sincroniza en disco antes de quedar
  expuesta en memoria.
- Al reiniciar, el diario reconstruye los contratos completos y valida sus
  invariantes.
- Un registro corrupto o una versión de esquema desconocida produce un error
  explícito; no se ignora información de auditoría.
- El esquema inicial queda versionado como `schema_version = 1`.
- No se amplían permisos, acciones ni niveles de autonomía.
