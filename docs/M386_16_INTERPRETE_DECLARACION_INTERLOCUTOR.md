# M386.16 — Intérprete explícito de declaración del interlocutor

## Propósito

M386.16 traduce comandos inequívocos de Carlos o Cristina al contrato M386.14.
Es un intérprete determinista, de lista cerrada y todavía aislado del runtime.

No aplica el estado M386.15 por sí mismo.

## Declaraciones admitidas

Las declaraciones iniciales aceptadas son:

- `Soy Carlos`;
- `Soy Cristina`;
- `Me identifico como Carlos`;
- `Me identifico como Cristina`.

Estas expresiones producen una solicitud pendiente de confirmación. No abren
todavía el contexto privado.

## Confirmación

Las expresiones:

- `Confirmo que soy Carlos`;
- `Confirmo que soy Cristina`;

producen una solicitud explícitamente confirmada.

## Cambio y revocación

El cambio exige una orden completa:

- `Confirmo cambiar interlocutor a Carlos`;
- `Confirmo cambiar interlocutor a Cristina`.

La revocación admite:

- `Confirmo revocar la identificación del interlocutor`;
- `Confirmo cerrar la identificación del interlocutor`.

## Lista cerrada

El intérprete no busca nombres dentro de una frase. Por ejemplo, no identifica
a nadie ante:

- `Carlos dijo que mañana llueve`;
- `Quiero consultar algo para Cristina`;
- `Soy amigo de Carlos`;
- `Soy Carlos o Cristina`;
- `Hola, soy Carlos`.

La última frase se rechaza deliberadamente porque contiene texto adicional. La
lista podrá ampliarse en otra etapa, pero cada variante tendrá pruebas propias.

## Normalización

Se ignoran mayúsculas, espacios repetidos, acentos y signos finales `.!?`. No se
eliminan palabras, prefijos o contenido intermedio. Esto conserva la exigencia
de coincidencia completa.

## Privacidad

El resultado no guarda el texto recibido. Sólo contiene tipo de comando,
candidato, solicitud estructurada y código técnico de respuesta.

## Límites

El intérprete:

- no usa LLM ni proveedores;
- no consulta memoria;
- no usa voz, cámara o biometría;
- no infiere identidad;
- no persiste;
- no modifica el estado de sesión;
- no ejecuta acciones;
- no está conectado a `UnifiedBrain` ni al pipeline.

M386.16 establece un lenguaje mínimo y controlable para la futura integración
productiva.
