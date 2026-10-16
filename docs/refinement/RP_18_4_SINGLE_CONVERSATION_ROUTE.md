# RP.18.4 — Ruta conversacional única

## Objetivo

Consolidar toda interacción conversacional en una única frontera oficial antes
de ingresar al pipeline gobernado de ROBY.

## Frontera oficial

`OfficialConversationGateway` es la única puerta de entrada interactiva. Todas
las superficies delegan en `submit(...)` y registran el origen del turno:

- `console`
- `desktop_text`
- `desktop_voice`
- `internal`

El gateway no contiene razonamiento, no llama providers y no reconstruye el
runtime. Delega exactamente una vez en `EndToEndLocalConversation.converse`,
que continúa siendo el dueño del pipeline gobernado, memoria, trazas y
persistencia.

## Compatibilidad

`converse(...)` permanece como alias compatible, pero atraviesa internamente
el mismo método `submit(...)`. Los adaptadores que todavía reciben una
instancia histórica de `EndToEndLocalConversation` la envuelven en el gateway,
en vez de crear una ruta alternativa.

## Resultado

Consola, escritorio escrito, escritorio por voz y llamadas internas comparten:

1. una frontera oficial;
2. un runtime conversacional;
3. un pipeline gobernado;
4. una memoria conversacional;
5. una traza operacional;
6. una política de capacidades y providers.
