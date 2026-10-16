# RP.24.3 — Noticias Inteligentes

## Propósito

Agregar una capa editorial local entre la recolección de actualidad y la
conversación. ROBY deja de tratar cada titular como una noticia aislada y puede
agrupar coberturas del mismo hecho, evaluar su relevancia y conservar sus
fuentes.

## Alcance

- fuentes configurables y desactivables;
- descarte de publicaciones vencidas, futuras o provenientes de fuentes
  deshabilitadas;
- deduplicación por similitud de titulares;
- clasificación temática determinista;
- puntuación de relevancia personal;
- confirmación mediante dominios independientes o una fuente oficial;
- tres destinos: interrupción, resumen diario o silencio;
- trazabilidad completa de las fuentes del grupo.

## Política inicial

Una noticia solo puede interrumpir cuando combina urgencia, posible impacto
inmediato y evidencia suficiente. Una fuente oficial puede satisfacer por sí
sola el requisito de confirmación. El contenido de bajo valor personal no
interrumpe.

La etapa no incorpora scraping, claves externas ni nuevos servicios de nube.
Se apoya en los recolectores existentes y puede probarse completamente sin
acceso a Internet.
