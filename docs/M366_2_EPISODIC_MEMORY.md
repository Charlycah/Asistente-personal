# M366.2 — Episodic Memory

## Propósito

M366.2 establece la autoridad gobernada de memoria episódica de ROBY XI.2 sobre las implementaciones existentes. El incremento reconcilia sus responsabilidades sin cambiar el comportamiento estable validado en M366.1a.

## Autoridad única

La autoridad canónica continúa siendo `episodic_memory`, subordinada a `CanonicalMemoryFacade` mediante la taxonomía de `CognitiveMemoryFoundation`.

M366.2 no crea un tercer modelo episódico. Declara dos capas existentes y complementarias:

- `CognitiveEpisodicMemory`: registro conciso de transiciones del modelo cognitivo durante el ciclo interno existente;
- `EpisodicMemoryManager`: agregado episódico gobernado de M85, con eventos, referencias, revisiones inmutables y captura explícita.

Ambas capas permanecen bajo la misma capacidad especializada. No compiten por autoridad ni se convierten en stores canónicos independientes.

## Admisión episódica

La capa de ciclo cognitivo conserva su admisión por transición observada. M366.2 sólo describe ese comportamiento ya existente y no agrega una nueva captura automática.

La capa de agregado gobernado conserva admisión explícita. Representa episodios delimitados y auditables, pero no queda conectada automáticamente al ciclo conversacional, al planner ni a la memoria persistente oficial.

## Persistencia y consolidación

M366.2 no habilita persistencia nueva, no crea repositorios ni activa implementaciones existentes que no estuvieran ya conectadas. Tampoco promueve episodios a memoria semántica o de largo plazo y no habilita consolidación automática.

La consolidación cognitiva histórica de episodios repetidos permanece intacta en `CognitiveEpisodicMemory`; M366.2 no modifica sus umbrales ni su semántica.

## Límites

M366.2:

- no modifica `CognitiveEpisodicMemory`;
- no modifica `EpisodicMemoryManager`;
- no crea un tercer modelo episódico;
- no habilita persistencia nueva;
- no agrega captura automática desde conversaciones;
- no cambia el runtime, planner ni ciclo cognitivo;
- no aprende hechos ni procedimientos desde episodios;
- no modifica `.roby/credentials.json`;
- no incorpora proveedores externos, embeddings ni índices vectoriales.

## Quality gates

- una sola autoridad canónica episódica;
- dos capas existentes declaradas una sola vez;
- responsabilidades no superpuestas;
- ningún cambio de runtime;
- ninguna persistencia o consolidación automática nueva;
- documentación raíz sincronizada;
- Ruff limpio y suite completa sin regresiones.
