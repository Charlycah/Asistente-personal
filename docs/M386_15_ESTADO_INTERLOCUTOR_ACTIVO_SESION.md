# M386.15 — Estado de interlocutor activo por sesión

## Propósito

M386.15 mantiene temporalmente el resultado del contrato M386.14 durante una
sesión. No interpreta frases, no autentica personas y todavía no se conecta al
runtime conversacional.

## Estado temporal

`ActiveInterlocutorSessionState` conserva en memoria como máximo 32 sesiones.
La capacidad puede configurarse, pero siempre debe ser positiva.

El estado:

- no escribe archivos;
- no modifica perfiles;
- no persiste entre reinicios;
- no toca credenciales;
- no concede permisos operativos.

## Aislamiento

Cada sesión conserva su propio resultado. Una declaración de Carlos en una
sesión no identifica ninguna otra sesión. Lo mismo se aplica a Cristina.

Cuando se supera la capacidad, se elimina la sesión menos recientemente usada,
incluida su identificación confirmada interna.

## Declaración pendiente y conflicto

Si una sesión resuelta recibe una nueva declaración todavía no confirmada, el
estado visible pasa a `pending_confirmation` y se suspende el uso de contexto
privado.

Si se intenta cambiar de persona sin reconfirmación explícita, queda `conflict`.
El último interlocutor confirmado se conserva sólo como referencia interna para
impedir que un segundo intento eluda la regla de cambio. Mientras existe
conflicto, el contexto privado continúa cerrado.

## Cambio y revocación

Un cambio válido requiere `explicit_reconfirmation`, confirmación y
`replace_existing=True`. Entonces la nueva persona queda activa para esa sesión.

La revocación también requiere reconfirmación. El resultado pasa a `revoked`, se
elimina la referencia confirmada y se cierra el acceso a contexto privado.

## Autoridad del estado

El llamador no decide quién era la persona activa anteriormente. El servicio
reemplaza cualquier valor `current_interlocutor` recibido por su propio estado
confirmado. Esto impide simular un estado anterior para evitar la reconfirmación.

## Diagnóstico

La instantánea inmutable informa:

- estados retenidos;
- cantidad de sesiones retenidas;
- cantidad actualmente resuelta;
- capacidad;
- ausencia de persistencia y autoridad de acción.

Esta vista es interna y contiene la identidad resuelta porque el servicio la
necesita. No debe copiarse al expediente técnico M386.9.

## Alcance

M386.15 prepara el estado de sesión. La siguiente integración deberá definir
cómo Carlos o Cristina realizan la declaración explícita desde Desktop o texto,
sin convertir cualquier frase casual en un cambio de identidad.
