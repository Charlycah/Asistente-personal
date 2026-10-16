# ROBY XI.2 M360.0.a — Inventario funcional verificable

## 1. Propósito

M360.0.a inaugura la auditoría general M360.0 sin agregar ni modificar capacidades
productivas. Su objetivo es establecer, desde la base oficial M359, qué puede hacer
realmente ROBY, qué existe sólo como infraestructura o contrato, qué está parcialmente
integrado y qué permanece pendiente.

Este documento es una fotografía funcional basada en código, pruebas y documentación
del repositorio. No reemplaza las auditorías arquitectónica, de calidad ni documental
previstas para M360.0.b, M360.0.c y M360.0.d.

## 2. Reglas aplicadas

La revisión respetó las autoridades y reglas de raíz:

- un único núcleo cognitivo;
- integración antes que duplicación;
- extensión antes que reemplazo;
- capacidades externas mediante contrato, adaptador, configuración, activación,
  `ToolGatewayManager`, trazabilidad y pruebas;
- ninguna capacidad se considera completa sólo porque exista una clase o documento;
- no se modificaron credenciales, configuración privada ni comportamiento productivo.

## 3. Método y escala de estado

Se inspeccionaron:

- documentos canónicos de raíz;
- `CHANGELOG.md` y documentos de milestones;
- módulos de `app/`, `application/`, `core/`, `domain/`, `infrastructure/` e
  `interfaces/`;
- pruebas específicas y contractuales;
- colección completa de pytest.

La colección local de esta base informa **8665 pruebas**, coincidente con la base M359
entregada.

Estados usados:

- **Completo interno**: contrato, implementación, gobernanza y pruebas existen para el
  alcance declarado, aunque pueda faltar exposición conversacional o hardware real.
- **Operativo gobernado**: existe un flujo integrado utilizable bajo configuración y
  permisos explícitos.
- **Parcial**: hay modelos, servicios o adaptadores reutilizables, pero no un flujo
  completo de extremo a extremo para el objetivo deseado.
- **Fundacional**: define arquitectura o estado lógico, sin I/O real ni integración
  física.
- **Pendiente**: no se encontró implementación operativa demostrable.

## 4. Resumen ejecutivo

La auditoría corrige la percepción de que la mayoría de las capacidades físicas debía
comenzarse desde cero. ROBY ya tiene una base visual gobernada considerable, un runtime
de escritorio, audio conversacional, Calendar, Gmail, planificación, memoria,
observabilidad, clima, noticias e inteligencia documental.

La principal brecha no es la ausencia de “cerebro”, sino la conexión entre capacidades
internas y experiencias operativas cotidianas. Por ejemplo, la visión puede capturar y
analizar una imagen puntual, pero todavía no ofrece de manera certificada todas las
órdenes conversacionales previstas ni vigilancia continua. Del mismo modo, el runtime
de escritorio no equivale a un administrador completo de Windows.

Los bloques realmente pendientes son Bluetooth operativo, Samsung Watch 7, MCP, Home
Assistant, cámara IP, impresión/escaneo gobernado y un puente Android con I/O real.

## 5. Inventario funcional consolidado

