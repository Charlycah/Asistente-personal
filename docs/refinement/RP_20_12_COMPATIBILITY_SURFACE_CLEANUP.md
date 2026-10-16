# RP.20.12 — Limpieza de superficie de compatibilidad

- Retira el alias histórico `InternalKnowledgeNeedPort`.
- Migra el composition root y sus pruebas al nombre canónico `OfficialKnowledgeRuntimeGateway`.
- Conserva reexports de paquetes que sí tienen consumidores internos reales.
- Añade invariantes para impedir la reaparición del alias.
