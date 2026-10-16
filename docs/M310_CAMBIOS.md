# M310 - Roby proactivo y actualidad verificada

## Alcance

Se agregó un residente independiente que puede avisar sin petición previa cuando encuentra información relevante y verificable.

## Comportamiento

- Revisa periódicamente actualidad general, política, economía, ciencia/NASA, salud, emergencias y deportes (Boca, River y fútbol).
- Solo anuncia noticias con fecha conocida, fuente y enlace.
- Descarta noticias futuras, antiguas o sin fecha.
- Revisa Gmail en modo solo lectura y prioriza asuntos sobre turnos médicos, salud, vencimientos, pagos, trámites, cancelaciones, seguridad y alertas.
- Conserva una memoria local en `.roby/proactive_verified_state.json` para no repetir avisos.
- Los avisos residentes se muestran en la interfaz y también se pronuncian.
- Respeta horario silencioso para noticias entre las 23:00 y las 08:00; los correos relevantes siguen pudiendo aparecer.

## Configuración opcional

- `ROBY_PROACTIVE_VERIFIED_ENABLED=true`
- `ROBY_PROACTIVE_VERIFIED_POLL_SECONDS=900`
- `ROBY_PROACTIVE_VERIFIED_MAX_NEWS_HOURS=18`
- `ROBY_PROACTIVE_VERIFIED_MAX_NEWS=1`
- `ROBY_PROACTIVE_QUIET_START_HOUR=23`
- `ROBY_PROACTIVE_QUIET_END_HOUR=8`

## Validación

- Compilación correcta.
- 6993 pruebas aprobadas.

## Actualización posterior — R-P0 Noticias a demanda

Se conserva la autoridad canónica de M310 en
`app/proactive_verified_runtime.py`, sin nuevos residentes
ni rutas paralelas.

- La fábrica de escritorio establece
  `spontaneous_news_enabled=False` por defecto.
- `tick()` omite noticias espontáneas cuando la opción
  está desactivada.
- Los avisos importantes de Gmail permanecen activos.
- `ProactiveVerifiedPolicy` conserva el valor histórico
  `spontaneous_news_enabled=True` en construcción directa.
- La actualidad solicitada permanece bajo
  `knowledge.current_affairs`.
- Desactivar globalmente el residente no equivale a
  desactivar solo las noticias.

### Certificación local

- Ruff específico y global: PASS.
- Contratos nuevos e históricos: 13/13 PASS.
- Suite global: 13.739 PASS; 47 FAIL.
- Las 47 fallas pertenecen a contratos `test_m377_`.
- M377 HOLD vigente; las fallas no se declaran aprobadas.
- STOP_PRODUCTIVE: ACTIVE.
