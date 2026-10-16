# M312.7 — Adaptador de memoria relacional y preferencias

## Objetivo

Agregar una vista de solo lectura del sistema histórico `RelationshipMemoryManager`
al BRAIN, sin activar la composición en el runtime conversacional.

## Cambios

- Nuevo `RelationshipPreferenceBrainAdapter`.
- Las preferencias, límites y ritmos de proyecto se exponen como `preference`.
- Las señales de confianza e interacción se exponen como `profile`.
- Nueva composición explícita `build_relational_memory_brain_composition`.
- No hay migración, escritura ni activación automática.
