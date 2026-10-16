# M63B — Semantic Capability Descriptors

## Objetivo

M63B amplía el registro de capacidades para que ROBY no dependa de comandos
rígidos ni de identificadores técnicos. Las capacidades ahora pueden declararse
con descriptores semánticos amplios: disparadores naturales, intenciones
soportadas y ejemplos de frases reales del usuario.

Esto permite que expresiones como:

- "ROBY, qué frío hace"
- "ROBY, me llevo paraguas?"
- "ROBY, hay algo urgente en el correo?"
- "ROBY, mirá esto"
- "ROBY, resumime este PDF"

puedan resolverse hacia capacidades registradas sin que el usuario nombre la
herramienta ni conozca el adapter interno.

## Principio arquitectónico

ROBY no aprende comandos de herramienta. ROBY entiende intención y solicita
capacidades.

```text
Usuario
  → lenguaje natural amplio
  → Capability Registry
  → coincidencia semántica
  → Tool Gateway
  → Permissions & Consent
  → adapter futuro
```

## Cambios principales

### CapabilityDescriptor

Se agregan campos declarativos:

- `semantic_triggers`
- `supported_intents`
- `example_utterances`

Estos campos no ejecutan herramientas. Solo enriquecen el descubrimiento y la
explicabilidad de capacidades.

### CapabilityRegistryEngine

El descubrimiento ya no se limita a una tabla interna de términos. Ahora evalúa:

- nombre técnico;
- descripción;
- tags;
- triggers semánticos;
- intenciones soportadas;
- ejemplos de uso;
- metadata declarativa.

El snapshot expone `semantic_matches` para auditar qué términos hicieron que una
capacidad fuera relevante al turno.

### Catálogo base

Se incorpora `default_semantic_capabilities()` como catálogo inicial amplio para
Fase VI:

- `weather.current`
- `weather.forecast`
- `mail.read`
- `mail.send`
- `camera.capture`
- `files.read`
- `calendar.read`
- `web.search`

Este catálogo no registra adapters reales. Solo define el lenguaje que ROBY podrá
entender cuando esas capacidades existan.

### Tool Gateway

El gateway puede usar los términos semánticos del registry para detectar
capacidades solicitadas, en vez de depender únicamente de reglas hardcodeadas.

## Contrato preservado

M63B no rompe M61, M62 ni M63:

- los campos nuevos tienen valores por defecto;
- los tests existentes siguen funcionando;
- las capacidades siguen siendo declarativas;
- los permisos siguen decidiendo antes de ejecutar;
- no se conecta ninguna API real.

## Resultado

ROBY queda preparado para frases naturales, incompletas o coloquiales, sin
convertirlas en comandos rígidos. Esto será clave para M64 y para los adapters
reales de clima, correo, cámara, archivos, calendario y web.