| Área | Estado M360.0.a | Evidencia principal | Alcance real y brecha |
|---|---|---|---|
| Núcleo conversacional | Operativo gobernado | `OfficialConversationGateway`, `CanonicalCognitiveCore`, serie M347 | Intención, contexto, estrategia, decisión, trazabilidad y respuesta integradas. |
| Planificación cognitiva | Completo interno | `ConversationStrategyPlanner`, M347.5–M347.7, planificación histórica | Planifica y selecciona acciones cognitivas; no equivale todavía a un plan de tarea durable y ejecutable de varios pasos. |
| Memoria | Operativo gobernado | M347.10–M347.13 y subsistemas históricos | Contexto, política de escritura, recuperación relevante y continuidad entre sesiones. |
| Tool Gateway | Operativo gobernado | `ToolGatewayManager`, capability registry y flujos externos | Autoridad única para herramientas; debe reutilizarse en toda expansión futura. |
| Voz y audio conversacional | Operativo gobernado | `app/audio_engine.py`, `voice_input.py`, Vosk, pruebas M300–M311 | Reconocimiento y salida de voz, sesión y diagnóstico. La estabilidad depende de configuración y hardware local. |
| Audio inteligente | Completo interno / parcial operativo | `core/intelligent_audio`, RP.24.7 | Gobierno de modos, consentimiento, actividad de voz y sesiones. No controla todavía volumen, salida Bluetooth o Spotify como experiencia integral. |
| Clima | Operativo gobernado | `infrastructure/weather`, runtime conversacional y pruebas | Consulta actual y pronóstico con integración conversacional. |
| Noticias/actualidad | Operativo gobernado | `app/intelligent_news.py`, current-affairs router y pruebas | Recuperación y presentación contextual; la relevancia temática puede seguir refinándose. |
| Google Calendar | Operativo gobernado | M348.2–M348.8, `infrastructure/calendar` | Contrato, adaptador, configuración, resiliencia, consultas y creación gobernada. |
| Gmail | Operativo gobernado condicionado | M226–M229, `infrastructure/mail` | OAuth, transporte, composición, diagnóstico, reintentos y certificación. Requiere credenciales/configuración reales. |
| Escritorio ROBY | Operativo gobernado | M176, M235, `desktop_ui.py`, bootstrap | Interfaz Tkinter y runtime personal unificado. No es todavía un Windows Workspace Manager. |
| Windows Workspace Manager | Parcial | desktop runtime, presenters y utilidades dispersas | Existe integración de escritorio, pero no una autoridad única certificada para brillo, Wi-Fi, energía, Bluetooth, ventanas, escritorios virtuales y aplicaciones. |
| Cámara USB / Vision Core | Completo interno | M348.9, `OfficialVisionCore`, camera adapter | Captura puntual local, autorizada y gobernada. Sin captura continua ni vigilancia. |
| Detección de personas | Completo interno | M349, `PersonDetector`, OpenCV HOG | Detecta presencia/cantidad en un frame. Falta exposición conversacional certificada de extremo a extremo. |
| Detección de rostros | Completo interno | M350, `FaceDetector` | Localiza rostros; no identifica personas ni usa biometría. |
| OCR | Completo interno | M351, `TextExtractor`, Tesseract/OpenCV opcional | Extrae texto de una captura. La lectura semántica se realiza después mediante capacidades documentales. |
| QR y códigos de barras | Completo interno | M352, `VisualCodeDecoder` | Decodifica sin abrir enlaces ni ejecutar contenido automáticamente. |
| Detección de objetos | Completo interno condicionado | M353, detector OpenCV DNN | Requiere modelo ONNX local provisto/configurado; entrega etiquetas y confianza. |
| Comprensión de escenas | Completo interno | M354, scene fusion | Fusiona personas, rostros, objetos, OCR y códigos. No infiere emociones, identidad, intención ni propiedad. |
| “IA visual” ampliada | Parcial | Vision Core + M349–M354 | La base cognitiva existe. Faltan flujos conversacionales completos, configuración simple, validación manual con webcam real y capacidades como seguimiento/movimiento. |
| Document reading | Operativo / parcial según formato | `app/document_reading.py`, M340.4 | Lectura de documentos conectada al runtime; debe verificarse por tipos y proveedores en auditorías posteriores. |
| Document Classification | Completo interno | M355 | Clasificación gobernada y probada. |
| Structured Document Extraction | Completo interno | M356 | Extracción estructurada separada y gobernada. |
| Web Enrichment | Completo interno / operativo condicionado | M357 | Enriquece con evidencia web bajo gobernanza y disponibilidad de proveedor. |
| Document Intelligence | Completo interno | M358 | Analiza completitud, consistencia, faltantes y observaciones. |
| Governed Document Actions | Operativo gobernado condicionado | M359 | Prepara y confirma recordatorio, guardado de resumen y apertura de fuente explícita mediante Tool Gateway. No modifica documentos ni paga facturas. |
| Mobile/Android conceptual | Fundacional | M110–M115, `core/mobile_*` | Modela elegibilidad, estados, presencia y contexto. No hay app/agente Android, transporte, sensores, notificaciones o GPS reales. |
| Samsung Watch 7 | Pendiente | Sin gateway, adaptador Wear OS o pruebas específicas | Las menciones genéricas de “watch” no representan integración con el reloj. Requerirá puente Android/Wear OS y permisos de salud/notificaciones. |
| Bluetooth Manager | Pendiente | Sólo referencias documentales/contextuales | No se encontró contrato/adaptador operativo para enumerar, conectar, desconectar o consultar batería de periféricos. |
| MCP | Pendiente | Referencias en documentación M348 | No hay servidor/cliente MCP, catálogo MCP ni pruebas. Debe integrarse subordinado al Tool Gateway. |
| Home Assistant | Pendiente | Alternativa documentada, sin código operativo | No hay cliente, autenticación, entidades, eventos ni acciones gobernadas. |
| Cámara IP | Pendiente | Sin RTSP/ONVIF/API específica | Vision Core puede ser reutilizado, pero falta una fuente IP gobernada y su política de privacidad. |
| Impresión y escaneo | Pendiente como gateway | Referencias dispersas, PDF export existente | Exportar PDF no equivale a imprimir o escanear. Falta contrato, adaptador Windows, confirmación y pruebas con cola/dispositivo. |
| Automatización física | Parcial/futura | agenda, autonomía gobernada y Tool Gateway | Hay fundamentos cognitivos y de gobernanza, pero no workflows físicos completos sobre Windows/dispositivos. |

