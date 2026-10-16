# M387.4 — Integración de memoria y conocimiento

## Propósito

M387.4 incorpora al expediente cognitivo evidencia productiva y separada de
memoria y conocimiento. No fusiona sus autoridades ni copia el contenido que
recuperan.

## Memoria

El nodo `memory_recall` informa si:

- la recuperación terminó con contexto relevante;
- la recuperación terminó sin recuerdos pertinentes;
- la identidad impidió acceder al contexto privado;
- el runtime de memoria no estaba disponible.

Una recuperación completada participa aunque no encuentre elementos: demuestra
que la autoridad fue consultada y respondió de manera válida. El aprendizaje
posterior continúa gobernado por M387.3 y no forma parte de esta evidencia.

## Conocimiento

El nodo `knowledge_retrieval` distingue:

- ejecución completada;
- resultado parcial o fallido;
- plan sin ejecución;
- consulta retenida;
- consulta no aplicable.

La mera creación de un plan nunca se declara como recuperación realizada.

## Privacidad y autoridad

Los registros contienen únicamente estados y códigos técnicos. No incluyen
consultas, recuerdos, artefactos, fuentes concretas, nombres o sesiones.

El adaptador observa; no consulta memoria, no ejecuta recuperación, no decide
fuentes y no concede permisos. Las autoridades productivas existentes siguen
siendo las únicas responsables de sus resultados.

## Estado del ciclo

M387.4 puede demostrar participación de `memory_recall` y
`knowledge_retrieval`. La primera interrupción secuencial continúa siendo
`perception_and_evidence` hasta que esa capacidad aporte evidencia canónica.
