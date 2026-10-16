# ROBY XI.2 M360.0.b — Auditoría arquitectónica

## 1. Propósito

M360.0.b audita la arquitectura real de la base M360.0.a validada por el usuario
(**8661 tests, Ruff limpio**) sin introducir comportamiento productivo nuevo. El objetivo
es identificar autoridades canónicas, composition roots, registros, contratos,
adaptadores, rutas de ejecución y piezas históricas reutilizables antes de iniciar nuevas
integraciones físicas.

## 2. Reglas rectoras verificadas

La auditoría toma como autoridad `architecture_rules.md` y aplica especialmente:

- un único núcleo cognitivo;
- una única fuente de verdad por responsabilidad;
- integración antes que duplicación;
- extensión antes que reemplazo;
- capacidades externas mediante contrato, adaptador, configuración, activación,
  `ToolGatewayManager`, trazabilidad y pruebas;
- preservación del sistema canónico de credenciales en `.roby/credentials.json`;
- prohibición de conectar directamente planificadores o autoridades cognitivas con
  proveedores externos.

## 3. Método

Se inspeccionaron estáticamente:

- `app/`, `application/`, `core/`, `domain/`, `infrastructure/` e `interfaces/`;
- composition roots, bootstraps, gateways, registries, runtimes y wiring;
- mapas de autoridad y catálogos de capacidades;
- implementaciones de Calendar, Gmail, visión, audio, escritorio, móvil y documentos;
- documentación canónica y pruebas contractuales existentes.

Esta etapa clasifica arquitectura; no certifica hardware ni sustituye la auditoría de
calidad M360.0.c.

## 4. Arquitectura canónica observada

### 4.1 Frontera conversacional

`app/official_conversation_gateway.py` constituye la frontera oficial para turnos de
usuario. Debe seguir siendo la entrada pública y no debe reemplazarse por gateways
específicos de cada integración.

### 4.2 Composición operativa

`app/official_runtime_composition.py` expone el grafo operacional oficial y
`OfficialROBYRuntime` actúa como autoridad de ciclo de vida. La composición reutiliza:

- `LocalRuntimeBootstrap`;
- `RuntimeCompositionRoot`;
- `LongLivedRuntimeLifecycle`;
- `RuntimeHeartbeatSupervisor`;
- registros residentes, readiness, recuperación y observabilidad.

Conclusión: los nuevos módulos deben incorporarse como residentes o capacidades del
grafo oficial; no deben crear un segundo runtime principal.

### 4.3 Mapa de autoridades cognitivas

`app/cognitive_authority_map.py` ya asigna una autoridad primaria única por
responsabilidad. Entre las asignaciones relevantes se encuentran:

- entrada: `conversation_entry`;
- contexto: `context_continuity`;
- memoria: `memory_gateway`;
- conocimiento: `knowledge_runtime`;
- razonamiento: `governed_reasoning`;
- planificación: `executive_planning`;
- decisión: `unified_cognitive_coordination`;
- ejecución: `capability_orchestrator`;
- gobernanza: `governed_capability_routing`;
- observabilidad: `runtime_observability`.

Este mapa reduce el riesgo de crear nuevos “cerebros” para visión, Windows, Bluetooth,
Android o Watch.

### 4.4 Autoridad de herramientas

`core/tool_gateway.py` conserva la autoridad canónica para registrar, gobernar y ejecutar
herramientas. Calendar, Gmail y acciones documentales ofrecen patrones reutilizables.
Toda nueva integración externa debe entrar por esta autoridad.

## 5. Registros existentes y límites de responsabilidad

La presencia de varios registros no implica necesariamente duplicación; representan
niveles diferentes:

| Registro | Responsabilidad correcta | Riesgo si se amplía fuera de alcance |
|---|---|---|
| `app/runtime_capability_registry.py` | Catálogo semántico/operativo de capacidades del runtime | Convertirlo en segundo Tool Gateway |
| `core/capability_registry.py` | Modelo y snapshot de capacidades declaradas | Usarlo como ejecutor o registro de dispositivos |
| `core/device_capabilities/registry.py` | Estado y compatibilidad de capacidades de un dispositivo | Usarlo para ejecutar acciones físicas |
| `app/resident_component_registry.py` | Ciclo de vida y salud de componentes residentes | Registrar herramientas de usuario |
| `app/cognitive_authority_map.py` | Autoridad primaria por responsabilidad cognitiva | Resolver disponibilidad física o permisos |

Directiva: mantener estos registros separados, pero documentar explícitamente sus
fronteras y evitar que cualquiera adquiera responsabilidad de ejecución ajena.

## 6. Composition roots y bootstraps

Se encontraron múltiples nombres relacionados con composición, pero con funciones
complementarias:

- `app/official_runtime_composition.py`: composición operacional canónica;
- `app/runtime_root_factory.py`: fábrica de ensamblaje;
- `core/runtime_composition_root/`: modelo y preparación del root;
- `core/local_runtime_bootstrap/`: arranque local;
- `app/desktop_bootstrap.py`: adaptación de escritorio;
- composiciones específicas de Calendar y Gmail: integración localizada.

No se recomienda fusionarlos en M360.0. Su coexistencia es aceptable mientras la única
salida operacional permanezca subordinada a `OfficialROBYRuntime`.

## 7. Auditoría por subsistema

### 7.1 Visión

Arquitectura avanzada y correctamente separada:

- contratos y modelos en `core/`;
- adaptadores de cámara y analizadores en `infrastructure/camera` e
  `infrastructure/vision`;
- capacidades de persona, rostro, OCR, QR, objetos y escena;
- políticas de consentimiento y contexto visual.

