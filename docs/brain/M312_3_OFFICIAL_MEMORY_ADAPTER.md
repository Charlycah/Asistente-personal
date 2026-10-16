# M312.3 — Adaptador de memoria oficial

M312.3 incorpora el primer lector histórico del BRAIN.

## Alcance

- `OfficialMemoryBrainAdapter` traduce resultados de `OfficialMemoryGateway`
  al modelo canónico `BrainMemory`.
- La integración en `BrainService` es optativa mediante `readers`.
- Sin lectores configurados, el servicio conserva el comportamiento de M312.1.
- La memoria oficial se presenta como memoria de perfil, de solo lectura.

## Límites de seguridad

- El adaptador no llama a `remember()`.
- No migra registros.
- No cambia el escritor oficial existente.
- No se conecta al runtime raíz ni modifica respuestas visibles.
- Los identificadores históricos reciben el prefijo `official:`.

## Próximo paso posible

Validar este adaptador contra el gateway real mediante composición controlada,
sin convertirlo todavía en dependencia del runtime conversacional.
