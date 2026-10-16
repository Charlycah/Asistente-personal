# ROBY XI.2 M360.0.c — Auditoría de calidad

## 1. Propósito y alcance

M360.0.c audita la calidad verificable de la base canónica M360.0.b, validada localmente
con **Ruff limpio y 8665 pruebas aprobadas**. No introduce comportamiento productivo,
no cambia contratos y no refactoriza componentes. Su finalidad es convertir evidencia
estática, pruebas existentes y decisiones arquitectónicas en un registro de riesgos y
prioridades para las siguientes versiones.

La ausencia de un hallazgo en este documento no equivale a certificación formal de
seguridad, rendimiento, cobertura o hardware. La auditoría utiliza señales reproducibles
y revisión estructural; no presenta estimaciones como métricas de cobertura.

## 2. Base de evidencia

Se inspeccionaron los árboles productivos `app/`, `application/`, `core/`, `domain/`,
`engines/`, `handlers/`, `infrastructure/`, `interfaces/` y los paquetes históricos
`m3/` a `m7/`, junto con `tests/`, documentación canónica y reglas arquitectónicas.

La fotografía estática observada contiene:

| Indicador | Resultado |
|---|---:|
| Archivos Python productivos | 911 |
| Archivos de prueba `test_*.py` | 643 |
| Líneas productivas no vacías aproximadas | 138969 |
| Excepciones amplias `Exception`/`BaseException` | 129 |
| Bloques `except:` desnudos | 0 |
| Marcadores TODO/FIXME/XXX | 0 |
| Validación canónica del usuario | Ruff limpio; 8665 tests |

Las cifras de líneas son indicadores de tamaño, no una valoración automática. Las
búsquedas de pruebas por nombre sirven para localizar evidencia, no para afirmar
cobertura de líneas o ramas.

## 3. Fortalezas confirmadas

1. **Estabilidad observable:** la suite canónica completa pasa y Ruff no reporta
   infracciones.
2. **Contratos históricos protegidos:** existen pruebas por hitos y una prueba explícita
   de unificación estructural.
3. **Ausencia de deuda textual obvia:** no se detectaron TODO, FIXME o XXX productivos.
4. **Manejo de excepciones disciplinado:** no existen `except:` desnudos.
5. **Gobernanza probada:** Calendar, Gmail, documentos, visión y ejecución de
   herramientas poseen contratos y pruebas específicas.
6. **Separación de proveedores:** las integraciones maduras usan contratos, adaptadores,
   composición localizada y activación explícita.
7. **Base refactorizable:** la amplitud de la suite permite reducir complejidad mediante
   cambios incrementales protegidos.

## 4. Riesgos de calidad

### Q1 — Concentración de complejidad en puntos de composición

Se observaron funciones especialmente extensas:

- `app/desktop_ui.py::run` — aproximadamente 572 líneas;
- `app/runtime_root_factory.py::build_runtime_root` — aproximadamente 564 líneas;
- `core/runtime_composition_root/root.py::compose` — aproximadamente 456 líneas;
- `core/cognitive_pipeline.py::process_turn` — aproximadamente 325 líneas;
- `core/cognitive_planning/diagnostics.py::run` — aproximadamente 319 líneas;
- `core/governed_provider_execution_adapter/adapter.py::execute` — aproximadamente 287 líneas.

El riesgo no es sólo legibilidad: estas funciones concentran wiring, políticas,
compatibilidad y control de flujo, haciendo más costoso aislar fallos o incorporar nuevas
capacidades. No deben reescribirse de una vez. Deben caracterizarse con pruebas y
extraerse por responsabilidades pequeñas.

**Prioridad:** alta, no bloqueante.

### Q2 — Archivos productivos de gran tamaño

Entre los archivos más extensos se encuentran:

- `app/desktop_ui.py`;
- `app/cognitive_agenda_manager.py`;
- `app/vision_core.py`;
- `app/secure_medication_registry.py`;
- `app/current_affairs_router.py`;
- `core/executive_runtime_integration/integration.py`;
- `core/cognitive_pipeline.py`.

El tamaño no demuestra mala calidad, pero señala módulos donde cambios futuros pueden
producir regresiones transversales. Vision y Desktop deben consolidarse mediante
fachadas y componentes internos, preservando sus APIs públicas.

**Prioridad:** alta para Desktop y composición; media para módulos estables.

### Q3 — Excepciones amplias

Se identificaron 129 capturas de `Exception` o `BaseException`. Algunas son apropiadas
en fronteras de resiliencia, UI, diagnóstico, proveedores y procesos residentes. Sin
embargo, una captura amplia puede ocultar errores de programación si no registra causa,
contexto y estado degradado.

Antes de modificar estas capturas debe clasificarse cada una como:

- frontera de aislamiento legítima;
- compatibilidad histórica;
- recuperación con observabilidad;
- captura reemplazable por excepciones específicas.

**Prioridad:** media. No realizar sustituciones masivas.

### Q4 — Evidencia desigual entre áreas

La búsqueda nominal de archivos/pruebas localizó abundante evidencia para runtime,
Gmail, memoria, voz, Calendar y móvil lógico. Vision, Desktop y Tool Gateway poseen
pruebas, pero su criticidad aconseja reforzar escenarios integrados y de composición.
Bluetooth, MCP, Home Assistant e impresión no tienen pruebas operativas porque todavía
no existen como capacidades implementadas; esto es una brecha de roadmap, no una falla
actual de cobertura.

