# ROBY XI.2 — R-CONV-EXP-02A
## Registro contractual de brecha — GREEN-02

**Estado:** HOLD CONTRACTUAL / NO-GO PRODUCTIVO  
**Modalidad:** documental, sin cambios de código, tests ni documentación del repositorio  
**STOP_PRODUCTIVE:** ACTIVE  
**Carácter:** propuesta de registro para incorporación gobernada; no se declara aplicada al árbol local.

### 1. Objeto

Registrar la distancia entre el contrato RED de idioma visible y las capacidades productivas demostradas, sin rebajar el objetivo funcional: ROBY debe responder en español argentino por defecto, respetar una solicitud explícita de inglés y proteger citas, código, rutas, términos técnicos, metadatos y procedencia.

### 2. Evidencia examinada

- `ROBY_EXP02A_GREEN02_DOCUMENTARY_RECONCILIATION.txt`: extractos de `README.md`, `architecture_rules.md`, `ROBY_XI_2_CURRENT_TRUTH.md`, registro maestro de capacidades y contenido de doce tests RED. La sección de candidatos documentales EXP-02A está vacía **según la búsqueda por nombre efectuada**; esto no acredita inexistencia de documentación con otros nombres.
- `ROBY_EXP02A_GREEN02_FINAL_BOUNDARY_INSPECTION.txt`: fronteras de inferencia, estilo, proveedor, presentación, traducción explícita y UI; búsqueda focal de identificadores de mecanismos lingüísticos sin coincidencias. Esta búsqueda negativa no es una prueba exhaustiva de inexistencia.
- Inspecciones anteriores: `ROBY_EXP02A_TRANSLATION_CONTRACT_INSPECTION.txt` y `ROBY_EXP02A_LANGUAGE_AUTHORITY_INVENTORY.txt`.

### 3. Autoridades y fronteras preservadas

| Componente | Competencia comprobada | Límite |
|---|---|---|
| `EnvironmentInferenceRequestPort.build` | Selección de instrucción de idioma previa a inferencia | No verifica idioma de salida |
| `HouseholdConversationStyle` | Política doméstica de estilo y prompts español/inglés | No traduce |
| `LocalProviderRuntimeAdapter` | Composición de prompt y ejecución de proveedor | No garantiza obediencia del modelo |
| `UnifiedExperienceLayer.present` / `present_operational_response` | Frontera de presentación y normalización visible | No se demostró detector general de incumplimiento lingüístico |
| `ConversationalTranslation` | Reconocimiento de pedidos explícitos de traducción | No es traductor automático de respuestas no conformes |
| `ROBYUIAdapter` | Adaptación de respuesta y fallo de UI | No define degradación por idioma |
| `AdaptivePersonalityAuthority` (M377) | Modulación expresiva canónica | HOLD INTACT; no intervenir |

### 4. Brecha discriminante

**Entrada:** `Decime como esta el clima hoy.`  
**Salida simulada del proveedor:** `The weather is sunny and warm today.`

El RED exige que la respuesta visible no sea la inglesa original y, en el caso semántico, que contenga `soleado` y `calor` con `rationale` preservado. Esto presupone traducción semántica fiable o una capacidad equivalente, no demostrada en las fronteras inspeccionadas. Cambiar sólo `rationale` no resuelve el incumplimiento. Tampoco es admisible satisfacer el caso mediante texto meteorológico fijo, glosarios ad hoc o una segunda llamada al proveedor.

**Brecha G-01 — detección:** no se ha identificado una capacidad gobernada y suficientemente fiable para clasificar idioma de respuestas arbitrarias y distinguir citas, código y terminología técnica.

**Brecha G-02 — tratamiento:** no se ha demostrado una política integrada que trate respuestas no conformes sin inventar hechos, ocultar errores, alterar procedencia ni hacer otra inferencia.

**Brecha G-03 — semántica:** no se ha demostrado una capacidad de transformación semántica general de inglés no solicitado a español que preserve fielmente el contenido con una sola llamada al proveedor.

### 5. Contratos que permanecen vigentes

1. Español argentino predeterminado e inglés cuando se solicita explícitamente.
2. Precedencia correcta de idioma frente a instrucciones configuradas y personalidad, sin conflicto de prompts.
3. Conservación de código, rutas, citas y términos técnicos en inglés sin cambio de idioma por falsos positivos.
4. Preservación de `rationale`, `origin`, `network_access_performed` y demás procedencia aplicable.
5. Una sola llamada de inferencia por turno en la ruta contratada; sin mutaciones de plataforma no autorizadas.
6. Ninguna autoridad, detector, gestor, traductor o circuito paralelo.
7. Una respuesta inglesa no solicitada no se declara conforme sólo por modificar metadatos.

### 6. Decisión contractual

**GREEN-01:** preservar la certificación local reportada de 39 PASS; no extrapolarla a cumplimiento de salida.  
**GREEN-02:** HOLD / NO-GO productivo.  
**RED:** conservar los doce archivos intactos como evidencia contractual, incluidos los casos semánticos pendientes; no reescribir ni desactivar aserciones para forzar GREEN.  
**EXP-02B / EXP-02C:** preservar sus estados GREEN previamente reportados.  
**M377:** HOLD INTACT.  
**STOP_PRODUCTIVE:** ACTIVE.

### 7. Criterios de reapertura (todos obligatorios)

