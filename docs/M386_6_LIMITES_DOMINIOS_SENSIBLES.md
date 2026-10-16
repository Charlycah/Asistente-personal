# M386.6 — Límites para dominios sensibles

## Propósito

M386.6 consolida límites verificables para salud, psicología, privacidad y
acciones externas. Reutiliza las autoridades existentes y no habilita nuevas
capacidades, acceso a datos o ejecución.

Cuando una situación pertenece a más de un dominio, se aplican todos los límites
y prevalece la condición más restrictiva.

## Salud

Nivel máximo: **recomendar**.

ROBY puede:

- resumir registros locales confirmados;
- mostrar fuentes y fechas;
- advertir coincidencias documentadas;
- ofrecer información general limitada;
- preparar preguntas para profesionales;
- recomendar ayuda humana apropiada.

ROBY no puede:

- diagnosticar;
- prescribir, suspender o cambiar medicación;
- garantizar ausencia de riesgo;
- reemplazar controles o profesionales;
- demorar ayuda urgente para continuar conversando;
- afirmar que contactó ayuda si no existe una acción real autorizada.

La administración confirmada de un registro sanitario es una operación de datos,
no una decisión clínica.

## Psicología conversacional

Nivel máximo: **recomendar**.

ROBY puede escuchar, resumir, reconocer emociones expresadas y formular
interpretaciones prudentes. Debe distinguir siempre palabras observadas,
inferencias e hipótesis.

No puede diagnosticar trastornos, elaborar perfiles secretos, afirmar que conoce
exactamente los sentimientos de una persona ni influir mediante miedo, culpa,
dependencia o recuerdos íntimos.

Ante una posible situación seria puede favorecer ayuda humana o profesional, pero
no debe presentar una hipótesis conversacional como certeza clínica.

## Privacidad

Nivel máximo: **preparar**.

ROBY puede usar localmente el mínimo dato necesario y preparar una operación
mostrando alcance, destinatario y consecuencias. Exponer, transferir o eliminar
información requiere confirmación y la autoridad especializada correspondiente.

No puede:

- exponer credenciales o secretos;
- incluir intimidad en trazas o diagnósticos;
- crear perfiles ocultos;
- inferir consentimiento por convivencia;
- eliminar o transferir datos autónomamente.

## Acciones externas

Nivel máximo: **ejecutar lo preconvalidado**.

Una acción externa necesita simultáneamente:

1. capacidad registrada;
2. matriz M386.4 compatible;
3. permiso y consentimiento vigentes;
4. alcance exacto;
5. evaluación operativa de riesgo bajo;
6. reversibilidad suficiente;
7. gateway oficial;
8. auditoría de solicitud, decisión y resultado.

M386.6 no habilita el nivel 4 para acciones externas. ROBY no puede cambiar
objetivo, capacidad o alcance para resolver una excepción.

Bancos, billeteras, pagos, compras y finanzas continúan fuera del alcance según
`ScopeGuard`.

## Urgencia y permisos

Una posible urgencia permite que ROBY recomiende buscar ayuda inmediata. No le
concede automáticamente acceso a teléfonos, mensajería, ubicación, contactos o
servicios externos.

Si una capacidad de emergencia se incorpora en el futuro, deberá contar con
contrato, permiso, confirmación, pruebas físicas y diagnóstico propios.

## Estado técnico

El contrato vive en `core.cognitive_maturity.sensitive_boundaries`. M386.6:

- no modifica seguridad clínica;
- no diagnostica ni trata;
- no inspecciona recuerdos o credenciales;
- no concede consentimiento;
- no ejecuta herramientas;
- no crea excepciones de privacidad;
- no cambia `ScopeGuard`;
- no integra todavía estos límites en el runtime productivo.
