# M386.9 — Contrato canónico del ciclo cognitivo completo

## Propósito

M386.9 define el expediente técnico común que podrá acompañar un turno por los
18 nodos del grafo de M386.7. El contrato registra participación, omisión,
degradación, bloqueo o ausencia de observación sin guardar la conversación.

Esta etapa define estructura; no conecta ni ejecuta el ciclo.

## Diferencia con ciclos anteriores

ROBY conserva ciclos y trazas históricos con otros propósitos. Algunos ejecutan
gestores y otros incluyen contenido. M386.9 no los elimina ni los declara como
el cerebro actual.

El nuevo contrato es una envoltura canónica, neutral y sin autoridad. En etapas
futuras, adaptadores explícitos podrán traducir metadatos permitidos desde los
componentes reales sin trasladar su autoridad.

## Estados por nodo

Cada nodo tiene exactamente uno de estos estados:

- `not_recorded`: no existe evidencia suficiente para afirmar qué ocurrió;
- `participated`: participó y aporta al menos un código de evidencia;
- `omitted`: fue omitido conscientemente y declara el motivo;
- `degraded`: participó parcialmente y declara evidencia y motivo;
- `blocked`: una frontera impidió continuar y declara el motivo.

`not_recorded` no equivale a `omitted`. Esta diferencia evita convertir ausencia
de observación en una afirmación falsa.

## Resultado del ciclo

El resultado se deriva de los 18 registros:

1. `blocked` si algún nodo está bloqueado;
2. `degraded` si existe degradación y no hay bloqueo;
3. `complete` sólo si participaron los 18 nodos;
4. `unobserved` si ninguno fue registrado;
5. `partial` para cualquier otra combinación.

El resultado describe cobertura del expediente. No juzga por sí solo la calidad
de la respuesta y no concede permiso para actuar.

## Evidencia segura

El contrato sólo acepta códigos técnicos breves y normalizados. No admite texto
libre, mensajes, respuestas, recuerdos, nombres de interlocutores, razonamiento
privado ni credenciales.

Ejemplos válidos:

- `gateway:accepted`;
- `recall:partial`;
- `permission:denied`;
- `network:unavailable`.

Estos códigos prueban un estado técnico; no contienen el dato procesado.

## Invariantes

- siempre aparecen los 18 nodos y en el orden del grafo objetivo;
- no pueden existir nodos desconocidos o duplicados;
- participar requiere evidencia;
- degradarse requiere evidencia parcial y motivo;
- omitir o bloquear requiere motivo;
- el contrato es inmutable y de solo lectura;
- el contrato no ejecuta, persiste, decide ni amplía autonomía;
- la versión inicial del esquema es `m386.9`.

## Alcance de esta etapa

M386.9 no modifica `UnifiedBrain`, el pipeline, M50 ni la orquestación cognitiva
productiva. Tampoco escribe memoria o diagnósticos. La primera instancia creada
sin adaptadores registra los 18 nodos como `not_recorded`, que es la única
afirmación honesta antes de conectar observadores reales.
