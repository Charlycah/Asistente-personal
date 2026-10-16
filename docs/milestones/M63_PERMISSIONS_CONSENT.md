# M63 — Permissions & Consent

## Estado

Completado como tercer milestone de la Fase VI — Autonomía.

## Propósito

M63 introduce una capa explícita de permisos y consentimiento para que ROBY no
solo descubra y enrute capacidades externas, sino que también distinga qué puede
hacer, bajo qué ámbito y cuándo necesita autorización del usuario.

Principio rector:

> ROBY puede solicitar capacidades, pero las herramientas sensibles no se ejecutan
> sin una decisión previa de permisos y consentimiento.

## Alcance

M63 define el contrato de autorización previo a cualquier adapter real:

- ámbitos de permiso reutilizando `PermissionScope` de M62;
- grants explícitos por capacidad;
- decisiones auditables de consentimiento;
- evaluación de capacidades solicitadas en el turno;
- bloqueo preventivo desde `ToolGatewayManager` si falta consentimiento;
- integración opcional con `CognitivePipeline`.

No incluye clima real, Gmail real, cámara real ni ejecución segura avanzada.
Esos puntos quedan para M64+.

## Componentes

- `PermissionConsentSignal`
- `ConsentDecisionStatus`
- `PermissionConsentPolicy`
- `PermissionGrant`
- `ConsentDecision`
- `PermissionConsentSnapshot`
- `PermissionConsentEngine`
- `PermissionConsentManager`

## Integración

`CognitivePipeline` acepta `permission_consent` como dependencia opcional. Si
está presente, observa las capacidades relevantes descubiertas por M62 y agrega
líneas auditables al `system_prompt`.

`ToolGatewayManager` puede recibir un `PermissionConsentManager`. Antes de
buscar un handler, verifica si la capacidad requiere consentimiento por ámbito,
riesgo o confirmación explícita. Si el consentimiento falta, bloquea la ejecución
con un error auditable como `consent_required:device`.

## Comportamiento esperado

- Las capacidades de scope `none` pueden permitirse sin consentimiento.
- Lectura o red de bajo riesgo pueden permitirse según política.
- Escritura y dispositivo requieren consentimiento explícito por defecto.
- Una capacidad con `requires_confirmation=True` siempre requiere permiso.
- Un `PermissionGrant` activo permite ejecutar una capacidad previamente
  autorizada.
- El prompt explica qué capacidades fueron evaluadas, permitidas o bloqueadas
  por consentimiento.

## Garantías

- No se rompe M50–M62.
- No se introduce ninguna llamada externa real.
- El pipeline no decide permisos por su cuenta.
- Los permisos quedan centralizados antes de M64/M65.
- Clima, correo y cámara podrán integrarse después como adapters gobernados.
