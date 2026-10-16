# M62 — Capability Registry

## Estado

Completado como segundo milestone de la Fase VI — Autonomía.

## Propósito

M62 introduce un registro formal de capacidades para que ROBY deje de pensar en
APIs concretas y empiece a trabajar con capacidades declaradas.

Principio rector:

> ROBY descubre y solicita capacidades. El Capability Registry describe qué existe;
> el Tool Gateway enruta, audita y bloquea o ejecuta según contrato.

## Alcance

M62 define el catálogo declarativo de herramientas externas:

- descriptores de capacidad;
- familias de capacidad (`weather`, `mail`, `camera`, etc.);
- riesgo declarativo;
- ámbito mínimo de permiso;
- descubrimiento de capacidades relevantes en el turno;
- compatibilidad explícita con M61 Tool Gateway;
- integración opcional con `CognitivePipeline`.

No incluye adaptadores reales ni llamadas externas. Weather, Gmail y cámara
siguen pendientes para milestones posteriores.

## Componentes

- `CapabilityRegistrySignal`
- `CapabilityKind`
- `CapabilityRisk`
- `PermissionScope`
- `CapabilityRegistryPolicy`
- `CapabilityDescriptor`
- `CapabilityRegistrySnapshot`
- `CapabilityRegistryEngine`
- `CapabilityRegistryManager`

## Integración

`CognitivePipeline` acepta `capability_registry` como dependencia opcional. Si
está presente, observa el turno antes del gateway y agrega líneas auditables al
`system_prompt`.

`ToolGatewayManager` puede recibir un `CapabilityRegistryManager` y derivar sus
capacidades desde el registro. Esto evita duplicar declaraciones cuando todavía
no hay handlers reales.

## Comportamiento esperado

- Las capacidades se registran como descriptores independientes de APIs.
- El registro puede filtrar por familia de capacidad.
- El texto del usuario puede descubrir capacidades relevantes como
  `weather.current`, `weather.forecast`, `mail.read` o `camera.capture`.
- El gateway puede reconocer capacidades declaradas por M62 aunque todavía no
  exista un handler, quedando en `waiting_for_capability`.
- El prompt explica qué capacidades existen y cuáles son relevantes al turno.

## Garantías

- No se rompe M50 ni M61.
- No se introducen dependencias de APIs externas.
- El pipeline no conoce implementaciones concretas.
- Las herramientas futuras se incorporarán como capacidades declaradas y luego
  como adapters.
- La integración sigue siendo opcional y compatible hacia atrás.
