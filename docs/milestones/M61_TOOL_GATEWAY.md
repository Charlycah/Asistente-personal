# M61 — Tool Gateway

## Estado

Completado como primer milestone de la Fase VI — Autonomía.

## Propósito

M61 introduce la puerta única por la que ROBY podrá usar herramientas externas.
El objetivo no es integrar clima, correo o cámara todavía, sino impedir que esas
capacidades entren como llamadas directas desde `CognitivePipeline`.

Principio rector:

> ROBY no invoca APIs directamente. ROBY solicita capacidades. El Tool Gateway
> registra, enruta, audita y devuelve resultados normalizados.

## Alcance

M61 define arquitectura y contratos para herramientas externas:

- registro de capacidades;
- solicitudes normalizadas;
- resultados auditables;
- bloqueo de capacidades no registradas;
- espera explícita cuando falta un handler;
- detección inicial de intención de herramienta en el turno;
- integración opcional con `CognitivePipeline`.

No incluye adaptadores reales ni llamadas a APIs. Weather, Gmail y cámara quedan
para milestones posteriores de Fase VI.

## Componentes

- `ToolGatewaySignal`
- `ToolGatewayStatus`
- `ToolGatewayPolicy`
- `ToolCapability`
- `ToolRequest`
- `ToolResult`
- `ToolGatewaySnapshot`
- `ToolGatewayEngine`
- `ToolGatewayManager`

## Integración

`CognitivePipeline` acepta `tool_gateway` como dependencia opcional. Si está
presente, observa el turno después del principio arquitectónico M60 y añade
líneas auditables al `system_prompt`.

El pipeline no conoce detalles de APIs ni adapters concretos. Solo conserva una
referencia opcional al gateway, igual que las capas M51–M60.

## Comportamiento esperado

- Una capacidad registrada con handler puede ejecutarse y queda auditada.
- Una capacidad no registrada se bloquea por defecto.
- Una capacidad registrada sin handler queda en espera.
- El texto del usuario puede marcar capacidades solicitadas como
  `weather.current`, `mail.read` o `camera.capture` sin ejecutarlas todavía.
- El gateway expone `system_prompt_lines()` para explicar el estado al LLM.

## Garantías

- No se rompe M50 ni la Fase V.
- No se introducen dependencias de APIs externas.
- No se versionan secretos ni credenciales.
- Toda herramienta futura deberá pasar por contrato y auditoría.
- La integración sigue siendo opcional y compatible hacia atrás.
