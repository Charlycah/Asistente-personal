## M363 — Windows Workspace Foundation

- Declara una única frontera de aplicación para el workspace Windows.
- Mantiene proveedores de plataforma detrás de un protocolo.
- Clasifica capacidades por riesgo y reserva mutaciones para Tool Gateway.
- Conecta screenshots con el gateway de visión gobernado.

## M362 — Governed Vision Gateway

- Establece `GovernedVisionGateway` como frontera oficial de aplicación.
- Conserva `OfficialVisionCore` como motor visual interno ya validado.
- Añade un repositorio local gobernado para imágenes guardadas voluntariamente.
- Exige solicitud y consentimiento explícitos y prohíbe biometría implícita.
- No agrega reconocimiento facial, vigilancia ni proveedores externos.

# M361 — Quality Baseline

- Congela una referencia cuantitativa reproducible antes de M362.
- Clasifica subsistemas por criticidad y concentra revisión en runtime, Tool Gateway, memoria y planificación.
- Define umbrales de revisión sin convertirlos en refactorización automática.
- Prohíbe nuevas autoridades paralelas y preserva la ejecución gobernada.
- No modifica arquitectura productiva.

## M360.0.e — Plan Maestro de la Fase II

- Se establece una única secuencia de prioridades desde fundaciones de calidad hasta planificación gobernada.
- Vision y Desktop se consolidarán antes de abrir nuevas rutas de dispositivos.
- Android Bridge precederá al Samsung Watch Gateway.
- MCP y Home Assistant serán gateways gobernados bajo ToolGatewayManager.

## M360.0.d — Auditoría documental

- Se define autoridad temática para cada documento canónico.
- Se separan estado vigente, referencias históricas y documentos reemplazados.
- El Plan Maestro M360.0.e pasa a ser la única autoridad de planificación de la Fase II.


## M360.0.c — Auditoría de calidad

- La deuda prioritaria se clasifica como complejidad concentrada, no como inestabilidad observable.
- Se exige caracterización antes de refactorizar composition roots, pipeline o Desktop UI.
- Se prohíben limpiezas masivas de excepciones o componentes históricos sin evidencia.
- Se fijan puertas de calidad para cada futura integración externa o física.

## M360.0.b — Auditoría arquitectónica

- Se ratifica `OfficialROBYRuntime` como composición operacional canónica.
- Se ratifica `ToolGatewayManager` como única frontera de ejecución de herramientas.
- Se delimitan los registros de runtime, capacidades cognitivas y capacidades de dispositivos.
- Se establece que Samsung Watch 7 dependerá prioritariamente del Android Bridge.
- Se prohíben rutas paralelas para Vision, Windows, Bluetooth, MCP y Home Assistant.

## M360.0.a — Auditoría funcional sin cambio de arquitectura

M360.0.a no crea autoridades, contratos ni rutas productivas. Documenta el estado funcional verificable de M359, preserva las reglas canónicas y establece evidencia para las auditorías arquitectónica, de calidad y documental siguientes.

# ROBY XI.2 — CHANGELOG_ARCHITECTURE.md

> **Historial canónico de decisiones arquitectónicas**

Este documento registra decisiones estructurales y documentales. No sustituye al
changelog funcional ni al historial de código.

## M347.15 — Base canónica estabilizada

- Se valida la base con 8494 pruebas.
- Se preserva un único núcleo cognitivo.
- Se consolida el punto de partida para la siguiente etapa.
- `.roby/credentials.json` permanece como componente canónico y privado.

## M348.0 — Inventario de capacidades externas

- Se crea `external_capabilities.md`.
- Se establece un inventario obligatorio antes de nuevas integraciones.
- Se formaliza el flujo de contrato, adaptador, activación, gateway,
  trazabilidad y pruebas.
- No se modifica código productivo.

## M348.1 — Selección de la primera brecha real

- Se revisa el inventario contra capacidades existentes.
- Gmail deja de figurar como pendiente: ya está implementado y gobernado.
- Ollama / LLM local deja de figurar como pendiente: ya existe el proveedor
  local gobernado.
- Se selecciona Google Calendar como primera brecha real.
- Se crea `integration_decision.md`.
- Se crea `VISION.md`.
- Se formaliza que ROBY XI.2 es personal, privado, no comercial y no
  distribuible.
- Se formaliza que su propósito es cuidar, informar, organizar, acompañar y
  entretener a Carlos y Cristina.
- Se actualiza `architecture_rules.md` con gobernanza documental y de
  credenciales.
- Se establece que `.roby/credentials.json` no debe eliminarse ni reemplazarse,
  y que las nuevas APIs deben integrarse al sistema canónico existente.
- No se modifica código productivo.
- No se modifican secretos ni credenciales reales.


## M348.2 — Contrato o extensión mínima

- Se confirma que Calendar ya existe como capacidad cognitiva declarada.
- No se crea una nueva autoridad ni un nuevo gateway.
- Se incorpora `CalendarProvider`, contrato neutral del proveedor.
- Se incorporan modelos normalizados y timezone-aware para intervalos, eventos,
  borradores y disponibilidad.
- El alcance se limita a listar eventos, consultar disponibilidad y crear un
  evento.
- Se agregan pruebas unitarias específicas de contrato.
- No se integra Google API, OAuth ni red.
- No se modifica `.roby/credentials.json`.

## Próximos registros previstos

### M348.2

Contrato o extensión mínima para Calendar.

### M348.3

Adaptador del proveedor.

### M348.4

Configuración y activación controlada.

### M348.5

Errores, readiness y recuperación.

### M348.6

Trazabilidad cognitiva integral.

### M348.7

Pruebas end-to-end.

### M348.8

Validación manual con servicio real.

### M348.9

Estabilización y creación de `integration_pattern.md`.

