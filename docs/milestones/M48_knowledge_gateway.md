# M48 — ROBY Knowledge Gateway (Phase IV.8)

## Objetivo

Introducir una puerta cognitiva de conocimiento para que ROBY pueda reconocer
cuándo no alcanza el contexto interno y debe consultar fuentes externas sin
perder su identidad.

M48 no convierte a ROBY en un modelo externo. Define el contrato por el cual ROBY
puede usar modelos, web, noticias, documentación o enciclopedias como
herramientas subordinadas a su propio criterio cognitivo.

## Principio arquitectónico

ROBY conserva su identidad, memoria, atención, razonamiento, planificación y
aprendizaje. El Knowledge Gateway solo amplía o verifica información cuando el
turno lo requiere.

> ROBY no es la fuente externa. ROBY decide cuándo consultarla.

## Componentes

- `KnowledgeRequest`: solicitud explícita de conocimiento externo.
- `KnowledgeNeed`: motivo de consulta externa.
- `KnowledgeSourceKind`: tipo de fuente compatible.
- `KnowledgeSourceResult`: respuesta normalizada de un proveedor.
- `KnowledgeAnswer`: respuesta consolidada por ROBY.
- `KnowledgeProvider`: contrato mínimo para proveedores enchufables.
- `KnowledgeGatewayEngine`: decide necesidad, fuentes y selección.
- `KnowledgeGatewayManager`: fachada con historial y prompt context.

## Integración

La integración con `CognitivePipeline` es opcional y no invasiva. Si se inyecta
un `KnowledgeGatewayManager`, el pipeline puede evaluar la consulta, abrir el
gateway y añadir su estado al system prompt.

## Reglas

1. ROBY consulta fuentes externas solo cuando el contexto lo justifica.
2. ROBY distingue conocimiento interno, conocimiento actual y verificación.
3. Los proveedores son intercambiables.
4. El resultado externo puede entrar en la Working Memory como hecho activo.
5. La identidad de ROBY siempre permanece por encima del proveedor utilizado.

## Hito cognitivo

Today ROBY learned to seek knowledge beyond itself without losing who it is.
