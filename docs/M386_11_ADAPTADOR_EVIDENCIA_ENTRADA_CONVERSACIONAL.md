# M386.11 — Adaptador de evidencia del punto de entrada conversacional

## Propósito

M386.11 conecta el primer hecho productivo del grafo objetivo con el observador
M386.10: la aceptación de un turno por `OfficialConversationGateway`.

La conexión demuestra únicamente `conversation_ingress`. Los otros diecisiete
nodos permanecen como `not_recorded`.

## Identidad del ciclo

El gateway ya generaba un identificador técnico mediante su observador
operacional. M386.11 reutiliza exactamente ese valor, por ejemplo
`turn-000001`. No crea otro contador, sesión o identidad paralela.

## Evidencia

Cuando comienza un turno, el adaptador registra:

- nodo: `conversation_ingress`;
- estado: `participated`;
- evidencia: `gateway:accepted`.

La evidencia significa que la frontera oficial aceptó el turno. No afirma que
el runtime respondió, que la memoria participó ni que ocurrió razonamiento.

## Éxito y fallo posterior

La aceptación se registra antes de delegar al runtime. Después, tanto ante una
respuesta válida como ante una excepción, el observador se sella.

Si el runtime falla, la entrada continúa demostrada porque ocurrió realmente.
Los demás nodos siguen sin registrar. El error original se propaga sin cambios.

## Privacidad

La vista no conserva:

- texto del mensaje;
- respuesta;
- identificador de sesión;
- propietario o interlocutor;
- memoria;
- detalles de la excepción.

Sólo conserva identificador técnico del turno, estado y código de evidencia.

## Retención

El adaptador conserva como máximo cien ciclos sellados. La capacidad es
configurable y siempre positiva. El contador histórico de turnos aceptados no
se confunde con la cantidad retenida.

## Autoridad

El adaptador traduce un hecho ya ocurrido. No puede:

- iniciar una conversación;
- alterar el texto o la respuesta;
- consultar memoria;
- razonar, planificar o decidir;
- ejecutar acciones;
- persistir datos;
- elevar autonomía.

## Resultado

Por primera vez, el contrato M386.9 recibe evidencia productiva real: `1 / 18`
nodos por turno. El ciclo permanece `partial`, que es la descripción correcta
hasta conectar observadores específicos para otras autoridades.
