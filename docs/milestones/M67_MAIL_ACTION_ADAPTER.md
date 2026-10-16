# M67 — Mail Action Adapter

## Objetivo

M67 completa el ciclo de correo incorporando acciones controladas: redactar,
responder y enviar mensajes. A diferencia de M66, este milestone puede mutar el
mundo externo, por lo que toda operación pasa por Permissions & Consent M63.

## Principio

ROBY no envía ni responde correos directamente desde el pipeline. ROBY solicita la
capacidad `mail.send`; el Tool Gateway enruta; Capability Registry describe la
capacidad; Permissions & Consent exige consentimiento explícito; el adapter
realiza la acción.

## Capacidades

- Crear borradores.
- Preparar respuestas vinculadas al mensaje original.
- Enviar mensajes solo con permiso activo.
- Bloquear acciones de envío si la política local lo deshabilita.
- Normalizar resultados para respuesta natural y auditoría.

## Seguridad

- `mail.send` es `WRITE` y `HIGH` risk.
- Requiere confirmación explícita.
- Los tests usan providers falsos; no hay llamadas reales a SMTP.
- Las credenciales se leen únicamente desde configuración segura.

## Integración

```text
Cognitive Pipeline
  -> Tool Gateway M61
  -> Capability Registry M62 / M63B
  -> Permissions & Consent M63
  -> Mail Action Adapter M67
```

## Estado

M67 preserva los contratos M50-M66 y mantiene separado el modo lectura (M66) del
modo acción (M67).
