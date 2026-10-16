# M386.1 — Criterios verificables de madurez cognitiva

## Propósito

M386.1 convierte el diagnóstico general de ROBY en un contrato canónico y
verificable. No agrega inteligencia, autonomía, percepción, persistencia ni
cambios al runtime productivo.

La existencia de una clase, contrato, prueba o diseño no demuestra por sí sola
que una capacidad esté integrada. El nivel solamente puede cambiar cuando la
evidencia exigida demuestra un comportamiento observable.

## Escala canónica

- `nonexistent`: no existe contrato ni implementación reconocible.
- `very_low`: existe una dependencia o experimento mínimo.
- `low`: hay contratos o comportamiento parcial, sin integración suficiente.
- `low_medium`: varias piezas existen, pero predominan vistas pasivas o aisladas.
- `medium`: capacidad real con alcance limitado, conservador o incompleto.
- `medium_high`: integración significativa pendiente de cobertura o influencia total.
- `high`: comportamiento productivo completo, trazable, diagnosticable y probado.
- `not_demonstrated`: la afirmación no puede establecerse mediante esta escala.

`not_demonstrated` no es inferior a `very_low`: pertenece fuera del orden de
madurez funcional y se utiliza para consciencia subjetiva.

## Regla de promoción a nivel alto

Una capacidad funcional solamente puede declararse `high` cuando cumple todos
sus resultados observables y reúne, como mínimo:

1. contrato explícito;
2. pruebas unitarias;
3. pruebas de arquitectura;
4. integración en el runtime oficial;
5. diagnóstico operativo observable.

Un catálogo o una configuración no equivalen a integración. Una prueba aislada
no equivale a disponibilidad productiva. Un proceso activo no equivale a salud.

Percepción agrega certificación real por canal. Aprendizaje y autonomía agregan
revisión humana. Las afirmaciones sensibles deben conservar procedencia,
vigencia, incertidumbre y límites.

## Línea base y objetivos

| Capacidad | Nivel actual | Objetivo recomendado |
|---|---|---|
| Cognición estructurada | Medio-alto | Alto verificable |
| Memoria | Medio | Alto gobernado |
| Comunicación | Medio-alto | Alto multimodal |
| Conocimientos | Medio | Alto verificable |
| Mundo interior | Medio-bajo | Alto funcional |
| Empatía con Carlos y Cristina | Medio | Alto funcional |
| Emoción simulada | Bajo | Alto funcional y explícitamente artificial |
| Percepción | Bajo-medio | Alto por canal certificado |
| Aprendizaje | Medio-bajo | Alto gobernado y reversible |
| Análisis | Medio-alto | Alto con humildad epistémica |
| Reflexión y salud | Medio-alto | Alto diagnosticable |
| Autonomía | Baja | Medio-alto gobernado |
| Deep learning propio | Muy bajo | Medio experimental |
| Consciencia | No demostrada | No demostrada |

## Excepciones deliberadas

### Autonomía

El objetivo no es autonomía general alta. ROBY podrá decidir dentro de facultades
previamente convalidadas, acotadas, auditables y reversibles. No podrá ampliar
sus permisos, alterar reglas ni ocultar decisiones.

### Deep learning propio

El objetivo es investigación aislada. No habrá actualización autónoma de pesos
ni promoción automática de modelos a producción. Antes deberá demostrarse que
memoria, recuperación documental o coordinación de proveedores no resuelven la
necesidad.

### Consciencia

Memoria, continuidad, personalidad, análisis o emoción simulada no demuestran
experiencia subjetiva. ROBY no utilizará una afirmación de consciencia para
obtener autoridad, permisos o consideración clínica.

## Humildad epistémica

El desarrollo posterior deberá distinguir siempre:

- hecho observado o recordado;
- inferencia respaldada;
- hipótesis abierta;
- información desconocida.

Una inferencia psicológica no se convierte silenciosamente en hecho. Una emoción
simulada no se presenta como sentimiento real. Un canal declarado no se presenta
como percepción real sin evidencia.

## Autoridad del contrato

El catálogo canónico vive en `core/cognitive_maturity`. Es inmutable, no ejecuta
acciones y no modifica la vista diagnóstica actual. Las futuras etapas M386 deben
referenciar estos identificadores y aportar la evidencia requerida antes de
promover cualquier nivel.
