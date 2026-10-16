# M394.3 — Estado Gobernado de Recursos Externos

## Propósito

Ampliar la infraestructura externa gobernada para que ROBY pueda representar de forma explícita el estado descriptivo de un recurso externo ya registrado, sin observarlo activamente ni operar sobre él.

## Autoridad

`ExternalResourceRegistryAuthority` continúa siendo la única autoridad de registro, identidad y estado de recursos externos. M394.3 no crea un gestor paralelo ni modifica `OfficialDeviceGateway`.

## Estados incluidos

- `known`: el recurso está registrado y su existencia es conocida.
- `available`: una fuente autorizada declaró que el recurso está disponible.
- `unavailable`: una fuente autorizada declaró que el recurso no está disponible.

`connected`, `authorized` y `active` quedan reservados para incrementos posteriores y son rechazados por el contrato M394.3.

## Semántica

`declare_state()` sólo modifica la representación interna gobernada. No escanea redes, no consulta dispositivos, no hace polling, no abre sockets, no autentica, no conecta, no autoriza, no activa y no ejecuta recursos externos.

Registrar un recurso sigue comenzando en `known`. Las declaraciones de estado conservan `resource_id`, identidad canónica, etiqueta, tipo, procedencia, capacidades y metadatos.

## Invariantes preservados

- Una única autoridad por capacidad.
- Sin gestores paralelos.
- `OfficialDeviceGateway` conserva su autoridad existente.
- `CanonicalCognitiveCore(` permanece en su posición contractual.
- `.roby/credentials.json` no se modifica ni forma parte del incremento.
- Sin persistencia nueva ni efectos externos.
- Documentación sincronizada con el código.
