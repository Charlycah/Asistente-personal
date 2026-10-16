# CERTIFICATION RP.18.4

## Single Conversation Route

Se certifica que las entradas conversacionales interactivas de ROBY atraviesan
una única frontera oficial:

- gateway canónico `OfficialConversationGateway`;
- consola integrada mediante origen `console`;
- texto de escritorio integrado mediante origen `desktop_text`;
- voz de escritorio integrada mediante origen `desktop_voice`;
- compatibilidad interna integrada mediante origen `internal`;
- una sola delegación al `EndToEndLocalConversation` gobernado;
- ausencia de llamadas directas a providers desde las interfaces modificadas;
- preservación de memoria, journal y trazas existentes.

Validación del contenedor:

- pruebas focalizadas: 51 aprobadas;
- suite completa: 6466 pruebas aprobadas;
- `compileall`: correcto.
