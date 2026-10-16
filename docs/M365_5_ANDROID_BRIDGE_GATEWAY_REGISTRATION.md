# M365.5 — Android Bridge Gateway Registration

M365.5 registra el Android Bridge exclusivamente como metadata pasiva detrás de `ToolGatewayManager`.

La capacidad canónica es `android.bridge.readiness`. Siempre se registra deshabilitada, sin handler y con `executable=false`. Un estado `AVAILABLE` sólo expresa que readiness es `READY`; no autoriza ninguna ejecución.

No se abren conexiones, no se envían mensajes y no se incorporan acciones Android. Toda capacidad futura deberá ser separada, explícita y gobernada por `ToolGatewayManager`.
