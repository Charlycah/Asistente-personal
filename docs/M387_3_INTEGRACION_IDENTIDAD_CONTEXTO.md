# M387.3 — Integración de identidad y contexto

## Propósito

M387.3 hace que la identidad explícita y confirmada controle el acceso al
contexto privado durante el turno oficial. No cambia la copropiedad y no crea
memorias separadas para Carlos y Cristina.

## Regla productiva

En la entrada oficial, el acceso privado sólo se habilita cuando:

1. el interlocutor fue confirmado explícitamente;
2. la confirmación pertenece a la sesión solicitada;
3. esa sesión coincide con la sesión real que conserva el contexto;
4. la resolución continúa vigente.

Una identidad desconocida, pendiente, conflictiva, revocada o perteneciente a
otra sesión mantiene cerrado el contexto privado.

## Recursos gobernados

La misma decisión efímera controla:

- historial conversacional reciente;
- enriquecimiento del pedido mediante memoria privada;
- aprendizaje automático del runtime de memoria después del turno.

Cuando el acceso está cerrado, ROBY todavía puede responder al mensaje actual,
pero lo hace sin incorporar esos recursos privados.

## Compatibilidad

Los usos internos históricos que invocan directamente el runtime conservan su
conducta anterior. La política restrictiva se activa al atravesar
`OfficialConversationGateway`, que es la frontera productiva oficial.

## Privacidad y autoridad

La decisión transmitida contiene sólo booleanos y un código técnico. No contiene
nombres, sesión, mensajes o recuerdos; no persiste y desaparece al terminar el
turno. Carlos y Cristina continúan siendo copropietarios con idéntica autoridad.

La habilitación de contexto no autoriza acciones externas ni modifica permisos.
