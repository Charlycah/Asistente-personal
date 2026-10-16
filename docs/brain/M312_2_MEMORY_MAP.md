# M312.2 — Catálogo y mapa de memorias históricas

## Alcance

Esta versión documenta las memorias existentes. No migra datos, no cambia rutas,
no conecta adaptadores y no modifica el runtime de ROBY.

El catálogo estructurado está en `docs/brain/memory_catalog.json`.

## Regla arquitectónica

`BrainService` será la fachada única futura. Los almacenes especializados podrán
continuar existiendo detrás de adaptadores. Unificar significa una sola puerta de
acceso, no necesariamente una sola base física.

## Sistemas identificados

1. Memoria personal oficial persistente.
2. Memoria y política de aprendizaje cognitivo.
3. Memoria ejecutiva de trabajo.
4. Memoria episódica cognitiva.
5. Memoria de relación y preferencias.
6. Identidad y perfiles locales.
7. Conocimiento doméstico.
8. Objetivos, proyectos y agenda cognitiva.
9. Recordatorios y seguimientos.
10. Continuidad contextual de conversación.
11. Contexto ambiental explícito.
12. Estado operativo de avisos proactivos.

## Clasificación importante

- **Memoria personal:** puede converger conceptualmente en BRAIN.
- **Contexto breve:** debe permanecer acotado por sesión y vencer rápido.
- **Recordatorios:** BRAIN puede referenciarlos, pero no duplicar el programador.
- **Estado operativo:** no debe confundirse con recuerdos personales.
- **Secretos:** nunca ingresan al BRAIN.

## Orden de integración propuesto

1. Adaptador de lectura para la memoria personal oficial.
2. Estado del proyecto ROBY y objetivos activos.
3. Contexto conversacional breve.
4. Identidad y perfil.
5. Episodios confirmados.
6. Memoria cognitiva y aprendizaje.
7. Relación, preferencias y hábitos.
8. Conocimiento doméstico.
9. Referencias a recordatorios.

## Regla de transición

Cada sistema se integra inicialmente en modo de solo lectura. Durante la
transición puede haber varias fuentes de lectura, pero debe existir una sola
fuente oficial de escritura para cada tipo de recuerdo.

## Estado de M312.2

- Catálogo creado.
- Rutas y puertas principales registradas.
- Riesgos y estrategias de integración documentados.
- BRAIN sigue desconectado del runtime visible.
