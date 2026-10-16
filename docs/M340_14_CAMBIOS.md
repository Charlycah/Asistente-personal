# M340.14 - Historial longitudinal de signos vitales

- Agrega un registro local y atómico independiente en `.roby/vital_signs.json`.
- Mantiene completamente separados los controles de Carlos y Cristina.
- Permite registrar presión, glucemia, peso, saturación, temperatura y frecuencia cardíaca.
- Exige confirmación explícita antes de persistir cada control.
- Incorpora historial por período, tendencias descriptivas y resúmenes semanales o mensuales.
- Las tendencias muestran variaciones numéricas entre el primer y el último registro, sin diagnóstico ni interpretación clínica.
- Los resúmenes calculan promedios descriptivos a partir de datos confirmados y excluyen registros archivados.
- Integra el último control disponible en el resumen del Health Orchestrator.
- Integra los comandos de signos vitales tanto en el flujo escrito como en el flujo de voz.
- Agrega 9 pruebas específicas de M340.14.
- Validación funcional completa esperada: 7988 tests OK.

## Comandos principales

- `registrar signos de Carlos: fecha=2026-07-28T09:00 | presión=128/82 | glucemia=101 | peso=76,5 | saturación=97 | temperatura=36,4 | pulso=68`
- `confirmar signos`
- `cancelar signos`
- `historial de signos de Cristina`
- `historial de signos de Carlos de los últimos 7 días`
- `tendencia de presión de Cristina`
- `tendencia de peso de Carlos de los últimos 30 días`
- `resumen semanal de signos de Carlos`
- `resumen mensual de signos de Cristina`
