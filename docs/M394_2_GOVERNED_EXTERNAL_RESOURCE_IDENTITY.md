# M394.2 — Identidad Gobernada de Recursos Externos

## Propósito

M394.2 amplía el registro canónico de M394.1 para formalizar una identidad estable y
gobernada para cada recurso externo conocido por ROBY XI.2. La identidad deja de
depender de una etiqueta humana o de metadatos descriptivos y queda representada por
un espacio de nombres explícito y un identificador local estable.

## Autoridad

`ExternalResourceRegistryAuthority` continúa siendo la única autoridad de la
capacidad. M394.2 no crea un gestor de identidad paralelo: la misma autoridad que
registra un recurso garantiza la unicidad de su identidad canónica y permite
resolverla mediante `resolve_identity()`.

`OfficialDeviceGateway` conserva intacta su autoridad sobre dispositivos. La identidad
externa sólo describe y referencia recursos; no absorbe perfiles, observaciones,
acciones ni permisos de otras autoridades.

## Contratos incorporados

- `ExternalResourceIdentity`: identidad inmutable compuesta por `namespace` y
  `local_id`.
- `canonical_id`: representación determinista `namespace:local_id`.
- Identidad compatible hacia atrás: un registro M394.1 sin identidad explícita recibe
  `roby.external:<resource_id>` sin modificar su `resource_id`.
- Índice de identidad dentro de `ExternalResourceRegistryAuthority`.
- `resolve_identity()`: resolución declarativa bajo la misma autoridad canónica.
- Rechazo de identidades canónicas duplicadas aunque los `resource_id` sean distintos.

## Invariantes

- Identidad no equivale a autenticación.
- Identidad no equivale a disponibilidad.
- Identidad no implica conexión, autorización, activación ni control.
- El único estado registral continúa siendo `known`.
- No existe descubrimiento, escaneo, polling, background ni automatización.
- No se añade persistencia ni almacenamiento nuevo.
- No se modifica runtime ni la composición de `CanonicalCognitiveCore(`.
- `.roby/credentials.json` permanece fuera de alcance y no debe modificarse.
- No se modifica `OfficialDeviceGateway` ni se crea una autoridad paralela.

## Evolución prevista

M394.2 deja preparada una identidad estable sobre la cual incrementos posteriores
podrán expresar disponibilidad, conexión, autorización y activación. Esos estados y
sus transiciones no forman parte de este incremento y deberán incorporar evidencia,
permisos, auditoría y fallo seguro cuando corresponda.
