# ROBY XI.2 — R-RIQ-00
## Marco rector de investigación sobre inteligencia racional y preservación del baseline

**Estado:** DOCUMENTARY CANDIDATE — PENDING OWNER APPROVAL  
**Modo:** Investigación documental; sin autorización RED/GREEN ni cambios productivos.  
**Estado de partida:** GOVERNED_PLATEAU / EVIDENCE_WAITING; STOP productivo vigente.

### 1. Decisión estratégica
ROBY XI.2 buscará resultados **comparables o superiores a los humanos en tareas y condiciones explícitamente definidas**, mediante su **propia arquitectura racional, integrada y gobernada**. No se fija como requisito imitar los procesos mentales humanos ni se presupone conciencia, AGI o superinteligencia. Toda afirmación de desempeño deberá sustentarse en evaluaciones reproducibles y comparaciones justas.

### 2. Punto de partida certificado y límites de la evidencia
- R-EVO-S1/S2/S3: frentes de continuidad, integración de conocimiento y calibración epistemológica documentalmente cerrados.
- R-EVO-POST-S3 y R-EVO-FR-FINAL: aprobados por el Owner.
- F1: 6 PASS / 0 FAIL en validación focalizada de continuidad multisource.
- F3: 52 PASS / 0 FAIL en validación focalizada de contratos epistemológicos y operacionales.
- F2: diferencia de transporte entre memoria recuperada y selección multisource explícita; requisito conjunto no establecido y regresión no demostrada.
- Los 58 PASS son dos ejecuciones focalizadas, **no** una certificación global de ROBY ni evidencia de inteligencia general.
- Permanece sin demostrar una garantía universal de abstención epistemológica en la respuesta final.

### 3. Pregunta científica rectora
¿Qué mecanismos permiten que ROBY razone, decida, actúe y aprenda con resultados progresivamente mejores, transfiera capacidades a problemas nuevos y verifique sus resultados, sin perder coherencia, trazabilidad, seguridad, corregibilidad ni control humano?

### 4. Líneas de investigación — no son autorizaciones de implementación
**L1. Fundamentos científicos:** lógica e inferencia; epistemología y metacognición; teoría de decisiones; aprendizaje automático y redes neuronales; ciencias cognitivas; generalización y transferencia; seguridad y corregibilidad; filosofía de la inteligencia.

**L2. Evaluación experimental:** tareas nuevas y representativas; criterios observables; métricas de precisión, consistencia, calidad de decisiones, uso de evidencia, abstención calibrada, eficiencia, robustez, transferencia y seguridad; comparación con referencias humanas o sistemas pertinentes cuando exista protocolo válido.

**L3. Capacidades avanzadas (horizonte condicionado):** aprendizaje continuo fiable, autocorrección, planificación prolongada y transferencia entre dominios; estudio de AGI/ASI solo como horizontes de investigación, no como capacidades demostradas ni metas productivas autorizadas.

### 5. Hipótesis iniciales investigables
- H1: una integración correctamente gobernada de memoria y evidencia pertinente mejora resultados en tareas que requieren ambas, frente a una condición de comparación controlada.
- H2: distinguir observación, inferencia, posibilidad e insuficiencia reduce afirmaciones infundadas y mejora la calibración.
- H3: planificación, autorización, ejecución y verificación integradas mejoran el cumplimiento de objetivos sin aumentar acciones indebidas.
- H4: mecanismos de revisión de errores mejoran el desempeño en tareas nuevas sin deteriorar competencias previas.

Estas son **hipótesis**, no conclusiones ni requisitos funcionales aprobados. Cada una necesita definición operacional, controles, métricas, criterios de éxito/fracaso y autorización antes de experimentación.

