# M386.17 — Flujo controlado de identificación conversacional

## Propósito

M386.17 une tres contratos aislados:

1. intérprete explícito M386.16;
2. resolvedor canónico M386.14;
3. estado temporal por sesión M386.15.

El resultado es un servicio conversacional determinista que todavía no está
conectado al gateway oficial.

## Flujo

```text
Texto
  ↓
¿Coincide exactamente con un comando permitido?
  ├─ No → not_handled; identidad intacta
  └─ Sí
       ↓
Solicitud M386.14
       ↓
Estado temporal M386.15
       ↓
Respuesta fija y explicable
```

## Declaración inicial

`Soy Carlos` produce:

> Entendí que sos Carlos. Para confirmarlo, escribí exactamente: Confirmo que
> soy Carlos.

La sesión queda pendiente y el contexto privado permanece cerrado. Cristina
recibe exactamente el mismo tratamiento.

## Confirmación

`Confirmo que soy Carlos` o `Confirmo que soy Cristina` activa a esa persona
para la sesión indicada. No afecta ninguna otra sesión.

## Conflicto y cambio

Si Carlos estaba confirmado y aparece `Confirmo que soy Cristina`, el flujo no
cambia silenciosamente. Suspende el contexto privado y solicita el comando
completo:

`Confirmo cambiar interlocutor a Cristina`.

El cambio confirmado mantiene explícitamente la igualdad de autoridad de Carlos
y Cristina.

## Revocación

La orden confirmada de revocación elimina la identidad activa de la sesión y
cierra el contexto privado.

## Conversación común

Todo texto que no sea un comando exacto devuelve `handled=False`, sin respuesta
propia y sin modificación de estado. El flujo no conserva ese texto.

## Límites

M386.17:

- no usa LLM o proveedores;
- no consulta memoria;
- no escribe archivos;
- no persiste identidad;
- no ejecuta acciones;
- no concede autoridad;
- no está conectado a `UnifiedBrain`, Desktop, voz o al pipeline.

La próxima etapa podrá integrar este servicio como interceptor estrecho del
punto de entrada, preservando el paso normal de todos los mensajes no manejados.
