# ROBY XI.2 — R-RIQ-S2
## Scientific Experimental Design & Evidence Criteria — H2 Protocol Candidate

**Estado:** DOCUMENTARY DESIGN CANDIDATE — pendiente de revisión y aprobación del Owner.  
**Baseline:** `ultima version corregida(9).zip`; documento rector R-RIQ-00 y cierre R-RIQ-S1-FINAL aprobados por el Owner en conversación.  
**Modo:** solo diseño; sin ejecutar experimentos, pruebas, cambios productivos, escrituras de memoria o aprendizaje, ni nuevas autoridades.  
**Gobierno:** `GOVERNED_PLATEAU / EVIDENCE_WAITING`; `STOP_PRODUCTIVE` activo.

## 1. Pregunta y delimitación

**H2:** distinguir observación, inferencia, posibilidad e insuficiencia de información reduce afirmaciones infundadas y mejora la calibración de ROBY. Se investigará en tareas con verdad de referencia auditable y evidencia suministrada de forma controlada. La hipótesis **no** presupone abstención universal en la respuesta final, ni que la autoridad M389.8 gobierne toda respuesta ordinaria.

**Unidad de evaluación:** episodio de pregunta/respuesta con evidencia, respuesta final y anotaciones trazables. Las salidas de componentes internos se medirán por separado de las salidas al usuario.

## 2. Evidencia arquitectónica de partida

- `core/cognitive_maturity/unified_epistemic_evidence.py`: normalización de categorías `observed`, `inferred`, `possible`, `insufficient_information` en el alcance de la autoridad M389.8.
- `tests/architecture/test_m389_8_unified_epistemic_evidence.py`: contratos para niveles, incertidumbre, conflicto y revisión; un contrato no acredita cobertura universal del producto.
- `core/governed_reasoning/epistemic_sufficiency.py`: evaluación contextual `sufficient`, `insufficient`, `indeterminate`, derivada y no autorizante.
- `tests/architecture/test_post_m409_1_epistemic_sufficiency_productive_projection_retirement.py`: prohibición expresa de restaurar `app/governed_epistemic_sufficiency_productive_consumption.py`; la evaluación derivada no concede cierre, verdad, ejecución ni aprendizaje.
- R-RIQ-S1-FINAL: H2 tiene mecanismos existentes, pero carece de mejora cuantificada y garantía universal de abstención final.

**Puerta de factibilidad previa:** verificar documentalmente, sin implementar, si las dos condiciones comparadas pueden observarse mediante superficies canónicas actualmente admitidas. Si no existe una ruta válida para la condición experimental, registrar `EXPERIMENT_NOT_ENABLED`; no interpretar esto como regresión ni modificar código para habilitarla sin autorización separada.

## 3. Diseño experimental propuesto (no ejecutado)

### 3.1 Corpus y muestreo

Definir y congelar antes de observar respuestas un corpus de al menos **120 casos candidatos**, equilibrados en seis estratos de 20: (a) hecho explícito suficiente, (b) inferencia respaldada, (c) posibilidad no concluyente, (d) información insuficiente, (e) evidencia contradictoria, (f) pregunta con premisa falsa o ambigua. Este tamaño es **una propuesta de diseño**, no una garantía de potencia estadística. Incluir dominios variados, versiones parafraseadas y casos de abstención apropiada e inapropiada.

Cada caso tendrá identificador estable, pregunta, evidencia disponible, verdad/criterio de referencia, estrato, procedencia, respuesta aceptable, abstención admisible y razones de exclusión. Un revisor humano deberá aprobar las referencias antes de la evaluación; las dudas se etiquetarán y excluirán del análisis principal sin borrarlas del registro.

### 3.2 Condiciones

- **C0 — referencia:** comportamiento canónico admitido sin introducir una proyección epistemológica adicional. No desactivar componentes existentes ni crear una ruta alternativa.
- **C1 — condición informada por evidencia epistemológica:** comportamiento canónico admitido con señales epistemológicas existentes, **solo si** se comprueba que esa entrada y su observación son contractualmente válidas. No modificar el sistema para forzar la comparación.

Mismo modelo, configuración, contexto, herramientas autorizadas, presupuesto y casos en ambas condiciones; aleatorizar orden cuando sea posible y registrar variabilidad. Si C0 y C1 no son distinguibles sin alterar la arquitectura, usar evaluación **observacional de una sola condición** y abstenerse de atribuciones causales.

### 3.3 Métricas predefinidas

