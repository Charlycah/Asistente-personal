# M387.5 — Intención y razonamiento canónicos

## Propósito

M387.5 incorpora al expediente una sola evidencia de intención y razonamiento.
No introduce un nuevo clasificador ni solicita al proveedor que describa su
propio razonamiento.

## Autoridades observadas

La intención proviene de la clasificación ya utilizada por
`ConversationEntryPoint`. Cuando esa clasificación exige razonamiento, el estado
proviene del `OfficialGovernedReasoningRuntimeGateway` ejecutado a través del
runtime cognitivo existente.

El adaptador sólo recibe las categorías técnicas resultantes. Nunca recibe el
texto del mensaje, claims, inferencias, conclusiones o explicaciones.

## Estados

- Una ruta conversacional que no requiere razonamiento participa con
  `reasoning:not_required`.
- Un razonamiento gobernado completado participa.
- Abstención o revisión humana degradan el nodo de forma explícita.
- Un razonamiento bloqueado mantiene el nodo bloqueado.
- Una ruta que exige razonamiento pero no produce resultado queda degradada.
- Una entrada incompleta o retenida queda bloqueada.

Abstenerse no es un fallo oculto: es una salida cognitiva segura y visible.

## Límites

El nodo no concede autoridad de decisión o acción. Tampoco demuestra todavía la
participación de clasificación epistemológica, estado cognitivo o contexto
afectivo; esas dependencias continúan visibles como `not_recorded` hasta contar
con evidencia productiva propia.
