# M386.18 — Integración controlada de identificación en la entrada oficial

## Propósito

M386.18 conecta el flujo M386.17 al `OfficialConversationGateway` como un
interceptor estrecho. Sólo los comandos exactos M386.16 se manejan localmente.
Todo texto restante conserva el runtime anterior.

## Intercepción local

Un comando de identidad produce un `LocalConversationTurn` válido con:

- ruta `interceptor`;
- estado `completed`;
- cero llamadas a proveedor;
- cero recuperación;
- cero acceso de red;
- linaje local derivado de la resolución M386.14.

El comando no entra al pipeline ni al historial persistente normal.

## Conversación normal

Si M386.16 devuelve `no_match`, el gateway llama exactamente al mismo método
`runtime.converse()` utilizado antes de M386.18. Los errores del runtime se
propagan y el contador de turnos mantiene su conducta anterior.

## Estado por sesión

El gateway conserva una instancia M386.15 durante su vida útil. Las sesiones
permanecen aisladas. Reiniciar el gateway elimina las identificaciones porque no
existe persistencia.

La instantánea `interlocutor_sessions` permite inspección local del estado, pero
no forma parte del expediente técnico M386.9.

## Evidencia cognitiva

Los comandos de identificación registran:

- entrada conversacional;
- coordinación, si el turno llegó por `UnifiedBrain`;
- identidad y contexto.

Una declaración pendiente, conflicto o revocación registra identidad degradada
con `interlocutor:not_resolved`. Una confirmación válida registra el nodo como
participado.

Para turnos normales posteriores, el gateway transmite al runtime sólo el
booleano `interlocutor_resolved`. M386.13 nunca recibe el nombre ni la sesión.

## Privacidad

La respuesta local contiene el nombre declarado porque debe conversar con la
persona. El expediente M386.9 contiene únicamente códigos técnicos y no incluye
Carlos, Cristina, mensaje o sesión.

## Autoridad

La integración identifica al interlocutor y puede habilitar la elegibilidad de
contexto privado. No concede permisos de acción, no modifica recuerdos y no
identifica automáticamente por voz, cámara, estilo o contenido.

## Cobertura

Después de una confirmación válida por `UnifiedBrain`, el turno demuestra tres
nodos:

1. `conversation_ingress`;
2. `unified_coordination`;
3. `identity_and_context`.

Los quince nodos restantes continúan como `not_recorded`.
