# M393.1 — Fundamento de Memoria Relacional Enriquecida Gobernada

M393.1 inicia la serie M393 completando la brecha pendiente del Atlas Cognitivo
Maestro: memoria relacional enriquecida con evidencia explícita.

La autoridad canónica continúa siendo `relationship_memory`, materializada por
`RelationshipMemoryManager`. No se crea otro gestor, repositorio ni memoria.

## Alcance

- incorpora referencias explícitas de evidencia asociadas a registros
  `RelationshipMemoryRecord` ya existentes;
- construye una vista inmutable y determinista del registro junto con su
  evidencia declarada;
- conserva visible qué registros no poseen todavía evidencia explícita y por
  ello requieren revisión;
- rechaza referencias a registros inexistentes y enlaces duplicados;
- conserva intactos contenido, confianza, origen, fecha e identidad del registro
  relacional fuente.

## Invariantes

- ninguna evidencia se infiere desde texto libre;
- una referencia de evidencia no convierte una señal relacional en hecho;
- la vista enriquecida no modifica `RelationshipMemorySnapshot` ni el historial;
- `relationship_memory` permanece como única autoridad relacional;
- la operación es de solo lectura y no autoriza acciones.

## Fuera de alcance

M393.1 no añade persistencia, aprendizaje, consolidación automática, resolución
de contradicciones, modificación del runtime, procesos en background,
automatización ni ejecución. Tampoco cambia la heurística histórica M52 de
captura de candidatos relacionales.
