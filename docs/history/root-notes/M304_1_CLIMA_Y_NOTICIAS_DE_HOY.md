# M304.1 — Clima y noticias de hoy

Hotfix sobre M304 para corregir dos comportamientos observados en uso real.

## Clima

Las consultas meteorológicas directas ya no pueden ser capturadas por el router
de actualidad. Expresiones como «cómo está el clima», «qué temperatura hace» o
«va a llover» quedan disponibles para OpenWeather. Las noticias meteorológicas
siguen funcionando cuando la solicitud menciona explícitamente noticias.

## Noticias relevantes

Las solicitudes generales como «¿hay alguna noticia relevante?» se interpretan
como noticias de hoy según la fecha local de Buenos Aires. Se descartan artículos
de días anteriores, aunque tengan menos de 24 horas en UTC. Si no existe una
publicación de hoy con fecha verificable, ROBY se abstiene en vez de completar la
respuesta con notas antiguas.

Las publicaciones aceptadas se muestran como «hoy, HH:MM» en hora argentina.
Los períodos explícitos —últimas 24 horas, esta semana, este mes— conservan su
alcance solicitado.