- **Autoridad:** demostrar que el mecanismo propuesto pertenece a una frontera canónica existente y no duplica capacidades.
- **Detección:** especificar cobertura, límites y casos de falsos positivos con código, citas y lenguaje mixto; no afirmar fiabilidad universal sin evidencia.
- **Tratamiento:** definir contractualmente cómo se informa o transforma una respuesta no conforme, incluyendo errores, estado y preservación de procedencia; una degradación honesta no equivale a traducción satisfactoria.
- **Semántica:** si se pretende certificar `soleado` / `calor`, demostrar un mecanismo general y verificable de preservación de significado, no una solución específica del test.
- **Integración:** mantener una llamada al proveedor, ausencia de efectos secundarios y respeto por M377 y autoridades previas.
- **Verificación:** acordar RED contractual antes de cambios productivos; ejecutar pruebas focales, Ruff, regresión pertinente y certificación local con evidencia reproducible.
- **Documentación:** sincronizar raíz, estado maestro, registro de capacidades y documentación del bloque en la etapa de cierre autorizada.

### 8. Exclusiones explícitas

No se autoriza crear módulos/servicios/gestores paralelos, instalar un traductor implícito, usar respuestas prefabricadas, añadir una segunda llamada LLM, alterar metadatos para aparentar conformidad, modificar tests sin reconciliación ni certificar GREEN-02 por la sola presencia del prompt español.

### 9. Próxima decisión gobernada

El próximo paso **no es implementar GREEN-02**. Corresponde aceptar o ajustar este registro documental y determinar si la brecha se planifica como una capacidad general futura bajo autoridad existente. Cualquier reapertura productiva exige un RED reconciliado y una decisión GO explícita; de lo contrario permanece el HOLD.

---

**Trazabilidad:** registro elaborado a partir de los informes de inspección recibidos. No representa certificación de ejecución local, ni modificación del repositorio, ni verificación de la suite completa.

## Adenda A — Decisión de viabilidad arquitectónica GREEN-02

**Clasificación:** decisión documental de viabilidad, no autorización productiva.  
**Dictamen:** VIABILIDAD CONDICIONADA / NO-GO PRODUCTIVO.  
**GREEN-02:** HOLD CONTRACTUAL. **M377:** HOLD INTACT. **STOP_PRODUCTIVE:** ACTIVE.

### A.1. Alcance y evidencia

Esta decisión desarrolla las brechas G-01, G-02 y G-03 ya registradas. Se basa en las inspecciones de fronteras, contratos RED y reconciliación documental citadas en las secciones 2 a 7; no declara una auditoría nueva ni prueba exhaustiva de ausencia de mecanismos. La incorporación inicial del registro y su referencia en `ROBY_XI_2_CURRENT_TRUTH.md` fueron reportadas y verificadas localmente antes de esta adenda. Las afirmaciones históricas del encabezado y cierre originales describen el estado de preparación del registro, no su estado posterior de incorporación.

### A.2. Decisión por ruta candidata

| Ruta | Alcance acreditado o límite | Decisión |
|---|---|---|
| Prompt español/inglés existente | Prevención anterior a la inferencia; no garantiza idioma visible | PARCIAL / INSUFICIENTE |
| Detección del idioma visible | No se demostró fiabilidad frente a código, citas y contenido mixto | NO CERTIFICADA |
| Normalización superficial | No preserva necesariamente el significado | INSUFICIENTE |
| Reglas fijas o respuestas ad hoc | No constituyen transformación semántica general | NO AUTORIZADAS |
| Segunda llamada al proveedor | Contradice el contrato de una sola inferencia | EXCLUIDA |
| `ConversationalTranslation` | Reconoce traducción solicitada explícitamente; no acredita traducción automática de salidas | NO EXTENDER IMPLÍCITAMENTE |
| Contención en `UnifiedExperienceLayer` | Frontera existente para presentación; no acredita corrección semántica | CANDIDATA CONDICIONADA |

### A.3. Resolución de autoridad

Se preservan las competencias comprobadas de `EnvironmentInferenceRequestPort`, `HouseholdConversationStyle`, `LocalProviderRuntimeAdapter`, `UnifiedExperienceLayer` y `ConversationalTranslation`. La frontera de presentación es un punto de integración candidato, **no** una atribución automática de capacidad de traducción. No se autoriza nuevo detector, traductor, gestor, circuito paralelo ni cambio de autoridad.

### A.4. Condición discriminante

Detectar y contener una respuesta en inglés no solicitado **no** satisface por sí solo el RED semántico que requiere conservar `soleado` y `calor` para la respuesta meteorológica simulada. La abstención honesta puede ser un tratamiento válido de incumplimiento, pero no equivale a transformación semántica satisfactoria. No se debilitan los doce RED ni se aceptan glosarios, respuestas fijas, manipulación de metadatos o una segunda inferencia para simular cumplimiento.

### A.5. Condiciones acumulativas para un futuro GO

1. Evidencia de una ruta general y verificable de preservación semántica dentro de una autoridad canónica existente.
2. Detección y tratamiento gobernados con cobertura explícita de falsos positivos, citas, código, rutas y términos técnicos.
3. Español argentino por defecto e inglés explícito con precedencia correcta, sin alterar `rationale`, `origin`, `network_access_performed` ni otra procedencia aplicable.
4. Una sola inferencia por turno y ausencia de efectos secundarios o autoridades paralelas.
5. Los doce RED intactos, pruebas focales y regresión pertinente, Ruff y certificación local reproducible antes de cualquier declaración GREEN.
6. Decisión GO productiva explícita y sincronización documental posterior, sin afectar EXP-02B/EXP-02C ni M377.

**Cierre de decisión:** REAPERTURA ANALÍTICA ADMITIDA; GO PRODUCTIVO DENEGADO. La brecha G-03 sigue sin mecanismo general demostrado. GREEN-02 continúa en HOLD CONTRACTUAL y `STOP_PRODUCTIVE` permanece ACTIVE. Esta adenda no cambia código, tests, registro de capacidades ni estado del documento maestro.
