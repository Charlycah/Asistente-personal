# M386.5 — Niveles de autonomía gobernada

## Propósito

M386.5 define seis grados comprensibles de iniciativa y los relaciona con la
autoridad existente de `core.controlled_autonomy`. No activa ejecución nueva ni
modifica las políticas productivas.

Una etapa expresa cuánto puede avanzar ROBY en un proceso. No equivale a permiso.
La matriz M386.4, el consentimiento, el riesgo, la reversibilidad y la compuerta
operativa continúan aplicándose simultáneamente.

## Nivel 0 — Informar

ROBY observa, describe y explica. No recomienda, persiste ni ejecuta.

Correspondencia existente: `observe_only`.

## Nivel 1 — Recomendar

Compara alternativas, explica riesgos y propone una opción. Carlos o Cristina
mantienen la decisión.

Correspondencia existente: `recommend`.

## Nivel 2 — Preparar

Construye un plan, borrador o acción lista para revisión. Puede mostrar efecto,
destinatario y datos relevantes, pero no ejecuta.

Correspondencia existente: `confirm_before_action` y planificación M69.

## Nivel 3 — Ejecutar lo preconvalidado

Puede ejecutar una acción concreta solamente cuando:

- la familia es delegable según M386.4;
- existe consentimiento activo y acotado;
- la compuerta operativa la clasifica como riesgo bajo;
- la acción es reversible;
- decisión, ejecución y resultado quedan auditados.

Correspondencia existente: `autonomous_low_risk`.

Una familia de riesgo medio puede contener una instancia concreta evaluada como
riesgo bajo. Deben aprobarse ambas clasificaciones; ninguna reemplaza a la otra.

## Nivel 4 — Resolver excepciones menores

Puede aplicar una recuperación segura —por ejemplo, un reintento limitado o una
alternativa equivalente— sin cambiar objetivo, capacidad, alcance, permiso o
riesgo. Debe respetar prevención de bucles y revelar degradaciones.

Utiliza la misma compuerta `autonomous_low_risk`. No crea una facultad operativa
nueva.

## Nivel 5 — Solicitar ampliación

ROBY puede explicar por qué una facultad nueva resultaría útil, describir riesgos
y proponer límites. Después debe esperar la decisión de Carlos o Cristina.

Este nivel es `request_only`: no ejecuta, no concede y no modifica permisos. Su
correspondencia operativa máxima sigue siendo `recommend`.

## Reglas de degradación

- Una etapa de autonomía no sustituye permisos.
- Denegación, revocación o conflicto bloquean la acción afectada.
- Falta de evidencia, confianza, capacidad o reversibilidad obliga a degradar.
- Riesgo alto, crítico, irreversible o no acotado nunca se ejecuta autónomamente.
- Las excepciones no se convierten automáticamente en reglas.
- ROBY no eleva su etapa ni amplía su alcance por autoridad propia.

## Estado productivo actual

M69 continúa proponiendo planes y difiriendo ejecución. La autoridad existente
permite representar autorización autónoma únicamente para riesgo bajo y conserva
compuerta, diario, resultados, reversión y prevención de bucles.

M386.5 formaliza la escala objetivo, pero no promueve el runtime a ningún nivel.
Una integración posterior deberá demostrar, mediante pruebas específicas, qué
familias concretas pueden alcanzar los niveles 3 o 4.

## Límites

El contrato inmutable vive en `core.cognitive_maturity.autonomy`. M386.5:

- no ejecuta herramientas;
- no persiste decisiones;
- no crea permisos;
- no cambia el nivel productivo;
- no habilita acciones de riesgo medio, alto o crítico;
- no modifica la autoridad M326 ni el planificador M69;
- no toca memoria, credenciales, código o modelos.
