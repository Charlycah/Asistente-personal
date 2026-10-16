# ROBY XI.2 — M360.0.e Plan Maestro de la Fase II

## 1. Propósito

M360.0.e transforma las auditorías funcional, arquitectónica, de calidad y documental en un roadmap definitivo, incremental y gobernado.

No introduce comportamiento productivo. Establece prioridades, dependencias, puertas de entrada y criterios de cierre para las próximas series.

## 2. Principio rector

La Fase II no reimplementará capacidades ya existentes. Primero consolidará y expondrá lo que ROBY ya posee; después incorporará percepción, sistema operativo, dispositivos y automatización mediante las autoridades canónicas.

Toda ejecución externa deberá pasar por `ToolGatewayManager`. Ningún dispositivo, planificador o modelo podrá crear una ruta paralela de ejecución.

## 3. Prioridades definitivas

### P0 — Fundaciones transversales

1. Certificación de autoridades y composition roots.
2. Línea base reproducible de cobertura y complejidad.
3. Contrato común de capacidades de dispositivo: disponibilidad, permisos, readiness, diagnóstico y desactivación.
4. Política documental de vigencia definida en M360.0.d.
5. Pruebas de caracterización para puntos de alta complejidad antes de refactorizarlos.

**Motivo:** sin estas fundaciones, cada integración física aumenta la deuda y el riesgo de rutas paralelas.

### P1 — Consolidación de capacidades existentes

1. Vision Core: exponer y certificar OCR, QR, personas, rostros, objetos y escena mediante un gateway gobernado.
2. Desktop/Windows: consolidar consulta del entorno y acciones mínimas seguras sobre aplicaciones y archivos.
3. Calendar y Gmail: usarlos como patrones de referencia y completar diagnósticos/documentación pendientes.
4. Audio Intelligence: consolidar entrada, sesiones y diagnóstico; separar control del sistema de la transcripción.

**Motivo:** entrega valor con menor riesgo porque reutiliza implementación existente.

### P2 — Puentes de dispositivos

1. Android Bridge.
2. Bluetooth Manager.
3. Samsung Watch Gateway sobre Android Bridge cuando sea viable.
4. Impresora y escáner gobernados.
5. Cámara IP como fuente de Vision, no como segundo núcleo visual.

**Dependencia:** contrato común de dispositivos y Tool Gateway operativo.

### P3 — Automatización del entorno

1. Home Assistant Gateway.
2. Flujos domésticos con consentimiento, límites y trazabilidad.
3. Automatizaciones programadas y condicionales gobernadas.

**Dependencia:** dispositivos, permisos, diagnóstico y política de acciones físicas.

### P4 — Interoperabilidad avanzada

1. MCP como adaptador de herramientas, nunca como autoridad cognitiva.
2. Catálogo gobernado de servidores y capacidades MCP.
3. Aislamiento, permisos, límites de red y auditoría por servidor.

**Motivo:** MCP amplía superficie y riesgo; debe incorporarse después de estabilizar el modelo interno de herramientas y dispositivos.

### P5 — Planificación gobernada de mayor alcance

1. Planes multietapa explicables.
2. Estado persistente de tareas.
3. Pausas, reanudación y cancelación.
4. Confirmaciones por acción irreversible.
5. Coordinación entre herramientas sin agentes paralelos.

**Dependencia:** gateways consolidados y calidad demostrada en integraciones reales.

## 4. Secuencia propuesta de milestones

| Serie | Objetivo | Salida verificable |
|---|---|---|
| M361 — Quality Baseline | métricas reproducibles y pruebas de caracterización |
| M362 — Governed Vision Gateway | visión existente accesible y certificada |
| M363 — Windows Workspace Foundation | consultas y acciones mínimas gobernadas |
| M364 — Device Capability Foundation | contrato común, readiness, permisos y diagnóstico |
| M365 — Android Bridge | comunicación local gobernada con Android |
| M366 — Memoria Cognitiva | fundación episódica, semántica, procedimental y de largo plazo |
| M367 — Samsung Watch Gateway | funciones seleccionadas a través de Android |
| M368 — Printing and Scanning | impresión/escaneo con preview y confirmación |
| M369 — IP Camera Vision Source | cámara IP integrada al Vision Gateway |
| M370 — Home Assistant Gateway | automatización doméstica gobernada |
| M371 — MCP Gateway | interoperabilidad aislada y auditable |
| M372 — Governed Task Planning | planes persistentes multietapa sobre gateways existentes |

La numeración puede subdividirse (`.1`, `.2`, etc.) y debe mantenerse incremental. No obliga a implementar una serie cuando su hardware, credenciales o entorno no estén disponibles.

## 5. Puertas obligatorias por milestone

Cada milestone funcional deberá incluir:

1. una sola finalidad;
2. inventario previo de capacidades reutilizables;
3. contrato neutral;
4. adaptador reemplazable;
5. activación explícita y modo desactivado seguro;
6. permisos y consentimiento proporcionales al riesgo;
7. ejecución mediante Tool Gateway;
8. trazabilidad sin secretos;
9. pruebas unitarias, negativas, de composición y degradación;
10. documentación y rollback;
11. Ruff limpio y suite completa aprobada;
12. certificación manual separada cuando dependa de hardware o servicios reales.

