# M386.14 — Contrato canónico de resolución del interlocutor

## Propósito

M386.14 define cómo ROBY podrá saber si conversa con Carlos o Cristina sin
biometría, vigilancia, inferencias ocultas ni una identidad familiar técnica.

Esta etapa crea el contrato y el resolvedor puro. Todavía no modifica el flujo
conversacional ni persiste la selección.

## Principio de igualdad

Carlos y Cristina son los dos únicos copropietarios y tienen exactamente la
misma autoridad. Resolver quién habla:

- permite seleccionar contexto privado de esa persona;
- no convierte a nadie en propietario principal;
- no concede permiso para ejecutar acciones;
- no reduce la autoridad del otro copropietario.

## Fuentes permitidas

El contrato sólo admite fuentes explícitas:

- declaración directa;
- selección explícita al iniciar una sesión;
- reconfirmación explícita para cambiar o revocar.

No admite reconocimiento facial, huella de voz, cámara, estilo de escritura,
hábitos, memoria ni suposiciones por contenido.

## Estados

- `unknown`: nadie fue declarado;
- `pending_confirmation`: existe candidato pero falta confirmación;
- `resolved`: Carlos o Cristina fueron confirmados para esa sesión;
- `conflict`: se intentó cambiar de persona sin reemplazo explícito;
- `revoked`: la identificación fue retirada conscientemente.

Sólo `resolved` permite usar contexto privado de la persona identificada.

## Cambio de interlocutor

Una sesión ya resuelta no cambia silenciosamente. Para pasar de Carlos a
Cristina o viceversa se necesitan:

1. nueva declaración;
2. confirmación;
3. indicador explícito de reemplazo;
4. fuente `explicit_reconfirmation`.

El contrato no transfiere recuerdos ni modifica sus propietarios.

## Revocación

La revocación requiere confirmación y vuelve a impedir el uso de contexto
privado. No borra perfiles, sesiones, recuerdos ni historial.

## Relación con autoridades existentes

ROBY ya posee perfiles privados `carlos` y `cristina`, un perfil conjunto
`carlos-cristina` y un resolvedor histórico no biométrico. M386.14 conserva esa
base conceptual, pero establece el contrato futuro compatible con M385:

- no existe `Familia`;
- la sesión conjunta no identifica automáticamente al hablante;
- el perfil conjunto representa copropiedad, no interlocución individual.

## Privacidad

La resolución contiene la persona confirmada porque ése es su propósito
interno, pero no debe copiarse al expediente técnico M386.9. El adaptador de
evidencia sólo recibirá en el futuro el booleano `interlocutor_resolved`.

## Alcance actual

M386.14 no se conecta todavía a `UnifiedBrain`, Desktop, voz o al runtime local.
No escribe archivos ni credenciales. La integración productiva deberá tener una
etapa separada con selección, vigencia, revocación y pruebas de aislamiento.
