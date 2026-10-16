# ROBY XI.2 — M360.0.d Auditoría documental

## 1. Propósito

M360.0.d valida las reglas y la documentación de la raíz contra la arquitectura y el estado verificable alcanzado por M360.0.a, M360.0.b y M360.0.c.

No introduce comportamiento productivo. Su objetivo es evitar que instrucciones históricas, cifras antiguas o decisiones superadas funcionen como autoridades vigentes por accidente.

## 2. Base auditada

- Base funcional: M360.0.c.
- Validación recibida: Ruff limpio y 8669 pruebas aprobadas.
- Documentos raíz revisados: `README.md`, `VISION.md`, `architecture_rules.md`, `external_capabilities.md`, `integration_decision.md`, `ROOT_DOCUMENTATION_INSTALLATION.md`, `CHANGELOG.md` y `CHANGELOG_ARCHITECTURE.md`.
- Evidencia complementaria: inventario funcional M360.0.a, auditoría arquitectónica M360.0.b y auditoría de calidad M360.0.c.

## 3. Reglas documentales ratificadas

1. Un único núcleo cognitivo y una sola autoridad por responsabilidad.
2. Extensión antes que reemplazo y compatibilidad hacia atrás.
3. Toda capacidad externa debe integrarse mediante contratos neutrales, activación explícita, diagnóstico, trazabilidad y Tool Gateway.
4. Ningún milestone es canónico sin Ruff y suite completa aprobados.
5. Las credenciales permanecen en `.roby/credentials.json` y no deben duplicarse ni documentarse con valores reales.
6. ROBY es privado, personal, no comercial y orientado a Carlos y Cristina.
7. La documentación debe describir el sistema existente y distinguir hechos, decisiones, propuestas y brechas.

## 4. Hallazgos

### D1 — Base canónica desactualizada en la raíz — Prioridad alta

`README.md`, `VISION.md`, `architecture_rules.md` y `external_capabilities.md` todavía presentan M347.15 o M348.1 como base vigente. Es información histórica válida, pero ya no debe ocupar el campo de estado actual.

**Resolución:** actualizar las referencias de estado vigente a M360.0.d y conservar la procedencia histórica en secciones explícitas.

### D2 — Registro de integraciones detenido en M348.1 — Prioridad alta

`integration_decision.md` conserva como brechas reales Calendar, Home Assistant y MCP. Calendar ya fue desarrollado y Gmail fue confirmado como maduro; el inventario M360.0.a identifica además Windows, Bluetooth, Android Bridge, Watch, cámara IP e impresión.

**Resolución:** mantener la decisión M348.1 como historial y añadir una decisión M360.0.d que remita al Plan Maestro M360.0.e.

### D3 — Documento de instalación convertido en residuo histórico — Prioridad media

`ROOT_DOCUMENTATION_INSTALLATION.md` describe una operación puntual de M348.1 y un total esperado de 8494 pruebas. No es una guía de instalación general.

**Resolución:** marcarlo como registro histórico de instalación documental; no usarlo como autoridad operacional actual.

### D4 — Duplicidad semántica entre README, reglas e inventario externo — Prioridad media

Los principios fundamentales se repiten, pero no se contradicen. El riesgo surge cuando se actualiza una copia y no las otras.

**Resolución:** definir autoridad por tema:

- `VISION.md`: propósito y límites permanentes.
- `architecture_rules.md`: reglas obligatorias de evolución.
- `README.md`: orientación operativa y estado actual.
- `external_capabilities.md`: inventario de integraciones.
- `integration_decision.md`: decisiones históricas y vigentes.
- `CHANGELOG*.md`: secuencia cronológica, nunca reglas primarias.

### D5 — Ausencia de política explícita de vigencia documental — Prioridad media

No existe una convención única para distinguir “base histórica”, “base vigente”, “fecha de revisión” y “estado”.

**Resolución:** todo documento canónico deberá incluir, cuando corresponda:

- estado (`Vigente`, `Histórico` o `Reemplazado`);
- milestone de última revisión;
- autoridad temática;
- referencia al documento sucesor cuando deje de ser vigente.

### D6 — Riesgo de cifras de tests embebidas — Prioridad baja

Las cifras históricas son útiles como evidencia, pero envejecen rápido cuando se presentan como expectativa actual.

**Resolución:** conservar cifras dentro del milestone que certifican y mantener una sola cifra vigente en README y CHANGELOG del milestone actual.

## 5. Validación de documentos raíz

| Documento | Autoridad | Estado tras M360.0.d | Acción |
|---|---|---|---|
| `VISION.md` | Propósito permanente | Vigente | Actualizar metadatos, preservar contenido |
| `architecture_rules.md` | Reglas arquitectónicas | Vigente | Actualizar base y añadir política documental |
| `README.md` | Entrada operativa | Vigente | Actualizar base y mapa documental |
| `external_capabilities.md` | Inventario externo | Vigente con revisión pendiente por capacidad | Remitir a M360.0.a/e |
| `integration_decision.md` | Registro de decisiones | Vigente como registro | Añadir decisión M360.0.d |
| `ROOT_DOCUMENTATION_INSTALLATION.md` | Instalación documental M348.1 | Histórico | Marcar explícitamente |
| `CHANGELOG.md` | Historial funcional | Vigente | Añadir M360.0.d/e |
| `CHANGELOG_ARCHITECTURE.md` | Historial estructural | Vigente | Añadir decisiones documentales |

## 6. Criterios de aceptación documental

Una futura entrega no se considerará cerrada hasta que:

1. la base vigente aparezca de forma consistente;
2. no se presenten planes como capacidades existentes;
3. las decisiones históricas permanezcan trazables;
4. las autoridades temáticas no se contradigan;
5. los documentos nuevos tengan prueba contractual mínima;
6. los secretos y datos privados no aparezcan en documentación ni fixtures;
7. Ruff y la suite completa permanezcan verdes.

## 7. Conclusión

La documentación es extensa y conserva bien la historia, pero necesita una jerarquía de vigencia más explícita. La corrección recomendada es incremental: actualizar metadatos y referencias, clasificar el documento de instalación como histórico y usar M360.0.e como única autoridad de planificación de la Fase II.