## 6. Exclusiones de la Fase II

No se crearán:

- un segundo núcleo cognitivo;
- un segundo planificador general;
- ejecución directa desde modelos o dispositivos;
- automatización silenciosa de acciones irreversibles;
- almacenamiento alternativo de credenciales;
- refactorizaciones masivas sin caracterización;
- soporte genérico para usuarios hipotéticos.

## 7. Criterio de reordenamiento

Una prioridad sólo podrá adelantarse cuando:

- resuelva una necesidad concreta de Carlos o Cristina;
- sus dependencias estén satisfechas;
- exista entorno real para certificarla;
- no fuerce una autoridad paralela;
- el cambio sea pequeño y reversible.

Las prioridades podrán posponerse por falta de hardware, APIs, permisos o utilidad inmediata sin considerarse fracaso del plan.

## 8. Primer paso recomendado

El siguiente milestone funcional recomendado es **M361 — Quality Baseline**. Debe medir, no refactorizar: cobertura, complejidad, módulos críticos y pruebas de caracterización. Después, **M362 — Governed Vision Gateway** es la primera entrega de capacidad porque aprovecha un subsistema ya avanzado y permite validar el patrón que usarán Windows y los dispositivos.

## 9. Conclusión

La Fase II queda ordenada desde consolidación interna hacia percepción, sistema operativo, dispositivos, automatización, interoperabilidad y planificación avanzada. El roadmap prioriza valor personal, reutilización, gobernanza y validación completa por encima de la novedad tecnológica.

---

## Anexo evolutivo R-MP-EVOL-S2 — Objetivos cognitivos, humanización y entorno local (2026-10-12)

**Tipo:** integración documental aprobada por el Owner; sin habilitación productiva ni experimental.
**Alcance:** amplía objetivos y condiciones de reentrada; no reemplaza el orden histórico M360 ni los cierres posteriores.
**Precedencia:** `ROBY_XI_2_CURRENT_TRUTH.md` y última decisión del Owner; luego registro canónico raíz, inventario cognitivo y reconciliaciones posteriores. Las prioridades P0–P3 de este anexo **no sustituyen** las prioridades P0–P4 históricas de M360: son prioridades temáticas de evaluación.
**Antecedentes:** `R_MP_EVOL_S1_RECONCILIACION_PREVIA_OBJETIVOS_COGNITIVOS.md`, `R_MP_EVOL_S1_CONTRASTE_COBERTURA_CANONICA_ZIP10.md`, `R_MP_EVOL_S2_PROPUESTA_ACTUALIZACION_QUIRURGICA_PLAN_MAESTRO_ZIP10.md` y 25 documentos `docs/R_RIQ_S2_*.md`. Los tres R-MP-EVOL son documentos de trabajo locales y deben incorporarse por separado a `docs/` si se desea referenciarlos desde el repositorio.

### A. Objetivos y límites de maduración

### Eje EVOL-C — Maduración cognitiva gobernada

**Propósito.** Mejorar capacidad efectiva de ROBY para razonar, generalizar, recordar, planificar, explicar incertidumbre y corregirse, reutilizando las autoridades canónicas. Se distinguen: **documentado**, **integrado productivamente**, **medido**, **validado científicamente**. Ninguna categoría implica automáticamente la siguiente.

| Objetivo Owner | Reutilización / estado documental S1 | Resultado exigible antes de declarar mejora | Dependencia y límite |
|---|---|---|---|
| Razonamiento abstracto | CAP-04/07/08, razonamiento gobernado; acotado | Resolver problemas inéditos con evidencia y explicación | Sin segundo razonador |
| Zero-shot / few-shot | CAP-08/11/12; parcial | Transferencia comparativa con tareas independientes | Protocolo y admisión separados |
| Memoria de trabajo y largo plazo | CAP-01/02/03, Memory Gateway/Knowledge; gobernada | Recuperación pertinente, procedencia y conexión a salida | H1 científico: evidencia insuficiente |
| Multimodalidad | H5 parcial; rutas visuales y audio distintas | Composición verificable de modalidades efectivamente disponibles | No afirmar tacto/sensores inexistentes |
| Modelos de mundo | CAP-06; predicción causal/temporal acotada | Predicciones contrastables y límites explícitos | No simulador universal |
| Aprendizaje continuo | CAP-12/20, aprobación humana; parcial | Retención, transferencia, no regresión T0/T1/T2 | H4 científico sin admisión |
| Metacognición | CAP-09/13/15; acotada | Detección de límites, revisión y atribución a respuesta final | H2 científico sin admisión |
| Agencialidad y planificación | CAP-11/13 y autorización canónica | Planes revisables, trazabilidad decisión–resultado | H3 científico parcialmente factible |
| Teoría de la mente | Contexto/presencia; evidencia específica pendiente | Hipótesis sociales prudentes, calibradas y corregibles | No lectura mental ni inferencia sensible gratuita |
| Alineación y ética | Gates, consentimiento, supervisión; gobernada | Cumplimiento de restricciones y justificación | No equivaler a ética humana general |
| Bucles de crítica y corrección | CAP-05/09/14; efectividad pendiente | Mejora observable del resultado, sin degradación | No loop/autoridad paralela |
| Entropía y confianza | CAP-09; evidencia específica pendiente | Calibración de confianza; entropía solo si hay distribución válida | No porcentajes inventados |
| Planificación por imaginación | CAP-06/11/13; acotada | Comparar escenarios y consecuencias antes de actuar | Simulación ≠ permiso de ejecución |

