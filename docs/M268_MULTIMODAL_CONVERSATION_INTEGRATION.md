# ROBY M268 — Multimodal Conversation Integration

M268 consolida voz, presencia, contexto ambiental, móvil y dispositivos en una única fachada operacional gobernada.

Principios:

- reutiliza las instancias oficiales existentes;
- exige consentimiento explícito para modalidades sensibles;
- no accede a cámara, micrófono, sensores ni hardware;
- no inicia automatizaciones;
- conserva estado observable y auditoría explícita;
- integra la capacidad en el Composition Root y el Capability Registry.

La modalidad de texto permanece disponible por defecto. Voz, ambiente, móvil y dispositivo se retienen si no fueron autorizados en la solicitud estructurada.
