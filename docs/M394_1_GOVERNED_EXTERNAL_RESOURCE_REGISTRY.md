# M394.1 — Registro Gobernado de Recursos Externos

## Propósito

M394.1 inicia la serie M394 — Infraestructura Externa Gobernada mediante un registro
canónico y explícito de recursos externos conocidos por ROBY XI.2. El incremento
permite declarar que un recurso existe y conservar su identidad descriptiva sin
confundir conocimiento con disponibilidad, conexión, autorización, activación o
control.

## Autoridad

`ExternalResourceRegistryAuthority` es la única autoridad de la nueva capacidad de
registro de recursos externos y declara `authority_id = "external_resource_registry"`.
No reemplaza autoridades existentes. En particular, `OfficialDeviceGateway` conserva
la autoridad sobre perfiles, observaciones y preparación gobernada de acciones de
dispositivos; M394.1 sólo puede referenciar esa procedencia mediante
`source_authority` y `external_ref` explícitos.

## Contratos incorporados

- `ExternalResourceKind`: clasificación descriptiva amplia del recurso.
- `ExternalResourceRegistryState.KNOWN`: único estado permitido por M394.1.
- `ExternalResourceRegistration`: declaración inmutable de identidad, etiqueta,
  clase, autoridad de procedencia, referencia externa, capacidades declaradas y
  metadatos explícitos.
- `ExternalResourceRegistrySnapshot`: vista inmutable y determinista del registro.
- `ExternalResourceRegistryAuthority`: registro en memoria con identidad única por
  `resource_id`.

## Invariantes

- Registrar significa únicamente **conocido**.
- No se infiere disponibilidad.
- No se descubre ni escanea red o hardware.
- No se conecta ningún recurso.
- No se conceden permisos ni autorizaciones.
- No se activa cámara, sensor, servicio, nodo ni dispositivo.
- No existe polling, background, automatización ni ejecución.
- No se añade persistencia ni almacenamiento nuevo.
- No se modifica runtime ni composición de `CanonicalCognitiveCore(`.
- `.roby/credentials.json` permanece fuera de alcance y no debe modificarse.
- No se introduce un gestor paralelo para dispositivos u otras capacidades ya
  gobernadas.

## Evolución prevista

Los estados `available`, `connected`, `authorized` y `active` pertenecen a incrementos
posteriores de M394 y no forman parte del contrato M394.1. Cada transición futura
deberá conservar la separación entre conocer, observar y actuar, e incorporar su
propia evidencia, permisos y fallo seguro bajo autoridad gobernada.