### Eje EVOL-H — Identidad, humanización y conversación

ROBY debe conservar identidad propia y expresión natural, coherente, configurable y respetuosa. TARS (humor/franqueza), Data (precisión/curiosidad), Samantha (fluidez), Dolores (continuidad narrativa) y Giskard/Daneel (prudencia) son **referencias de diseño**, no identidades a copiar ni evidencia de conciencia. Reutilizar M55/M377 y la proyección canónica post-GREEN ya documentada; verificar consumidor ordinario antes de abrir residual. Conciencia funcional = autodescripción veraz, continuidad y metacognición evaluable; **no** prometer experiencia subjetiva. La identidad vocal permanece FUTURE salvo evidencia específica.

### Eje EVOL-L — Fuentes locales y experiencia multimedia

Mantener acceso explícito y gobernado por raíz configurada, propósito, autorización y límites. `D:\Biblioteca` tiene antecedente CAP-17; `D:\Documentos` y `D:\Roby` cuentan con GREEN de admisión/consulta específicos; no generalizar a exploración irrestricta. La petición Owner `D:\Pinacoteca` requiere identificar si el contenido es visual, musical o mixto y verificar configuración real. CAP-18 visual **no** equivale a catálogo musical. Para música, separar búsqueda, selección, reproducción, STOP y controles adicionales; no afirmar que todas las pistas están indexadas. Consulta de historia de desarrollo = lectura autorizada, no autoedición de código.

### Eje EVOL-G — Aprendizaje y mejora bajo gobierno

Las propuestas de mejora de ROBY pueden ser evaluadas por Owner y autoridades existentes; nunca equivalen a auto-modificación productiva. Cualquier red neuronal o proveedor adicional permanece `MODEL_ACQUISITION: UNMAPPED / DENY / NO-GO` hasta nueva autorización y seam concreto. Preservar `M377: HOLD`, privacidad, reversibilidad, no regresión y `STOP_PRODUCTIVE`.

### B. Orden condicionado de evaluación

**P0 — Experiencia conversacional ordinaria:** comprobar de forma focalizada la llegada efectiva de capacidades existentes al turno real; sin repetir auditoría histórica post-GREEN.  
**P1 — Autocrítica, calibración y planificación:** definir un caso observable y autorizado por cada residual demostrado; sin reabrir experimentalmente R-RIQ-H1–H4.  
**P2 — Directorios y música:** verificar requisitos concretos del Owner frente a raíces, tipos de activo y funciones ya disponibles.  
**P3 — Multimodalidad ampliada, aprendizaje longitudinal y modelos nuevos:** condicionados a evidencia, dependencias, seguridad y autorizaciones adicionales.

Estas prioridades son **orden de análisis de requisitos**, no backlog autorizado de implementación. Si no hay brecha reproducible y reutilización agotada: `NO PRODUCTIVE RESIDUAL / EVIDENCE_WAITING`.

### C. Barreras científicas preservadas

H1 memoria/evidencia `INSUFFICIENT_EVIDENCE`; H2 calibración `INSUFFICIENT_EVIDENCE`; H3 acción/resultado `PARTIALLY_FEASIBLE`; H4 aprendizaje `INSUFFICIENT_EVIDENCE`. `EXPERIMENTAL_ADMISSION: NOT_GRANTED`. Cualquier experimento requiere B1 autorización específica; B2 trazabilidad; B3 referencia independiente; B4 comparabilidad; B5 seguridad/privacidad; B6 protocolo, Owner y STOP. La propuesta no satisface esas barreras por sí sola.

### D. Control de cambios y autorización

- No crear nuevos módulos, gestores, agentes, cerebros, loops, stores o autoridades sin prueba de residual y contrato separado.
- No modificar Current Truth, Capability Registry, Cognitive Inventory, R-MPHR ni R-RIQ-S2 mediante este anexo.
- No confundir metas de capacidad, integración productiva y validación científica.
- `M377: HOLD`; `MODEL_ACQUISITION: UNMAPPED / DENY / NO-GO`.
- `EXPERIMENTAL_ADMISSION: NOT_GRANTED`; `NEXT_PRODUCTIVE_HORIZON: NOT_SELECTED`.
- `STOP_PRODUCTIVE: ACTIVE`.