### 6. Principios arquitectónicos no negociables
1. Una autoridad canónica por capacidad y un solo Reasoning integrado.
2. No duplicar módulos, agentes, managers, planificadores, evaluadores, loops ni autoridades.
3. Consultar antes de cada cambio: documentación maestra raíz, inventarios, registro maestro de capacidades, estado actual, reglas arquitectónicas, documentación del bloque, código y tests existentes.
4. Respetar precedencias y retiros documentados; no reintroducir la proyección Post-M409.1 retirada.
5. Mantener sincronizados código, pruebas y documentación; preservar imports ordenados y límites de longitud de línea.
6. Reentrada productiva solo con requisito autorizado, evidencia concreta y flujo gobernado: reconciliación quirúrgica → RED contractual → certificación local → GREEN quirúrgico → ZIP completo → certificación local.
7. Sin acciones autónomas no autorizadas ni ampliación implícita de permisos.

### 7. Protocolo obligatorio de cierre de cada etapa de investigación
Al finalizar cada etapa, emitir un acta breve que responda:
1. ¿Qué pregunta o hipótesis investigamos?
2. ¿Qué documentos y contratos existentes consultamos, con su precedencia?
3. ¿Qué evidencia obtuvimos (estática, documental, tests, experimentos)?
4. ¿Qué quedó demostrado, refutado o indeterminado?
5. ¿Qué capacidad canónica ya resuelve parte del problema?
6. ¿Existe una necesidad funcional nueva realmente demostrada?
7. ¿Qué riesgos, incertidumbres y alternativas quedan abiertos?
8. ¿Se modificó código, documentación maestra o baseline? ¿Con qué autorización?
9. ¿Cuál es la decisión explícita del Owner: cerrar, continuar, detener o revertir?
10. ¿Cuál es el punto de restauración verificable?

Ninguna etapa se considerará certificada sin aprobación explícita del Owner.

### 8. Preservación y backup antes de investigar
**Recomendación:** efectuar ahora un backup completo y externo del estado actual del proyecto, antes de cualquier nueva modificación. Este documento no acredita que el backup ya exista.

**Contenido mínimo del resguardo:** árbol completo del proyecto y `docs/`, inventarios y registros maestros, código, tests, configuraciones necesarias (sin exponer secretos), lockfiles/dependencias, actas aprobadas y evidencia de ejecución. Si se usa Git, registrar commit y rama; si no, preservar ZIP completo.

**Manifiesto:** fecha y hora local, nombre y tamaño del archivo, SHA-256 del ZIP, identificación de versión/commit si existe, estado `GOVERNED_PLATEAU / EVIDENCE_WAITING`, actas de cierre y resultados focalizados 6+52 PASS. Guardar el manifiesto junto al backup y otra copia en lugar separado.

**Verificación:** comprobar integridad por hash y probar extracción/restauración en una carpeta aislada; no basta con que el archivo ZIP exista. Conservar una copia independiente del equipo y del directorio de trabajo. No incluir credenciales en archivos destinados a compartirse.

**Regla de retorno:** ante divergencia arquitectónica, regresión reproducida o cambio no autorizado, detener, comparar con el manifiesto y restaurar solo por decisión explícita del Owner, preservando evidencia del incidente.

### 9. Primera etapa propuesta
**R-RIQ-S1 — SCIENTIFIC FOUNDATIONS & EXISTING CAPABILITY MAPPING**: revisión documental de fundamentos científicos y su correspondencia con capacidades canónicas ya existentes, con hipótesis falsables y sin código nuevo. Su apertura requiere autorización expresa del Owner tras aprobar este marco y confirmar el backup.

### 10. Disposición
`RESEARCH_CHARTER: CANDIDATE`  
`BASELINE_BACKUP: OWNER_ACTION_PENDING`  
`NEW_PRODUCTIVE_AUTHORIZATION: NONE`  
`CURRENT_STATE: GOVERNED_PLATEAU / EVIDENCE_WAITING`  
`PRODUCTIVE_STOP: ACTIVE`  
`OWNER_APPROVAL: PENDING`
