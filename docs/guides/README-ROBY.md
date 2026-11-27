# ROBY XI.2 — Guía de inicio y mapa del repositorio

ROBY es un asistente personal y familiar de escritorio. Permite conversar en
español, consultar colecciones locales autorizadas y utilizar fuentes externas
cuando la capacidad correspondiente está habilitada. El punto de entrada
ejecutable es [main.py](../../main.py). El estado operativo y los límites de las
capacidades se registran en [Current Truth](../../ROBY_XI_2_CURRENT_TRUTH.md).

## Arranque en Windows

Desde la raíz del proyecto, con el entorno de Python de la instalación activo,
ejecutá:

```powershell
python -B main.py --doctor
python -B main.py
```

En una instalación nueva, `python -B main.py --setup` crea o valida
`.roby/config.json`. Para seleccionar explícitamente el modelo local durante esa
configuración, usá `python -B main.py --setup --model llama3:latest`.
Si el proveedor configurado es Ollama, el servicio debe estar iniciado y
tener disponible el modelo que indica el archivo de configuración.

La voz depende del backend elegido. Con Vosk, una ruta de modelo relativa se
resuelve desde la raíz de esa copia del proyecto. Al trabajar con varias copias,
se puede indicar una ruta absoluta en la configuración local. Las credenciales
se guardan en `.roby/credentials.json` y se mantienen fuera de Git.

## Qué podés probar desde el chat

| Capacidad | Ejemplo | Requisito |
| --- | --- | --- |
| Conversación local | «Hoy tuve un día complicado» → «¿Qué me recomendás?» | Proveedor de modelos disponible. |
| Búsqueda visual | «¿Me mostrás una imagen de un colibrí?» | Wikimedia Commons habilitada. |
| Consulta de actualidad | «Buscá información sobre nuevas misiones de la NASA» | Ruta de actualidad habilitada y resultados utilizables. |
| Catálogo musical | «Buscá algo de música» | Colección local configurada con `ROBY_LOCAL_MUSIC_ROOT`. |
| Reproducción musical | «La opción 1», después de recibir una lista, o «Poné música, Roby» | Catálogo y reproductor configurados. |
| Control de reproducción | «Buscá otra pista» o «Para Roby» | Reproducción iniciada por ROBY. |

## Dónde buscar en el árbol

| Ruta | Contenido |
| --- | --- |
| [app/](../../app/) | Composición del runtime, interfaz de escritorio y conexión de servicios. |
| [application/](../../application/) | Casos de uso y contratos de aplicación. |
| [core/](../../core/) | Capacidades cognitivas, políticas e integraciones centrales. |
| [domain/](../../domain/) | Modelos y reglas de dominio. |
| [infrastructure/](../../infrastructure/) | Adaptadores y servicios de infraestructura. |
| [interfaces/](../../interfaces/) | Interfaces de entrada y salida. |
| [tests/](../../tests/) | Pruebas funcionales y contratos de arquitectura. |
| [scripts/](../../scripts/) y [benchmarks/](../../benchmarks/) | Herramientas de mantenimiento y mediciones. |
| [docs/architecture/](../architecture/) y [docs/adr/](../adr/) | Arquitectura y decisiones técnicas. |
| [docs/guides/](./) | Guías de uso y de mantenimiento. |
| [docs/history/](../history/) y [evidence/](../../evidence/) | Historial y registros de validación. |

Para entender el diseño, consultá [VISION](../../VISION.md) y las
[reglas de arquitectura](../../architecture_rules.md). Para antecedentes de
cambios, consultá el [README de raíz](../../README.md) y el
[CHANGELOG](../../CHANGELOG.md).

## Revisión de archivos de raíz

Los puntos de entrada, los contratos de arquitectura y la documentación
canónica se consultan desde sus ubicaciones actuales. Los informes,
transcripciones de pruebas, parches históricos y paquetes antiguos de la raíz
son candidatos a inventario.

Para cada archivo candidato, registrá su ruta, propósito y referencias desde
código, pruebas, scripts o documentación. La
[limpieza conservadora M306.2](../ROOT_CLEANUP_M306_2.md) documenta ubicaciones de
archivo histórico. Revisá las referencias antes de proponer un movimiento y
volvé a comprobar el arranque y las pruebas que dependan de la ruta.