## 6. Evaluación de las opciones prioritarias del usuario

### 6.1 Cámara USB + Visión

**Estado: avanzado, no pendiente desde cero.**

Ya existen captura puntual gobernada, detección de personas y rostros, OCR, QR/códigos,
objetos y fusión de escena. El trabajo siguiente no debería crear otro Vision Gateway,
sino cerrar la experiencia operativa sobre `OfficialVisionCore`:

1. confirmar composición y configuración real de cada analizador;
2. exponer intenciones conversacionales seguras;
3. validar manualmente con la webcam del equipo;
4. definir movimiento como capacidad separada;
5. evitar reconocimiento de identidad o emociones sin una decisión explícita posterior.

### 6.2 Audio inteligente

**Estado: base sólida, control del sistema pendiente.**

ROBY ya gobierna escucha, consentimiento, actividad de voz, sesiones y diagnóstico. El
control de volumen, selección de salida, Spotify y transferencia a auriculares debe
construirse sobre una autoridad de audio del sistema operativo, no dentro del motor de
reconocimiento de voz.

### 6.3 Bluetooth Manager

**Estado: pendiente.**

Debe diseñarse como capacidad externa única, con lectura separada de mutaciones. Listar
y consultar estado pueden ser operaciones de bajo riesgo; conectar, desconectar o
cambiar perfiles requieren confirmación y trazabilidad.

### 6.4 Windows Manager / Escritorio inteligente

**Estado: parcialmente avanzado.**

Existe runtime de escritorio y UI oficial, pero falta el administrador del entorno
Windows. Debe inventariarse primero toda utilidad existente y luego consolidarse bajo
una sola autoridad, evitando mezclar interfaz gráfica con mutación del sistema.

### 6.5 Cámara IP

**Estado: pendiente, reutilizable sobre visión.**

Conviene incorporarla sólo después de cerrar Vision Core para webcam. La fuente IP debe
ser un adaptador nuevo detrás del contrato visual, con activación explícita, credenciales
canónicas, límites de retención y prohibición de vigilancia silenciosa.

### 6.6 Android

**Estado: fundación lógica existente, integración física pendiente.**

No corresponde reescribir `core/mobile_*`. El siguiente paso real es definir transporte,
identidad del dispositivo, permisos, protocolo de eventos y agente Android mínimo.

### 6.7 Impresora

**Estado: pendiente.**

Debe separar: descubrir impresoras, consultar cola, preparar impresión, confirmar e
imprimir. El escaneo constituye otra capacidad y probablemente otro adaptador.

