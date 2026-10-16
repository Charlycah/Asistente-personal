# M66 — Mail Reader Adapter

## Objetivo

M66 incorpora la primera capacidad de correo de Fase VI en modo estrictamente
lectura. ROBY puede listar, buscar, resumir y leer mensajes sin enviar, borrar,
archivar ni modificar la casilla.

El adapter se conecta a la arquitectura ya definida:

```text
Lenguaje natural
  ↓
Capability Registry / M63B
  ↓
mail.read
  ↓
Permissions & Consent / M63
  ↓
Tool Gateway / M61
  ↓
Mail Reader Adapter / M66
  ↓
Proveedor IMAP o compatible
```

## Alcance

M66 agrega:

- `infrastructure/mail/mail_client.py`
- `infrastructure/mail/mail_adapter.py`
- `tests/test_m66_mail_reader_adapter.py`

La capacidad registrada es:

- `mail.read`

Acciones soportadas por el adapter:

- `summary` / `recent`: listar correos recientes;
- `search`: buscar correos por texto;
- `read`: leer un mensaje puntual por ID;
- filtro `unread_only` para correos no leídos;
- límites configurables para evitar lecturas masivas accidentales.

## Seguridad

M66 es deliberadamente read-only.

No permite:

- enviar correos;
- responder;
- reenviar;
- borrar;
- archivar;
- marcar como leído/no leído;
- modificar etiquetas.

Las credenciales se leen desde configuración centralizada:

- `GMAIL_ADDRESS`
- `GMAIL_APP_PASSWORD`

No se versiona ningún secreto real. Los tests usan un provider falso y no hacen
llamadas reales a Gmail ni a internet.

## Lenguaje natural

M66 aprovecha los descriptores semánticos de M63B. Frases como las siguientes
pueden descubrir `mail.read`:

- “ROBY, ¿tengo correos nuevos?”
- “ROBY, ¿hay algo importante?”
- “ROBY, ¿me escribió Ana?”
- “ROBY, ¿llegó algo urgente?”
- “ROBY, buscá el correo del presupuesto.”

El usuario no necesita conocer la herramienta ni decir `mail.read`.

## Contratos preservados

M66 no modifica el ciclo cognitivo M50 ni acopla correo al pipeline. El correo
entra como adapter opcional detrás del gateway, con permisos de lectura y salida
normalizada.

Esto mantiene:

- compatibilidad M50–M60;
- contratos M61/M62/M63/M63B;
- separación core/infrastructure;
- reemplazo futuro de IMAP por Gmail OAuth sin tocar ROBY.

## Estado

M66 queda listo cuando:

- `tests/test_m66_mail_reader_adapter.py` pasa completo;
- la suite general permanece en verde;
- Ruff no reporta errores;
- no hay secretos reales versionados.
