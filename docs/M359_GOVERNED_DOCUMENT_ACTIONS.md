# M359 — Governed Document Actions

M359 añade una capa separada para preparar y ejecutar acciones derivadas de un
documento entendido. Las acciones iniciales son crear un recordatorio, guardar
un resumen y abrir una fuente explícita.

Toda acción exige consentimiento y confirmación del usuario. Antes de la
confirmación solo se devuelve una propuesta. La ejecución confirmada pasa por
`ToolGatewayManager`, queda auditable y depende de un handler registrado.

M359 no ejecuta acciones silenciosas, no paga facturas, no modifica documentos,
no abre enlaces inferidos y no elude permisos de calendario, almacenamiento o
navegación.
