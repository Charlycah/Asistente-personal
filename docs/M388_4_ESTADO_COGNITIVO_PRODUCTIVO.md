# M388.4 — Estado cognitivo productivo por turno

## Objetivo

Hacer observable el estado cognitivo canónico realmente disponible durante un
turno, sin inventar mundo interior ni crear una autoridad paralela.

## Integración

El gateway oficial reconoce una autoridad de estado aportada explícitamente por
el runtime y la vincula una sola vez a `CanonicalCognitiveStateFacade`. El
adaptador lee esa fachada y aporta evidencia al nodo `cognitive_state`.

## Evidencia permitida

El ciclo puede indicar que existe objetivo, foco, decisión anterior o confianza.
No copia sus textos, valores privados, identidad, sesión ni contenido del turno.

Un estado vacío participa porque demuestra una lectura válida. Una fachada sin
autoridad queda omitida explícitamente. Una lectura fallida queda degradada.

## Límites

- No actualiza ni reinicia el estado.
- No crea objetivos, dudas, decisiones o emociones.
- No persiste datos ni crea almacenes alternativos.
- No concede autoridad de planificación, decisión o acción.
- No interpreta este estado funcional como consciencia o experiencia subjetiva.