**Prioridad:** alta antes de habilitar hardware o mutaciones externas.

### Q5 — Riesgo de divergencia documental

La base tiene changelogs, reglas, inventarios y documentos por hitos. Esa riqueza crea
riesgo de que cantidades de tests, estado de capacidades o autoridad canónica queden
obsoletos en documentos históricos. M360.0.d deberá distinguir explícitamente:

- documentos normativos vigentes;
- registros históricos inmutables;
- inventarios temporales;
- guías operativas actualizables.

**Prioridad:** alta para M360.0.d.

### Q6 — Paquetes históricos y superficie de mantenimiento

Los paquetes `m3/` a `m7/` y múltiples capas de compatibilidad amplían la superficie del
repositorio. No deben eliminarse sólo por antigüedad: primero hay que demostrar imports,
rutas de ejecución, contratos y consumidores. Cualquier retiro requerirá inventario de
referencias y una versión dedicada.

**Prioridad:** media, diferida.

### Q7 — Ausencia de medición formal de cobertura y complejidad

La suite es extensa, pero el repositorio auditado no aporta en esta fase un umbral
canónico de cobertura de líneas/ramas ni un presupuesto formal de complejidad. El número
de pruebas no sustituye esas métricas. Introducirlas de forma abrupta podría producir
ruido; primero debe medirse una línea base sin convertirla inmediatamente en bloqueo.

**Prioridad:** media.

## 5. Auditoría por atributo

| Atributo | Estado | Evidencia | Acción recomendada |
|---|---|---|---|
| Correctitud regresiva | Fuerte | 8665 tests | Mantener suite completa por versión |
| Estilo estático | Fuerte | Ruff limpio | No relajar configuración |
| Arquitectura | Fuerte con concentración | M360.0.b y composition roots extensos | Refactor incremental protegido |
| Gobernanza | Fuerte | Tool Gateway y contratos | Añadir pruebas negativas por integración |
| Observabilidad | Parcialmente fuerte | diagnósticos y runtimes | Revisar excepciones amplias |
| Mantenibilidad | Media | módulos/funciones extensos | Caracterización y extracción gradual |
| Cobertura formal | No certificada | gran suite, sin métrica canónica aquí | Medir baseline en fase dedicada |
| Documentación | Amplia pero dispersa | múltiples autoridades documentales | Reconciliar en M360.0.d |
| Hardware real | No certificado | dobles y contratos | Certificación por dispositivo |
| Seguridad externa | Gobernada, no universalmente certificada | permisos/consentimiento | threat model por gateway físico |

## 6. Matriz de prioridades

### P0 — Preservación obligatoria

- Ruff y suite completa deben permanecer verdes.
- No introducir rutas externas fuera de `ToolGatewayManager`.
- No eliminar compatibilidad histórica sin prueba de no uso.
- No usar el número de tests como sustituto de cobertura formal.

### P1 — Próximas acciones de calidad

1. Completar M360.0.d para reconciliar autoridades documentales.
2. Crear pruebas de caracterización alrededor de `build_runtime_root`, `compose`,
   `process_turn` y `desktop_ui` antes de cualquier extracción.
3. Definir una lista revisada de capturas amplias en fronteras críticas.
4. Exigir pruebas negativas de permiso, consentimiento, indisponibilidad y degradación
   para cada nueva integración física.

### P2 — Mejoras incrementales

- Medir cobertura y complejidad como baseline informativo.
- Separar wiring declarativo de políticas en composition roots.
- Reducir responsabilidades de Desktop UI sin cambiar comportamiento.
- Consolidar la composición productiva de Vision.
- Documentar estado de paquetes históricos antes de considerar retiros.

### P3 — Evolución posterior

- Presupuestos de complejidad por módulo crítico.
- Pruebas de rendimiento y soak tests de runtimes residentes.
- fault injection para proveedores y dispositivos.
- certificación por hardware real y sistema operativo.

## 7. Puertas de calidad para nuevas capacidades

Bluetooth, Windows, Android Bridge, Watch, cámara IP, impresora, MCP y Home Assistant
no deberán considerarse completas sin:

1. contrato neutral y modelos normalizados;
2. adaptador reemplazable;
3. activación explícita y diagnóstico;
4. permisos, consentimiento y confirmación según riesgo;
5. ejecución exclusiva mediante Tool Gateway;
6. pruebas unitarias, negativas, de composición y degradación;
7. trazabilidad sin exponer secretos ni datos sensibles;
8. documentación de límites y procedimiento de desactivación;
9. certificación separada cuando dependa de hardware real.

## 8. Decisiones de M360.0.c

- La base se clasifica como **estable y ampliamente probada**, no como libre de deuda.
- La deuda prioritaria es complejidad concentrada, no proliferación de errores visibles.
- No se autoriza una limpieza masiva de excepciones, runtimes o paquetes históricos.
- Los futuros refactors deben ser pequeños, caracterizados y reversibles.
- M360.0.d deberá resolver la jerarquía documental antes del roadmap maestro M360.0.e.
- La próxima implementación funcional deberá elegir una capacidad ya fundamentada y
  aplicar las puertas de calidad definidas aquí.

## 9. Criterio de cierre

M360.0.c queda cerrada cuando:

- este documento está presente;
- los changelogs registran la auditoría sin alterar historia canónica;
- las pruebas documentales de M360.0.c pasan;
- Ruff y la suite completa permanecen verdes en la validación local.

No se modifica comportamiento productivo ni se declara cobertura formal inexistente.
