# ADR-079 — Modelo normalizado de evidencia

## Estado
Aceptado para M77.

## Contexto
ROBY conserva información en Household Memory, Document Inbox, Personal Knowledge
Base, Task Intelligence y Daily Briefing. Cada subsistema posee entidades, estados,
propietarios, huellas y fechas diferentes. La FASE VIII necesita razonar sobre esas
fuentes sin acoplar el motor futuro a sus representaciones concretas ni convertir una
síntesis o inferencia en un hecho.

## Decisión
Crear el paquete `core.governed_reasoning` y comenzar con un modelo común de
evidencia en `evidence.py`.

M77 introduce:

- `EvidenceReference`, referencia inmutable a un registro fuente;
- `EvidenceBundle`, colección ordenada y deduplicada;
- enums normalizados de fuente, naturaleza, estado y sensibilidad;
- un protocolo `EvidenceAdapter`;
- adaptadores explícitos para M72–M76;
- `EvidenceRegistry`, responsable de seleccionar el adaptador, validar Scope Guard,
  registrar la referencia y conservar un enlace de solo lectura al objeto original.

El identificador de evidencia se deriva de tipo de fuente, identificador original y
huella del contenido relevante. Por tanto, la misma versión de una fuente produce la
misma referencia y una modificación relevante produce una nueva identidad de
evidencia.

Los adaptadores no escriben en los repositorios de origen. El Daily Briefing se marca
como `SUMMARY` y `derived_summary=true`, porque orienta el contexto pero no sustituye
las fuentes primarias que lo originaron.

## Alternativas descartadas

### Modificar las entidades M72–M76
Se descartó porque introduciría acoplamiento inverso desde fases estables hacia la
FASE VIII y aumentaría el riesgo de regresión.

### Copiar el contenido completo a un nuevo repositorio
Se descartó para evitar duplicación, divergencia y exposición innecesaria de datos.
M77 conserva una referencia trazable y un resumen limitado.

### Usar únicamente diccionarios sin contrato
Se descartó porque impediría validar invariantes, tipar estados y ofrecer suites de
contrato estables para milestones posteriores.

## Consecuencias

- M78 podrá enlazar claims a evidencia uniforme.
- M79 podrá seleccionar contexto sin conocer cada entidad concreta.
- La sensibilidad se hereda conservadoramente y nunca se degrada durante la
  normalización.
- La vigencia y el estado original quedan visibles en una forma común.
- Los adaptadores futuros deberán declarar un único `source_type` y pasar las mismas
  invariantes.
- M77 no crea claims, no aplica inferencias y no ejecuta acciones externas.