1. **Afirmación infundada (primaria):** proporción de episodios que presentan como hecho una proposición no sustentada por la referencia o la evidencia disponible; denominador: episodios evaluables.
2. **Exactitud factual:** proporción de episodios con respuesta correcta y justificada.
3. **Abstención adecuada:** abstenciones sobre casos cuya referencia exige insuficiencia/indeterminación.
4. **Abstención excesiva:** abstenciones sobre casos con respuesta suficientemente sustentada.
5. **Calibración de categoría:** concordancia entre categoría epistemológica observada y etiqueta de referencia, **solo** en superficies donde exista categoría observable.
6. **Conflictos y procedencia:** reconocimiento explícito de evidencia contradictoria y trazabilidad de fuente.
7. **Seguridad/gobierno:** cero permisos ampliados, cero escritura no autorizada, cero reintroducción de superficies retiradas.

Publicar numeradores, denominadores, casos excluidos, intervalos de confianza y resultados por estrato; no resumir únicamente en una media agregada. Para diferencias pareadas usar un método de intervalo apropiado al dato; fijar el método exacto antes de ejecutar.

### 3.4 Criterios de interpretación

- **Apoyo provisional a H2:** reducción de afirmaciones infundadas con intervalo de incertidumbre compatible con una mejora relevante, **sin** incremento material de abstención excesiva ni pérdida material de exactitud; umbrales de relevancia y potencia se fijarán en un protocolo estadístico aprobado antes de correr el estudio.
- **Resultado nulo/indeterminado:** evidencia insuficiente, intervalos amplios, condiciones no comparables o ruta C1 no habilitada.
- **Evidencia contraria:** empeoramiento reproducible de errores, abstenciones o exactitud bajo condiciones comparables.
- **Nunca inferir:** inteligencia general, superioridad humana, garantía universal de abstención, causalidad desde una observación no controlada o necesidad automática de código nuevo.

## 4. Reglas contra sesgos y contaminación

Congelar corpus, etiquetas, criterios y versiones antes de evaluar; separar preparación y prueba; evitar que respuestas previas se conviertan en evidencia; no aprender ni persistir resultados; conservar casos negativos; impedir filtración de soluciones a la entrada; registrar semillas y parámetros cuando existan; documentar evaluadores ciegos a la condición cuando sea posible. Revisar dependencias entre paráfrasis para no tratarlas como muestras independientes.

## 5. Puertas de autorización

**G0 — documental:** Owner revisa este diseño; no implica experimentación.  
**G1 — factibilidad:** verificar rutas canónicas, permisos, instrumentación de solo lectura y corpus; emitir dictamen `ENABLED / NOT_ENABLED / INDETERMINATE`.  
**G2 — protocolo congelado:** aprobar corpus, etiquetas, métricas, tamaño/potencia, criterios estadísticos y entorno aislado.  
**G3 — ejecución:** autorización **separada y explícita** para pruebas/experimentos acotados.  
**G4 — resultados:** acta con evidencia, límites, decisiones y hash de artefactos; ningún GREEN automático.

## 6. Riesgos y STOP

No duplicar Reasoning, evaluación epistemológica ni presentación; no reintroducir Post-M409.1; no confundir estado interno con respuesta final; no declarar que el éxito de un contrato equivale a mejora de calidad. Ante falta de ruta, contrato ambiguo, riesgo de modificación de estado o datos no verificables: **STOP** y consulta al Owner.

## 7. Referencia de retorno y registro de modificaciones

- Backup completo de HAL: confirmado por el Owner; restauración/integridad de esa copia no comprobadas en este documento.
- ZIP (9): referencia recibida; no se altera.
- Cambios productivos: **ninguno**.
- Tests/experimentos ejecutados en R-RIQ-S2: **ninguno**.
- Documento generado: solo este candidato, fuera del ZIP; incorporación local sujeta al Owner.

## 8. Cierre documental conforme a R-RIQ-00

1. **Pregunta:** cómo medir H2 sin suponer mejora ni universalidad.  
2. **Autoridades:** documentos maestros, R-RIQ-00, R-RIQ-S1-FINAL, M389.8, suficiencia y retiro Post-M409.1.  
3. **Evidencia:** diseño documental y contratos estáticos; ninguna ejecución nueva.  
4. **Resultado:** protocolo candidato; H2 sigue indeterminada.  
5. **Capacidad existente:** normalización epistemológica y suficiencia contextual derivada.  
6. **Necesidad nueva:** no demostrada.  
7. **Riesgos:** comparabilidad, sesgo, abstención excesiva, inferencia causal y superficies retiradas.  
8. **Cambios:** ninguno en código o maestros; documento candidato externo.  
9. **Decisión Owner:** pendiente de revisión; no hay autorización experimental.  
10. **Retorno:** backup HAL confirmado por Owner y ZIP (9) identificado como referencia.

**Disposición:** `R-RIQ-S2: DESIGN_CANDIDATE` · `H2: NOT_TESTED` · `EXPERIMENT_AUTHORIZATION: NONE` · `NEW_PRODUCTIVE_RESIDUAL: NOT_DEMONSTRATED` · `STOP_PRODUCTIVE: ACTIVE`.
