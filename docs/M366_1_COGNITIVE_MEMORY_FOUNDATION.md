# M366.1 — Cognitive Memory Foundation

## Propósito

M366.1 establece la taxonomía gobernada de la memoria cognitiva de ROBY XI.2. Define memoria episódica, semántica, procedimental y de largo plazo sin alterar el comportamiento productivo estable de M365.7.

La base oficial es M365.7, validada con 8806 pruebas aprobadas y Ruff limpio.

## Autoridad reutilizada

`CognitiveMemoryFoundation` se subordina a `CanonicalMemoryFacade`. La autoridad operativa continúa siendo `memory_gateway`; M366.1 no crea un nuevo store, repositorio, base de datos, índice, gateway ni ruta paralela de escritura.

La memoria episódica existente conserva su autoridad especializada `episodic_memory`. Los restantes dominios se declaran bajo la autoridad canónica ya existente hasta que milestones posteriores definan contratos más específicos sin duplicar responsabilidades.

## Dominios declarados

- memoria episódica: experiencias cognitivas situadas y trazables;
- memoria semántica: conocimiento estable, revisable y con procedencia;
- memoria procedimental: procedimientos aprobados representados sin ejecución;
- memoria de largo plazo: consolidación durable de recuerdos autorizados.

Cada dominio declara persistencia prevista, modo de escritura, tratamiento de datos personales y autoridad canónica responsable.

## Gobierno de escritura

M366.1 distingue dos controles futuros:

- aceptación explícita para conocimiento semántico y procedimental;
- consolidación gobernada para memoria episódica y de largo plazo.

Estas declaraciones no habilitan escritura. El snapshot conserva `persistence_enabled=False` y `automatic_learning_enabled=False`.

## Límites de M366.1

M366.1:

- no persiste nuevos recuerdos;
- no migra datos existentes;
- no modifica `OfficialMemoryGateway`;
- no modifica `CanonicalMemoryFacade`;
- no aprende automáticamente desde conversaciones;
- no ejecuta procedimientos;
- no incorpora embeddings, índices vectoriales ni proveedores externos;
- no conecta memoria nueva al planner, al runtime ni al ciclo conversacional;
- no crea schedulers ni trabajo en segundo plano;
- no modifica `.roby/credentials.json` ni bases locales.

## Próximo incremento

M366.2 podrá definir el contrato neutral de eventos episódicos y sus criterios de admisión, reutilizando `CognitiveEpisodicMemory` y sin habilitar persistencia automática.

## Quality gates

- cuatro dominios únicos y completos;
- una sola autoridad canónica de memoria;
- ninguna capacidad operacional nueva;
- escritura y aprendizaje automático deshabilitados;
- modelos inmutables y validados;
- documentación raíz sincronizada;
- Ruff limpio y suite completa sin regresiones.