### 6.8 IA visual

**Estado: avanzada en percepción objetiva; incompleta como experiencia.**

ROBY ya puede producir observaciones visuales gobernadas. No debe presentar inferencias
de emociones como hechos ni tomar decisiones sensibles a partir de ellas. La prioridad
es completar conversación, configuración y pruebas reales antes de ampliar modelos.

### 6.9 Samsung Watch 7

**Estado: pendiente y dependiente del puente móvil.**

La ruta recomendada es Samsung Watch 7 → Wear OS/Health Connect o APIs disponibles →
agente Android autorizado → gateway móvil de ROBY. Bluetooth directo desde Windows no
debe asumirse suficiente para datos de salud, notificaciones o sensores.

## 7. Capacidades que ya reducen el trabajo futuro

- `ToolGatewayManager` y registro de capacidades para ejecutar acciones gobernadas.
- políticas de consentimiento y privacidad ya aplicadas a visión y audio;
- adaptadores intercambiables para cámara y analizadores visuales;
- runtime móvil lógico y modelos de presencia/contexto;
- runtime de escritorio unificado;
- credenciales canónicas en `.roby/credentials.json`;
- planificación, trazabilidad, memoria y observabilidad consolidadas;
- patrones completos de Calendar y Gmail que sirven como referencia para nuevas
  integraciones externas.

## 8. Hallazgos y riesgos para las siguientes auditorías

1. **Documentación canónica desactualizada:** `README.md` aún declara M347.15 como base
   actual y `architecture_rules.md` conserva M347.15/M348.1. M360.0.a registra el hecho
   sin corregirlo, porque la reconciliación documental pertenece a M360.0.d.
2. **Existencia no implica exposición:** varias capacidades visuales son APIs internas
   probadas, pero sus propios documentos declaran que faltan intenciones conversacionales
   o pruebas manuales con hardware real.
3. **Dependencias opcionales:** OpenCV, Tesseract, pyzbar y modelos ONNX pueden no estar
   instalados/configurados en todos los entornos.
4. **Hardware no certificado:** la suite prueba contratos y adaptadores con dobles; no
   demuestra por sí sola webcam, Bluetooth, impresora, Android o Watch reales.
5. **Nombres históricos:** algunos milestones antiguos describen fundamentos lógicos y
   no capacidades operativas; el roadmap debe evitar interpretarlos como producto final.
6. **Seguridad y privacidad:** cámara continua, reconocimiento de identidad, emociones,
   salud y vigilancia requieren decisiones separadas y no están autorizados por la base.

## 9. Recomendación de dirección

No iniciar todavía un gran módulo nuevo. Continuar M360.0 en el orden acordado:

1. **M360.0.b — Auditoría arquitectónica:** localizar autoridades, contratos,
   composición, rutas productivas y piezas aisladas.
2. **M360.0.c — Auditoría de calidad:** cobertura por subsistema, tipos de pruebas,
   dependencias opcionales y validaciones manuales pendientes.
3. **M360.0.d — Auditoría documental:** reconciliar versiones, contradicciones y reglas
   de raíz.
4. **M360.0.e — Plan maestro:** priorizar cierres basados en evidencia.

Como hipótesis inicial —no todavía como roadmap definitivo— los cierres de mayor valor
parecen ser:

1. experiencia conversacional y certificación manual del Vision Core existente;
2. consolidación del Windows Workspace Manager y audio del sistema;
3. Bluetooth Manager;
4. puente Android;
5. Samsung Watch 7;
6. impresora/escáner y cámara IP;
7. MCP y Home Assistant sobre el Tool Gateway existente.

## 10. Criterio de cierre M360.0.a

M360.0.a se considera documentalmente completo cuando:

- el inventario distingue operación, implementación interna, fundación y pendiente;
- cada gran afirmación señala una evidencia del repositorio;
- no se añade código productivo;
- la suite sigue coleccionando 8665 pruebas;
- Ruff y la regresión completa son validados por el usuario antes de declarar la base
  canónica.
