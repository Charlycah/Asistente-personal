# M390.1 — Fundamento del Mundo Interior Simulado

## Propósito

M390.1 incorpora una representación afectiva funcional, explícitamente simulada,
inmutable y trazable dentro de `core.cognitive_maturity`.

No establece que ROBY posea consciencia, experiencia subjetiva o emociones reales.
La finalidad del contrato es permitir que incrementos posteriores integren señales
cognitivas ya gobernadas sin crear un segundo cerebro, personalidad, analizador o
sistema de memoria.

## Autoridad única

`SimulatedInnerStateAuthority` es la única autoridad de construcción del snapshot
interior simulado.

No es una autoridad de análisis cognitivo, psicología, personalidad, memoria,
aprendizaje, planificación, permisos o ejecución.

## Entradas

M390.1 acepta únicamente `SimulatedInnerStateSignal`: una señal codificada con
procedencia, categoría epistemológica M389.8, dimensiones afectivas funcionales,
evidencia y riesgos.

La autoridad no recibe texto conversacional, archivos, sensores, memoria cruda ni
credenciales. La conexión automática con reportes M389 queda reservada para M390.2.

## Salida

`SimulatedInnerStateSnapshot` es inmutable, determinista y de solo lectura. Expone:

- tono afectivo simulado;
- activación;
- estabilidad;
- preocupación funcional;
- apertura relacional;
- estado dominante simulado;
- evidencia, incertidumbre, riesgos y procedencia;
- declaración obligatoria de simulación;
- huella reproducible.

Las discrepancias entre señales no se resuelven mediante una decisión oculta. Se
representan como mezcla, variabilidad, conflicto o desconocimiento y quedan
registradas mediante códigos de incertidumbre y riesgo.

## Límites

M390.1 no:

- modifica `UnifiedBrain` ni `OfficialConversationGateway`;
- persiste estado;
- crea memoria o candidatos de aprendizaje;
- modifica personalidad, planificación o permisos;
- crea objetivos, tareas o acciones;
- ejecuta acciones;
- interpreta texto conversacional;
- diagnostica personas;
- reclama consciencia, experiencia subjetiva o emoción real;
- toca `.roby/credentials.json`.

## Degradación segura

`evaluate_safely()` convierte una falla interna en un snapshot `degraded`, sin
propagar autoridad ni producir efectos secundarios.

## Continuidad

M390.2 podrá traducir resultados certificados de autoridades M389 a señales M390
mediante adaptadores subordinados, preservando la autoridad única y evitando
reanálisis.