## M348.3 — Adaptador Google Calendar

- Se implementa `GoogleCalendarAdapter` detrás de `CalendarProvider`.
- Se agrega una fábrica diferida del cliente Google Calendar API v3.
- Se traducen eventos, disponibilidad y creación a modelos neutrales de ROBY.
- Se soportan eventos con horario y eventos de día completo.
- Se omiten eventos cancelados en los resultados normalizados.
- Se normalizan errores de autenticación, límite, rechazo, timeout y disponibilidad.
- El SDK de Google no se filtra hacia el núcleo cognitivo.
- No se conecta todavía el adaptador al runtime ni al planner.
- No se implementa activación OAuth en este milestone.
- No se modifica `.roby/credentials.json`.
- Se agregan 11 pruebas específicas del adaptador.

## M348.4 — Configuración y activación controlada

- Se incorpora `CalendarRuntimeComposition` con estados `disabled`, `degraded` y `ready`.
- La activación depende exclusivamente de `ROBY_CALENDAR_ENABLED`.
- Se reutilizan `GOOGLE_TOKEN_FILE` y `GOOGLE_CLIENT_SECRET_FILE` desde el sistema canónico de credenciales.
- La autorización interactiva permanece deshabilitada salvo `ROBY_CALENDAR_ALLOW_INTERACTIVE_OAUTH=true`.
- Se requieren scopes mínimos para eventos y disponibilidad.
- Calendar se integra al único `RuntimeCompositionRoot` sin conectarse todavía al planner ni al `ToolGatewayManager`.
- La ausencia o invalidez de credenciales produce degradación segura y no altera otras capacidades.
- No se modifica `.roby/credentials.json` ni se persisten secretos durante el armado del runtime.
- Se agregan 9 pruebas específicas de configuración, activación y degradación controlada.

## M348.5 — Errores, readiness y recuperación

- Se incorpora una taxonomía estable y neutral de errores de Calendar.
- Se agrega un informe de readiness sin secretos con niveles `disabled`, `blocked` y `ready`.
- Se agregan planes deterministas de recuperación, siempre explícitos y nunca automáticos.
- Los fallos de autenticación, límite, rechazo, timeout, conectividad y desconocidos se normalizan sin filtrar tipos del SDK.
- `CalendarRuntimeComposition` expone `readiness()`, `recovery_plan()` y `recover()`.
- `recover()` reutiliza exclusivamente la activación OAuth gobernada ya existente.
- La configuración faltante y la habilitación requieren intervención del operador; no se modifican silenciosamente.
- El arranque continúa sin reautorizaciones, escrituras ni reintentos ocultos.
- No se modifica `.roby/credentials.json`.
- Se agregan 12 pruebas específicas de resiliencia y diagnóstico.


## M348.6 — Registro en ToolGateway y exposición controlada al planner

- Se agrega `CalendarToolGatewayRegistration` como frontera M61 para Calendar.
- Se registran `calendar.events.list` y `calendar.availability.check` como capacidades de lectura.
- Las lecturas sólo quedan habilitadas cuando `CalendarRuntimeComposition` está `ready`.
- `calendar.event.create` queda declarada, deshabilitada y con confirmación obligatoria.
- Se incorpora `CalendarConversationInterceptionPort` para exponer agenda y disponibilidad al runtime oficial.
- `OfficialRuntimeCapabilityRegistry.register()` acepta ahora `kind` explícito y Calendar se declara como `CapabilityKind.CALENDAR`.
- El planner puede usar implícitamente sólo la capacidad de lectura, de riesgo bajo y sin confirmación.
- La creación conversacional permanece bloqueada y no ejecuta llamadas al proveedor.
- No se modifica `.roby/credentials.json`.
- Se agregan 7 pruebas específicas de gateway, registro y exposición controlada.

### Corrección de validación M348.6

- Se preserva el orden histórico del registro oficial de capacidades cuando Calendar está deshabilitado o no está listo.
- `calendar.read` se registra en el runtime oficial únicamente cuando `CalendarRuntimeComposition` informa estado `ready`.
- La exposición controlada al planner deja de alterar capacidades existentes en configuraciones sin Calendar activo.
- Se incorporó la versión corregida y ordenada de `app/runtime_root_factory.py` suministrada durante la validación.

## M348.7 — Consulta conversacional completa de agenda y disponibilidad

- Se amplía `CalendarConversationInterceptionPort` sin crear una autoridad paralela.
- Las consultas admiten hoy, mañana, pasado mañana, esta semana, próxima semana, días de la semana y fechas `DD/MM[/AAAA]`.
- Se incorporan franjas mañana, tarde y noche, rangos horarios explícitos y consultas de una hora concreta.
- La agenda se presenta ordenada, con hora de inicio, fin y ubicación cuando está disponible.
- La disponibilidad informa bloques ocupados concretos en lugar de una respuesta binaria genérica.
- El intervalo por defecto continúa siendo las próximas 24 horas.
- La creación conversacional permanece bloqueada antes de ejecutar cualquier operación del proveedor.
- No se modifica `.roby/credentials.json`.
- Se agregan 10 pruebas específicas de comprensión temporal y presentación conversacional.

## M348.8 — Creación gobernada de eventos con confirmación explícita

- Calendar construye un borrador conversacional sin mutar el proveedor.
- La disponibilidad se valida al preparar el borrador y se revalida antes de crear.
- La confirmación queda aislada por propietario y sesión y requiere una fórmula inequívoca.
- Cancelar descarta el borrador sin modificar Calendar.
- `calendar.event.create` queda disponible sólo con runtime `ready`, riesgo alto,
  permiso de escritura y confirmación explícita obligatoria.
- La capacidad de escritura no se expone al planner como ejecución implícita.
