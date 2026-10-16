# M357 — Web Enrichment gobernado

M357 agrega una capa pasiva de enriquecimiento externo para datos documentales
ya extraídos por M356. La extracción local no accede a Internet: solo el servicio
`GovernedWebEnrichmentService` puede solicitar una consulta y siempre lo hace a
través de `ToolGatewayManager`.

## Garantías

- exige solicitud y consentimiento explícitos;
- transmite únicamente campos permitidos por la solicitud;
- registra la ejecución en la auditoría del gateway;
- devuelve hallazgos, confianza, fuentes y advertencias;
- no abre enlaces;
- no descarga archivos;
- no realiza pagos;
- no valida fiscalmente por sí mismo;
- no modifica ni persiste el documento;
- no ejecuta contenido QR ni códigos de barras.

El adaptador concreto queda detrás de `WebEnrichmentProvider`. M357 no incorpora
un buscador ni proveedor de red predeterminado y, por tanto, no añade conexiones
externas ocultas. Una integración real deberá registrarse como la capacidad
`web.enrichment.lookup` y respetar las políticas de permisos y consentimiento.