Brecha arquitectónica: confirmar un único composition path productivo para todos los
analizadores y una sola exposición conversacional. No crear otro Vision Gateway.

### 7.2 Escritorio y Windows

Existe `desktop_runtime_integration`, `desktop_bootstrap`, UI y adaptadores operativos,
pero no una autoridad completa de sistema operativo. La ampliación correcta es definir
un contrato único de workspace/Windows detrás del Tool Gateway y separar:

- consultas de estado;
- acciones reversibles;
- acciones sensibles;
- UI y presentación.

### 7.3 Audio

El reconocimiento y la conversación por voz están desacoplados del gobierno de audio.
El futuro control de volumen, salida y multimedia no debe entrar en `voice_input.py` ni
en el motor Vosk. Debe ser una capacidad de sistema/Windows independiente y gobernada.

### 7.4 Bluetooth

No existe autoridad operativa. Puede reutilizar:

- `DeviceCapabilityRegistry` para describir disponibilidad y requisitos;
- Tool Gateway para ejecución;
- consentimiento y trazabilidad existentes;
- runtime de escritorio como entorno anfitrión.

Debe crearse un único contrato Bluetooth, no varios managers por tipo de dispositivo.

### 7.5 Android y Samsung Watch 7

`core/mobile_*` modela estados, contexto, presencia y continuidad, pero no transporte
físico. La arquitectura recomendada es:

Android Agent autorizado → Mobile Gateway → Tool Gateway → runtime oficial.

El Watch 7 debe integrarse a través del puente Android/Wear OS cuando la API lo requiera.
No debe diseñarse como acceso Bluetooth directo independiente salvo para funciones que
se demuestren compatibles y seguras.

### 7.6 Calendar y Gmail

Son los mejores patrones existentes para nuevas integraciones:

- composición localizada;
- contratos y adaptadores;
- credenciales canónicas;
- activación explícita;
- Tool Gateway;
- diagnóstico y trazabilidad.

MCP, Home Assistant, impresora y cámara IP deberían copiar este patrón arquitectónico,
no implementar flujos laterales.

### 7.7 Documentos

La cadena clasificación → extracción → inteligencia → acciones gobernadas está bien
separada. `core/document_actions` depende del Tool Gateway y no debe convertirse en un
motor general de automatización.

## 8. Solapamientos y riesgos detectados

1. **Abundancia de runtimes históricos:** numerosos módulos contienen “runtime” en el
   nombre. No son automáticamente duplicados, pero dificultan identificar la ruta
   productiva sin documentación de composición.
2. **Registros con nombres similares:** capability registries de distinto nivel pueden
   confundirse. Sus responsabilidades deben quedar fijadas en M360.0.d.
3. **Autoridades documentales desactualizadas:** reglas y README todavía declaran bases
   históricas. La reconciliación corresponde a M360.0.d.
4. **Capacidades internas no siempre conectadas:** una implementación probada puede no
   estar incluida en el grafo oficial o expuesta conversacionalmente.
5. **Dobles y contratos versus hardware real:** la arquitectura soporta pruebas sin
   certificar dispositivos físicos.
6. **Expansión directa desde planners:** cualquier nuevo proveedor conectado fuera del
   Tool Gateway violaría la arquitectura canónica.
7. **Autonomía física prematura:** Bluetooth, Windows, impresora, cámara y Watch exigen
   políticas explícitas por riesgo antes de habilitar mutaciones.

## 9. Decisiones arquitectónicas para la Fase II

### Decisión A — Preservar el runtime oficial

Toda nueva capacidad será ensamblada en `OfficialROBYRuntime` mediante composición
localizada y no mediante un segundo proceso cognitivo principal.

### Decisión B — Tool Gateway como única frontera de ejecución

Vision, Windows, Bluetooth, Android, Watch, impresora, MCP y Home Assistant no tendrán
rutas de ejecución paralelas.

### Decisión C — Device Capability Registry sólo describe

Puede registrar estado, versión, acceso y features de dispositivos, pero no ejecutar
conexiones, comandos ni automatizaciones.

### Decisión D — Separar lectura de mutación

Consultar batería, dispositivos o estado tendrá contratos distintos de conectar,
desconectar, imprimir, grabar, cambiar audio o controlar energía.

### Decisión E — Watch depende del puente móvil

Samsung Watch 7 se planificará después del Android Bridge mínimo, salvo evidencia técnica
posterior que justifique una ruta adicional limitada.

### Decisión F — Visión se consolida, no se reescribe

La prioridad será certificar composición, conversación y hardware del Vision Core
existente.

## 10. Orden técnico recomendado tras M360.0

Este orden sigue siendo provisional hasta completar calidad y documentación:

1. consolidación del grafo oficial y trazabilidad de capacidades existentes;
2. cierre operativo de Vision USB;
3. Windows Workspace Manager y audio del sistema;
4. Bluetooth Manager;
5. Android Bridge mínimo;
6. Samsung Watch 7;
7. impresora/escáner y cámara IP;
8. MCP;
9. Home Assistant;
10. workflows físicos gobernados.

## 11. Entregables para M360.0.c

La auditoría de calidad deberá medir por subsistema:

- pruebas unitarias, contractuales, integración y manuales;
- rutas realmente incluidas en la composición oficial;
- dependencias opcionales y degradación;
- cobertura de errores y permisos;
- hardware pendiente de certificación;
- pruebas de regresión y tiempos de suite.

## 12. Criterio de cierre

M360.0.b queda completo cuando:

- las autoridades canónicas están identificadas;
- los registros y composition roots tienen límites explícitos;
- cada integración futura tiene una ruta arquitectónica aprobada;
- no se modifica comportamiento productivo;
- Ruff y la regresión completa permanecen verdes en la validación local del usuario.
