# M65 — Weather Adapter

## Objetivo

M65 incorpora el primer adapter real de la Fase VI: clima actual y pronóstico
extendido. La capacidad queda conectada al mundo exterior sin romper la regla
arquitectónica establecida desde M61:

> ROBY solicita capacidades; no invoca APIs directamente.

El adapter de clima se registra detrás del `ToolGatewayManager`, se descubre por
`CapabilityRegistryManager` y queda gobernado por `PermissionConsentManager`.

## Alcance

M65 agrega:

- `infrastructure/weather/weather_client.py`
- `infrastructure/weather/extended_weather_client.py`
- `infrastructure/weather/weather_adapter.py`
- `tests/test_m65_weather_adapter.py`

La implementación permite:

- clima actual (`weather.current`);
- pronóstico extendido (`weather.forecast`);
- resumen natural para ROBY;
- consejos simples de abrigo, calor o paraguas;
- cliente OpenWeatherMap con `OPENWEATHER_API_KEY` desde `.env`;
- tests con proveedor falso, sin llamadas reales a internet.

## Flujo arquitectónico

```text
Usuario
  ↓
Lenguaje natural amplio
  ↓
Capability Registry
  ↓
weather.current / weather.forecast
  ↓
Permissions & Consent
  ↓
Tool Gateway
  ↓
Weather Adapter
  ↓
OpenWeatherMapClient o proveedor compatible
```

## Lenguaje natural

M65 aprovecha M63B para que frases no exactas puedan descubrir la capacidad:

- “ROBY, ¿cómo está el clima?”
- “ROBY, qué frío hace”
- “ROBY, ¿necesito abrigo?”
- “ROBY, ¿me llevo paraguas?”
- “ROBY, ¿cómo viene el extendido?”
- “ROBY, ¿va a llover mañana?”

El adapter no introduce comandos rígidos. La detección sigue siendo semántica y
la ejecución sigue pasando por el gateway.

## Seguridad

- La API key no se guarda en código.
- La factory `build_weather_adapter_from_config` exige `OPENWEATHER_API_KEY`.
- Los tests no realizan llamadas reales a APIs.
- El permiso de red queda modelado como `PermissionScope.NETWORK`.
- Al ser clima de bajo riesgo, M63 permite ejecución sin consentimiento explícito.

## Contratos preservados

M65 no modifica el ciclo cognitivo M50 ni el pipeline como requisito obligatorio.
El adapter es conectable de forma externa y opcional.

Esto preserva:

- compatibilidad M50–M60;
- contratos M61/M62/M63/M63B;
- separación entre core cognitivo e infraestructura externa;
- reemplazo futuro del proveedor sin tocar ROBY.

## Estado

M65 queda listo cuando:

- `tests/test_m65_weather_adapter.py` pasa completo;
- la suite general permanece en verde;
- Ruff no reporta errores;
- no hay secretos reales versionados.
