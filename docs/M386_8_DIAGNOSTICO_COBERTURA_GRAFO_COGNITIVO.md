# M386.8 — Diagnóstico de cobertura del grafo cognitivo objetivo

## Propósito

M386.8 convierte la arquitectura objetivo de M386.7 en una vista de cobertura
inmutable, explicable y de solo lectura. Informa qué está declarado, qué tiene
integración productiva y qué todavía necesita evidencia.

No observa conversaciones, no lee memoria y no concede permisos ni autoridad.

## Línea base

El diagnóstico cubre los 18 nodos del grafo:

- 10 operativos y con integración productiva declarada;
- 7 parciales;
- 1 contractual: clasificación epistemológica;
- 0 nodos observados todavía por un diagnóstico operativo común.

Por eso la cobertura operativa y de integración inicial es `10 / 18`, mientras
que la cobertura diagnóstica común es `0 / 18`.

La palabra `operativo` no significa madurez alta ni observación completa. Indica
que una autoridad participa productivamente en algún alcance certificado.

## Evidencia requerida

Cada nodo debe reunir cuatro niveles mínimos antes de considerarse completamente
cubierto:

1. contrato explícito;
2. test de arquitectura;
3. integración real en el runtime;
4. diagnóstico operativo que demuestre su participación y degradación.

M386.8 conserva por separado evidencia demostrada y evidencia ausente. No
infiere funcionamiento por la sola existencia de una clase o archivo.

## Orden de brechas

La primera prioridad es `epistemic_classification`, porque su contrato existe
pero todavía no participa en el turno productivo. Después se presentan los
siete nodos parciales en el orden del grafo:

1. percepción y evidencia;
2. recuperación de conocimiento;
3. estado cognitivo;
4. contexto relacional y afectivo simulado;
5. compuerta de acción;
6. candidato de aprendizaje;
7. diagnóstico cognitivo unificado.

Este orden no autoriza su integración automática. Cada avance requerirá una
etapa propia, pruebas, degradación segura y control de Carlos y Cristina.

## Información protegida

La vista contiene únicamente:

- identificadores técnicos de nodos;
- estados declarados;
- tipos de evidencia;
- cantidades y proporciones;
- brechas de madurez;
- indicación de posible efecto externo.

No contiene mensajes, respuestas, recuerdos, nombres del interlocutor, datos de
identidad, credenciales ni razonamiento privado.

## Autoridad

`CognitiveGraphCoverageDiagnostic` es informativo. No puede:

- conversar;
- recuperar o escribir memoria;
- decidir;
- ejecutar herramientas;
- cambiar el estado de un nodo;
- promover aprendizaje;
- modificar el grafo;
- elevar autonomía.

La única indicación de efecto externo sigue perteneciendo a `action_gate`, que
permanece parcial. El diagnóstico sólo informa esa propiedad.

## Resultado

M386.8 ofrece una línea base honesta para organizar la convergencia futura. El
grafo ya puede decir qué falta sin fingir capacidades y sin convertirse en otro
cerebro paralelo.
