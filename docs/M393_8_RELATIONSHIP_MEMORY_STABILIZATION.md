# M393.8 — Estabilización Integral de la Memoria Relacional Gobernada

## Objetivo

Cerrar y certificar la serie M393 sin añadir una capacidad productiva nueva. M393.8 estabiliza los contratos construidos entre M393.1 y M393.7 mediante pruebas integrales, invariantes explícitos y documentación sincronizada.

## Autoridad

`RelationshipMemoryManager` continúa siendo la única fachada y autoridad de la capacidad `relationship_memory`. M393.8 no crea gestores, repositorios, motores, planificadores ni autoridades paralelas.

## Cadena estabilizada

1. M393.1 — enriquecimiento relacional mediante evidencia explícita.
2. M393.2 — metadatos y respaldo epistemológico gobernado.
3. M393.3 — consolidación diagnóstica.
4. M393.4 — consistencia relacional explícita.
5. M393.5 — evolución observable entre estados.
6. M393.6 — trazabilidad del linaje relacional.
7. M393.7 — auditoría diagnóstica final.

## Invariantes de cierre

- una única autoridad: `relationship_memory`;
- vistas públicas inmutables y deterministas;
- diagnósticos de sólo lectura;
- evidencia, conflictos y cambios permanecen explícitos;
- ninguna vista M393 modifica el historial de memoria relacional;
- sin persistencia nueva, aprendizaje, automatización, permisos o ejecución;
- sin inferencia semántica nueva en el cierre;
- sin cambios contractuales en `CanonicalCognitiveCore(`;
- `.roby/credentials.json` permanece fuera de alcance.

## Resultado

La serie M393 queda cerrada como una ampliación gobernada y auditable de la memoria relacional existente. M393.8 agrega únicamente estabilización contractual, pruebas y documentación; no amplía la superficie productiva de `RelationshipMemoryManager`.
