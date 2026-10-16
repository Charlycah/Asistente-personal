# M387.2 — Expediente cognitivo unificado por turno

## Propósito

M387.2 proyecta cada ciclo canónico M386.9 en un expediente único, inmutable y
trazable. El expediente será el soporte común para conectar capacidades durante
M387 sin convertir al coordinador en autoridad de memoria, decisión o acción.

## Contenido

Cada expediente contiene:

- identificador técnico derivado del ciclo;
- los 18 nodos en orden canónico;
- estado, códigos de evidencia y razones por nodo;
- resultado general del ciclo;
- nodos participantes y no participantes;
- prefijo conectado y primera interrupción;
- huella SHA-256 determinista de la evidencia técnica.

## Privacidad

El expediente no contiene mensajes, respuestas, nombres, interlocutores,
sesiones, recuerdos ni razonamientos privados. La huella sólo resume códigos
técnicos ya redactados; no resume contenido conversacional.

## Autoridad

El expediente es una proyección de sólo lectura. No recuerda, razona, decide,
ejecuta, llama proveedores ni modifica el turno. Tener un campo en el expediente
no demuestra participación: cada nodo conserva `not_recorded` hasta recibir
evidencia productiva explícita.

## Estado actual

Un turno identificado por la entrada oficial genera un expediente con tres
nodos participantes y el primer corte en `perception_and_evidence`. Las etapas
siguientes de M387 deberán completar el mismo expediente de forma incremental.
