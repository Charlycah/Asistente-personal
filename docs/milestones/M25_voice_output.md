# M25 — Voice Output

## Objetivo

Introducir salida por voz para ROBY como una capa externa al núcleo conversacional.

ROBY sigue devolviendo texto. La UI decide si ese texto se muestra, se lee en voz alta o ambas cosas.

## Decisión arquitectónica

M25 no integra un proveedor TTS obligatorio.

La arquitectura prioriza:

- ejecución local/offline;
- ausencia de APIs pagas;
- seguridad ante fallos de voz;
- facilidad para cambiar el motor de voz;
- compatibilidad futura con Piper TTS u otros motores locales.

## Política de voz ROBY

La voz objetivo para ROBY queda definida como:

- masculina;
- cálida;
- clara;
- serena;
- no metálica;
- ritmo medio;
- tono conversacional.

Esta política se modela con `VoiceProfile` y no queda acoplada a un motor concreto.

## Componentes agregados

Archivo:

```text
app/voice_output.py
```

Componentes:

- `VoiceOutput`
- `VoiceProfile`
- `NullVoiceOutput`
- `SafeVoiceOutput`
- `LocalCommandVoiceConfig`
- `LocalCommandVoiceOutput`
- `VoiceResponseReader`

## Integración con Desktop UI

`DesktopConversationController` acepta opcionalmente un `VoiceOutput`.

Flujo:

```text
Usuario escribe texto
↓
ROBYUIAdapter
↓
UIResponse
↓
Desktop UI muestra texto
↓
VoiceResponseReader lee la respuesta de ROBY
```

## Contrato

- La salida de voz es opcional.
- La voz no modifica `ROBY.process()`.
- La voz no modifica `UserResponse`.
- Los fallos de TTS son no críticos.
- `NullVoiceOutput` es el valor seguro por defecto.
- `LocalCommandVoiceOutput` permite integrar motores offline por comando.

## No incluido en M25

- Selección final de modelo Piper.
- Instalador de voces.
- Speech-to-text.
- Micrófono.
- Configuración visual avanzada de la UI.
- Dependencias obligatorias de TTS.

## Tests agregados

Archivos:

```text
tests/test_m25_voice_output.py
tests/test_m24_desktop_ui.py
```

Cobertura:

- política de voz por defecto;
- salida nula segura;
- fallos de TTS no críticos;
- lectura de `UIResponse`;
- ignorar texto vacío;
- ejecución de comando local offline;
- integración del controller desktop con `VoiceOutput`.

## Estado

Completo.
