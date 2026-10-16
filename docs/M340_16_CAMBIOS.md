# ROBY XI.2 M340.16 — Seguridad clínica avanzada

## Alcance

- Revisión descriptiva separada para Carlos y Cristina.
- Detección de medicamentos activos duplicados por nombre normalizado.
- Identificación de registros todavía activos cuya fecha final ya pasó.
- Aviso administrativo de medicamentos que finalizan dentro de 30 días.
- Registro confirmado de reglas documentadas de interacción potencial.
- Cruce de esas reglas únicamente contra medicamentos activos de la misma persona.
- Registro confirmado de fechas de controles médicos y aviso de vencidos o próximos.
- Integración con entrada escrita y voz en la interfaz de escritorio.

## Límites de seguridad

ROBY no incorpora una base autónoma de interacciones, no diagnostica y no indica
suspender, duplicar ni cambiar medicación. Las reglas de interacción deben incluir
una fuente explícita y requieren confirmación antes de guardarse.
